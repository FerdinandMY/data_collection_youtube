"""
collect_videos.py
=================
Étape 1 — Collecte des métadonnées vidéo via yt-dlp
Recherche YouTube par mots-clés contextualisés Cameroun

Usage :
    python collect_videos.py --system all --max-per-query 15 --output data/raw/videos.csv
    python collect_videos.py --system francophone --subject mathematiques --level terminale
    python collect_videos.py --dry-run   # Affiche les requêtes sans lancer yt-dlp
"""

import subprocess
import json
import csv
import time
import argparse
import logging
import random
from pathlib import Path
from datetime import datetime
from typing import Optional

from config.keywords_config import (
    KEYWORDS_FR,
    KEYWORDS_EN,
    QUALITY_FILTERS,
    CSV_VIDEO_COLUMNS,
)

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/collect_videos.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

DELAY_BETWEEN_QUERIES = (3, 7)   # Secondes (min, max) — évite le rate-limit
OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ─────────────────────────────────────────────────────────────────────────────

def build_yt_dlp_search_command(query: str, max_results: int) -> list[str]:
    """
    Construit la commande yt-dlp pour une recherche YouTube.
    Retourne uniquement les métadonnées (pas de téléchargement vidéo).
    """
    return [
        "yt-dlp",
        f"ytsearch{max_results}:{query}",
        "--skip-download",
        "--print-json",
        "--no-warnings",
        "--ignore-errors",
        "--flat-playlist",           # Ne récupère que les métadonnées basiques
        "--extractor-args", "youtube:skip=dash,hls",
    ]


def build_yt_dlp_info_command(video_id: str) -> list[str]:
    """
    Récupère les métadonnées complètes d'une vidéo (vues, likes, durée, etc.)
    """
    return [
        "yt-dlp",
        f"https://www.youtube.com/watch?v={video_id}",
        "--skip-download",
        "--print-json",
        "--no-warnings",
        "--ignore-errors",
    ]


def parse_duration(duration_str) -> int:
    """Convertit la durée yt-dlp (secondes int ou string HH:MM:SS) en secondes."""
    if duration_str is None:
        return 0
    if isinstance(duration_str, (int, float)):
        return int(duration_str)
    try:
        parts = str(duration_str).split(":")
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return int(duration_str)
    except (ValueError, AttributeError):
        return 0


def passes_quality_filter(video_data: dict) -> tuple[bool, str]:
    """
    Vérifie qu'une vidéo respecte les filtres de qualité définis dans keywords_config.
    Retourne (True, "") si OK, (False, raison) sinon.
    """
    duration = parse_duration(video_data.get("duration"))
    views = video_data.get("view_count") or 0
    comments = video_data.get("comment_count") or 0

    if duration < QUALITY_FILTERS["min_duration_seconds"]:
        return False, f"Durée trop courte : {duration}s < {QUALITY_FILTERS['min_duration_seconds']}s"
    if duration > QUALITY_FILTERS["max_duration_seconds"]:
        return False, f"Durée trop longue : {duration}s > {QUALITY_FILTERS['max_duration_seconds']}s"
    if views < QUALITY_FILTERS["min_view_count"]:
        return False, f"Vues insuffisantes : {views} < {QUALITY_FILTERS['min_view_count']}"
    if comments < QUALITY_FILTERS["min_comment_count"]:
        return False, f"Commentaires insuffisants : {comments} < {QUALITY_FILTERS['min_comment_count']}"

    return True, ""


def extract_video_row(video_data: dict, system: str, level: str,
                       subject: str, query: str) -> dict:
    """Extrait les champs nécessaires depuis les métadonnées yt-dlp."""
    return {
        "video_id":       video_data.get("id", ""),
        "title":          video_data.get("title", ""),
        "channel_name":   video_data.get("uploader") or video_data.get("channel", ""),
        "channel_id":     video_data.get("channel_id", ""),
        "published_at":   video_data.get("upload_date", ""),
        "duration_seconds": parse_duration(video_data.get("duration")),
        "view_count":     video_data.get("view_count") or 0,
        "like_count":     video_data.get("like_count") or 0,
        "comment_count":  video_data.get("comment_count") or 0,
        "language":       "fr" if system == "francophone" else "en",
        "system":         system,
        "level":          level,
        "subject":        subject,
        "search_query":   query,
        "url":            f"https://www.youtube.com/watch?v={video_data.get('id', '')}",
    }


# ─────────────────────────────────────────────────────────────────────────────
# COLLECTE PRINCIPALE
# ─────────────────────────────────────────────────────────────────────────────

def search_videos_for_query(
    query: str,
    system: str,
    level: str,
    subject: str,
    max_results: int = 15,
    dry_run: bool = False,
) -> list[dict]:
    """
    Lance yt-dlp pour une requête et retourne une liste de dicts vidéo validés.
    """
    if dry_run:
        log.info(f"[DRY-RUN] Requête : {query!r}")
        return []

    cmd = build_yt_dlp_search_command(query, max_results)
    log.info(f"🔍 Recherche : {query!r} ({max_results} résultats max)")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8",
        )
    except subprocess.TimeoutExpired:
        log.warning(f"⏱️  Timeout pour la requête : {query!r}")
        return []
    except FileNotFoundError:
        log.error("❌ yt-dlp introuvable. Installez-le avec : pip install yt-dlp")
        raise

    videos = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            ok, reason = passes_quality_filter(data)
            if ok:
                row = extract_video_row(data, system, level, subject, query)
                if row["video_id"]:
                    videos.append(row)
                    log.info(f"  ✅ {row['title'][:60]} | vues={row['view_count']} | dur={row['duration_seconds']}s")
            else:
                log.debug(f"  ⛔ Filtré ({reason}) : {data.get('title', 'N/A')[:50]}")
        except json.JSONDecodeError:
            continue

    log.info(f"  → {len(videos)} vidéo(s) retenues pour : {query!r}")
    return videos


def collect_all_videos(
    systems: list[str] = None,
    subjects: list[str] = None,
    levels: list[str] = None,
    max_per_query: int = 15,
    output_file: str = "data/raw/videos.csv",
    dry_run: bool = False,
) -> list[dict]:
    """
    Itère sur toutes les combinaisons (système, matière, niveau, requête)
    et collecte les vidéos éducatives camerounaises.
    """
    all_keywords = {
        "francophone": KEYWORDS_FR,
        "anglophone": KEYWORDS_EN,
    }

    if systems is None:
        systems = ["francophone", "anglophone"]

    all_videos: list[dict] = []
    seen_ids: set[str] = set()
    total_queries = 0
    total_retained = 0

    for system in systems:
        keyword_bank = all_keywords[system]
        selected_subjects = subjects or list(keyword_bank.keys())

        for subject in selected_subjects:
            if subject not in keyword_bank:
                log.warning(f"⚠️  Matière inconnue pour {system} : {subject}")
                continue

            selected_levels = levels or list(keyword_bank[subject].keys())

            for level in selected_levels:
                if level not in keyword_bank[subject]:
                    continue

                queries = keyword_bank[subject][level]

                for query in queries:
                    total_queries += 1
                    videos = search_videos_for_query(
                        query=query,
                        system=system,
                        level=level,
                        subject=subject,
                        max_results=max_per_query,
                        dry_run=dry_run,
                    )

                    for v in videos:
                        if v["video_id"] not in seen_ids:
                            seen_ids.add(v["video_id"])
                            all_videos.append(v)
                            total_retained += 1

                    if not dry_run:
                        delay = random.uniform(*DELAY_BETWEEN_QUERIES)
                        log.debug(f"  💤 Pause {delay:.1f}s")
                        time.sleep(delay)

    log.info(f"\n{'='*60}")
    log.info(f"📊 RÉSUMÉ COLLECTE VIDÉOS")
    log.info(f"  Requêtes exécutées : {total_queries}")
    log.info(f"  Vidéos uniques retenues : {total_retained}")
    log.info(f"{'='*60}")

    if not dry_run and all_videos:
        save_to_csv(all_videos, output_file, CSV_VIDEO_COLUMNS)

    return all_videos


def save_to_csv(data: list[dict], filepath: str, columns: list[str]) -> None:
    """Sauvegarde une liste de dicts en CSV avec les colonnes spécifiées."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)
    log.info(f"💾 Sauvegardé : {path} ({len(data)} lignes)")


# ─────────────────────────────────────────────────────────────────────────────
# POINT D'ENTRÉE CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Collecte de vidéos YouTube éducatives — Cameroun"
    )
    parser.add_argument(
        "--system",
        choices=["francophone", "anglophone", "all"],
        default="all",
        help="Système scolaire cible (défaut: all)",
    )
    parser.add_argument(
        "--subject",
        nargs="+",
        default=None,
        help="Matière(s) à collecter (ex: mathematiques svt). Défaut: toutes.",
    )
    parser.add_argument(
        "--level",
        nargs="+",
        default=None,
        help="Niveau(x) à collecter (ex: terminale form4_5). Défaut: tous.",
    )
    parser.add_argument(
        "--max-per-query",
        type=int,
        default=15,
        help="Nombre max de résultats par requête (défaut: 15)",
    )
    parser.add_argument(
        "--output",
        default="data/raw/videos.csv",
        help="Fichier CSV de sortie (défaut: data/raw/videos.csv)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche les requêtes sans lancer yt-dlp",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    systems = ["francophone", "anglophone"] if args.system == "all" else [args.system]
    collect_all_videos(
        systems=systems,
        subjects=args.subject,
        levels=args.level,
        max_per_query=args.max_per_query,
        output_file=args.output,
        dry_run=args.dry_run,
    )
