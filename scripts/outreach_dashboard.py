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

Uso:
    python outreach_dashboard.py lead_valdarno.csv --demo-base-url https://tuosito.netlify.app

Poi apri il file "outreach.html" generato: per ogni lead senza sito trovi
un link "Apri su WhatsApp" già pronto con nome e link demo inseriti nel testo.
"""

import argparse
import csv
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
  .sub{color:#6b6455;margin-bottom:30px;font-size:0.9rem;}
  .card{background:#fff;border:1px solid #e4dcc9;border-radius:6px;padding:18px 22px;margin-bottom:14px;display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;}
  .card h3{margin:0 0 4px 0;font-size:1.05rem;}
  .card .meta{font-size:0.85rem;color:#6b6455;}
  .actions{display:flex;gap:10px;flex-wrap:wrap;}
  .btn{display:inline-block;padding:9px 16px;border-radius:4px;text-decoration:none;font-size:0.88rem;font-weight:bold;}
  .btn-wa{background:#25D366;color:#fff;}
  .btn-copy{background:#eee;color:#333;border:1px solid #ccc;cursor:pointer;}
  .done{opacity:0.4;}
  .count{font-size:0.85rem;color:#6b6455;margin-bottom:16px;}
</style>
</head>
<body>
<h1>Dashboard contatti — Valdarno</h1>
<p class="sub">Clicca "Apri su WhatsApp" per aprire il messaggio gia pronto: controllalo e premi invia tu stesso dentro WhatsApp. Ogni invio resta una tua azione volontaria.</p>
"""

HTML_TAIL = """
<script>
  // Segna localmente (solo in questa sessione del browser) i contatti gia aperti,
  // giusto per tenere traccia visiva mentre scorri la lista.
  document.querySelectorAll('.mark-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.closest('.card').classList.toggle('done');
    });
  });
</script>
</body>
</html>
"""


def build_card(row):
    nome = row.get("nome", "").strip()
    telefono = row.get("telefono", "").strip()
    categoria = row.get("categoria", "").strip()
    comune = row.get("comune", "").strip()
    demo_link = row.get("demo_link", "").strip() or "[INSERISCI LINK DEMO]"

    message = MESSAGE_TEMPLATE.format(nome=nome or "la vostra attivita", demo_link=demo_link)
    encoded_message = urllib.parse.quote(message)

    phone_clean = "".join(ch for ch in telefono if ch.isdigit())
    if phone_clean and not phone_clean.startswith("39") and len(phone_clean) <= 10:
        phone_clean = "39" + phone_clean  # prefisso Italia

    wa_link = f"https://wa.me/{phone_clean}?text={encoded_message}" if phone_clean else f"https://wa.me/?text={encoded_message}"

    return f"""
<div class="card">
  <div>
    <h3>{nome}</h3>
    <div class="meta">{categoria} — {comune} — {telefono or 'telefono non trovato'}</div>
  </div>
  <div class="actions">
    <a class="btn btn-wa" href="{wa_link}" target="_blank" rel="noopener">Apri su WhatsApp</a>
    <button class="btn btn-copy mark-btn" type="button">Segna come contattato</button>
  </div>
</div>
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", help="CSV generato da lead_finder.py")
    parser.add_argument("--demo-base-url", default="", help="URL base della demo da inserire nei messaggi (facoltativo, puoi anche modificarlo dopo nell'HTML)")
    parser.add_argument("--only-without-site", action="store_true", help="Includi solo i lead senza sito (ha_sito=False)")
    parser.add_argument("-o", "--output", default="outreach.html")
    args = parser.parse_args()

    with open(args.csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if args.only_without_site:
        rows = [r for r in rows if str(r.get("ha_sito", "")).lower() in ("false", "", "0")]

    for r in rows:
        r["demo_link"] = args.demo_base_url

    cards_html = "\n".join(build_card(r) for r in rows)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(HTML_HEAD)
        f.write(f'<div class="count">{len(rows)} contatti pronti</div>\n')
        f.write(cards_html)
        f.write(HTML_TAIL)

    print(f"Generato {args.output} con {len(rows)} contatti.")


if __name__ == "__main__":
    main()
