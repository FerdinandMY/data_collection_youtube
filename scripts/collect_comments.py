"""
collect_comments.py
===================
Étape 2 — Collecte des commentaires YouTube via yt-dlp
Entrée  : data/raw/videos.csv (produit par collect_videos.py)
Sortie  : data/raw/comments.csv (aligné avec PRD Agent A1)

Usage :
    python collect_comments.py --input data/raw/videos.csv --max-per-video 500
    python collect_comments.py --input data/raw/videos.csv --video-id dQw4w9WgXcQ
    python collect_comments.py --resume   # Reprend depuis le dernier checkpoint
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

from config.keywords_config import (
    QUALITY_FILTERS,
    CSV_COMMENTS_COLUMNS,
)

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/collect_comments.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

DELAY_BETWEEN_VIDEOS = (5, 12)       # Secondes — yt-dlp + YouTube rate-limit
CHECKPOINT_FILE = Path("data/raw/.checkpoint_comments.json")
OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# CHECKPOINT — REPRISE EN CAS D'INTERRUPTION
# ─────────────────────────────────────────────────────────────────────────────

def load_checkpoint() -> set[str]:
    """Charge la liste des video_ids déjà traités."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, "r") as f:
            data = json.load(f)
            return set(data.get("processed_ids", []))
    return set()


def save_checkpoint(processed_ids: set[str]) -> None:
    """Sauvegarde la liste des video_ids traités."""
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({
            "processed_ids": list(processed_ids),
            "last_updated": datetime.utcnow().isoformat(),
        }, f, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# COMMANDE yt-dlp POUR LES COMMENTAIRES
# ─────────────────────────────────────────────────────────────────────────────

def build_comments_command(video_id: str, max_comments: int) -> list[str]:
    """
    Construit la commande yt-dlp pour extraire les commentaires d'une vidéo.
    
    Notes importantes :
    - --write-comments : active l'extraction des commentaires
    - --extractor-args youtube:max_comments=N : limite le nombre de commentaires
    - --skip-download : n'est PAS compatible avec --write-comments (on utilise print-json)
    """
    return [
        "yt-dlp",
        f"https://www.youtube.com/watch?v={video_id}",
        "--skip-download",
        "--write-comments",
        "--print-json",
        "--no-warnings",
        "--ignore-errors",
        "--extractor-args",
        f"youtube:max_comments={max_comments},max_comment_depth=2",
    ]


def parse_comments_from_output(raw_json: dict, video_id: str) -> list[dict]:
    """
    Extrait et formate les commentaires depuis le JSON yt-dlp.
    Gère les commentaires top-level et les réponses (replies).
    
    Structure yt-dlp comments :
    [
        {
            "id": "...",
            "text": "...",
            "author": "...",
            "like_count": N,
            "reply_count": N,
            "timestamp": ...,
            "parent": "root" | "comment_id",
        }
    ]
    """
    comments_raw = raw_json.get("comments") or []
    if not comments_raw:
        log.warning(f"  ⚠️  Aucun commentaire trouvé pour {video_id}")
        return []

    rows = []
    for c in comments_raw:
        parent_id = c.get("parent", "root")
        is_reply = parent_id != "root"

        # Conversion timestamp Unix → ISO date
        ts = c.get("timestamp")
        published_at = (
            datetime.utcfromtimestamp(ts).isoformat()
            if isinstance(ts, (int, float)) else str(ts or "")
        )

        row = {
            "video_id":         video_id,
            "comment_id":       c.get("id", ""),
            "text":             c.get("text", "").strip(),
            "author":           c.get("author", ""),
            "author_likes":     c.get("like_count") or 0,
            "reply_count":      c.get("reply_count") or 0,
            "published_at":     published_at,
            "is_reply":         is_reply,
            "parent_id":        parent_id if is_reply else "",
            "language_detected": "",   # Sera rempli par Agent A2
        }

        # Ignorer les commentaires vides
        if row["text"]:
            rows.append(row)

    return rows


# ─────────────────────────────────────────────────────────────────────────────
# COLLECTE DES COMMENTAIRES
# ─────────────────────────────────────────────────────────────────────────────

def collect_comments_for_video(
    video_id: str,
    max_comments: int = 500,
) -> list[dict]:
    """
    Collecte les commentaires d'une vidéo via yt-dlp.
    Retourne une liste de dicts prêts pour le CSV.
    """
    cmd = build_comments_command(video_id, max_comments)
    log.info(f"💬 Collecte commentaires : {video_id} (max={max_comments})")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,   # 2 minutes max par vidéo
            encoding="utf-8",
        )
    except subprocess.TimeoutExpired:
        log.warning(f"  ⏱️  Timeout pour {video_id}")
        return []
    except FileNotFoundError:
        log.error("❌ yt-dlp introuvable. Installez-le avec : pip install yt-dlp")
        raise

    if result.returncode != 0 and not result.stdout:
        log.warning(f"  ⚠️  Erreur yt-dlp pour {video_id} : {result.stderr[:200]}")
        return []

    # Le JSON complet est sur la dernière ligne non-vide du stdout
    lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
    if not lines:
        log.warning(f"  ⚠️  Pas de sortie pour {video_id}")
        return []

    try:
        raw_json = json.loads(lines[-1])
    except json.JSONDecodeError:
        log.warning(f"  ⚠️  JSON invalide pour {video_id}")
        return []

    comments = parse_comments_from_output(raw_json, video_id)

    # Limiter au max défini (sécurité supplémentaire)
    comments = comments[:max_comments]
    log.info(f"  ✅ {len(comments)} commentaire(s) collecté(s) pour {video_id}")

    return comments


def collect_all_comments(
    input_file: str = "data/raw/videos.csv",
    output_file: str = "data/raw/comments.csv",
    max_per_video: int = None,
    target_video_id: str = None,
    resume: bool = False,
) -> None:
    """
    Lit videos.csv et collecte les commentaires pour chaque vidéo.
    Gère la reprise sur checkpoint et la déduplication.
    """
    max_per_video = max_per_video or QUALITY_FILTERS["max_comments_per_video"]
    
    # Charger les vidéos
    input_path = Path(input_file)
    if not input_path.exists():
        log.error(f"❌ Fichier introuvable : {input_file}")
        log.error("   Lancez d'abord collect_videos.py")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        videos = list(reader)

    if target_video_id:
        videos = [v for v in videos if v["video_id"] == target_video_id]
        if not videos:
            log.error(f"❌ video_id {target_video_id!r} non trouvé dans {input_file}")
            return

    log.info(f"📂 {len(videos)} vidéo(s) à traiter depuis {input_file}")

    # Checkpoint — vidéos déjà traitées
    processed_ids = load_checkpoint() if resume else set()
    if resume and processed_ids:
        log.info(f"🔄 Reprise : {len(processed_ids)} vidéo(s) déjà traitées, on continue.")

    # Préparer le fichier de sortie (append si resume, sinon écrase)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_mode = "a" if (resume and output_path.exists()) else "w"

    total_comments = 0
    total_videos_ok = 0
    total_videos_skipped = 0

    with open(output_path, write_mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=CSV_COMMENTS_COLUMNS,
            extrasaction="ignore"
        )
        if write_mode == "w":
            writer.writeheader()

        for i, video in enumerate(videos, 1):
            vid_id = video.get("video_id", "").strip()
            if not vid_id:
                continue

            if vid_id in processed_ids:
                log.debug(f"  ⏩ Déjà traité : {vid_id}")
                total_videos_skipped += 1
                continue

            log.info(f"\n[{i}/{len(videos)}] {video.get('title', vid_id)[:60]}")
            log.info(f"  📺 {video.get('url', '')}")

            comments = collect_comments_for_video(vid_id, max_per_video)

            if len(comments) >= QUALITY_FILTERS["min_comments_per_video"]:
                writer.writerows(comments)
                f.flush()    # Écriture immédiate (protection contre crash)
                total_comments += len(comments)
                total_videos_ok += 1
            else:
                log.warning(
                    f"  ⛔ Vidéo rejetée : seulement {len(comments)} commentaire(s) "
                    f"(min={QUALITY_FILTERS['min_comments_per_video']})"
                )

            processed_ids.add(vid_id)
            save_checkpoint(processed_ids)

            # Pause anti-rate-limit
            delay = random.uniform(*DELAY_BETWEEN_VIDEOS)
            log.debug(f"  💤 Pause {delay:.1f}s")
            time.sleep(delay)

    log.info(f"\n{'='*60}")
    log.info(f"📊 RÉSUMÉ COLLECTE COMMENTAIRES")
    log.info(f"  Vidéos traitées avec succès : {total_videos_ok}")
    log.info(f"  Vidéos ignorées (checkpoint) : {total_videos_skipped}")
    log.info(f"  Total commentaires collectés : {total_comments}")
    log.info(f"  Fichier de sortie : {output_path}")
    log.info(f"{'='*60}")


# ─────────────────────────────────────────────────────────────────────────────
# POINT D'ENTRÉE CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Collecte de commentaires YouTube — Cameroun"
    )
    parser.add_argument(
        "--input",
        default="data/raw/videos.csv",
        help="Fichier CSV des vidéos (produit par collect_videos.py)",
    )
    parser.add_argument(
        "--output",
        default="data/raw/comments.csv",
        help="Fichier CSV de sortie des commentaires",
    )
    parser.add_argument(
        "--max-per-video",
        type=int,
        default=500,
        help=f"Max commentaires par vidéo (défaut: 500)",
    )
    parser.add_argument(
        "--video-id",
        default=None,
        help="Traiter une seule vidéo (pour tests)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Reprendre depuis le dernier checkpoint",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    collect_all_comments(
        input_file=args.input,
        output_file=args.output,
        max_per_video=args.max_per_video,
        target_video_id=args.video_id,
        resume=args.resume,
    )
