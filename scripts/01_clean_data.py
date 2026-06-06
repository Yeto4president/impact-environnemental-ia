"""
Script 01 — Nettoyage et préparation des données
Entrées  : data/raw/
Sorties  : data/processed/
"""

import pandas as pd
import os

RAW = "data/raw"
OUT = "data/processed"
os.makedirs(OUT, exist_ok=True)

# ============================================================
# 1. MAPPING FOURNISSEURS
# ============================================================
mapping_fournisseur = {
    'claude-3-5-sonnet-v2': 'Anthropic', 'claude-3-7-sonnet': 'Anthropic',
    'claude-4-5-sonnet': 'Anthropic', 'claude-4-6-sonnet': 'Anthropic',
    'claude-4-sonnet': 'Anthropic', 'gpt-4.1-mini': 'OpenAI',
    'gpt-4.1-nano': 'OpenAI', 'gpt-4o-2024-08-06': 'OpenAI',
    'gpt-4o-mini-2024-07-18': 'OpenAI', 'gpt-5': 'OpenAI',
    'gpt-5-mini': 'OpenAI', 'gpt-5-nano': 'OpenAI', 'gpt-5.1': 'OpenAI',
    'gpt-5.2': 'OpenAI', 'gpt-5.3': 'OpenAI', 'gpt-5.4': 'OpenAI',
    'gpt-5.4-mini': 'OpenAI', 'gpt-5.4-nano': 'OpenAI',
    'gpt-oss-120b': 'OpenAI', 'gpt-oss-20b': 'OpenAI',
    'o3-mini': 'OpenAI', 'o4-mini': 'OpenAI',
    'gemini-1.5-pro': 'Google', 'gemini-2.0-flash': 'Google',
    'gemini-2.5-flash': 'Google', 'gemini-3-flash-preview': 'Google',
    'gemini-3-pro-preview': 'Google', 'gemini-3.1-flash-lite-preview': 'Google',
    'gemini-3.1-pro-preview': 'Google', 'gemma-2-27b-it-q8': 'Google',
    'gemma-2-9b-it': 'Google', 'gemma-3-12b': 'Google',
    'gemma-3-27b': 'Google', 'gemma-3-4b': 'Google',
    'gemma-3n-e4b-it': 'Google', 'gemma-4-26b-a4b-it': 'Google',
    'gemma-4-31b-it': 'Google', 'llama-3.1-405b': 'Meta',
    'llama-3.1-70b': 'Meta', 'llama-3.1-8b': 'Meta',
    'llama-3.1-nemotron-70b-instruct': 'Meta', 'llama-3.3-70b': 'Meta',
    'llama-4-scout': 'Meta', 'llama-maverick': 'Meta',
    'magistral-medium': 'Mistral', 'magistral-small-2506': 'Mistral',
    'ministral-8b-instruct-2410': 'Mistral', 'mistral-large-2411': 'Mistral',
    'mistral-large-2512': 'Mistral', 'mistral-medium-2508': 'Mistral',
    'mistral-nemo-2407': 'Mistral', 'mistral-saba': 'Mistral',
    'mistral-small-24b-instruct-2501': 'Mistral', 'mistral-small-2506': 'Mistral',
    'mistral-small-2603': 'Mistral', 'mistral-small-3.1-24b': 'Mistral',
    'mixtral-8x22b-instruct-v0.1': 'Mistral', 'mixtral-8x7b-instruct-v0.1': 'Mistral',
    'deepseek-chat-v3.1': 'DeepSeek', 'deepseek-r1': 'DeepSeek',
    'deepseek-r1-0528': 'DeepSeek', 'deepseek-r1-distill-llama-70b': 'DeepSeek',
    'deepseek-v3-0324': 'DeepSeek', 'deepseek-v3-chat': 'DeepSeek',
    'DeepSeek-V3.2': 'DeepSeek', 'qwen-3-8b': 'Alibaba',
    'qwen2-7b-instruct': 'Alibaba', 'qwen2.5-32b-instruct': 'Alibaba',
    'qwen2.5-7b-instruct': 'Alibaba', 'qwen2.5-coder-32b-instruct': 'Alibaba',
    'qwen3-30b-a3b': 'Alibaba', 'qwen3-32b': 'Alibaba',
    'qwen3-coder-next': 'Alibaba', 'qwen3-max-2025-09-23': 'Alibaba',
    'qwen3.5-35b-a3b': 'Alibaba', 'qwen3.5-397b-a17b': 'Alibaba',
    'qwen3.6-plus': 'Alibaba', 'qwq-32b': 'Alibaba',
    'Qwen3-Coder-480B-A35B-Instruct': 'Alibaba',
    'grok-3-mini-beta': 'xAI', 'grok-4-fast': 'xAI',
    'grok-4.1-fast': 'xAI', 'grok-4.20': 'xAI',
    'command-a': 'Amazon', 'aya-expanse-32b': 'Cohere',
    'aya-expanse-8b': 'Cohere', 'c4ai-command-r-08-2024': 'Cohere',
    'phi-3.5-mini-instruct': 'Microsoft', 'phi-4': 'Microsoft',
    'nemotron-3-super-120b-a12b': 'Nvidia',
    'Apertus-70B-Instruct-2509': 'Mistral', 'Apertus-8B-Instruct-2509': 'Mistral',
    'EuroLLM-22B-Instruct-2512': 'Autre', 'Yi-1.5-9B-Chat': 'Autre',
    'chocolatine-14b-instruct-dpo-v1.2-q4': 'Autre',
    'chocolatine-2-14b-instruct-v2.0.3-q8': 'Autre',
    'glm-4.5': 'Autre', 'glm-4.6': 'Autre', 'glm-4.7': 'Autre',
    'glm-5': 'Autre', 'glm-5.1': 'Autre',
    'hermes-3-llama-3.1-405b': 'Autre', 'hermes-4-70b': 'Autre',
    'jamba-1.5-large': 'AI21 Labs', 'kimi-k2': 'Autre',
    'kimi-k2-thinking': 'Autre', 'kimi-k2.5': 'Autre', 'kimi-k2.6': 'Autre',
    'lfm-40b': 'Autre', 'lfm2-24b-a2b': 'Autre', 'lfm2-8b-a1b': 'Autre',
    'minimax-m2': 'Autre', 'minimax-m2.5': 'Autre', 'minimax-m2.7': 'Autre',
    'olmo-3-32b-think': 'Autre', 'trinity-large-preview': 'Autre',
}

datacenter_pays = {
   'OpenAI': 'États-Unis', 'Google': 'États-Unis', 'Anthropic': 'États-Unis',
    'Meta': 'États-Unis', 'xAI': 'États-Unis', 'Amazon': 'États-Unis',
    'Microsoft': 'États-Unis', 'Mistral': 'France', 'DeepSeek': 'Chine',
    'Alibaba': 'Chine', 'Cohere': 'Canada', 'AI21 Labs': 'États-Unis',
    'Nvidia': 'États-Unis',
    # Fournisseurs FMTI sans modèles dans Compar:IA
    'IBM': 'États-Unis',
    'Midjourney': 'États-Unis',
    'Writer': 'États-Unis',
}

# ============================================================
# 2. CHARGEMENT
# ============================================================
print("Chargement des données...")
conv = pd.read_parquet(f"{RAW}/conversations.parquet")
react = pd.read_parquet(f"{RAW}/reactions.parquet")
votes = pd.read_parquet(f"{RAW}/votes.parquet")
scores = pd.read_csv(f"{RAW}/Dec2025_scores (1).csv")
indicators = pd.read_csv(f"{RAW}/Dec2025_indicators.csv")
ademe = pd.read_csv(f"{RAW}/Base_Carbone_V23.6.csv",
                    encoding='latin1', sep=';', low_memory=False)

# ============================================================
# 3. NETTOYAGE CONVERSATIONS
# ============================================================
print("Nettoyage conversations...")
conv = conv[[
    'id', 'timestamp', 'model_a_name', 'model_b_name',
    'conversation_pair_id', 'conv_turns',
    'total_conv_a_output_tokens', 'total_conv_b_output_tokens',
    'total_conv_a_kwh', 'total_conv_b_kwh',
    'model_a_total_params', 'model_b_total_params',
    'categories', 'languages'
]].copy()
conv['fournisseur_a'] = conv['model_a_name'].map(mapping_fournisseur)
conv['fournisseur_b'] = conv['model_b_name'].map(mapping_fournisseur)
conv['wh_per_token_a'] = (conv['total_conv_a_kwh'] * 1000) / conv['total_conv_a_output_tokens'].replace(0, pd.NA)
conv['wh_per_token_b'] = (conv['total_conv_b_kwh'] * 1000) / conv['total_conv_b_output_tokens'].replace(0, pd.NA)
print(f"  → {len(conv)} lignes")

# ============================================================
# 4. NETTOYAGE REACTIONS
# ============================================================
print("Nettoyage reactions...")
react = react[[
    'id', 'conversation_pair_id', 'refers_to_model',
    'model_a_name', 'model_b_name',
    'liked', 'disliked', 'useful', 'complete',
    'incorrect', 'superficial', 'instructions_not_followed'
]].copy()
print(f"  → {len(react)} lignes")

# ============================================================
# 5. NETTOYAGE VOTES
# ============================================================
print("Nettoyage votes...")
votes = votes[[
    'id', 'conversation_pair_id', 'model_a_name', 'model_b_name',
    'chosen_model_name', 'both_equal',
    'conv_useful_a', 'conv_useful_b',
    'conv_incorrect_a', 'conv_incorrect_b',
    'conv_complete_a', 'conv_complete_b'
]].copy()
votes['fournisseur_gagnant'] = votes['chosen_model_name'].map(mapping_fournisseur)
print(f"  → {len(votes)} lignes")

# ============================================================
# 6. AGRÉGATION PAR MODÈLE (global)
# ============================================================
print("Agrégation par modèle...")
conv_a = conv[['model_a_name', 'fournisseur_a', 'total_conv_a_kwh',
               'total_conv_a_output_tokens', 'wh_per_token_a',
               'model_a_total_params']].rename(columns={
    'model_a_name': 'model', 'fournisseur_a': 'fournisseur',
    'total_conv_a_kwh': 'kwh', 'total_conv_a_output_tokens': 'tokens',
    'wh_per_token_a': 'wh_per_token', 'model_a_total_params': 'total_params'
})
conv_b = conv[['model_b_name', 'fournisseur_b', 'total_conv_b_kwh',
               'total_conv_b_output_tokens', 'wh_per_token_b',
               'model_b_total_params']].rename(columns={
    'model_b_name': 'model', 'fournisseur_b': 'fournisseur',
    'total_conv_b_kwh': 'kwh', 'total_conv_b_output_tokens': 'tokens',
    'wh_per_token_b': 'wh_per_token', 'model_b_total_params': 'total_params'
})
conv_long = pd.concat([conv_a, conv_b], ignore_index=True)

energie_modele = conv_long.groupby(['model', 'fournisseur']).agg(
    nb_conversations=('kwh', 'count'),
    kwh_moyen=('kwh', 'mean'),
    kwh_median=('kwh', 'median'),
    wh_per_token_moyen=('wh_per_token', 'mean'),
    total_params=('total_params', 'first')
).reset_index().round(6)

satisfaction = react.groupby('refers_to_model').agg(
    nb_likes=('liked', 'sum'),
    nb_dislikes=('disliked', 'sum'),
    taux_incorrect=('incorrect', 'mean'),
    taux_superficial=('superficial', 'mean'),
).reset_index()
satisfaction['taux_satisfaction'] = (
    satisfaction['nb_likes'] /
    (satisfaction['nb_likes'] + satisfaction['nb_dislikes'])
).round(3)
satisfaction = satisfaction.rename(columns={'refers_to_model': 'model'})

victoires = votes[votes['chosen_model_name'].notna()].groupby(
    'chosen_model_name'
).size().reset_index(name='nb_victoires')
total_duels = votes.groupby('model_a_name').size().reset_index(name='nb_duels')
total_duels = total_duels.rename(columns={'model_a_name': 'model'})
victoires = victoires.rename(columns={'chosen_model_name': 'model'})
victoires = victoires.merge(total_duels, on='model', how='left')
victoires['taux_victoire'] = (victoires['nb_victoires'] / victoires['nb_duels']).round(3)

modeles_final = energie_modele.merge(satisfaction, on='model', how='left')
modeles_final = modeles_final.merge(
    victoires[['model', 'taux_victoire']], on='model', how='left'
)
print(f"  → {len(modeles_final)} modèles")

# ============================================================
# 7. AGRÉGATION PAR MODÈLE + CATÉGORIE
# ============================================================
print("Agrégation par modèle et catégorie...")
conv_cat_a = conv[['model_a_name', 'fournisseur_a', 'total_conv_a_kwh',
                   'total_conv_a_output_tokens', 'wh_per_token_a', 'categories']].rename(columns={
    'model_a_name': 'model', 'fournisseur_a': 'fournisseur',
    'total_conv_a_kwh': 'kwh', 'total_conv_a_output_tokens': 'tokens',
    'wh_per_token_a': 'wh_per_token'
})
conv_cat_b = conv[['model_b_name', 'fournisseur_b', 'total_conv_b_kwh',
                   'total_conv_b_output_tokens', 'wh_per_token_b', 'categories']].rename(columns={
    'model_b_name': 'model', 'fournisseur_b': 'fournisseur',
    'total_conv_b_kwh': 'kwh', 'total_conv_b_output_tokens': 'tokens',
    'wh_per_token_b': 'wh_per_token'
})
conv_cat = pd.concat([conv_cat_a, conv_cat_b], ignore_index=True)
conv_cat['categories'] = conv_cat['categories'].astype(str).str.strip()

modeles_par_categorie = conv_cat.groupby(['model', 'fournisseur', 'categories']).agg(
    nb_conversations=('kwh', 'count'),
    kwh_moyen=('kwh', 'mean'),
    wh_per_token_moyen=('wh_per_token', 'mean'),
).reset_index().round(6)
print(f"  → {len(modeles_par_categorie)} lignes modèle×catégorie")

# ============================================================
# 8. FMTI
# ============================================================
print("Nettoyage FMTI...")
fmti_long = scores.melt(id_vars='Indicator', var_name='fournisseur', value_name='score')
fmti_long = fmti_long.merge(indicators[['Indicator', 'Domain', 'Subdomain']], on='Indicator')
fmti_global = fmti_long.groupby('fournisseur')['score'].sum().reset_index()
fmti_global.columns = ['fournisseur', 'score_fmti_total']
fmti_domaine = fmti_long.groupby(['fournisseur', 'Domain'])['score'].sum().reset_index()
print(f"  → {len(fmti_global)} fournisseurs")

# ============================================================
# 9. ADEME
# ============================================================
print("Nettoyage ADEME...")
mask = (
    ademe['Nom base français'].astype(str).str.lower().str.contains('électricité|electricit', na=False)
) & (
    ademe["Statut de l'élément"] == 'Valide générique'
) & (
    ademe['Nom attribut français'].astype(str).str.contains('mix moyen', na=False)
)
elec = ademe[mask][[
    'Sous-localisation géographique français',
    'Total poste non décomposé'
]].rename(columns={
    'Sous-localisation géographique français': 'pays',
    'Total poste non décomposé': 'facteur_kgco2_kwh'
})
elec['facteur_kgco2_kwh'] = elec['facteur_kgco2_kwh'].astype(str).str.replace(',', '.').str.strip()
elec['facteur_kgco2_kwh'] = pd.to_numeric(elec['facteur_kgco2_kwh'], errors='coerce')
elec = elec.groupby('pays')['facteur_kgco2_kwh'].sum().reset_index()
elec = elec.dropna(subset=['pays'])
print(f"  → {len(elec)} pays")

# ============================================================
# 10. TABLE FOURNISSEURS ENRICHIE
# ============================================================
fournisseurs = pd.DataFrame([
    {'fournisseur': f, 'pays_datacenter': p}
    for f, p in datacenter_pays.items()
])
fournisseurs = fournisseurs.merge(fmti_global, on='fournisseur', how='left')
fournisseurs = fournisseurs.merge(
    elec.rename(columns={
        'pays': 'pays_datacenter',
        'facteur_kgco2_kwh': 'facteur_co2_datacenter'
    }),
    on='pays_datacenter', how='left'
)

# ============================================================
# 11. EXPORTS JSON
# ============================================================
print("\nExport JSON...")

modeles_final.to_json(f"{OUT}/modeles.json", orient='records', force_ascii=False, indent=2)
modeles_par_categorie.to_json(f"{OUT}/modeles_par_categorie.json", orient='records', force_ascii=False, indent=2)
fmti_global.to_json(f"{OUT}/fmti_scores_global.json", orient='records', force_ascii=False, indent=2)
fmti_domaine.to_json(f"{OUT}/fmti_scores_domaine.json", orient='records', force_ascii=False, indent=2)
fmti_long.to_json(f"{OUT}/fmti_detail.json", orient='records', force_ascii=False, indent=2)
elec.to_json(f"{OUT}/facteurs_emissions.json", orient='records', force_ascii=False, indent=2)
fournisseurs.to_json(f"{OUT}/fournisseurs.json", orient='records', force_ascii=False, indent=2)

# Supprimer les anciens fichiers bruts si présents
for f_brut in ['conversations.json', 'reactions.json', 'votes.json']:
    path = f"{OUT}/{f_brut}"
    if os.path.exists(path):
        os.remove(path)
        print(f"  Supprimé : {f_brut}")

print("Fichiers exportés :")
for f in sorted(os.listdir(OUT)):
    if f != '.gitkeep':
        size = os.path.getsize(f"{OUT}/{f}") / 1024
        print(f"  {f} — {size:.0f} Ko")

print("\nTerminé.")