#!/usr/bin/env bash
# clone_template.sh
# ------------------
# Duplica questo template ("S.Maria") in una nuova cartella e sostituisce
# ovunque nome, indirizzo e telefono, in modo da avere in pochi secondi
# una demo pronta con l'identità del nuovo cliente.
#
# NOTA: sostituisce solo i dati "ripetuti ovunque" (nome, indirizzo, telefono).
# I contenuti specifici (stanze, menu, attrazioni vicine, recensioni) vanno
# comunque adattati a mano in src/data.ts (o nella sezione dati di index.html),
# perché sono diversi per ogni attività.
#
# Uso:
#   ./clone_template.sh "Nome Nuova Struttura" "Via Nuova, 10 - Comune (FI)" "+39 333 1234567" nome-cartella-output
#
# Esempio:
#   ./clone_template.sh "Fontepetrini" "Via Fontepetrini, 102 - Rignano sull'Arno (FI)" "328 9652935" fontepetrini

set -euo pipefail

if [ "$#" -ne 4 ]; then
  echo "Uso: $0 \"Nome Struttura\" \"Indirizzo completo\" \"Telefono\" cartella-output"
  exit 1
fi

NEW_NAME="$1"
NEW_ADDRESS="$2"
NEW_PHONE="$3"
OUT_DIR="$4"

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -d "$OUT_DIR" ]; then
  echo "La cartella $OUT_DIR esiste già, scegli un altro nome."
  exit 1
fi

echo "Copio il template in $OUT_DIR ..."
cp -r "$SRC_DIR" "$OUT_DIR"
rm -rf "$OUT_DIR/.git" "$OUT_DIR/node_modules" 2>/dev/null || true

OLD_NAME="Podere Santa Maria"
OLD_ADDRESS_IT="Via S. Martino Altoreggi, 8 — Figline e Incisa Valdarno (FI)"
OLD_ADDRESS_SIMPLE="Via S. Martino Altoreggi, 8"
OLD_PHONE_PLACEHOLDER="+39 000 0000000"  # verifica se nel repo c'è un numero reale da sostituire

echo "Sostituisco nome struttura in tutti i file di testo..."
grep -rlZ --include="*.ts" --include="*.tsx" --include="*.html" --include="*.js" --include="*.json" "$OLD_NAME" "$OUT_DIR" 2>/dev/null \
  | xargs -0 -r sed -i "s|$OLD_NAME|$NEW_NAME|g"

echo "Sostituisco indirizzo in tutti i file di testo..."
grep -rlZ --include="*.ts" --include="*.tsx" --include="*.html" --include="*.js" --include="*.json" "$OLD_ADDRESS_SIMPLE" "$OUT_DIR" 2>/dev/null \
  | xargs -0 -r sed -i "s|$OLD_ADDRESS_IT|$NEW_ADDRESS|g; s|$OLD_ADDRESS_SIMPLE|$NEW_ADDRESS|g"

echo "Fatto. Struttura creata in: $OUT_DIR"
echo ""
echo "Prossimi passi manuali (obbligatori, non automatizzabili):"
echo "1. In $OUT_DIR/src/data.ts: aggiorna ROOM_OPTIONS/ATTRACTIONS/FAQS/INITIAL_REVIEWS con i contenuti reali del cliente"
echo "2. In $OUT_DIR/images/: sostituisci le foto con quelle vere della struttura"
echo "3. Cerca ancora '$OLD_NAME' rimasti con: grep -rn '$OLD_NAME' $OUT_DIR --include='*.ts' --include='*.tsx' --include='*.html'"
echo "4. npm install && npm run build (dentro $OUT_DIR) per generare la versione statica da caricare su Netlify"
