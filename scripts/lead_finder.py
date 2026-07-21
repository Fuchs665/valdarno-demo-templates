"""
lead_finder.py
================
Trova attività locali (per categoria e area) che NON hanno un sito web
registrato su OpenStreetMap, e controlla la qualità dei siti di chi invece
ce l'ha già (vecchio/lento/non mobile-friendly).

Fonti dati usate (entrambe legali e gratuite, nessuno scraping di Google/Facebook):
- Overpass API (dati OpenStreetMap) per l'elenco delle attività
- Google PageSpeed Insights API (pubblica, gratuita fino a una certa quota)
  per valutare la qualità/velocità dei siti esistenti

Installazione:
    pip install requests --break-system-packages

Uso base:
    python lead_finder.py
(modifica i parametri qui sotto: area, categorie, raggio)
"""

import csv
import json
import re
import time
from datetime import datetime

import requests

# ---------------------------------------------------------------------------
# CONFIGURAZIONE
# ---------------------------------------------------------------------------

# Centro dell'area di ricerca (lat, lon). Esempio: punto medio tra Rignano e Figline.
CENTER_LAT = 43.7550
CENTER_LON = 11.4100
RADIUS_METERS = 15000  # 15 km

# Categorie OSM da cercare. Puoi aggiungerne quante ne vuoi.
# Formato: (etichetta leggibile, tag OSM chiave=valore)
CATEGORIES = [
    ("Agriturismo", "tourism=guest_house"),
    ("Agriturismo/Farm stay", "tourism=chalet"),
    ("Hotel/B&B", "tourism=hotel"),
    ("Ristorante", "amenity=restaurant"),
    ("Cantina/vendita vino", "shop=wine"),
    ("Frantoio/olio", "craft=winery"),
    ("Centro benessere/Spa", "leisure=spa"),
    ("Palestra", "leisure=fitness_centre"),
    ("Location matrimoni", "amenity=events_venue"),
    ("Maneggio", "sport=equestrian"),
]

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
PAGESPEED_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

OUTPUT_CSV = "lead_valdarno.csv"


# ---------------------------------------------------------------------------
# STEP 1: interrogare Overpass per ogni categoria
# ---------------------------------------------------------------------------

def build_overpass_query(tag_expr, lat, lon, radius):
    key, value = tag_expr.split("=")
    return f"""
    [out:json][timeout:60];
    (
      node["{key}"="{value}"](around:{radius},{lat},{lon});
      way["{key}"="{value}"](around:{radius},{lat},{lon});
    );
    out center tags;
    """


def fetch_category(label, tag_expr, max_retries=3):
    query = build_overpass_query(tag_expr, CENTER_LAT, CENTER_LON, RADIUS_METERS)
    headers = {"User-Agent": "valdarno-lead-finder/1.0 (uso personale, ricerca attivita locali)"}

    resp = None
    for attempt in range(1, max_retries + 1):
        resp = requests.post(OVERPASS_URL, data={"data": query}, headers=headers, timeout=90)
        if resp.status_code == 429 or resp.status_code >= 500:
            wait = 15 * attempt
            print(f"  Overpass occupato (status {resp.status_code}), riprovo tra {wait}s...")
            time.sleep(wait)
            continue
        break

    resp.raise_for_status()
    data = resp.json()

    results = []
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue  # scartiamo elementi senza nome, poco utili

        website = tags.get("website") or tags.get("contact:website")
        phone = tags.get("phone") or tags.get("contact:phone")
        email = tags.get("email") or tags.get("contact:email")

        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")

        results.append({
            "categoria": label,
            "nome": name,
            "indirizzo": tags.get("addr:street", "") + " " + tags.get("addr:housenumber", ""),
            "comune": tags.get("addr:city", ""),
            "telefono": phone or "",
            "email": email or "",
            "sito_web": website or "",
            "ha_sito": bool(website),
            "lat": lat,
            "lon": lon,
        })
    return results


# ---------------------------------------------------------------------------
# STEP 2: per chi ha un sito, valutarne rapidamente la qualità
# ---------------------------------------------------------------------------

def check_site_quality(url, api_key=None):
    """
    Ritorna un piccolo report sulla qualità del sito:
    - punteggio mobile PageSpeed (0-100) se hai una API key di Google
    - anno copyright trovato nell'HTML (segnale di sito vecchio)
    - se il sito risponde correttamente (status code)
    """
    report = {"status_code": None, "copyright_year": None, "pagespeed_mobile": None}

    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        report["status_code"] = r.status_code
        match = re.search(r"(?:©|copyright)\s*(\d{4})", r.text, re.IGNORECASE)
        if match:
            report["copyright_year"] = int(match.group(1))
    except requests.RequestException:
        report["status_code"] = "ERRORE/non raggiungibile"

    # PageSpeed Insights: richiede una API key gratuita di Google Cloud
    # (Google Cloud Console -> abilita "PageSpeed Insights API" -> crea chiave)
    if api_key:
        try:
            params = {"url": url, "strategy": "mobile", "key": api_key}
            r = requests.get(PAGESPEED_URL, params=params, timeout=30)
            if r.status_code == 200:
                score = r.json()["lighthouseResult"]["categories"]["performance"]["score"]
                report["pagespeed_mobile"] = round(score * 100)
        except Exception:
            pass

    return report


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main(pagespeed_api_key=None):
    all_rows = []

    for label, tag_expr in CATEGORIES:
        print(f"Cerco categoria: {label} ...")
        try:
            rows = fetch_category(label, tag_expr)
        except Exception as e:
            print(f"  Errore su {label}: {e}")
            continue
        print(f"  Trovate {len(rows)} attività")
        all_rows.extend(rows)
        time.sleep(5)  # essere gentili con l'API pubblica di Overpass, evita 429

    # Arricchisci con controllo qualità sito, solo per chi ha un sito
    for row in all_rows:
        if row["ha_sito"]:
            print(f"Controllo sito: {row['nome']} -> {row['sito_web']}")
            q = check_site_quality(row["sito_web"], api_key=pagespeed_api_key)
            row.update(q)
            time.sleep(1)

    # Ordina: prima chi NON ha sito (i lead migliori), poi chi ha siti scadenti
    all_rows.sort(key=lambda r: (r["ha_sito"], r.get("pagespeed_mobile") or 0))

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["categoria", "nome", "indirizzo", "comune", "telefono", "email",
                      "sito_web", "ha_sito", "status_code", "copyright_year",
                      "pagespeed_mobile", "lat", "lon"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    print(f"\nFatto. {len(all_rows)} attività salvate in {OUTPUT_CSV}")
    print(f"Generato il {datetime.now().isoformat()}")


if __name__ == "__main__":
    # Se hai una API key gratuita di Google PageSpeed Insights, mettila qui.
    # Senza key lo script funziona comunque, semplicemente non calcola il punteggio velocità.
    main(pagespeed_api_key=None)
