"""
validate_dataset.py
===================
Étape 3 — Validation, nettoyage et rapport EDA du dataset collecté
Prépare le CSV final conforme aux exigences de l'Agent A1 (PRD)

Usage :
    python validate_dataset.py --videos data/raw/videos.csv --comments data/raw/comments.csv
    python validate_dataset.py --report-only    # Génère uniquement le rapport EDA
"""

import csv
import json
import argparse
import logging
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

from config.keywords_config import (
    QUALITY_FILTERS,
    CSV_VIDEO_COLUMNS,
    CSV_COMMENTS_COLUMNS,
)

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

OUTPUT_DIR = Path("data/validated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Colonnes obligatoires pour A1 (PRD)
REQUIRED_COMMENT_COLS = {"video_id", "text", "author_likes", "reply_count"}
REQUIRED_VIDEO_COLS   = {"video_id", "title", "level", "subject", "system"}

# Seuil minimum de commentaires par vidéo pour inclusion dans dataset final
MIN_COMMENTS_FINAL = QUALITY_FILTERS["min_comments_per_video"]

# ─────────────────────────────────────────────────────────────────────────────
# CHARGEMENT
# ─────────────────────────────────────────────────────────────────────────────

def load_csv(filepath: str) -> tuple[list[dict], list[str]]:
    """Charge un CSV et retourne (rows, fieldnames)."""
    path = Path(filepath)
    if not path.exists():
        log.error(f"❌ Fichier introuvable : {filepath}")
        return [], []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    log.info(f"📂 Chargé : {filepath} — {len(rows)} lignes")
    return rows, fieldnames


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

class ValidationReport:
    """Accumule les erreurs et avertissements de validation."""

    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def error(self, msg: str):
        self.errors.append(msg)
        log.error(f"  ❌ {msg}")

    def warning(self, msg: str):
        self.warnings.append(msg)
        log.warning(f"  ⚠️  {msg}")

    def ok(self, msg: str):
        self.info.append(msg)
        log.info(f"  ✅ {msg}")

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> dict:
        return {
            "valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
        }


def validate_videos(videos: list[dict], report: ValidationReport) -> list[dict]:
    """Valide et nettoie les métadonnées vidéo."""
    log.info("\n── Validation VIDÉOS ──")

    if not videos:
        report.error("Aucune vidéo dans le dataset")
        return []

    # Vérifier les colonnes obligatoires
    present_cols = set(videos[0].keys())
    missing_cols = REQUIRED_VIDEO_COLS - present_cols
    if missing_cols:
        report.error(f"Colonnes manquantes dans videos.csv : {missing_cols}")
    else:
        report.ok(f"Toutes les colonnes obligatoires présentes : {REQUIRED_VIDEO_COLS}")

    # Dédupliquer par video_id
    seen = set()
    clean_videos = []
    duplicates = 0
    for v in videos:
        vid_id = v.get("video_id", "").strip()
        if not vid_id:
            report.warning("video_id vide détecté — ligne ignorée")
            continue
        if vid_id in seen:
            duplicates += 1
            continue
        seen.add(vid_id)
        clean_videos.append(v)

    if duplicates:
        report.warning(f"{duplicates} doublon(s) supprimé(s) dans videos.csv")
    report.ok(f"{len(clean_videos)} vidéos uniques après déduplication")

    # Vérifier les champs numériques
    bad_numeric = 0
    for v in clean_videos:
        for field in ["view_count", "like_count", "comment_count", "duration_seconds"]:
            try:
                int(v.get(field) or 0)
            except ValueError:
                bad_numeric += 1
                v[field] = 0

    if bad_numeric:
        report.warning(f"{bad_numeric} valeur(s) numérique(s) corrigée(s) à 0")

    # Vérifier la distribution système/niveau/matière
    systems = Counter(v.get("system", "?") for v in clean_videos)
    levels = Counter(v.get("level", "?") for v in clean_videos)
    subjects = Counter(v.get("subject", "?") for v in clean_videos)

    report.ok(f"Distribution système : {dict(systems)}")
    report.ok(f"Distribution niveaux : {dict(levels)}")
    report.ok(f"Distribution matières : {dict(subjects)}")

    if len(clean_videos) < 50:
        report.warning(f"Peu de vidéos ({len(clean_videos)}). Cible recommandée : 200+")

    return clean_videos


def validate_comments(
    comments: list[dict],
    valid_video_ids: set[str],
    report: ValidationReport,
) -> list[dict]:
    """Valide et nettoie les commentaires."""
    log.info("\n── Validation COMMENTAIRES ──")

    if not comments:
        report.error("Aucun commentaire dans le dataset")
        return []

    # Vérifier les colonnes obligatoires (PRD Agent A1)
    present_cols = set(comments[0].keys())
    missing_cols = REQUIRED_COMMENT_COLS - present_cols
    if missing_cols:
        report.error(f"Colonnes manquantes dans comments.csv (requises par A1) : {missing_cols}")
    else:
        report.ok(f"Colonnes A1 obligatoires présentes : {REQUIRED_COMMENT_COLS}")

    clean_comments = []
    stats = {
        "empty_text": 0,
        "unknown_video_id": 0,
        "duplicates": 0,
    }
    seen_comment_ids = set()

    for c in comments:
        # Texte vide
        text = (c.get("text") or "").strip()
        if not text:
            stats["empty_text"] += 1
            continue

        # video_id inconnu
        vid_id = c.get("video_id", "").strip()
        if vid_id not in valid_video_ids:
            stats["unknown_video_id"] += 1
            continue

        # Déduplications par comment_id
        cmt_id = c.get("comment_id", "").strip()
        if cmt_id and cmt_id in seen_comment_ids:
            stats["duplicates"] += 1
            continue
        if cmt_id:
            seen_comment_ids.add(cmt_id)

        # Corriger les types numériques
        c["author_likes"] = int(c.get("author_likes") or 0)
        c["reply_count"]  = int(c.get("reply_count") or 0)
        c["text"]         = text

        clean_comments.append(c)

    for key, count in stats.items():
        if count > 0:
            report.warning(f"{count} commentaire(s) rejetés — {key}")

    report.ok(f"{len(clean_comments)} commentaires valides après nettoyage")

    # Vérifier la distribution des commentaires par vidéo
    comments_per_video = Counter(c["video_id"] for c in clean_comments)
    too_few = [vid for vid, cnt in comments_per_video.items()
               if cnt < MIN_COMMENTS_FINAL]

    if too_few:
        report.warning(
            f"{len(too_few)} vidéo(s) ont moins de {MIN_COMMENTS_FINAL} commentaires "
            f"— elles seront exclues du dataset final"
        )

    avg_comments = (
        sum(comments_per_video.values()) / len(comments_per_video)
        if comments_per_video else 0
    )
    report.ok(f"Moyenne commentaires/vidéo : {avg_comments:.1f}")
    report.ok(f"Max commentaires/vidéo : {max(comments_per_video.values(), default=0)}")
    report.ok(f"Min commentaires/vidéo : {min(comments_per_video.values(), default=0)}")

    return clean_comments, comments_per_video, too_few


# ─────────────────────────────────────────────────────────────────────────────
# RAPPORT EDA
# ─────────────────────────────────────────────────────────────────────────────

def generate_eda_report(
    videos: list[dict],
    comments: list[dict],
    comments_per_video: Counter,
    validation_report: ValidationReport,
) -> dict:
    """Génère un rapport EDA complet au format JSON."""

    # Statistiques vidéos
    view_counts = [int(v.get("view_count") or 0) for v in videos]
    durations   = [int(v.get("duration_seconds") or 0) for v in videos]
    systems_dist  = Counter(v.get("system", "?") for v in videos)
    levels_dist   = Counter(v.get("level", "?") for v in videos)
    subjects_dist = Counter(v.get("subject", "?") for v in videos)
    langs_dist    = Counter(v.get("language", "?") for v in videos)

    # Statistiques commentaires
    text_lengths = [len(c.get("text", "")) for c in comments]
    reply_counts = [int(c.get("reply_count") or 0) for c in comments]
    like_counts  = [int(c.get("author_likes") or 0) for c in comments]

    def safe_mean(lst): return sum(lst) / len(lst) if lst else 0
    def safe_max(lst):  return max(lst) if lst else 0
    def safe_min(lst):  return min(lst) if lst else 0

    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "validation": validation_report.summary(),

        "videos": {
            "total": len(videos),
            "by_system": dict(systems_dist),
            "by_level": dict(levels_dist),
            "by_subject": dict(subjects_dist),
            "by_language": dict(langs_dist),
            "views": {
                "mean": round(safe_mean(view_counts)),
                "max": safe_max(view_counts),
                "min": safe_min(view_counts),
            },
            "duration_seconds": {
                "mean": round(safe_mean(durations)),
                "max": safe_max(durations),
                "min": safe_min(durations),
            },
        },

        "comments": {
            "total": len(comments),
            "per_video": {
                "mean": round(safe_mean(list(comments_per_video.values())), 1),
                "max": safe_max(list(comments_per_video.values())),
                "min": safe_min(list(comments_per_video.values())),
            },
            "text_length_chars": {
                "mean": round(safe_mean(text_lengths), 1),
                "max": safe_max(text_lengths),
                "min": safe_min(text_lengths),
            },
            "author_likes": {
                "mean": round(safe_mean(like_counts), 2),
                "max": safe_max(like_counts),
            },
            "reply_count": {
                "mean": round(safe_mean(reply_counts), 2),
                "max": safe_max(reply_counts),
            },
        },

        "a1_compatibility": {
            "required_columns_present": list(REQUIRED_COMMENT_COLS),
            "ready_for_pipeline": validation_report.is_valid,
            "note": (
                "Dataset prêt pour Agent A1 (Loader/Validator)"
                if validation_report.is_valid
                else "Corriger les erreurs ci-dessus avant d'alimenter le pipeline"
            ),
        },
    }
    return report


# ─────────────────────────────────────────────────────────────────────────────
# SAUVEGARDE DATASET FINAL
# ─────────────────────────────────────────────────────────────────────────────

def save_final_dataset(
    videos: list[dict],
    comments: list[dict],
    excluded_ids: list[str],
) -> None:
    """
    Sauvegarde le dataset final validé dans data/validated/.
    Exclut les vidéos avec trop peu de commentaires.
    """
    excluded_set = set(excluded_ids)

    final_videos   = [v for v in videos   if v["video_id"] not in excluded_set]
    final_comments = [c for c in comments if c["video_id"] not in excluded_set]

    # videos_final.csv
    vpath = OUTPUT_DIR / "videos_final.csv"
    with open(vpath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_VIDEO_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(final_videos)
    log.info(f"💾 {vpath} — {len(final_videos)} vidéos")

    # comments_final.csv
    cpath = OUTPUT_DIR / "comments_final.csv"
    with open(cpath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COMMENTS_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(final_comments)
    log.info(f"💾 {cpath} — {len(final_comments)} commentaires")

    log.info(f"\n✅ Dataset final prêt dans {OUTPUT_DIR}/")
    log.info(f"   → Alimentez Agent A1 avec : {cpath}")


# ─────────────────────────────────────────────────────────────────────────────
# POINT D'ENTRÉE PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def run_validation(
    videos_file: str = "data/raw/videos.csv",
    comments_file: str = "data/raw/comments.csv",
    report_only: bool = False,
) -> None:
    report = ValidationReport()

    log.info("\n" + "="*60)
    log.info("🔍 VALIDATION DU DATASET — YouTube Quality Analyzer")
    log.info("="*60)

    # Charger
    videos, _   = load_csv(videos_file)
    comments, _ = load_csv(comments_file)

    # Valider vidéos
    clean_videos = validate_videos(videos, report)
    valid_ids = {v["video_id"] for v in clean_videos}

    # Valider commentaires
    clean_comments, comments_per_video, low_count_ids = validate_comments(
        comments, valid_ids, report
    )

    # EDA
    log.info("\n── Génération du rapport EDA ──")
    eda = generate_eda_report(clean_videos, clean_comments, comments_per_video, report)

    eda_path = OUTPUT_DIR / "eda_report.json"
    with open(eda_path, "w", encoding="utf-8") as f:
        json.dump(eda, f, indent=2, ensure_ascii=False)
    log.info(f"📊 Rapport EDA sauvegardé : {eda_path}")

    # Afficher résumé EDA
    log.info("\n── Résumé EDA ──")
    log.info(f"  Vidéos totales         : {eda['videos']['total']}")
    log.info(f"  Commentaires totaux    : {eda['comments']['total']}")
    log.info(f"  Commentaires/vidéo moy : {eda['comments']['per_video']['mean']}")
    log.info(f"  Prêt pour pipeline A1  : {eda['a1_compatibility']['ready_for_pipeline']}")

    if not report_only:
        log.info("\n── Sauvegarde dataset final ──")
        save_final_dataset(clean_videos, clean_comments, low_count_ids)

    log.info("\n" + "="*60)
    status = "✅ VALIDATION RÉUSSIE" if report.is_valid else "❌ VALIDATION ÉCHOUÉE"
    log.info(status)
    log.info("="*60)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validation et EDA du dataset YouTube Cameroun"
    )
    parser.add_argument("--videos",   default="data/raw/videos.csv")
    parser.add_argument("--comments", default="data/raw/comments.csv")
    parser.add_argument("--report-only", action="store_true",
                        help="Génère le rapport EDA sans sauvegarder le dataset final")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_validation(
        videos_file=args.videos,
        comments_file=args.comments,
        report_only=args.report_only,
    )
