import requests

prices = requests.get(
    'https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json'
).json()

prefixes_a_exclure = ['azure', 'bedrock', 'anyscale', 'databricks',
                      'deepinfra', 'gradient_ai', 'ft:', 'anthropic.',
                      'cloudflare', 'eu.', 'us.', 'au.', 'global.',
                      'replicate', 'vercel', 'crusoe', 'nebius', 'nscale',
                      'ovhcloud', 'perplexity', 'fireworks', 'cerebras/llama3',
                      'gmi/']

a_chercher = {
    'claude': ['claude-3-5-sonnet', 'claude-sonnet-4', 'claude-4'],
    'gemini-1.5': ['gemini-1.5'],
    'llama-3.1': ['llama-3.1', 'llama3.1'],
    'mistral-large': ['mistral-large'],
    'mistral-small': ['mistral-small'],
    'ministral': ['ministral'],
    'mixtral': ['open-mixtral', 'mixtral-8x'],
    'deepseek-v3': ['deepseek-v3'],
    'qwen': ['qwen2.5', 'qwen-plus', 'qwen-turbo', 'dashscope/qwen'],
}

for label, keywords in a_chercher.items():
    print(f'\n=== {label} ===')
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
        for m in matches[:4]:
            p = prices[m]
            inp = p.get('input_cost_per_token', 0) * 1000
            out = p.get('output_cost_per_token', 0) * 1000
            print(f'  {m} → ${inp:.4f} / ${out:.4f}')