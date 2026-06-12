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
# 6. BENCHMARK TACHES (Louis — ML.ENERGY Benchmark V3)
# ============================================================
print("Export benchmark_taches.json...")
df_btk = pd.read_sql_query("""
    SELECT
        m.mdl_nom,
        f.frs_nom,
        bt.btk_tache,
        bt.btk_gpu_modele,
        bt.btk_nb_gpu,
        bt.btk_joules_par_token,
        bt.btk_kwh_par_1k_tokens,
        bt.btk_watt_moyen,
        bt.btk_debit_tokens_s,
        bt.btk_latence_itl_ms,
        bt.btk_model_id_hf,
        bt.btk_source
    FROM Benchmark_Tache bt
    LEFT JOIN Modele m ON bt.mdl_id = m.mdl_id
    LEFT JOIN Fournisseur f ON m.frs_id = f.frs_id
    ORDER BY bt.btk_tache, bt.btk_joules_par_token ASC
""", conn)

if len(df_btk) == 0:
    print("  Table vide — lancer d'abord : python scripts/05_add_benchmark.py")
else:
    df_btk.to_json(f"{OUT}/benchmark_taches.json", orient='records',
                   force_ascii=False, indent=2)
    print(f"  → {len(df_btk)} entrees ({df_btk['mdl_nom'].nunique()} modeles, "
          f"{df_btk['btk_tache'].nunique()} taches)")

# ============================================================
# 7. DETECTEUR DE GASPILLAGE
# ============================================================
print("Export detecteur_gaspillage.json...")
df_gaspillage = pd.read_sql_query("""
    SELECT
        m.mdl_nom,
        f.frs_nom,
        e.nrg_wh_par_token,
        (e.nrg_wh_par_token / 1000.0) * 1000 AS nrg_kwh_par_1k_tokens_reel,
        e.nrg_kwh_moyen,
        e.nrg_nb_conversations,
        AVG(bt.btk_kwh_par_1k_tokens) AS btk_kwh_par_1k_tokens_labo,
        AVG(bt.btk_joules_par_token)  AS btk_joules_par_token_labo,
        AVG(bt.btk_watt_moyen)        AS btk_watt_moyen,
        COUNT(bt.btk_id)              AS btk_nb_mesures,
        CASE
            WHEN AVG(bt.btk_kwh_par_1k_tokens) > 0
             AND e.nrg_wh_par_token IS NOT NULL
            THEN ROUND(
                ((e.nrg_wh_par_token / 1000.0) * 1000) / AVG(bt.btk_kwh_par_1k_tokens),
                2
            )
            ELSE NULL
        END AS ratio_reel_sur_labo,
        NULL AS score_frugalite
    FROM Modele m
    LEFT JOIN Fournisseur f ON m.frs_id = f.frs_id
    LEFT JOIN Metrique_Energie e ON m.mdl_id = e.mdl_id
    LEFT JOIN Benchmark_Tache bt ON m.mdl_id = bt.mdl_id
    WHERE e.nrg_wh_par_token IS NOT NULL
      AND bt.btk_id IS NOT NULL
    GROUP BY m.mdl_id
    ORDER BY ratio_reel_sur_labo ASC
""", conn)

if len(df_gaspillage) == 0:
    print("  Aucun modele en commun entre Compar:IA et ML.ENERGY.")
else:
    df_valid = df_gaspillage[df_gaspillage['ratio_reel_sur_labo'].notna()].copy()
    if len(df_valid) > 1:
        r_min = df_valid['ratio_reel_sur_labo'].min()
        r_max = df_valid['ratio_reel_sur_labo'].max()
        if r_max > r_min:
            df_gaspillage.loc[df_valid.index, 'score_frugalite'] = (
                1 - (df_valid['ratio_reel_sur_labo'] - r_min) / (r_max - r_min)
            ).round(3)

    df_gaspillage.to_json(f"{OUT}/detecteur_gaspillage.json", orient='records',
                          force_ascii=False, indent=2)
    print(f"  → {len(df_gaspillage)} modeles compares")

# ============================================================
# 7bis. MODELES NORMALISÉS — pour le score d'efficience front
# ============================================================
print("Export modeles_normalises.json...")
df_norm = pd.read_sql_query("""
    SELECT
        m.mdl_nom,
        f.frs_nom,
        f.frs_pays_datacenter,
        f.frs_co2_datacenter,
        f.frs_score_fmti,
        e.nrg_nb_conversations,
        e.nrg_kwh_moyen,
        e.nrg_wh_par_token,
        q.qlt_taux_satisfaction,
        q.qlt_taux_victoire,
        t.trf_input_1k,
        t.trf_output_1k
    FROM Modele m
    LEFT JOIN Fournisseur f ON m.frs_id = f.frs_id
    LEFT JOIN Metrique_Energie e ON m.mdl_id = e.mdl_id
    LEFT JOIN Metrique_Qualite q ON m.mdl_id = q.mdl_id
    LEFT JOIN Tarif t ON m.mdl_id = t.mdl_id
    WHERE e.nrg_kwh_moyen IS NOT NULL
""", conn)

kwh_min = df_norm['nrg_kwh_moyen'].min()
kwh_max = df_norm['nrg_kwh_moyen'].max()
prix_min = df_norm['trf_input_1k'].min()
prix_max = df_norm['trf_input_1k'].max()
fmti_min = df_norm['frs_score_fmti'].min()
fmti_max = df_norm['frs_score_fmti'].max()

df_norm['score_eco'] = (
    1 - (df_norm['nrg_kwh_moyen'] - kwh_min) / (kwh_max - kwh_min)
).round(4)

df_norm['score_perf'] = df_norm['qlt_taux_satisfaction'].round(4)

df_norm['score_prix'] = df_norm['trf_input_1k'].apply(
    lambda x: round(1 - (x - prix_min) / (prix_max - prix_min), 4)
    if pd.notna(x) and prix_max > prix_min else 0.5
)

df_norm['score_transparence'] = df_norm['frs_score_fmti'].apply(
    lambda x: round((x - fmti_min) / (fmti_max - fmti_min), 4)
    if pd.notna(x) and fmti_max > fmti_min else 0.5
)

df_norm['score_efficience'] = (
    df_norm['score_eco'] * 0.4 +
    df_norm['score_perf'] * 0.3 +
    df_norm['score_prix'] * 0.2 +
    df_norm['score_transparence'] * 0.1
).round(4)

df_norm = df_norm.sort_values('score_efficience', ascending=False)
df_norm.to_json(f"{OUT}/modeles_normalises.json", orient='records', force_ascii=False, indent=2)
print(f"  → {len(df_norm)} modeles normalises")

# ============================================================
# 8. STATS GLOBALES
# ============================================================
print("\nStats globales :")
stats = pd.read_sql_query("""
    SELECT
        COUNT(DISTINCT m.mdl_id) AS nb_modeles,
        COUNT(DISTINCT f.frs_id) AS nb_fournisseurs,
        SUM(e.nrg_nb_conversations) AS nb_conversations_total,
        ROUND(AVG(e.nrg_kwh_moyen), 6) AS kwh_moyen_global,
        ROUND(AVG(q.qlt_taux_satisfaction), 3) AS satisfaction_moyenne,
        COUNT(DISTINCT t.mdl_id) AS nb_modeles_avec_tarif,
        (SELECT COUNT(*) FROM Benchmark_Tache) AS nb_mesures_benchmark,
        (SELECT COUNT(DISTINCT mdl_id) FROM Benchmark_Tache) AS nb_modeles_benchmark
    FROM Modele m
    LEFT JOIN Fournisseur f ON m.frs_id = f.frs_id
    LEFT JOIN Metrique_Energie e ON m.mdl_id = e.mdl_id
    LEFT JOIN Metrique_Qualite q ON m.mdl_id = q.mdl_id
    LEFT JOIN Tarif t ON m.mdl_id = t.mdl_id
""", conn)
print(stats.to_string(index=False))

print("\nFichiers exportes :")
for fname in sorted(os.listdir(OUT)):
    if fname != '.gitkeep':
        size = os.path.getsize(f"{OUT}/{fname}") / 1024
        print(f"  {fname} — {size:.0f} Ko")

conn.close()
print("\nTermine.")