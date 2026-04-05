# Phase 2 — Collecte des Données
## Vidéos Éducatives YouTube — Contexte Cameroun

> Systèmes : Francophone (BEPC / Bac) + Anglophone (GCE O-Level / A-Level)  
> Niveaux  : 3ème · Première · Terminale | Form 4-5 · Lower 6th · Upper 6th  
> Outil    : yt-dlp (sans clé API)

---

## Structure des Fichiers

```
data_collection/
├── config/
│   └── keywords_config.py      # Banque de ~200 requêtes + filtres qualité + schémas CSV
├── scripts/
│   ├── collect_videos.py       # Étape 1 — Collecte métadonnées vidéo
│   ├── collect_comments.py     # Étape 2 — Collecte des commentaires
│   └── validate_dataset.py     # Étape 3 — Validation + rapport EDA
├── notebooks/
│   └── phase2_data_collection_cameroun.ipynb   # Notebook Kaggle tout-en-un
├── data/
│   ├── raw/                    # Sorties brutes (videos.csv, comments.csv)
│   └── validated/              # Dataset final (videos_final.csv, comments_final.csv)
└── logs/                       # Logs d'exécution
```

---

## Installation

```bash
pip install yt-dlp langdetect
```

---

## Utilisation Rapide (3 Étapes)

### Étape 1 — Collecter les vidéos

```bash
# Tout collecter (francophone + anglophone, toutes matières, tous niveaux)
python scripts/collect_videos.py --system all --max-per-query 15 --output data/raw/videos.csv

# Cibler uniquement le francophone, maths + SVT, classes d'examen
python scripts/collect_videos.py \
  --system francophone \
  --subject mathematiques svt physique_chimie \
  --level troisieme terminale \
  --max-per-query 20

# Mode dry-run : afficher les requêtes sans exécuter
python scripts/collect_videos.py --dry-run
```

### Étape 2 — Collecter les commentaires

```bash
# Collecter les commentaires pour toutes les vidéos de videos.csv
python scripts/collect_comments.py --input data/raw/videos.csv --max-per-video 500

# Reprendre après une interruption (checkpoint automatique)
python scripts/collect_comments.py --resume

# Tester sur une seule vidéo
python scripts/collect_comments.py --video-id VIDEO_ID_ICI
```

### Étape 3 — Valider et générer le rapport EDA

```bash
python scripts/validate_dataset.py \
  --videos data/raw/videos.csv \
  --comments data/raw/comments.csv
```

---

## Sur Kaggle (Notebook tout-en-un)

Ouvrir `notebooks/phase2_data_collection_cameroun.ipynb` sur Kaggle.  
Toutes les étapes sont intégrées — exécuter les cellules dans l'ordre.

---

## Schéma des CSV Produits

### `data/validated/videos_final.csv`

| Colonne            | Type    | Description                                  |
|--------------------|---------|----------------------------------------------|
| `video_id`         | string  | ID YouTube unique                            |
| `title`            | string  | Titre de la vidéo                            |
| `channel_name`     | string  | Nom de la chaîne                             |
| `published_at`     | string  | Date de publication (YYYYMMDD)               |
| `duration_seconds` | int     | Durée en secondes                            |
| `view_count`       | int     | Nombre de vues                               |
| `like_count`       | int     | Nombre de likes                              |
| `comment_count`    | int     | Nombre total de commentaires                 |
| `language`         | string  | `fr` ou `en`                                 |
| `system`           | string  | `francophone` ou `anglophone`                |
| `level`            | string  | `troisieme`, `premiere`, `terminale`, etc.   |
| `subject`          | string  | Matière (ex: `mathematiques`, `svt`)         |
| `search_query`     | string  | Requête de recherche utilisée                |
| `url`              | string  | URL complète YouTube                         |

### `data/validated/comments_final.csv` → Input Agent A1

| Colonne              | Type    | Description                          |
|----------------------|---------|--------------------------------------|
| `video_id`           | string  | Clé de jointure avec videos_final    |
| `comment_id`         | string  | ID unique du commentaire             |
| `text`               | string  | **Texte du commentaire** (requis A1) |
| `author`             | string  | Nom de l'auteur                      |
| `author_likes`       | int     | **Likes reçus** (requis A1)          |
| `reply_count`        | int     | **Nb de réponses** (requis A1)       |
| `published_at`       | string  | Date du commentaire                  |
| `is_reply`           | bool    | True si réponse à un autre commentaire|
| `parent_id`          | string  | ID commentaire parent                |
| `language_detected`  | string  | Rempli par Agent A2                  |

---

## Mots-Clés (Résumé)

### Système Francophone (~120 requêtes)

| Matière              | Niveaux couverts             | Nb requêtes |
|----------------------|------------------------------|-------------|
| Mathématiques        | 3ème, Première, Terminale    | 24          |
| SVT                  | 3ème, Première, Terminale    | 18          |
| Physique-Chimie      | 3ème, Première, Terminale    | 18          |
| Français/Littérature | 3ème, Première, Terminale    | 18          |
| Histoire-Géo         | 3ème, Première, Terminale    | 15          |
| Économie             | Première, Terminale          | 12          |

### Système Anglophone (~80 requêtes)

| Subject              | Levels covered               | Nb queries |
|----------------------|------------------------------|------------|
| Mathematics          | Form 4-5, Lower 6th, Upper 6th| 18        |
| Sciences (Bio/Chem/Phy)| Form 4-5, Lower 6th, Upper 6th| 18      |
| English/Literature   | Form 4-5, Lower 6th, Upper 6th| 12       |
| History & Geography  | Form 4-5, Upper 6th          | 10        |
| Economics            | Lower 6th, Upper 6th         | 8         |

---

## Filtres de Qualité Appliqués

| Filtre                   | Valeur         |
|--------------------------|----------------|
| Durée minimale           | 2 minutes      |
| Durée maximale           | 2 heures       |
| Vues minimum             | 100            |
| Commentaires minimum     | 5              |
| Max commentaires/vidéo   | 500 (limite PRD)|

---

## Connexion avec le Pipeline LangGraph (PRD)

```
data/validated/comments_final.csv
        │
        ▼
    Agent A1 (Loader/Validator)
        │
        ▼
    Agent A2 (Préprocesseur)
        │
   ┌────┼────┐
   ▼    ▼    ▼
  A3   A4   A5
(Sentiment)(Discours)(Bruit)
        │
        ▼
    Agent A6 (Synthétiseur)
        │
        ▼
    Agent A7 (Topic Matcher)
        │
        ▼
    Score Final [0-100]
```

---

## Reproductibilité (NFR-02)

- `random.seed(42)` fixé dans tous les scripts
- Toutes les dépendances versionnées dans `requirements.txt`
- Notebook Kaggle public exécutable par un tiers sans configuration

## Reprise sur Interruption (NFR-03)

- Checkpoint JSON automatique dans `data/raw/.checkpoint_comments.json`
- Relancer `collect_comments.py --resume` après une interruption Kaggle
