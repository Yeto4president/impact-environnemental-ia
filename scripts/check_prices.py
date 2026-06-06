import requests

prices = requests.get(
    'https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json'
).json()

# Chercher uniquement les entrées sans préfixe fournisseur tiers
# (pas azure/, bedrock/, anyscale/, etc.)
prefixes_a_exclure = ['azure', 'bedrock', 'anyscale', 'databricks', 
                      'deepinfra', 'gradient_ai', 'ft:', 'anthropic.']

keywords = ['gpt-4o', 'gpt-4.1', 'o3-mini', 'o4-mini', 'gemini', 'gemma',
            'llama', 'mistral', 'mixtral', 'deepseek', 'qwen', 'command', 'claude']

for kw in keywords:
    matches = []
    for k in prices.keys():
        if kw.lower() not in k.lower():
            continue
        if not prices[k].get('input_cost_per_token'):
            continue
        if any(k.startswith(p) for p in prefixes_a_exclure):
            continue
        matches.append(k)

    print(f'\n=== {kw} ===')
    for m in matches[:8]:
        p = prices[m]
        inp = p.get('input_cost_per_token', 0) * 1000
        out = p.get('output_cost_per_token', 0) * 1000
        print(f'  {m} → input: ${inp:.4f} / output: ${out:.4f}')