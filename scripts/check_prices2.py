import requests

prices = requests.get(
    'https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json'
).json()

# Modèles qu'on cherche encore
a_chercher = [
    'gpt-4o-2024-08-06', 'gpt-4o-mini-2024-07-18', 'gpt-4.1-mini', 'gpt-4.1-nano',
    'o3-mini', 'o4-mini', 'claude-3-5-sonnet-20241022', 'claude-3-7-sonnet-20250219',
    'claude-sonnet-4', 'gemini-1.5-pro', 'gemini-2.0-flash', 'gemini-2.5-flash',
    'llama3.1-8b', 'llama3.1-70b', 'mistral-large-2411', 'mistral-small-2506',
    'ministral-8b-2410', 'open-mixtral-8x7b', 'open-mixtral-8x22b',
    'deepseek-chat', 'deepseek-v3', 'qwen-plus', 'qwen-turbo', 'command-a-03-2025'
]

print("Recherche directe :")
for nom in a_chercher:
    if nom in prices:
        p = prices[nom]
        inp = p.get('input_cost_per_token', 0) * 1000
        out = p.get('output_cost_per_token', 0) * 1000
        print(f"  ✓ {nom} → ${inp:.4f} / ${out:.4f}")
    else:
        print(f"  ✗ {nom} — introuvable")