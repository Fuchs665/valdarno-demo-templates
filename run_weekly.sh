#!/usr/bin/env bash
# run_weekly.sh
# --------------
# Orchestratore usato dalla task programmata settimanale: lancia la ricerca
# lead e la generazione demo, partendo da un clone fresco del repo.
# Va eseguito dalla root del repo (dove ci sono le cartelle ristorante/,
# eventi/, scripts/).

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "== Installo dipendenze =="
pip install requests --break-system-packages --quiet

echo "== Ricerca lead nel Valdarno =="
python3 scripts/lead_finder.py

echo "== Clono il repo S.Maria (template agriturismi/B&B) =="
SMARIA_DIR="/tmp/S.Maria-fresh"
rm -rf "$SMARIA_DIR"
git clone --quiet https://github.com/Fuchs665/S.Maria.git "$SMARIA_DIR"
cp scripts/clone_template.sh "$SMARIA_DIR/clone_template.sh"
chmod +x "$SMARIA_DIR/clone_template.sh"

echo "== Generazione demo personalizzate =="
python3 scripts/generate_demo_batch.py lead_valdarno.csv \
  --ristorante-template ristorante/index.html \
  --eventi-template eventi/index.html \
  --smaria-dir "$SMARIA_DIR" \
  --style-variants scripts/style_variants.json \
  --out output_demo \
  --only-without-site \
  --limit 15

echo "== Fatto =="
echo "CSV: $ROOT_DIR/lead_valdarno.csv"
echo "Demo: $ROOT_DIR/output_demo/"
