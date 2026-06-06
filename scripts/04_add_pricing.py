"""
Script 04 — Ajout des tarifs depuis LiteLLM
Entrée  : data/db/impact_ia.db
Source  : https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json
"""

import sqlite3
import requests
import json
import os

DB_PATH = "data/db/impact_ia.db"

# Mapping noms Compar:IA → noms LiteLLM
NOM_MAPPING = {
    # Anthropic
    'claude-4-5-sonnet': 'claude-sonnet-4-5',
    'claude-3-7-sonnet': 'claude-3-7-sonnet-20250219',
    # OpenAI
    'gpt-5.3': 'gpt-5.3',
    'gpt-5.4': 'gpt-5.4',
    'gpt-5.4-mini': 'gpt-5.4-mini',
    'gpt-5.4-nano': 'gpt-5.4-nano',
    # Google
    'gemini-3-flash-preview': 'gemini-3-flash-preview',
    'gemma-3-4b': 'google.gemma-3-4b-it',
    'gemma-3-12b': 'google.gemma-3-12b-it',
    'gemma-3-27b': 'google.gemma-3-27b-it',
    # Meta
    'llama-3.3-70b': 'cerebras/llama-3.3-70b',
    'llama-4-scout': 'lambda_ai/llama4-scout-17b-16e-instruct',
    # Mistral
    'mistral-large-2512': 'mistral/mistral-large-2512',
    'mistral-medium-2508': 'mistral/mistral-medium-2505',
    'mistral-small-2506': 'mistral/mistral-small-3-2-2506',
    'mistral-small-2603': 'mistral/mistral-small-3-2-2506',
    # DeepSeek
    'DeepSeek-V3.2': 'deepseek/deepseek-v3.2',
    'deepseek-r1-0528': 'deepseek/deepseek-r1',
    # xAI
    'grok-4.1-fast': 'xai/grok-4-1-fast',
    'grok-4.20': 'xai/grok-4.20',
    # Alibaba
    'qwen3-coder-next': 'openrouter/qwen/qwen3-coder-next',
    'qwen3.5-35b-a3b': 'openrouter/qwen/qwen3.5-35b-a3b',
    'qwen3.5-397b-a17b': 'openrouter/qwen/qwen3.5-397b-a17b',
    # Moonshot
    'kimi-k2': 'openrouter/moonshotai/kimi-k2',
    'kimi-k2-thinking': 'openrouter/moonshotai/kimi-k2',
    # Minimax
    'minimax-m2': 'openrouter/minimax/minimax-m2',
}
# ============================================================
# TÉLÉCHARGEMENT
# ============================================================
print("Téléchargement des prix LiteLLM...")
url = "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"
response = requests.get(url, timeout=30)
prices = response.json()
print(f"  → {len(prices)} modèles dans LiteLLM")

# ============================================================
# CRÉATION TABLE TARIF
# ============================================================
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS Tarif")
cursor.execute("""
    CREATE TABLE Tarif (
        trf_id              INTEGER PRIMARY KEY AUTOINCREMENT,
        mdl_id              INTEGER UNIQUE,
        trf_input_1k        REAL,
        trf_output_1k       REAL,
        trf_source          TEXT,
        FOREIGN KEY (mdl_id) REFERENCES Modele(mdl_id)
    )
""")
conn.commit()
print("  → Table Tarif créée")

# ============================================================
# INSERTION
# ============================================================
mdl_ids = {row[1]: row[0] for row in cursor.execute(
    "SELECT mdl_id, mdl_nom FROM Modele"
)}

print("\nRecherche des prix...")
trouves = 0
non_trouves = []

for nom_comparia, nom_litellm in NOM_MAPPING.items():
    mdl_id = mdl_ids.get(nom_comparia)
    if not mdl_id:
        continue

    data = prices.get(nom_litellm)
    if not data:
        non_trouves.append(nom_comparia)
        continue

    input_cost = data.get('input_cost_per_token', 0) * 1000
    output_cost = data.get('output_cost_per_token', 0) * 1000

    cursor.execute("""
        INSERT OR REPLACE INTO Tarif (mdl_id, trf_input_1k, trf_output_1k, trf_source)
        VALUES (?, ?, ?, ?)
    """, (mdl_id, round(input_cost, 6), round(output_cost, 6), nom_litellm))
    trouves += 1
    print(f"  ✓ {nom_comparia} → input: ${input_cost:.4f} / output: ${output_cost:.4f} per 1k tokens")

conn.commit()

if non_trouves:
    print(f"\nNon trouvés dans LiteLLM ({len(non_trouves)}) :")
    for m in non_trouves:
        print(f"  - {m}")

print(f"\n{trouves} tarifs insérés")

# ============================================================
# VÉRIFICATION
# ============================================================
count = cursor.execute("SELECT COUNT(*) FROM Tarif").fetchone()[0]
print(f"Table Tarif : {count} lignes")

conn.close()
print("Terminé.")