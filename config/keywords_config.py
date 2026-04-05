"""
keywords_config.py
==================
Banque de mots-clés pour la collecte de vidéos éducatives YouTube
Contexte : Cameroun — Systèmes Francophone et Anglophone
Niveaux   : 3ème / Première / Terminale (FR) | Form 4-5 / Lower-Upper 6th (EN)
Matières  : Mathématiques, Sciences, Français/Littérature, Histoire-Géo, Économie
"""

# ─────────────────────────────────────────────────────────────────────────────
# 1. MÉTADONNÉES DES NIVEAUX
# ─────────────────────────────────────────────────────────────────────────────

LEVELS = {
    "francophone": {
        "troisieme": {
            "label": "3ème",
            "exam": "BEPC",
            "system": "francophone",
        },
        "premiere": {
            "label": "Première",
            "exam": "Probatoire",
            "system": "francophone",
        },
        "terminale": {
            "label": "Terminale",
            "exam": "Baccalauréat",
            "system": "francophone",
        },
    },
    "anglophone": {
        "form4_5": {
            "label": "Form 4-5",
            "exam": "GCE O-Level",
            "system": "anglophone",
        },
        "lower6th": {
            "label": "Lower 6th",
            "exam": "GCE A-Level",
            "system": "anglophone",
        },
        "upper6th": {
            "label": "Upper 6th",
            "exam": "GCE A-Level",
            "system": "anglophone",
        },
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. MOTS-CLÉS PAR MATIÈRE ET NIVEAU — SYSTÈME FRANCOPHONE
# ─────────────────────────────────────────────────────────────────────────────

KEYWORDS_FR = {

    # ── MATHÉMATIQUES ─────────────────────────────────────────────────────────
    "mathematiques": {
        "troisieme": [
            "mathématiques 3ème Cameroun",
            "cours maths troisième BEPC Cameroun",
            "exercices maths 3ème Cameroun corrigés",
            "algèbre 3ème Cameroun",
            "géométrie 3ème BEPC",
            "statistiques 3ème Cameroun",
            "fonctions mathématiques 3ème Cameroun",
            "BEPC mathématiques Cameroun révision",
            "arithmétique 3ème Cameroun",
            "maths collège Cameroun troisième",
        ],
        "premiere": [
            "mathématiques Première Cameroun",
            "cours maths Première C D Cameroun",
            "analyse mathématique Première Cameroun",
            "suites numériques Première Cameroun",
            "probabilités Première Cameroun",
            "géométrie analytique Première Cameroun",
            "Probatoire maths Cameroun",
            "dérivées fonctions Première Cameroun",
            "vecteurs Première Cameroun",
            "trigonométrie Première Cameroun",
        ],
        "terminale": [
            "mathématiques Terminale Cameroun",
            "cours maths Terminale C E Cameroun",
            "intégrales Terminale Cameroun",
            "limites fonctions Terminale Cameroun",
            "Baccalauréat maths Cameroun",
            "équations différentielles Terminale Cameroun",
            "nombres complexes Terminale Cameroun",
            "matrices Terminale Cameroun",
            "révision bac maths Cameroun",
            "probabilités Terminale Cameroun",
        ],
    },

    # ── SCIENCES SVT ──────────────────────────────────────────────────────────
    "svt": {
        "troisieme": [
            "SVT 3ème Cameroun",
            "sciences vie terre troisième Cameroun",
            "biologie 3ème Cameroun cours",
            "reproduction humaine 3ème Cameroun",
            "nutrition 3ème SVT Cameroun",
            "géologie 3ème Cameroun",
            "écologie 3ème Cameroun",
            "BEPC SVT Cameroun révision",
            "photosynthèse 3ème Cameroun",
            "génétique 3ème Cameroun",
        ],
        "premiere": [
            "SVT Première Cameroun",
            "biologie cellulaire Première Cameroun",
            "génétique Première Cameroun",
            "métabolisme cellulaire Première",
            "Probatoire SVT Cameroun",
            "immunologie Première Cameroun",
            "respiration cellulaire Première Cameroun",
            "neurobiologie Première Cameroun",
            "SVT Première C D Cameroun",
            "cours biologie Première Cameroun",
        ],
        "terminale": [
            "SVT Terminale Cameroun",
            "Baccalauréat SVT Cameroun",
            "géologie Terminale Cameroun",
            "évolution Terminale Cameroun",
            "biotechnologies Terminale Cameroun",
            "ADN réplication Terminale Cameroun",
            "biologie moléculaire Terminale Cameroun",
            "SVT Terminale C D Cameroun",
            "révision bac SVT Cameroun",
            "tectonique plaques Terminale Cameroun",
        ],
    },

    # ── PHYSIQUE-CHIMIE ───────────────────────────────────────────────────────
    "physique_chimie": {
        "troisieme": [
            "physique chimie 3ème Cameroun",
            "électricité 3ème Cameroun",
            "optique 3ème Cameroun",
            "chimie troisième Cameroun cours",
            "BEPC physique Cameroun",
            "mécanique 3ème Cameroun",
            "atome molécule 3ème Cameroun",
            "solutions chimiques 3ème Cameroun",
            "cours physique collège Cameroun",
            "exercices physique 3ème Cameroun corrigés",
        ],
        "premiere": [
            "physique Première Cameroun",
            "chimie Première Cameroun cours",
            "mécanique Première C Cameroun",
            "thermodynamique Première Cameroun",
            "électrocinétique Première Cameroun",
            "Probatoire physique Cameroun",
            "ondes mécaniques Première Cameroun",
            "chimie organique Première Cameroun",
            "oxydoréduction Première Cameroun",
            "cinématique Première Cameroun",
        ],
        "terminale": [
            "physique Terminale Cameroun",
            "chimie Terminale Cameroun",
            "Baccalauréat physique Cameroun",
            "mécanique quantique Terminale Cameroun",
            "électromagnétisme Terminale Cameroun",
            "réactions chimiques Terminale Cameroun",
            "optique ondulatoire Terminale Cameroun",
            "nucléaire Terminale Cameroun",
            "révision bac physique Cameroun",
            "physique Terminale C E Cameroun",
        ],
    },

    # ── FRANÇAIS / LITTÉRATURE ────────────────────────────────────────────────
    "francais_litterature": {
        "troisieme": [
            "français 3ème Cameroun",
            "grammaire troisième Cameroun cours",
            "expression écrite 3ème Cameroun",
            "commentaire texte 3ème Cameroun",
            "BEPC français Cameroun",
            "conjugaison 3ème Cameroun",
            "lecture texte 3ème Cameroun",
            "dissertation 3ème Cameroun",
            "analyse texte littéraire 3ème",
            "orthographe 3ème Cameroun",
        ],
        "premiere": [
            "français Première Cameroun",
            "littérature Première Cameroun",
            "dissertation littéraire Première Cameroun",
            "commentaire composé Première Cameroun",
            "roman africain Première Cameroun",
            "Probatoire français Cameroun",
            "poésie Première Cameroun analyse",
            "théâtre Première Cameroun",
            "contraction de texte Première Cameroun",
            "oeuvres au programme Première Cameroun",
        ],
        "terminale": [
            "français Terminale Cameroun",
            "littérature Terminale Cameroun",
            "Baccalauréat français Cameroun",
            "dissertation philosophique Terminale Cameroun",
            "oeuvres bac français Cameroun",
            "commentaire littéraire Terminale Cameroun",
            "francophonie littérature africaine Terminale",
            "Mongo Beti Ferdinand Oyono lycée Cameroun",
            "révision bac français Cameroun",
            "analyse oeuvre Terminale Cameroun",
        ],
    },

    # ── HISTOIRE-GÉOGRAPHIE ───────────────────────────────────────────────────
    "histoire_geo": {
        "troisieme": [
            "histoire géographie 3ème Cameroun",
            "histoire Afrique 3ème Cameroun",
            "géographie Cameroun troisième",
            "BEPC histoire géo Cameroun",
            "colonisation décolonisation 3ème Cameroun",
            "géographie physique Cameroun 3ème",
            "histoire contemporaine 3ème Cameroun",
            "carte Cameroun géographie",
            "Cameroun indépendance histoire",
            "mondialisation 3ème Cameroun",
        ],
        "premiere": [
            "histoire Première Cameroun",
            "géographie Première Cameroun",
            "Probatoire histoire géo Cameroun",
            "histoire politique Afrique Première Cameroun",
            "géopolitique Première Cameroun",
            "démographie Cameroun Première",
            "développement économique Afrique Première",
            "histoire guerre froide Première Cameroun",
            "géographie humaine Première Cameroun",
            "ressources naturelles Cameroun cours",
        ],
        "terminale": [
            "histoire Terminale Cameroun",
            "géographie Terminale Cameroun",
            "Baccalauréat histoire géo Cameroun",
            "histoire monde contemporain Terminale Cameroun",
            "géopolitique Afrique Terminale Cameroun",
            "développement durable Terminale Cameroun",
            "mondialisation Terminale Cameroun",
            "enjeux géopolitiques Afrique centrale",
            "révision bac histoire Cameroun",
            "organisations internationales Terminale Cameroun",
        ],
    },

    # ── ÉCONOMIE ──────────────────────────────────────────────────────────────
    "economie": {
        "premiere": [
            "économie Première Cameroun",
            "microéconomie Première Cameroun",
            "Probatoire économie Cameroun",
            "marchés économie Première Cameroun",
            "comptabilité Première Cameroun",
            "commerce international Première Cameroun",
            "économie générale lycée Cameroun",
            "droit économie Première Cameroun",
            "production consommation Première Cameroun",
            "système économique Première Cameroun",
        ],
        "terminale": [
            "économie Terminale Cameroun",
            "macroéconomie Terminale Cameroun",
            "Baccalauréat économie Cameroun",
            "croissance économique Terminale Cameroun",
            "politique économique Cameroun",
            "fiscal monétaire Terminale Cameroun",
            "économie africaine Terminale Cameroun",
            "chômage inflation Terminale Cameroun",
            "révision bac économie Cameroun",
            "développement économique Cameroun cours",
        ],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. MOTS-CLÉS PAR MATIÈRE ET NIVEAU — SYSTÈME ANGLOPHONE
# ─────────────────────────────────────────────────────────────────────────────

KEYWORDS_EN = {

    # ── MATHEMATICS ───────────────────────────────────────────────────────────
    "mathematics": {
        "form4_5": [
            "mathematics Form 4 Cameroon",
            "GCE O-Level maths Cameroon",
            "mathematics Form 5 Cameroon tutorial",
            "algebra Form 4 Cameroon",
            "geometry Form 5 Cameroon",
            "statistics O-Level Cameroon",
            "trigonometry Form 4 Cameroon",
            "O-Level mathematics revision Cameroon",
            "number theory Form 4 Cameroon",
            "coordinate geometry O-Level Cameroon",
        ],
        "lower6th": [
            "A-Level mathematics Lower 6 Cameroon",
            "GCE A-Level maths Cameroon",
            "calculus Lower 6th Cameroon",
            "pure mathematics A-Level Cameroon",
            "mechanics Lower 6 Cameroon",
            "statistics A-Level Cameroon",
            "vectors Lower 6th Cameroon",
            "functions A-Level Cameroon",
            "Lower 6 maths tutorial Cameroon",
            "differentiation A-Level Cameroon",
        ],
        "upper6th": [
            "A-Level mathematics Upper 6 Cameroon",
            "GCE A-Level revision maths Cameroon",
            "integration Upper 6th Cameroon",
            "differential equations A-Level Cameroon",
            "complex numbers Upper 6 Cameroon",
            "probability A-Level Cameroon",
            "matrices A-Level Cameroon",
            "further mathematics A-Level Cameroon",
            "Upper 6 maths exam Cameroon",
            "A-Level maths past questions Cameroon",
        ],
    },

    # ── SCIENCES ──────────────────────────────────────────────────────────────
    "sciences": {
        "form4_5": [
            "biology Form 4 Cameroon",
            "chemistry O-Level Cameroon",
            "physics Form 5 Cameroon",
            "GCE O-Level science Cameroon",
            "human biology Form 4 Cameroon",
            "chemistry Form 5 Cameroon tutorial",
            "physics O-Level revision Cameroon",
            "biology O-Level Cameroon past papers",
            "organic chemistry Form 4 Cameroon",
            "electricity physics Form 5 Cameroon",
        ],
        "lower6th": [
            "biology Lower 6th Cameroon",
            "chemistry A-Level Cameroon",
            "physics Lower 6 Cameroon",
            "GCE A-Level biology Cameroon",
            "cell biology A-Level Cameroon",
            "thermodynamics Lower 6 Cameroon",
            "genetics A-Level Cameroon",
            "organic chemistry Lower 6th Cameroon",
            "electromagnetism A-Level Cameroon",
            "ecology A-Level Cameroon",
        ],
        "upper6th": [
            "biology Upper 6th Cameroon",
            "chemistry A-Level revision Cameroon",
            "physics Upper 6 Cameroon",
            "GCE A-Level science revision Cameroon",
            "molecular biology A-Level Cameroon",
            "nuclear physics A-Level Cameroon",
            "biochemistry A-Level Cameroon",
            "genetics evolution A-Level Cameroon",
            "A-Level past papers science Cameroon",
            "Upper 6 biology tutorial Cameroon",
        ],
    },

    # ── ENGLISH LANGUAGE & LITERATURE ─────────────────────────────────────────
    "english_literature": {
        "form4_5": [
            "English language Form 4 Cameroon",
            "GCE O-Level English Cameroon",
            "English literature Form 5 Cameroon",
            "essay writing O-Level Cameroon",
            "comprehension O-Level Cameroon",
            "grammar Form 4 Cameroon",
            "African literature O-Level Cameroon",
            "O-Level English revision Cameroon",
            "summary writing Form 5 Cameroon",
            "English composition Form 4 Cameroon",
        ],
        "lower6th": [
            "English literature Lower 6th Cameroon",
            "A-Level English Cameroon",
            "prose analysis A-Level Cameroon",
            "African novel A-Level Cameroon",
            "poetry A-Level Cameroon",
            "drama A-Level Cameroon",
            "English language skills Lower 6 Cameroon",
            "critical writing A-Level Cameroon",
            "GCE A-Level English Cameroon",
            "Chinua Achebe GCE Cameroon",
        ],
        "upper6th": [
            "English literature Upper 6th Cameroon",
            "A-Level English revision Cameroon",
            "GCE A-Level literature Cameroon",
            "literary criticism A-Level Cameroon",
            "African literature A-Level Cameroon",
            "Shakespeare A-Level Cameroon",
            "essay technique A-Level Cameroon",
            "Upper 6 English tutorial Cameroon",
            "A-Level past papers English Cameroon",
            "postcolonial literature A-Level Cameroon",
        ],
    },

    # ── HISTORY & GEOGRAPHY ───────────────────────────────────────────────────
    "history_geography": {
        "form4_5": [
            "history Form 4 Cameroon",
            "geography O-Level Cameroon",
            "GCE O-Level history Cameroon",
            "African history Form 5 Cameroon",
            "physical geography Form 4 Cameroon",
            "Cameroon history O-Level",
            "colonialism Africa O-Level Cameroon",
            "map reading Form 4 Cameroon",
            "history revision O-Level Cameroon",
            "human geography Form 5 Cameroon",
        ],
        "upper6th": [
            "history A-Level Cameroon",
            "geography Upper 6th Cameroon",
            "GCE A-Level history Cameroon",
            "geopolitics A-Level Cameroon",
            "African development geography A-Level",
            "contemporary history A-Level Cameroon",
            "A-Level history past papers Cameroon",
            "climate geography A-Level Cameroon",
            "Cold War history A-Level Cameroon",
            "Upper 6 history tutorial Cameroon",
        ],
    },

    # ── ECONOMICS ────────────────────────────────────────────────────────────
    "economics": {
        "lower6th": [
            "economics Lower 6th Cameroon",
            "A-Level economics Cameroon",
            "microeconomics A-Level Cameroon",
            "demand supply A-Level Cameroon",
            "GCE economics Cameroon tutorial",
            "market structures A-Level Cameroon",
            "economics Lower 6 revision Cameroon",
        ],
        "upper6th": [
            "economics Upper 6th Cameroon",
            "macroeconomics A-Level Cameroon",
            "GCE A-Level economics Cameroon",
            "monetary policy A-Level Cameroon",
            "international trade A-Level Cameroon",
            "economic development A-Level Cameroon",
            "A-Level economics past papers Cameroon",
            "Upper 6 economics Cameroon",
        ],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# 4. TERMES CONTEXTUELS CAMEROUNAIS (boostent la pertinence)
# ─────────────────────────────────────────────────────────────────────────────

CAMEROON_CONTEXT_TERMS = [
    "Cameroun", "Cameroon",
    "BEPC", "Baccalauréat", "Probatoire",
    "GCE O-Level", "GCE A-Level",
    "lycée Cameroun", "collège Cameroun",
    "Yaoundé cours", "Douala cours",
    "Ministère éducation Cameroun",
    "système éducatif camerounais",
    "francophone Cameroun lycée",
    "anglophone Cameroon school",
]

# ─────────────────────────────────────────────────────────────────────────────
# 5. FILTRES DE QUALITÉ MINIMAUX
# ─────────────────────────────────────────────────────────────────────────────

QUALITY_FILTERS = {
    "min_duration_seconds": 120,        # Vidéo >= 2 min
    "max_duration_seconds": 7200,       # Vidéo <= 2h
    "min_view_count": 100,              # Audience minimale
    "min_comment_count": 5,             # Au moins 5 commentaires
    "max_comments_per_video": 500,      # Limite PRD (A1 Loader)
    "min_comments_per_video": 5,        # Seuil bas acceptable
    "target_comments_per_video": 100,   # Cible idéale
}

# ─────────────────────────────────────────────────────────────────────────────
# 6. COLONNES DU CSV DE SORTIE (alignées avec PRD — Agent A1)
# ─────────────────────────────────────────────────────────────────────────────

CSV_VIDEO_COLUMNS = [
    "video_id",
    "title",
    "channel_name",
    "channel_id",
    "published_at",
    "duration_seconds",
    "view_count",
    "like_count",
    "comment_count",
    "language",           # "fr" | "en"
    "system",             # "francophone" | "anglophone"
    "level",              # "troisieme" | "premiere" | "terminale" | "form4_5" | ...
    "subject",            # "mathematiques" | "svt" | "mathematics" | ...
    "search_query",       # Requête ayant trouvé la vidéo
    "url",
]

CSV_COMMENTS_COLUMNS = [
    "video_id",           # Clé de jointure avec videos.csv
    "comment_id",
    "text",               # Texte du commentaire (colonne principale PRD)
    "author",
    "author_likes",       # Likes reçus par l'auteur sur le commentaire
    "reply_count",        # Nombre de réponses (requis PRD A1)
    "published_at",
    "is_reply",           # True si c'est une réponse à un commentaire parent
    "parent_id",          # ID du commentaire parent si is_reply=True
    "language_detected",  # Langue détectée par langdetect (ajoutée par A2)
]
