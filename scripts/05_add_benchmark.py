"""
Script 05 — Ajout des données ML.ENERGY Benchmark V3
=======================================================
Source  : ml-energy/benchmark-v3 (HuggingFace, Apache 2.0, NeurIPS 2025)
Paper   : "The ML.ENERGY Benchmark: Toward Automated Inference Energy
           Measurement and Optimization" — NeurIPS Datasets & Benchmarks 2025
Dataset : 46 modèles × 7 tâches × GPU H100/B200 (~1 858 configurations)

Prérequis :
    pip install datasets huggingface_hub

Accès HuggingFace :
    1. Créer un compte sur huggingface.co
    2. Accepter les conditions sur : huggingface.co/datasets/ml-energy/benchmark-v3
    3. Générer un token sur     : huggingface.co/settings/tokens
    4. Exporter la variable     : export HF_TOKEN=hf_xxxxxxxxxxxx

Entrée  : data/db/impact_ia.db  (table Modele et Benchmark_Tache existantes)
Sortie  : table Benchmark_Tache remplie dans impact_ia.db

Ordre dans le pipeline :
    python scripts/01_clean_data.py
    python scripts/02_build_db.py
    python scripts/04_add_pricing.py
    python scripts/05_add_benchmark.py   ← ce script
    python scripts/03_export_json.py
"""

import os
import sqlite3
import pandas as pd

DB_PATH = "data/db/impact_ia.db"

# ============================================================
# MAPPING : fragments model_id ML.ENERGY → mdl_nom Compar:IA
# ============================================================
MLENERGY_TO_COMPARAIA = {
    # Meta / Llama
    "Llama-3.1-8B":               "llama-3.1-8b",
    "Llama-3.1-70B":              "llama-3.1-70b",
    "Llama-3.1-405B":             "llama-3.1-405b",
    "Llama-3.3-70B":              "llama-3.3-70b",
    "Llama-4-Scout":              "llama-4-scout",
    "Llama-4-Maverick":           "llama-maverick",
    "Llama-3.1-Nemotron-70B":     "llama-3.1-nemotron-70b-instruct",
    # Mistral
    "Mistral-7B":                 "mistral-small-24b-instruct-2501",
    "Mistral-Small-3":            "mistral-small-3.1-24b",
    "Mistral-Small-2501":         "mistral-small-24b-instruct-2501",
    "Mistral-Small-2506":         "mistral-small-2506",
    "Mistral-Large-2411":         "mistral-large-2411",
    "Mistral-Large-2512":         "mistral-large-2512",
    "Mixtral-8x7B":               "mixtral-8x7b-instruct-v0.1",
    "Mixtral-8x22B":              "mixtral-8x22b-instruct-v0.1",
    "Mistral-Nemo":               "mistral-nemo-2407",
    "Ministral-8B":               "ministral-8b-instruct-2410",
    # Google / Gemma
    "gemma-2-9b":                 "gemma-2-9b-it",
    "gemma-2-27b":                "gemma-2-27b-it-q8",
    "gemma-3-4b":                 "gemma-3-4b",
    "gemma-3-12b":                "gemma-3-12b",
    "gemma-3-27b":                "gemma-3-27b",
    # Alibaba / Qwen
    "Qwen2-7B":                   "qwen2-7b-instruct",
    "Qwen2.5-7B":                 "qwen2.5-7b-instruct",
    "Qwen2.5-32B":                "qwen2.5-32b-instruct",
    "Qwen2.5-Coder-32B":          "qwen2.5-coder-32b-instruct",
    "Qwen3-8B":                   "qwen-3-8b",
    "Qwen3-32B":                  "qwen3-32b",
    "QwQ-32B":                    "qwq-32b",
    # DeepSeek
    "DeepSeek-V3":                "deepseek-v3-chat",
    "DeepSeek-R1-0528":           "deepseek-r1-0528",
    "DeepSeek-R1-Distill-Llama-70B": "deepseek-r1-distill-llama-70b",
    # Microsoft / Phi
    "Phi-3.5-mini":               "phi-3.5-mini-instruct",
    "phi-4":                      "phi-4",
    # Cohere / Aya
    "aya-expanse-8b":             "aya-expanse-8b",
    "aya-expanse-32b":            "aya-expanse-32b",
}


def load_mlenergy_data():
    """Télécharge le dataset ML.ENERGY Benchmark V3 depuis HuggingFace."""
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("\n⚠️  Variable HF_TOKEN non définie.")
        print("   Étapes pour obtenir l'accès :")
        print("   1. Créer un compte sur huggingface.co")
        print("   2. Accepter les conditions : huggingface.co/datasets/ml-energy/benchmark-v3")
        print("   3. Générer un token : huggingface.co/settings/tokens")
        print("   4. Puis lancer :")
        print("      $env:HF_TOKEN = \"hf_xxxxxxxxxxxx\"")
        print("      python scripts/05_add_benchmark.py")
        raise EnvironmentError("HF_TOKEN manquant — voir instructions ci-dessus")

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        raise ImportError(
            "Package manquant. Installer avec :\n  pip install huggingface_hub"
        )

    print("Téléchargement de ml-energy/benchmark-v3 depuis HuggingFace...")
    # Téléchargement direct du parquet (plus fiable que load_dataset pour ce repo)
    parquet_path = hf_hub_download(
        repo_id="ml-energy/benchmark-v3",
        filename="runs/llm.parquet",
        repo_type="dataset",
        token=hf_token,
    )
    df = pd.read_parquet(parquet_path)
    print(f"  → {len(df)} enregistrements ({df['model_id'].nunique()} modèles, "
          f"{df['task'].nunique()} tâches)")
    return df


def build_mapping(df_mlenergy, mdl_ids):
    """
    Construit la correspondance ML.ENERGY model_id → mdl_id de notre BDD.
    Stratégie en 2 passes :
      1. Correspondance via le dictionnaire MLENERGY_TO_COMPARAIA
      2. Correspondance partielle automatique sur les noms normalisés
    """
    mapping = {}

    for model_id in df_mlenergy["model_id"].unique():
        short_name = model_id.split("/")[-1]  # ex: "Llama-3.1-70B-Instruct"

        # Passe 1 : mapping explicite
        for fragment, nom_bdd in MLENERGY_TO_COMPARAIA.items():
            if fragment.lower() in short_name.lower():
                if nom_bdd in mdl_ids:
                    mapping[model_id] = mdl_ids[nom_bdd]
                    break

        # Passe 2 : correspondance automatique normalisée
        if model_id not in mapping:
            def norm(s):
                return s.lower().replace("-", "").replace(".", "").replace("_", "")
            short_norm = norm(short_name)
            for nom_bdd, mid in mdl_ids.items():
                if norm(nom_bdd) in short_norm or short_norm in norm(nom_bdd):
                    mapping[model_id] = mid
                    break

    print(f"  → {len(mapping)}/{df_mlenergy['model_id'].nunique()} modèles ML.ENERGY "
          f"matchés dans notre BDD")
    unmatched = [m for m in df_mlenergy["model_id"].unique() if m not in mapping]
    if unmatched:
        print(f"  Non matchés ({len(unmatched)}) :")
        for m in sorted(unmatched):
            print(f"    - {m}")
    return mapping


def insert_benchmark_data(df_mlenergy, model_mapping, conn):
    """Insère les données benchmark dans la table Benchmark_Tache."""
    cursor = conn.cursor()

    # Vider la table avant ré-insertion (idempotent)
    cursor.execute("DELETE FROM Benchmark_Tache")
    conn.commit()

    JOULES_TO_KWH = 1 / 3_600_000  # 1 J = 1/3 600 000 kWh

    inserted = 0
    skipped_no_match = 0
    skipped_unstable = 0

    for _, row in df_mlenergy.iterrows():
        mdl_id = model_mapping.get(row["model_id"])
        if mdl_id is None:
            skipped_no_match += 1
            continue

        # Filtrer les runs instables si la colonne existe
        if "is_stable" in df_mlenergy.columns and row.get("is_stable") is False:
            skipped_unstable += 1
            continue

        joules = row.get("energy_per_token_joules")
        kwh_1k = (float(joules) * 1000 * JOULES_TO_KWH) if pd.notna(joules) else None

        cursor.execute("""
            INSERT INTO Benchmark_Tache
            (mdl_id, btk_tache, btk_gpu_modele, btk_nb_gpu,
             btk_joules_par_token, btk_kwh_par_1k_tokens,
             btk_watt_moyen, btk_debit_tokens_s, btk_latence_itl_ms,
             btk_model_id_hf, btk_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mdl_id,
            row.get("task"),
            row.get("gpu_model"),
            row.get("num_gpus"),
            float(joules) if pd.notna(joules) else None,
            kwh_1k,
            float(row["avg_power_watts"]) if pd.notna(row.get("avg_power_watts")) else None,
            float(row["output_throughput_tokens_per_sec"])
                if pd.notna(row.get("output_throughput_tokens_per_sec")) else None,
            float(row["mean_itl_ms"]) if pd.notna(row.get("mean_itl_ms")) else None,
            row.get("model_id"),
            "mlenergy-v3"
        ))
        inserted += 1

    conn.commit()
    print(f"  → {inserted} lignes insérées")
    if skipped_no_match:
        print(f"    {skipped_no_match} ignorées (modèle absent de notre BDD)")
    if skipped_unstable:
        print(f"    {skipped_unstable} ignorées (run instable)")
    return inserted


def main():
    print("=" * 60)
    print("Script 05 — ML.ENERGY Benchmark V3")
    print("=" * 60)

    # Vérification BDD
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"BDD introuvable : {DB_PATH}\n"
            "Lancer d'abord : python scripts/02_build_db.py"
        )

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Vérification table Benchmark_Tache
    tables = [r[0] for r in cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    if "Benchmark_Tache" not in tables:
        raise RuntimeError(
            "Table Benchmark_Tache absente de la BDD.\n"
            "Relancer : python scripts/02_build_db.py"
        )

    # Modèles disponibles dans la BDD
    mdl_ids = {row[1]: row[0] for row in cursor.execute(
        "SELECT mdl_id, mdl_nom FROM Modele"
    )}
    print(f"\nBDD : {len(mdl_ids)} modèles présents")

    # Chargement ML.ENERGY
    print("\nChargement des données ML.ENERGY...")
    df = load_mlenergy_data()

    print(f"\nTâches disponibles  : {sorted(df['task'].unique())}")
    print(f"GPU disponibles     : {sorted(df['gpu_model'].unique())}")
    print(f"Modèles ({df['model_id'].nunique()}) :")
    for m in sorted(df["model_id"].unique()):
        print(f"  {m}")

    # Mapping
    print("\nMapping des noms de modèles...")
    model_mapping = build_mapping(df, mdl_ids)

    # Insertion
    print("\nInsertion dans Benchmark_Tache...")
    insert_benchmark_data(df, model_mapping, conn)

    # Résumé par tâche
    print("\nRésumé par tâche :")
    rows = cursor.execute("""
        SELECT btk_tache,
               COUNT(*) AS n,
               ROUND(AVG(btk_joules_par_token), 4) AS joules_moy,
               ROUND(MIN(btk_joules_par_token), 4) AS joules_min,
               ROUND(MAX(btk_joules_par_token), 4) AS joules_max
        FROM Benchmark_Tache
        GROUP BY btk_tache ORDER BY btk_tache
    """).fetchall()
    print(f"  {'Tâche':<35} {'N':>4}  {'J/tok moy':>10} {'J/tok min':>10} {'J/tok max':>10}")
    print("  " + "-" * 75)
    for r in rows:
        print(f"  {str(r[0]):<35} {r[1]:>4}  {str(r[2]):>10} {str(r[3]):>10} {str(r[4]):>10}")

    # Modèles en commun avec Compar:IA
    matches = cursor.execute("""
        SELECT DISTINCT m.mdl_nom, bt.btk_model_id_hf
        FROM Benchmark_Tache bt
        JOIN Modele m ON bt.mdl_id = m.mdl_id
        ORDER BY m.mdl_nom
    """).fetchall()
    print(f"\nModèles présents dans les deux datasets ({len(matches)}) :")
    for nom_bdd, nom_hf in matches:
        print(f"  {nom_bdd:<42} ← {nom_hf}")

    total = cursor.execute("SELECT COUNT(*) FROM Benchmark_Tache").fetchone()[0]
    print(f"\nTotal Benchmark_Tache : {total} lignes")
    conn.close()

    print("\n✓ Terminé.")
    print("  Prochain : python scripts/03_export_json.py")


if __name__ == "__main__":
    main()
