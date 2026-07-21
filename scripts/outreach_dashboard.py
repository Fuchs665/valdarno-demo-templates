"""
outreach_dashboard.py
======================
Prende il CSV generato da lead_finder.py (lista attività senza sito o con
sito scadente) e genera una pagina HTML locale con, per ogni lead, un
messaggio già scritto e un bottone che apre WhatsApp con il testo
precompilato — tu devi solo controllare e premere "invia" dentro WhatsApp.

Nessun messaggio parte automaticamente: ogni invio resta un click tuo,
volontario, dentro l'app di WhatsApp. Questo rispetta i termini di WhatsApp
(l'invio massivo automatico da numero personale è vietato e rischia il ban)
ed è comunque molto più veloce che scrivere ogni messaggio a mano.

Uso (link demo uguale per tutti, come prima):
    python outreach_dashboard.py lead_valdarno.csv --demo-base-url https://tuosito.netlify.app

Uso consigliato (link reali per ciascun cliente, generati da deploy_batch.sh):
    python outreach_dashboard.py lead_valdarno.csv --demo-links-file demo_links.json --only-without-site

Poi apri il file "outreach.html" generato: per ogni lead con una demo pronta
trovi un link "Apri su WhatsApp" già pronto con nome e link demo inseriti nel
testo. Un solo click apre WhatsApp E segna il contatto come "aperto", per
farti risparmiare un secondo click ogni volta.
"""

import argparse
import csv
import json
import re
import urllib.parse

MESSAGE_TEMPLATE = """Buongiorno, mi scuso per il disturbo. Sono Davide, vivo a Rignano sull'Arno.

Ho notato che {nome} non ha un sito web proprio, e ho pensato che vi potesse interessare vederne uno gia pronto: vi ho preparato una demo gratuita, giusto per farvi vedere il potenziale.

Eccola qui: {demo_link}

Se vi piace il tipo di lavoro possiamo parlarne senza impegno, anche solo 5 minuti al telefono. Se non vi interessa nessun problema, buona giornata!"""

HTML_HEAD = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>Dashboard contatti — Valdarno</title>
<style>
  body{font-family:Arial,sans-serif;background:#f6f4ef;margin:0;padding:30px;color:#2a2621;}
  h1{font-size:1.4rem;margin-bottom:6px;}
  .sub{color:#6b6455;margin-bottom:22px;font-size:0.9rem;}
  .progress{position:sticky;top:0;background:#f6f4ef;padding:10px 0;font-size:0.9rem;font-weight:bold;border-bottom:1px solid #e4dcc9;margin-bottom:16px;}
  .card{background:#fff;border:1px solid #e4dcc9;border-radius:6px;padding:18px 22px;margin-bottom:14px;display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;}
  .card h3{margin:0 0 4px 0;font-size:1.05rem;}
  .card .meta{font-size:0.85rem;color:#6b6455;}
  .actions{display:flex;gap:10px;flex-wrap:wrap;}
  .btn{display:inline-block;padding:9px 16px;border-radius:4px;text-decoration:none;font-size:0.88rem;font-weight:bold;border:none;cursor:pointer;}
  .btn-wa{background:#25D366;color:#fff;}
  .btn-wa[disabled]{background:#ccc;color:#666;cursor:not-allowed;}
  .card.done{opacity:0.4;}
  .no-link .meta{color:#b4592e;}
  .count{font-size:0.85rem;color:#6b6455;margin-bottom:16px;}
</style>
</head>
<body>
<h1>Dashboard contatti — Valdarno</h1>
<p class="sub">Un click apre WhatsApp con il messaggio gia pronto E segna il contatto come "aperto". Controlla il messaggio e premi invia tu stesso dentro WhatsApp: l'invio resta sempre una tua azione volontaria.</p>
<div class="progress" id="progress"></div>
"""

HTML_TAIL = """
<script>
  function updateProgress(){
    const total = document.querySelectorAll('.card').length;
    const done = document.querySelectorAll('.card.done').length;
    document.getElementById('progress').textContent = done + ' / ' + total + ' contattati oggi (max consigliato 10-15 al giorno)';
  }
  document.querySelectorAll('.btn-wa').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.closest('.card').classList.add('done');
      updateProgress();
    });
  });
  updateProgress();
</script>
</body>
</html>
"""


def slugify(name):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return s or "cliente"


def build_card(row):
    nome = row.get("nome", "").strip()
    telefono = row.get("telefono", "").strip()
    categoria = row.get("categoria", "").strip()
    comune = row.get("comune", "").strip()
    demo_link = row.get("demo_link", "").strip()

    phone_clean = "".join(ch for ch in telefono if ch.isdigit())
    if phone_clean and not phone_clean.startswith("39") and len(phone_clean) <= 10:
        phone_clean = "39" + phone_clean  # prefisso Italia

    if not demo_link:
        # Nessun link demo pronto per questo cliente: mostralo comunque ma disabilitato,
        # cosi' non perdi tempo a scoprirlo solo dopo aver cliccato.
        return f"""
<div class="card no-link">
  <div>
    <h3>{nome}</h3>
    <div class="meta">{categoria} — {comune} — {telefono or 'telefono non trovato'} — demo non ancora pubblicata</div>
  </div>
  <div class="actions">
    <button class="btn btn-wa" disabled>Demo mancante</button>
  </div>
</div>
"""

    message = MESSAGE_TEMPLATE.format(nome=nome or "la vostra attivita", demo_link=demo_link)
    encoded_message = urllib.parse.quote(message)
    wa_link = f"https://wa.me/{phone_clean}?text={encoded_message}" if phone_clean else f"https://wa.me/?text={encoded_message}"

    return f"""
<div class="card">
  <div>
    <h3>{nome}</h3>
    <div class="meta">{categoria} — {comune} — {telefono or 'telefono non trovato'}</div>
  </div>
  <div class="actions">
    <a class="btn btn-wa" href="{wa_link}" target="_blank" rel="noopener">Apri su WhatsApp</a>
  </div>
</div>
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", help="CSV generato da lead_finder.py")
    parser.add_argument("--demo-base-url", default="", help="URL unico da usare per tutti (vecchia modalita', usa solo se non hai demo_links.json)")
    parser.add_argument("--demo-links-file", default="", help="File JSON {slug: url} generato da deploy_batch.sh, con i link reali per cliente")
    parser.add_argument("--only-without-site", action="store_true", help="Includi solo i lead senza sito (ha_sito=False)")
    parser.add_argument("-o", "--output", default="outreach.html")
    args = parser.parse_args()

    with open(args.csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if args.only_without_site:
        rows = [r for r in rows if str(r.get("ha_sito", "")).lower() in ("false", "", "0")]

    demo_links = {}
    if args.demo_links_file:
        try:
            with open(args.demo_links_file, encoding="utf-8") as f:
                demo_links = json.load(f)
        except FileNotFoundError:
            print(f"Attenzione: {args.demo_links_file} non trovato, procedo senza link pubblicati.")

    for r in rows:
        slug = slugify(r.get("nome", ""))
        r["demo_link"] = demo_links.get(slug, "") or args.demo_base_url

    # Prima i contatti con una demo pronta da mandare, poi quelli ancora senza link
    rows.sort(key=lambda r: 0 if r["demo_link"] else 1)

    cards_html = "\n".join(build_card(r) for r in rows)
    ready_count = sum(1 for r in rows if r["demo_link"])

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(HTML_HEAD)
        f.write(f'<div class="count">{ready_count} pronti da contattare su {len(rows)} totali</div>\n')
        f.write(cards_html)
        f.write(HTML_TAIL)

    print(f"Generato {args.output}: {ready_count} pronti da contattare su {len(rows)} totali.")


if __name__ == "__main__":
    main()
