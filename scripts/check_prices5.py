import requests

prices = requests.get(
    'https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json'
).json()

# Modèles réellement dans notre BDD
modeles_bdd = [
    'DeepSeek-V3.2', 'claude-4-5-sonnet', 'claude-4-6-sonnet',
    'deepseek-r1-0528', 'gemini-3-flash-preview', 'gemma-3-12b',
    'gemma-3-27b', 'gemma-3-4b', 'gpt-5.3', 'gpt-5.4', 'gpt-5.4-mini',
    'gpt-5.4-nano', 'grok-4.1-fast', 'grok-4.20', 'llama-3.3-70b',
    'llama-4-scout', 'llama-maverick', 'mistral-large-2512',
    'mistral-medium-2508', 'mistral-small-2506', 'mistral-small-2603',
    'qwen3-coder-next', 'qwen3-max-2025-09-23', 'qwen3.5-35b-a3b',
    'qwen3.5-397b-a17b', 'kimi-k2', 'minimax-m2',
]

print("=== Recherche dans LiteLLM ===")
for nom in modeles_bdd:
    # Cherche correspondances partielles
    matches = [k for k in prices.keys()
               if nom.lower().replace('-', '').replace('.', '') in
               k.lower().replace('-', '').replace('.', '')
               and prices[k].get('input_cost_per_token')]
    if matches:
        best = matches[0]
        p = prices[best]
        inp = p.get('input_cost_per_token', 0) * 1000
        out = p.get('output_cost_per_token', 0) * 1000
        print(f"  ✓ {nom} → {best} (${inp:.4f} / ${out:.4f})")
    else:
        print(f"  ✗ {nom} — introuvable")