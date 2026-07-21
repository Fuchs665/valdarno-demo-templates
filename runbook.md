# Runbook — Side Hustle Siti Valdarno

Segui questi step nell'ordine, senza deviare. La prima volta (setup) richiede più tempo, dopo diventa una routine di pochi minuti a sera. Tutti i comandi vanno lanciati dalla root della cartella `valdarno-demo-templates` (dove ci sono `ristorante/`, `eventi/`, `scripts/`).

---

## SETUP UNA TANTUM (da fare una sola volta, con calma, prima di iniziare)

1. Installa Python se non ce l'hai già: verifica con `python3 --version` nel terminale. Se manca, scaricalo da python.org.
2. Installa la libreria necessaria allo script di ricerca lead:
   ```
   pip install requests --break-system-packages
   ```
3. Assicurati di avere il repo `valdarno-demo-templates` clonato in locale (`git clone https://github.com/Fuchs665/valdarno-demo-templates.git`) e il repo `S.Maria` altrettanto, nella stessa cartella padre.
4. Installa Netlify CLI e fai il login una tantum (serve per pubblicare le demo con un comando invece di trascinarle a mano):
   ```
   npm install -g netlify-cli
   netlify login
   ```
5. Crea un account Netlify gratuito se non ce l'hai già.

---

## ROUTINE SETTIMANALE (sere feriali, 10-15 minuti totali, spezzabile)

### Lunedì sera — Automatico
La task programmata gira da sola alle 20:00: lancia `scripts/lead_finder.py` e `scripts/generate_demo_batch.py` (fino a 15 demo, priorità a ristoranti/eventi), e ti manda un riepilogo in chat. Non devi fare nulla, solo leggerlo.

### Martedì sera — Completa gli agriturismi con Claude Code
1. Lancia: `bash scripts/list_pending_style.sh output_demo/`
2. Ti elenca tutti gli agriturismi/B&B ancora da rifinire, con cartella e prompt già pronti
3. Apri Claude Code su ciascuna cartella `*-sito` elencata, incolla il relativo `prompt_claude_code.txt`, verifica il risultato

### Mercoledì sera — Pubblica e prepara i messaggi
1. Lancia: `bash scripts/deploy_batch.sh output_demo/`
   - Ti mostra la lista di cosa sta per pubblicare, conferma una volta con "s"
   - Pubblica tutto su Netlify e salva i link reali in `demo_links.json` (non ripubblica mai due volte lo stesso cliente)
2. Lancia: `python3 scripts/outreach_dashboard.py lead_valdarno.csv --demo-links-file demo_links.json --only-without-site`
3. Apri `outreach.html`: ogni contatto ha già il link demo reale inserito nel messaggio (chi non ha ancora una demo pubblicata compare come "Demo mancante", niente placeholder rotti)

### Giovedì sera (o pausa pranzo) — Invia i primi messaggi
1. Apri `outreach.html` nel browser del telefono o computer
2. Scorri i contatti, clicca "Apri su WhatsApp": un click apre WhatsApp E segna il contatto come fatto (vedi il contatore in alto)
3. Dai un'occhiata al messaggio precompilato, premi invia tu dentro WhatsApp
4. Fermati a 10-15 messaggi per sera: non superare questo numero per non rischiare segnalazioni spam

### Venerdì sera — Prepara il weekend
1. Guarda chi ha risposto durante la settimana (WhatsApp/email)
2. Per chi ha risposto positivamente, fissa un appuntamento per sabato o domenica
3. Se serve una demo su misura (non generica) per un appuntamento fissato, usa `scripts/clone_template.sh` (agriturismi) o rilancia `generate_demo_batch.py` su un CSV con solo quel cliente

---

## ROUTINE WEEKEND

### Sabato/Domenica — Appuntamenti fissati
1. Vai solo agli incontri già confermati durante la settimana (non girare a vuoto, salvo la prima uscita esplorativa)
2. Porta il telefono/tablet con la demo pronta e aperta offline (salva la pagina o fai uno screenshot di backup nel caso non ci sia campo)
3. Usa lo script "approccio di persona" da `script_contatto.md` come traccia, non da recitare a memoria
4. Alla fine di ogni incontro, segna subito su una nota: nome, esito, prossimo passo, data di eventuale richiamo

### Domenica sera — Chiusura settimana
1. Aggiorna la lista contatti: chi ha detto sì, chi ha detto no, chi è ancora in sospeso
2. Programma i follow-up (messaggio 2 di `script_contatto.md`) per chi non ha risposto da 4-5 giorni
3. Se hai chiuso una vendita: ricordati della soglia dei 5000€/anno di cui parlavamo, tieni traccia di quanto hai incassato

---

## REGOLE FISSE (da non violare per non rovinare tutto)

- Mai più di 10-15 messaggi WhatsApp a sconosciuti nello stesso giorno
- Mai un terzo messaggio di follow-up se non rispondono nemmeno al secondo
- Sempre controllo visivo del messaggio prima di premere invia (mai fidarsi ciecamente dell'automazione)
- Nessuna pubblicazione online e nessun invio messaggi avviene mai senza una tua conferma esplicita — `deploy_batch.sh` chiede conferma prima di partire, `outreach.html` non invia nulla da solo
- Weekend solo per appuntamenti confermati, non per giri a vuoto (tranne la prima uscita esplorativa)
- Tieni traccia di ogni incasso per la questione dei 5000€/anno, e senti un commercialista prima di incassare il primo pagamento

---

## TASK PROGRAMMATA (automatica il lunedì sera)

Un'unica task gira ogni lunedì sera alle 20:00: clona il repo aggiornato da GitHub, lancia
`lead_finder.py` e `generate_demo_batch.py` (limite 15 demo a esecuzione, priorità a
ristoranti/eventi), e ti manda un riepilogo in chat con lead trovati, demo generate e
chi richiede il passaggio manuale con Claude Code. Non pubblica nulla e non invia nessun
messaggio: quelle restano sempre azioni tue, dai martedì in poi seguendo questo runbook.
