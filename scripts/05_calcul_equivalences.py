"""
Script 05 — Calcul des équivalences concrètes
Entrée  : data/db/impact_ia.db
Sortie  : data/processed/equivalences.json
"""

import sqlite3
import pandas as pd
import json
import os

DB_PATH = "data/db/impact_ia.db"
OUT = "data/processed"

# ============================================================
# CONSTANTES D'ÉQUIVALENCES
# Sources : ADEME, RTE, constructeurs
# ============================================================

# 1 kWh = combien de minutes d'ampoule LED 9W
# 1 kWh / 0.009 kW = 111 heures = 6667 minutes
KWH_TO_MIN_LED = 6667

# 1 kWh = combien de km en voiture électrique
# Conso moyenne VE : 0.2 kWh/km
KWH_TO_KM_VE = 5.0

# 1 kWh = combien de % de batterie smartphone
# Batterie moyenne smartphone : 15 Wh = 0.015 kWh
# 1 kWh / 0.015 = 66.7 charges complètes = 6670 %
KWH_TO_PCT_BATTERIE = 6670

# 1 kWh = combien de minutes de streaming HD
# Streaming HD : ~0.036 kWh/heure = 0.0006 kWh/minute
# 1 kWh / 0.0006 = 1667 minutes
KWH_TO_MIN_STREAMING = 1667

# 1 kWh = combien de recherches Google
# 1 recherche Google ≈ 0.0003 kWh
KWH_TO_RECHERCHES_GOOGLE = 3333

# ============================================================
# CHARGEMENT
# ============================================================
conn = sqlite3.connect(DB_PATH)

df = pd.read_sql_query("""
    SELECT
        m.mdl_nom,
        f.frs_nom,
        f.frs_pays_datacenter,
        f.frs_co2_datacenter,
        e.nrg_kwh_moyen,
        e.nrg_wh_par_token,
        e.nrg_nb_conversations
    FROM Modele m
    LEFT JOIN Fournisseur f ON m.frs_id = f.frs_id
    LEFT JOIN Metrique_Energie e ON m.mdl_id = e.mdl_id
    WHERE e.nrg_kwh_moyen IS NOT NULL
    AND e.nrg_nb_conversations IS NOT NULL
    ORDER BY e.nrg_kwh_moyen ASC
""", conn)

conn.close()

print(f"Modèles avec données : {len(df)}")

# ============================================================
# CALCUL DES ÉQUIVALENCES PAR REQUÊTE MOYENNE
# ============================================================
results = []

for _, row in df.iterrows():
    kwh = row['nrg_kwh_moyen']
    co2_facteur = row['frs_co2_datacenter'] if pd.notna(row['frs_co2_datacenter']) else 0.357  # moyenne mondiale
    
    # CO2 en grammes
    co2_g = kwh * co2_facteur * 1000

    # Équivalences
    equiv = {
        'mdl_nom': row['mdl_nom'],
        'frs_nom': row['frs_nom'],
        'pays_datacenter': row['frs_pays_datacenter'],
        'kwh_par_requete': round(kwh, 8),
        'co2_g_par_requete': round(co2_g, 6),
        'wh_par_token': round(row['nrg_wh_par_token'], 8) if pd.notna(row['nrg_wh_par_token']) else None,
        'nb_conversations': int(row['nrg_nb_conversations']),
        'equivalences': {
            'min_led_9w': round(kwh * KWH_TO_MIN_LED, 4),
            'km_voiture_electrique': round(kwh * KWH_TO_KM_VE, 6),
            'pct_batterie_smartphone': round(kwh * KWH_TO_PCT_BATTERIE, 4),
            'min_streaming_hd': round(kwh * KWH_TO_MIN_STREAMING, 4),
            'equiv_recherches_google': round(kwh * KWH_TO_RECHERCHES_GOOGLE, 2),
        }
    }
    results.append(equiv)

# ============================================================
# STATS GLOBALES
# ============================================================
kwh_moyen_global = df['nrg_kwh_moyen'].mean()
co2_moyen_global = df.apply(
    lambda r: r['nrg_kwh_moyen'] * (r['frs_co2_datacenter'] if pd.notna(r['frs_co2_datacenter']) else 0.357) * 1000,
    axis=1
).mean()

print(f"\nStats globales :")
print(f"  kWh moyen par requête : {kwh_moyen_global:.6f}")
print(f"  CO2 moyen par requête : {co2_moyen_global:.4f} g")
print(f"  Équivalent LED        : {kwh_moyen_global * KWH_TO_MIN_LED:.2f} minutes")
print(f"  Équivalent VE         : {kwh_moyen_global * KWH_TO_KM_VE * 1000:.4f} mètres")
print(f"  Équivalent batterie   : {kwh_moyen_global * KWH_TO_PCT_BATTERIE:.4f} %")

# ============================================================
# EXPORT
# ============================================================
output = {
    'meta': {
        'nb_modeles': len(results),
        'kwh_moyen_global': round(kwh_moyen_global, 8),
        'co2_moyen_global_g': round(co2_moyen_global, 6),
        'sources_constantes': {
            'led_9w': 'ADEME — 1 kWh = 6667 min ampoule LED 9W',
            'voiture_electrique': 'ADEME — conso moyenne VE 0.2 kWh/km',
            'batterie_smartphone': 'Batterie moyenne 15 Wh',
            'streaming_hd': 'IEA — streaming HD 0.036 kWh/h',
            'recherche_google': 'Google — 0.3 Wh par recherche',
        }
    },
    'modeles': results
}

with open(f"{OUT}/equivalences.json", 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

size = os.path.getsize(f"{OUT}/equivalences.json") / 1024
print(f"\nExporté : equivalences.json ({size:.0f} Ko)")
print("Terminé.")