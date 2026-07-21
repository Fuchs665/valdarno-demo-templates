# Prompt da incollare in Claude Code (o Claude Design) per generare una nuova demo

Copia il blocco qui sotto, riempi i campi tra [PARENTESI QUADRE] con i dati del cliente, scegli UNA variante di stile dal file `style_variants.json` (allegalo insieme a questo prompt), e incollalo in Claude Code dentro la cartella del progetto giusto (S.Maria, ristorante-template o eventi-template a seconda della categoria).

---

## PROMPT

```
Contesto: sto costruendo velocemente siti-demo da mostrare ad attività locali nel Valdarno
fiorentino (agriturismi, ristoranti, location eventi), partendo da un template esistente.
Il tuo compito è clonare il template di base in una nuova cartella e personalizzarlo con i
dati del nuovo cliente, applicando la variante di stile indicata, in modo che il risultato
finale NON sembri una copia visivamente identica delle altre demo che ho già fatto.

DATI DEL CLIENTE:
- Nome attività: [NOME]
- Categoria: [agriturismo / ristorante / location eventi]
- Indirizzo completo: [INDIRIZZO]
- Comune: [COMUNE]
- Telefono: [TELEFONO]
- WhatsApp (se diverso): [WHATSAPP]
- Email (se presente): [EMAIL]
- 3-5 frasi sulla storia/atmosfera del locale: [DESCRIZIONE BREVE]
- Elenco di ciò che offre (stanze/piatti/spazi, con eventuali prezzi indicativi se noti): [LISTA]
- Punti di forza da evidenziare (es. vista, prodotti bio, posizione, storicità): [PUNTI FORZA]
- Cartella con le foto reali fornite dal cliente (se le ho, altrimenti userai placeholder coerenti a tema): [PATH FOTO o "nessuna, usa placeholder"]

VARIANTE DI STILE DA APPLICARE (presa da style_variants.json):
- Numero variante: [1-6]
- Applica esattamente palette colori, coppia di font e hero_style indicati in quella variante.
  Non riusare la palette/font di varianti già impiegate in demo precedenti per lo stesso cliente
  o per clienti nello stesso paese, per evitare che due demo mostrate nella stessa zona sembrino
  fatte con lo stampino.

COSA DEVI FARE, IN ORDINE:
1. Copia l'intero template di base in una nuova cartella con nome slug del cliente
   (es. "fontepetrini-demo"), senza toccare l'originale.
2. Sostituisci OVUNQUE nome attività, indirizzo, telefono, email, link WhatsApp con i dati
   del cliente (cerca tutte le occorrenze nei file .html/.ts/.tsx/.js, non lasciarne indietro).
3. Riscrivi i contenuti testuali (storia, descrizione stanze/menu/spazi, punti di forza) usando
   le informazioni fornite sopra — se un'informazione manca, scrivi un testo plausibile e
   generico ma non inventare numeri, prezzi o dettagli specifici che potrebbero risultare falsi
   se il cliente li legge (es. non inventare "dal 1850" se non te l'ho detto).
4. Applica la variante di stile: cambia variabili CSS/colori, importa e applica la coppia di
   font indicata, e adatta la struttura dell'hero secondo "hero_style". Il layout generale
   (sezioni, componenti, funzionalità come i bottoni WhatsApp) deve restare uguale al template
   di base: sto cambiando la VESTE GRAFICA, non la struttura.
5. Se ho fornito foto reali, usale al posto delle immagini placeholder di Unsplash, mantenendo
   proporzioni/crop coerenti con il design. Se non ho fornito foto, lascia i placeholder ma
   scegline di tematicamente coerenti con la categoria e la variante di stile (es. tono scuro
   per la variante "Notte in Collina").
6. Alla fine, elenca in un breve riepilogo: cosa hai cambiato, quali file hai toccato, e se
   qualche dato del cliente (indirizzo, telefono...) non era presente e quindi hai lasciato un
   placeholder da compilare a mano — segnalamelo chiaramente così non me lo dimentico prima
   di mostrare la demo.

NON fare:
- Non modificare la struttura del sito, i componenti o le funzionalità esistenti (es. il
  bottone WhatsApp, il form di richiesta) a meno che non te lo chieda esplicitamente.
- Non lasciare riferimenti al cliente/nome precedente da cui hai clonato il template: prima di
  finire, cerca nel progetto il vecchio nome e verifica che non ne resti traccia.
- Non pubblicare/deployare nulla automaticamente: preparami solo i file, il deploy lo faccio
  io a mano su Netlify dopo aver controllato il risultato.
```

---

## Note d'uso

Tieni un piccolo registro (anche solo un file di testo) di quale variante di stile hai usato per quale cliente, così quando ne generi una nuova eviti di ripetere la stessa combinazione due volte nello stesso paese — è la cosa che fa la differenza tra "sembra fatto apposta per voi" e "sembra lo stesso sito riverniciato". Se dopo aver usato tutte e 6 le varianti ti servono ancora demo nuove, puoi chiedermi di generarne altre seguendo lo stesso schema (palette + coppia font + hero_style), così amplii la banca senza ripartire da zero.
