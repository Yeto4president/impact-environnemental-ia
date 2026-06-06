import requests

prices = requests.get(
    'https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json'
).json()

# Vérification directe des noms exacts
a_verifier = [
    'mistral/mistral-large-2411',
    'mistral/mistral-large-2512',
    'mistral/ministral-8b-2410',
    'groq/llama-3.1-8b-instant',
    'groq/llama-3.1-70b-versatile',
    'groq/llama-3.1-405b-reasoning',
    'lambda_ai/llama3.1-70b-instruct-fp8',
    'lambda_ai/llama3.1-405b-instruct-fp8',
    'cerebras/llama-3.3-70b',
    'deepseek/deepseek-chat',
    'deepseek/deepseek-v3',
    'deepseek/deepseek-r1',
    'dashscope/qwen-plus',
    'dashscope/qwen-turbo',
    'dashscope/qwen-coder',
    'cerebras/qwen-3-32b',
    'gemini/gemini-1.5-flash',
    'claude-3-5-sonnet-20241022',
    'claude-3-7-sonnet-20250219',
    'claude-4-sonnet-20250514',
    'gpt-4o-2024-08-06',
    'gpt-4.1-mini',
    'command-a-03-2025',
]

for nom in a_verifier:
    if nom in prices:
        p = prices[nom]
        inp = p.get('input_cost_per_token', 0) * 1000
        out = p.get('output_cost_per_token', 0) * 1000
        print(f"  ✓ {nom} → ${inp:.4f} / ${out:.4f}")
    else:
        print(f"  ✗ {nom}")