"""
Script 02 — Construction de la BDD SQLite
Entrées  : data/processed/ + data/raw/
Sortie   : data/db/impact_ia.db
"""

import pandas as pd
import sqlite3
import os

OUT = "data/processed"
RAW = "data/raw"
DB_PATH = "data/db/impact_ia.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("Ancienne BDD supprimée")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ============================================================
# CRÉATION DES TABLES
# ============================================================
print("Création des tables...")

cursor.executescript("""
    CREATE TABLE Fournisseur (
        frs_id              INTEGER PRIMARY KEY AUTOINCREMENT,
        frs_nom             TEXT UNIQUE NOT NULL,
        frs_pays_datacenter TEXT,
        frs_co2_datacenter  REAL,
        frs_score_fmti      REAL
    );

    CREATE TABLE Modele (
        mdl_id              INTEGER PRIMARY KEY AUTOINCREMENT,
        mdl_nom             TEXT UNIQUE NOT NULL,
        frs_id              INTEGER,
        mdl_nb_params       REAL,
        FOREIGN KEY (frs_id) REFERENCES Fournisseur(frs_id)
    );

    CREATE TABLE Metrique_Energie (
        nrg_id              INTEGER PRIMARY KEY AUTOINCREMENT,
        mdl_id              INTEGER UNIQUE,
        nrg_nb_conversations INTEGER,
        nrg_kwh_moyen       REAL,
        nrg_kwh_median      REAL,
        nrg_wh_par_token    REAL,
        FOREIGN KEY (mdl_id) REFERENCES Modele(mdl_id)
    );

    CREATE TABLE Metrique_Qualite (
        qlt_id              INTEGER PRIMARY KEY AUTOINCREMENT,
        mdl_id              INTEGER UNIQUE,
        qlt_nb_likes        INTEGER,
        qlt_nb_dislikes     INTEGER,
        qlt_taux_satisfaction REAL,
        qlt_taux_incorrect  REAL,
        qlt_taux_superficial REAL,
        qlt_taux_victoire   REAL,
        FOREIGN KEY (mdl_id) REFERENCES Modele(mdl_id)
    );

    CREATE TABLE Metrique_Categorie (
        cat_id              INTEGER PRIMARY KEY AUTOINCREMENT,
        mdl_id              INTEGER,
        cat_nom             TEXT,
        cat_nb_conversations INTEGER,
        cat_kwh_moyen       REAL,
        cat_wh_par_token    REAL,
        FOREIGN KEY (mdl_id) REFERENCES Modele(mdl_id)
    );

    CREATE TABLE Facteur_Emission (
        fct_id              INTEGER PRIMARY KEY AUTOINCREMENT,
        fct_nom_pays        TEXT UNIQUE NOT NULL,
        fct_co2_kwh         REAL
    );

    CREATE TABLE FMTI_Indicateur (
        find_id             INTEGER PRIMARY KEY AUTOINCREMENT,
        find_indicateur     TEXT UNIQUE NOT NULL,
        find_domaine        TEXT,
        find_sous_domaine   TEXT,
        find_definition     TEXT,
        find_notes          TEXT
    );

    CREATE TABLE FMTI_Score (
        fmti_id             INTEGER PRIMARY KEY AUTOINCREMENT,
        frs_id              INTEGER,
        find_id             INTEGER,
        fmti_score          INTEGER,
        FOREIGN KEY (frs_id) REFERENCES Fournisseur(frs_id),
        FOREIGN KEY (find_id) REFERENCES FMTI_Indicateur(find_id)
    );
""")
print("  → Tables créées")

# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================
print("Chargement des données...")
modeles_df = pd.read_json(f"{OUT}/modeles.json")
fournisseurs_df = pd.read_json(f"{OUT}/fournisseurs.json")
facteurs_df = pd.read_json(f"{OUT}/facteurs_emissions.json")
scores_df = pd.read_csv(f"{RAW}/Dec2025_scores (1).csv")
indicators_df = pd.read_csv(f"{RAW}/Dec2025_indicators.csv")
modeles_cat_df = pd.read_json(f"{OUT}/modeles_par_categorie.json")

# ============================================================
# INSERTION FOURNISSEUR
# ============================================================
print("Insertion Fournisseur...")
for _, row in fournisseurs_df.iterrows():
    cursor.execute("""
        INSERT OR IGNORE INTO Fournisseur
        (frs_nom, frs_pays_datacenter, frs_co2_datacenter, frs_score_fmti)
        VALUES (?, ?, ?, ?)
    """, (
        row['fournisseur'],
        row.get('pays_datacenter'),
        row.get('facteur_co2_datacenter'),
        row.get('score_fmti_total')
    ))
conn.commit()

frs_ids = {row[1]: row[0] for row in cursor.execute(
    "SELECT frs_id, frs_nom FROM Fournisseur"
)}
print(f"  → {len(frs_ids)} fournisseurs")

# ============================================================
# INSERTION MODELE
# ============================================================
print("Insertion Modele...")
for _, row in modeles_df.iterrows():
    frs_id = frs_ids.get(row.get('fournisseur'))
    cursor.execute("""
        INSERT OR IGNORE INTO Modele (mdl_nom, frs_id, mdl_nb_params)
        VALUES (?, ?, ?)
    """, (row['model'], frs_id, row.get('total_params')))
conn.commit()

mdl_ids = {row[1]: row[0] for row in cursor.execute(
    "SELECT mdl_id, mdl_nom FROM Modele"
)}
print(f"  → {len(mdl_ids)} modèles")

# ============================================================
# INSERTION METRIQUE_ENERGIE
# ============================================================
print("Insertion Metrique_Energie...")
for _, row in modeles_df.iterrows():
    mdl_id = mdl_ids.get(row['model'])
    if mdl_id:
        cursor.execute("""
            INSERT OR IGNORE INTO Metrique_Energie
            (mdl_id, nrg_nb_conversations, nrg_kwh_moyen, nrg_kwh_median, nrg_wh_par_token)
            VALUES (?, ?, ?, ?, ?)
        """, (
            mdl_id,
            row.get('nb_conversations'),
            row.get('kwh_moyen'),
            row.get('kwh_median'),
            row.get('wh_per_token_moyen')
        ))
conn.commit()
print(f"  → {len(modeles_df)} entrées")

# ============================================================
# INSERTION METRIQUE_QUALITE
# ============================================================
print("Insertion Metrique_Qualite...")
for _, row in modeles_df.iterrows():
    mdl_id = mdl_ids.get(row['model'])
    if mdl_id:
        cursor.execute("""
            INSERT OR IGNORE INTO Metrique_Qualite
            (mdl_id, qlt_nb_likes, qlt_nb_dislikes, qlt_taux_satisfaction,
             qlt_taux_incorrect, qlt_taux_superficial, qlt_taux_victoire)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            mdl_id,
            row.get('nb_likes'),
            row.get('nb_dislikes'),
            row.get('taux_satisfaction'),
            row.get('taux_incorrect'),
            row.get('taux_superficial'),
            row.get('taux_victoire')
        ))
conn.commit()
print(f"  → {len(modeles_df)} entrées")

# ============================================================
# INSERTION METRIQUE_CATEGORIE
# ============================================================
print("Insertion Metrique_Categorie...")
count = 0
for _, row in modeles_cat_df.iterrows():
    mdl_id = mdl_ids.get(row['model'])
    if mdl_id:
        cursor.execute("""
            INSERT INTO Metrique_Categorie
            (mdl_id, cat_nom, cat_nb_conversations, cat_kwh_moyen, cat_wh_par_token)
            VALUES (?, ?, ?, ?, ?)
        """, (
            mdl_id,
            row.get('categories'),
            row.get('nb_conversations'),
            row.get('kwh_moyen'),
            row.get('wh_per_token_moyen')
        ))
        count += 1
conn.commit()
print(f"  → {count} entrées")

# ============================================================
# INSERTION FACTEUR_EMISSION
# ============================================================
print("Insertion Facteur_Emission...")
for _, row in facteurs_df.iterrows():
    cursor.execute("""
        INSERT OR IGNORE INTO Facteur_Emission (fct_nom_pays, fct_co2_kwh)
        VALUES (?, ?)
    """, (row['pays'], row['facteur_kgco2_kwh']))
conn.commit()
print(f"  → {len(facteurs_df)} pays")

# ============================================================
# INSERTION FMTI_INDICATEUR
# ============================================================
print("Insertion FMTI_Indicateur...")
for _, row in indicators_df.iterrows():
    cursor.execute("""
        INSERT OR IGNORE INTO FMTI_Indicateur
        (find_indicateur, find_domaine, find_sous_domaine, find_definition, find_notes)
        VALUES (?, ?, ?, ?, ?)
    """, (
        row['Indicator'],
        row['Domain'],
        row['Subdomain'],
        row.get('Definition'),
        row.get('Notes')
    ))
conn.commit()

find_ids = {row[1]: row[0] for row in cursor.execute(
    "SELECT find_id, find_indicateur FROM FMTI_Indicateur"
)}
print(f"  → {len(find_ids)} indicateurs")

# ============================================================
# INSERTION FMTI_SCORE
# ============================================================
print("Insertion FMTI_Score...")
fmti_long = scores_df.melt(id_vars='Indicator', var_name='fournisseur', value_name='score')
count = 0
for _, row in fmti_long.iterrows():
    frs_id = frs_ids.get(row['fournisseur'])
    find_id = find_ids.get(row['Indicator'])
    if frs_id and find_id:
        cursor.execute("""
            INSERT INTO FMTI_Score (frs_id, find_id, fmti_score)
            VALUES (?, ?, ?)
        """, (frs_id, find_id, row['score']))
        count += 1
conn.commit()
print(f"  → {count} entrées")

# ============================================================
# VÉRIFICATION
# ============================================================
print("\nVérification BDD :")
tables = [
    'Fournisseur', 'Modele', 'Metrique_Energie',
    'Metrique_Qualite', 'Metrique_Categorie',
    'Facteur_Emission', 'FMTI_Indicateur', 'FMTI_Score'
]
for table in tables:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table} : {count} lignes")

taille = os.path.getsize(DB_PATH) / 1024
print(f"\nBDD créée : {DB_PATH} ({taille:.0f} Ko)")
conn.close()
print("Terminé.")