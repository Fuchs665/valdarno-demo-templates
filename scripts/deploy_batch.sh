#!/usr/bin/env bash
# deploy_batch.sh
# ----------------
# Pubblica su Netlify, in un solo comando, tutte le demo pronte dentro
# output_demo/ (quelle con index.html: ristoranti/eventi/cantine).
# NON tocca le cartelle degli agriturismi (quelle con solo
# prompt_claude_code.txt), perché quelle vanno completate prima con
# Claude Code.
#
# Il controllo resta tuo: lo script ti mostra la lista di cosa sta per
# pubblicare e chiede conferma UNA VOLTA prima di partire con tutte,
# invece di farti trascinare ogni cartella singolarmente su Netlify.
#
# Prerequisiti (una tantum, li fai tu sul tuo computer, io non tocco le
# tue credenziali):
#   npm install -g netlify-cli
#   netlify login
#
# Uso:
#   bash scripts/deploy_batch.sh output_demo/

set -euo pipefail

OUT_DIR="${1:-output_demo}"
LINKS_FILE="demo_links.json"

if ! command -v netlify &> /dev/null; then
  echo "Netlify CLI non trovata. Installala con: npm install -g netlify-cli"
  echo "Poi fai il login una tantum con: netlify login"
  exit 1
fi

# Trova tutte le cartelle con index.html pronto (esclude quelle con solo il prompt per Claude Code)
mapfile -t READY_DIRS < <(find "$OUT_DIR" -maxdepth 2 -name "index.html" -exec dirname {} \;)

if [ ${#READY_DIRS[@]} -eq 0 ]; then
  echo "Nessuna demo pronta trovata in $OUT_DIR (niente index.html)."
  exit 0
fi

echo "Trovate ${#READY_DIRS[@]} demo pronte da pubblicare:"
for d in "${READY_DIRS[@]}"; do
  echo "  - $(basename "$d")"
done
echo ""
read -p "Confermi la pubblicazione di tutte queste su Netlify? [s/N] " CONFIRM
if [[ ! "$CONFIRM" =~ ^[sS]$ ]]; then
  echo "Annullato, nessuna pubblicazione effettuata."
  exit 0
fi

# Carica (o crea) il file dei link già pubblicati, per non ripubblicare inutilmente
if [ -f "$LINKS_FILE" ]; then
  LINKS_JSON=$(cat "$LINKS_FILE")
else
  LINKS_JSON="{}"
fi

for d in "${READY_DIRS[@]}"; do
  slug=$(basename "$d")
  already=$(python3 -c "import json,sys; d=json.loads('''$LINKS_JSON'''); print(d.get('$slug',''))" 2>/dev/null || echo "")
  if [ -n "$already" ]; then
    echo "-> $slug gia' pubblicato in precedenza ($already), salto."
    continue
  fi

  echo ""
  echo "== Pubblico $slug =="
  DEPLOY_OUTPUT=$(netlify deploy --dir="$d" --prod --json 2>&1) || {
    echo "  Errore nel deploy di $slug, controlla a mano:"
    echo "$DEPLOY_OUTPUT" | tail -10
    continue
  }
  URL=$(echo "$DEPLOY_OUTPUT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('deploy_url',''))" 2>/dev/null || echo "")
  if [ -n "$URL" ]; then
    echo "  Pubblicato: $URL"
    LINKS_JSON=$(python3 -c "import json; d=json.loads('''$LINKS_JSON'''); d['$slug']='$URL'; print(json.dumps(d))")
  fi
done

echo "$LINKS_JSON" > "$LINKS_FILE"
echo ""
echo "Fatto. Link salvati in $LINKS_FILE (usali con outreach_dashboard.py --demo-links-file $LINKS_FILE)"
