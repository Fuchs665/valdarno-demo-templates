#!/usr/bin/env bash
# list_pending_style.sh
# -----------------------
# Elenca in un colpo solo, con percorso completo pronto da incollare,
# tutti i prompt_claude_code.txt ancora da lavorare dentro output_demo/,
# invece di doverli cercare cartella per cartella.
#
# Non lancia niente in automatico: apri Claude Code tu, apri la cartella
# giusta, e incolli il prompt che questo script ti elenca. Il controllo
# di cosa scrive resta sempre tuo, dentro Claude Code.
#
# Uso:
#   bash scripts/list_pending_style.sh output_demo/

set -euo pipefail
OUT_DIR="${1:-output_demo}"

mapfile -t PROMPTS < <(find "$OUT_DIR" -maxdepth 2 -name "prompt_claude_code.txt")

if [ ${#PROMPTS[@]} -eq 0 ]; then
  echo "Nessun prompt_claude_code.txt trovato in $OUT_DIR."
  exit 0
fi

echo "${#PROMPTS[@]} agriturismi/B&B da completare con Claude Code:"
echo ""
i=1
for p in "${PROMPTS[@]}"; do
  dir=$(dirname "$p")
  slug=$(basename "$dir")
  site_dir=$(find "$dir" -maxdepth 1 -type d -name "*-sito" | head -1)
  echo "$i. $slug"
  echo "   Cartella sito da aprire in Claude Code: ${site_dir:-NON TROVATA, controlla a mano}"
  echo "   Prompt da incollare: $p"
  echo ""
  i=$((i+1))
done

echo "Suggerimento: apri Claude Code una volta per ciascuna cartella elencata sopra,"
echo "incolla il relativo prompt (cat NOMEFILE per vederlo/copiarlo), e passa alla successiva."
echo "Con 2-3 al giorno in pochi giorni li smaltisci tutti senza doverli cercare uno a uno."
