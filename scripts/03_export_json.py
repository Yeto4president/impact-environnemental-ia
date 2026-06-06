"""
Script 03 — Export JSON depuis la BDD SQLite
Entrée  : data/db/impact_ia.db
Sortie  : data/processed/
"""

import sqlite3
import pandas as pd
import os

DB_PATH = "data/db/impact_ia.db"
OUT = "data/processed"
os.makedirs(OUT, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

# ============================================================
# 1. MODELES — métriques complètes + tarifs
# ============================================================
print("Export modeles.json...")
df = pd.read_sql_query("""
    SELECT
        m.mdl_nom,
        f.frs_nom,
        f.frs_pays_datacenter,
        f.frs_co2_datacenter,
        f.frs_score_fmti,
        m.mdl_nb_params,
        e.nrg_nb_conversations,
        e.nrg_kwh_moyen,
        e.nrg_kwh_median,
        e.nrg_wh_par_token,
        q.qlt_nb_likes,
        q.qlt_nb_dislikes,
        q.qlt_taux_satisfaction,
        q.qlt_taux_incorrect,
        q.qlt_taux_superficial,
        q.qlt_taux_victoire,
        t.trf_input_1k,
        t.trf_output_1k
    FROM Modele m
    LEFT JOIN Fournisseur f ON m.frs_id = f.frs_id
    LEFT JOIN Metrique_Energie e ON m.mdl_id = e.mdl_id
    LEFT JOIN Metrique_Qualite q ON m.mdl_id = q.mdl_id
    LEFT JOIN Tarif t ON m.mdl_id = t.mdl_id
    ORDER BY e.nrg_kwh_moyen ASC
""", conn)
df.to_json(f"{OUT}/modeles.json", orient='records', force_ascii=False, indent=2)
print(f"  → {len(df)} modèles")

# ============================================================
# 2. MODELES PAR CATEGORIE
# ============================================================
print("Export modeles_par_categorie.json...")
df = pd.read_sql_query("""
    SELECT
        m.mdl_nom,
        f.frs_nom,
        c.cat_nom,
        c.cat_nb_conversations,
        c.cat_kwh_moyen,
        c.cat_wh_par_token
    FROM Metrique_Categorie c
    LEFT JOIN Modele m ON c.mdl_id = m.mdl_id
    LEFT JOIN Fournisseur f ON m.frs_id = f.frs_id
    ORDER BY m.mdl_nom, c.cat_nom
""", conn)
df.to_json(f"{OUT}/modeles_par_categorie.json", orient='records', force_ascii=False, indent=2)
print(f"  → {len(df)} lignes")

# ============================================================
# 3. FOURNISSEURS — vue complète
# ============================================================
print("Export fournisseurs.json...")
df = pd.read_sql_query("""
    SELECT
        f.frs_nom,
        f.frs_pays_datacenter,
        f.frs_co2_datacenter,
        f.frs_score_fmti,
        SUM(CASE WHEN fi.find_domaine = 'Upstream' THEN fs.fmti_score ELSE 0 END) AS score_upstream,
        SUM(CASE WHEN fi.find_domaine = 'Model' THEN fs.fmti_score ELSE 0 END) AS score_model,
        SUM(CASE WHEN fi.find_domaine = 'Downstream' THEN fs.fmti_score ELSE 0 END) AS score_downstream,
        AVG(e.nrg_kwh_moyen) AS kwh_moyen_fournisseur
    FROM Fournisseur f
    LEFT JOIN FMTI_Score fs ON f.frs_id = fs.frs_id
    LEFT JOIN FMTI_Indicateur fi ON fs.find_id = fi.find_id
    LEFT JOIN Modele m ON f.frs_id = m.frs_id
    LEFT JOIN Metrique_Energie e ON m.mdl_id = e.mdl_id
    GROUP BY f.frs_id
    ORDER BY f.frs_score_fmti DESC
""", conn)
df.to_json(f"{OUT}/fournisseurs.json", orient='records', force_ascii=False, indent=2)
print(f"  → {len(df)} fournisseurs")

# ============================================================
# 4. FMTI DETAIL avec définitions
# ============================================================
print("Export fmti_detail.json...")
df = pd.read_sql_query("""
    SELECT
        f.frs_nom,
        fi.find_indicateur,
        fi.find_domaine,
        fi.find_sous_domaine,
        fi.find_definition,
        fi.find_notes,
        fs.fmti_score
    FROM FMTI_Score fs
    LEFT JOIN Fournisseur f ON fs.frs_id = f.frs_id
    LEFT JOIN FMTI_Indicateur fi ON fs.find_id = fi.find_id
    ORDER BY f.frs_nom, fi.find_domaine, fi.find_sous_domaine
""", conn)
df.to_json(f"{OUT}/fmti_detail.json", orient='records', force_ascii=False, indent=2)
print(f"  → {len(df)} lignes")

# ============================================================
# 5. FACTEURS EMISSIONS
# ============================================================
print("Export facteurs_emissions.json...")
df = pd.read_sql_query("""
    SELECT fct_nom_pays, fct_co2_kwh
    FROM Facteur_Emission
    ORDER BY fct_co2_kwh ASC
""", conn)
df.to_json(f"{OUT}/facteurs_emissions.json", orient='records', force_ascii=False, indent=2)
print(f"  → {len(df)} pays")

# ============================================================
# 6. STATS GLOBALES
# ============================================================
print("\nStats globales :")
stats = pd.read_sql_query("""
    SELECT
        COUNT(DISTINCT m.mdl_id) AS nb_modeles,
        COUNT(DISTINCT f.frs_id) AS nb_fournisseurs,
        SUM(e.nrg_nb_conversations) AS nb_conversations_total,
        ROUND(AVG(e.nrg_kwh_moyen), 6) AS kwh_moyen_global,
        ROUND(AVG(q.qlt_taux_satisfaction), 3) AS satisfaction_moyenne,
        COUNT(DISTINCT t.mdl_id) AS nb_modeles_avec_tarif
    FROM Modele m
    LEFT JOIN Fournisseur f ON m.frs_id = f.frs_id
    LEFT JOIN Metrique_Energie e ON m.mdl_id = e.mdl_id
    LEFT JOIN Metrique_Qualite q ON m.mdl_id = q.mdl_id
    LEFT JOIN Tarif t ON m.mdl_id = t.mdl_id
""", conn)
print(stats.to_string(index=False))

print("\nFichiers exportés :")
for f in sorted(os.listdir(OUT)):
    if f != '.gitkeep':
        size = os.path.getsize(f"{OUT}/{f}") / 1024
        print(f"  {f} — {size:.0f} Ko")

conn.close()
print("\nTerminé.")