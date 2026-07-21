"""
generate_demo_batch.py
========================
Collega lead_finder.py alla generazione delle demo: per ogni riga del CSV
(lead_valdarno.csv) genera automaticamente una cartella con l'anteprima
pronta, scegliendo una variante di stile diversa (evitando ripetizioni
nello stesso comune) cosi le demo non sono mai tutte uguali.

- Per categorie "Ristorante" e "Location matrimoni": genera direttamente
  il file HTML finale, gia con palette/font della variante applicati.
- Per categorie ricettive (Agriturismo, Hotel/B&B): esegue clone_template.sh
  per l'identita (nome/indirizzo/telefono) e prepara un file di prompt
  pronto da incollare in Claude Code per completare lo stile (il template
  S.Maria e' un'app React/Tailwind, troppo complesso per un find&replace
  automatico sicuro sui colori — meglio farlo fare a Claude Code).

Uso:
    python3 generate_demo_batch.py lead_valdarno.csv \
        --ristorante-template ristorante-template/index.html \
        --eventi-template eventi-template/index.html \
        --smaria-dir S.Maria \
        --style-variants style_variants.json \
        --out output_demo/

Richiede che lead_valdarno.csv abbia le colonne: categoria,nome,indirizzo,
comune,telefono,email,sito_web,ha_sito (prodotte da lead_finder.py).
"""

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict

CATEGORY_MAP = {
    "Ristorante": "ristorante",
    "Cantina/vendita vino": "ristorante",  # riusa il template ristorante, adatto a sale degustazione
    "Frantoio/olio": "ristorante",
    "Location matrimoni": "eventi",
    "Agriturismo": "ricettivo",
    "Agriturismo/Farm stay": "ricettivo",
    "Hotel/B&B": "ricettivo",
    # "Centro benessere/Spa", "Palestra", "Maneggio" restano intenzionalmente
    # senza template: sono categorie a priorita' piu' bassa (vedi analisi settori),
    # restano comunque nel CSV per una valutazione manuale futura.
}

# Ordine di priorita' nella generazione quando c'e' un limite: prima le categorie
# con demo completamente automatica (ristorante/eventi), poi quelle che richiedono
# comunque un passaggio manuale con Claude Code (ricettivo/S.Maria).
KIND_PRIORITY = {"ristorante": 0, "eventi": 0, "ricettivo": 1}

TEMPLATE_VARS = {
    "ristorante": {"primario": "--brick", "secondario": "--olive", "accento": "--gold", "sfondo": "--cream", "testo": "--ink"},
    "eventi": {"primario": "--rose", "secondario": "--sage", "accento": "--gold", "sfondo": "--cream", "testo": "--ink"},
}

GOOGLE_FONTS_TEMPLATE = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link href="https://fonts.googleapis.com/css2?family={titoli}&family={testo}&display=swap" rel="stylesheet">\n'
)


def slugify(name):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return s or "cliente"


def unique_slug(base_slug, out_dir, used_slugs):
    """Evita che due lead con lo stesso nome (es. 'Agriturismo' generico)
    finiscano nella stessa cartella, causando un fallimento del clone."""
    slug = base_slug
    i = 2
    while slug in used_slugs or os.path.isdir(os.path.join(out_dir, slug)):
        slug = f"{base_slug}-{i}"
        i += 1
    used_slugs.add(slug)
    return slug


def pick_variant_for(comune, variants, used_by_comune):
    used = used_by_comune[comune]
    available = [v for v in variants if v["id"] not in used]
    if not available:
        used.clear()  # ricomincia il giro se le abbiamo usate tutte in quel comune
        available = variants
    chosen = available[0]
    used.append(chosen["id"])
    return chosen


def apply_variant_to_html(html, category, variant):
    varnames = TEMPLATE_VARS[category]
    palette = variant["palette"]

    def replace_var(css_text, var_name, value):
        pattern = re.compile(re.escape(var_name) + r"\s*:\s*#[0-9A-Fa-f]{3,6}\s*;")
        return pattern.sub(f"{var_name}:{value};", css_text, count=1)

    mapping = {
        varnames["primario"]: palette["primario"],
        varnames["secondario"]: palette["secondario"],
        varnames["accento"]: palette["accento"],
        varnames["sfondo"]: palette["sfondo"],
        varnames["testo"]: palette["testo"],
    }
    for var_name, value in mapping.items():
        html = replace_var(html, var_name, value)

    # Estrae solo il nome del font (senza descrizione tra parentesi) per Google Fonts
    def font_slug(font_desc):
        name = font_desc.split("(")[0].strip()
        return name.replace(" ", "+")

    titoli_slug = font_slug(variant["font_titoli"]) + ":wght@400;600"
    testo_slug = font_slug(variant["font_testo"]) + ":wght@400;600"
    fonts_link = GOOGLE_FONTS_TEMPLATE.format(titoli=titoli_slug, testo=testo_slug)

    titoli_name = variant["font_titoli"].split("(")[0].strip()
    testo_name = variant["font_testo"].split("(")[0].strip()

    font_override = f"""<style>
  body{{font-family:'{testo_name}',sans-serif;}}
  h1,h2,h3,.logo,.hero h1{{font-family:'{titoli_name}',serif;}}
</style>
"""

    # Inserisce i link ai font e l'override subito prima di </head>
    html = html.replace("</head>", fonts_link + font_override + "</head>")

    return html


def fill_static_template(template_path, category, row, variant, out_dir, used_slugs):
    with open(template_path, encoding="utf-8") as f:
        html = f.read()

    nome = row["nome"].strip()
    telefono = "".join(ch for ch in row.get("telefono", "") if ch.isdigit())
    if telefono and not telefono.startswith("39") and len(telefono) <= 10:
        telefono = "39" + telefono

    # Sostituzioni identita (i nomi placeholder nei due template di partenza)
    placeholders = ["Osteria della Torre", "Villa delle Ginestre"]
    for ph in placeholders:
        html = html.replace(ph, nome)
    html = re.sub(r"390000000000", telefono or "390000000000", html)
    if row.get("indirizzo"):
        html = html.replace("Via del Valdarno, 12", row["indirizzo"])
        html = html.replace("Via delle Ginestre, 24", row["indirizzo"])
    if row.get("comune"):
        html = html.replace("Figline e Incisa Valdarno (FI)", row["comune"])
        html = html.replace("Rignano sull'Arno (FI)", row["comune"])

    html = apply_variant_to_html(html, category, variant)

    slug = unique_slug(slugify(nome), out_dir, used_slugs)
    dest_dir = os.path.join(out_dir, slug)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, "index.html")
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(html)

    return dest_path, slug


def prepare_smaria_prompt(row, variant, smaria_dir, out_dir, used_slugs, clone_script="clone_template.sh"):
    nome = row["nome"].strip()
    slug = unique_slug(slugify(nome), out_dir, used_slugs)
    dest_dir = os.path.join(out_dir, slug)
    os.makedirs(dest_dir, exist_ok=True)

    indirizzo = row.get("indirizzo", "").strip() or "[INDIRIZZO DA COMPLETARE]"
    telefono = row.get("telefono", "").strip() or "[TELEFONO DA COMPLETARE]"

    clone_target = os.path.join(dest_dir, f"{slug}-sito")
    ran_clone = False
    clone_error = None
    clone_path = os.path.join(smaria_dir, clone_script)
    if os.path.isfile(clone_path):
        try:
            subprocess.run(
                ["bash", clone_script, nome, indirizzo, telefono, os.path.abspath(clone_target)],
                cwd=smaria_dir, check=True, capture_output=True, text=True,
            )
            ran_clone = True
        except subprocess.CalledProcessError as e:
            clone_error = (e.stderr or e.stdout or "errore sconosciuto").strip().splitlines()[-1][:200]
            print(f"  Attenzione: clone_template.sh ha dato errore per {nome}: {clone_error}")
    else:
        clone_error = f"clone_template.sh non trovato in {smaria_dir}"

    prompt_text = f"""Contesto: sto costruendo velocemente siti-demo da mostrare ad attivita locali
nel Valdarno fiorentino, partendo da un template esistente (S.Maria, gia clonato
in questa cartella con nome/indirizzo/telefono aggiornati).

Il tuo compito ora e' SOLO applicare la veste grafica seguente, senza toccare
struttura, componenti o funzionalita' esistenti:

VARIANTE DI STILE "{variant['nome']}":
- Colori: primario {variant['palette']['primario']}, secondario {variant['palette']['secondario']}, accento {variant['palette']['accento']}, sfondo {variant['palette']['sfondo']}, testo {variant['palette']['testo']}
- Font titoli: {variant['font_titoli']}
- Font testo: {variant['font_testo']}
- Stile hero: {variant['hero_style']}
- Note layout: {variant['layout_note']}

DATI CLIENTE gia' inseriti dal clone automatico (verifica che siano corretti ovunque):
- Nome: {nome}
- Indirizzo: {indirizzo}
- Telefono: {telefono}

Ricordami alla fine, in un breve elenco, quali contenuti (stanze/servizi, foto,
recensioni) restano ancora da personalizzare a mano in src/data.ts perche' non
avevo dati sufficienti per scriverli io in automatico.
"""
    prompt_path = os.path.join(dest_dir, "prompt_claude_code.txt")
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt_text)

    return dest_dir, ran_clone, prompt_path, clone_error


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("--ristorante-template", required=True)
    parser.add_argument("--eventi-template", required=True)
    parser.add_argument("--smaria-dir", required=True)
    parser.add_argument("--style-variants", default="style_variants.json")
    parser.add_argument("--out", default="output_demo")
    parser.add_argument("--only-without-site", action="store_true")
    parser.add_argument("--limit", type=int, default=15,
                         help="Numero massimo di demo da generare in questa esecuzione "
                              "(default 15, tarato sul ritmo settimanale sostenibile). "
                              "Il resto dei lead resta comunque nel CSV per dopo.")
    args = parser.parse_args()

    with open(args.style_variants, encoding="utf-8") as f:
        variants = json.load(f)["variants"]

    with open(args.csv_file, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if args.only_without_site:
        rows = [r for r in rows if str(r.get("ha_sito", "")).lower() in ("false", "", "0")]

    total_matched = sum(1 for r in rows if CATEGORY_MAP.get(r.get("categoria", "").strip()))
    skipped_category = [r for r in rows if not CATEGORY_MAP.get(r.get("categoria", "").strip())]

    # Priorita': prima le categorie con demo 100% automatica (ristorante/eventi),
    # poi quelle che richiedono comunque un passaggio manuale con Claude Code.
    matched_rows = [r for r in rows if CATEGORY_MAP.get(r.get("categoria", "").strip())]
    matched_rows.sort(key=lambda r: KIND_PRIORITY.get(CATEGORY_MAP[r.get("categoria", "").strip()], 9))

    limited_rows = matched_rows[: args.limit]
    dropped_for_limit = len(matched_rows) - len(limited_rows)

    os.makedirs(args.out, exist_ok=True)
    used_by_comune = defaultdict(list)
    used_slugs = set()
    report = []

    for row in limited_rows:
        categoria_raw = row.get("categoria", "").strip()
        kind = CATEGORY_MAP[categoria_raw]

        comune = row.get("comune", "sconosciuto") or "sconosciuto"
        variant = pick_variant_for(comune, variants, used_by_comune)

        if kind == "ristorante":
            path, slug = fill_static_template(args.ristorante_template, "ristorante", row, variant, args.out, used_slugs)
            report.append((row.get("nome", "?"), categoria_raw, f'Demo pronta: {path} (variante "{variant["nome"]}")'))
        elif kind == "eventi":
            path, slug = fill_static_template(args.eventi_template, "eventi", row, variant, args.out, used_slugs)
            report.append((row.get("nome", "?"), categoria_raw, f'Demo pronta: {path} (variante "{variant["nome"]}")'))
        elif kind == "ricettivo":
            dest_dir, ran_clone, prompt_path, clone_error = prepare_smaria_prompt(row, variant, args.smaria_dir, args.out, used_slugs)
            if ran_clone:
                status = "identita' clonata, stile da completare con Claude Code"
            else:
                status = f"clone fallito ({clone_error}), controlla a mano"
            report.append((row.get("nome", "?"), categoria_raw, f'{status} -> {prompt_path} (variante "{variant["nome"]}")'))

    print("\nRIEPILOGO\n" + "-" * 60)
    for nome, cat, esito in report:
        print(f"- {nome} [{cat}]: {esito}")

    if skipped_category:
        cats = sorted(set(r.get("categoria", "?") for r in skipped_category))
        print(f"\n{len(skipped_category)} lead saltati per categoria senza template mappato: {', '.join(cats)} (restano nel CSV, nessuna demo generata).")

    if dropped_for_limit > 0:
        print(f"\n{dropped_for_limit} lead idonei non processati per il limite di {args.limit} demo a esecuzione "
              f"(restano nel CSV, verranno ripresi nelle prossime settimane).")

    print(f"\nFatto. {len(report)} demo generate su {total_matched} lead idonei nel CSV. Output in: {args.out}/")


if __name__ == "__main__":
    main()
