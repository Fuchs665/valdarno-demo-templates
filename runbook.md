# Runbook — Side Hustle Siti Valdarno

Segui questi step nell'ordine, senza deviare. La prima volta (setup) richiede più tempo, dopo diventa una routine di pochi minuti a sera.

---

## SETUP UNA TANTUM (da fare una sola volta, con calma, prima di iniziare)

1. Installa Python se non ce l'hai già: verifica con `python3 --version` nel terminale. Se manca, scaricalo da python.org.
2. Installa la libreria necessaria allo script di ricerca lead:
   ```
   pip install requests --break-system-packages
   ```
3. Scompatta e salva in una cartella fissa sul tuo computer (es. `~/valdarno-hustle/`) questi file che ti ho già dato:
   - `lead_finder.py`
   - `generate_demo_batch.py`
   - `outreach_dashboard.py`
   - `clone_template.sh` (dentro la cartella S.Maria)
   - i tre template: `S.Maria/`, `ristorante-template/index.html`, `eventi-template/index.html`
   - `style_variants.json` (le 6 varianti di stile)
   - `prompt_claude_code.md` (per completare lo stile delle demo S.Maria)
   - `script_contatto.md` (i testi dei messaggi)
4. Metti online le tre demo "master" su Netlify (drag & drop, come hai già fatto per Podere Santa Maria), così hai già pronti i tre link da riusare come base:
   - Link demo agriturismo/B&B: ___________________
   - Link demo ristorante: ___________________
   - Link demo eventi: ___________________
5. Crea un account Netlify gratuito se non ce l'hai già (serve per pubblicare velocemente ogni nuova demo).

---

## ROUTINE SETTIMANALE (sere feriali, 15-20 minuti totali, spezzabile)

### Lunedì sera — Aggiorna la lista contatti
1. Apri il terminale nella cartella del progetto
2. Lancia: `python3 lead_finder.py` (modifica prima centro/raggio/categorie in cima al file se vuoi cambiare zona)
3. Aspetta che finisca da solo (puoi fare altro nel frattempo), ti genera `lead_valdarno.csv`
4. Dai un'occhiata veloce al CSV, elimina a mano le righe palesemente sbagliate (nomi vuoti, doppioni)

Se hai attivato la task programmata (vedi sezione in fondo), questo step lo trovi già fatto quando apri la chat il lunedì sera — puoi saltare direttamente al punto successivo.

### Martedì sera — Genera le demo personalizzate
1. Lancia: `python3 generate_demo_batch.py lead_valdarno.csv --ristorante-template ristorante-template/index.html --eventi-template eventi-template/index.html --smaria-dir S.Maria --style-variants style_variants.json --out output_demo --only-without-site`
2. Per ristoranti ed eventi trovi il file `index.html` già pronto e stilisticamente diverso da cliente a cliente dentro `output_demo/nome-cliente/`
3. Per agriturismi/B&B trovi `output_demo/nome-cliente/prompt_claude_code.txt`: aprilo, copia il contenuto, incollalo in Claude Code dentro la cartella clonata per completare lo stile
4. Pubblica su Netlify (drag & drop) le demo dei clienti che contatterai questa settimana — non serve pubblicarle tutte, solo quelle che userai nei prossimi messaggi

### Mercoledì sera — Prepara i messaggi
1. Lancia: `python3 outreach_dashboard.py lead_valdarno.csv --demo-base-url "LINK-DEMO-GIUSTA" --only-without-site`
2. Ripeti se vuoi usare demo diverse per categorie diverse (agriturismi → link S.Maria, ristoranti → link Osteria della Torre, ecc. — filtra il CSV per categoria prima, o modifica il link a mano dopo)
3. Apri il file `outreach.html` generato, controlla che i messaggi abbiano senso

### Giovedì sera (o pausa pranzo) — Invia i primi messaggi
1. Apri `outreach.html` nel browser del telefono o computer
2. Scorri i contatti, clicca "Apri su WhatsApp" uno alla volta
3. Dai un'occhiata al messaggio precompilato (giusto per controllare che il nome sia corretto), premi invia
4. Fermati a 10-15 messaggi per sera: non superare questo numero per non rischiare segnalazioni spam su WhatsApp
5. Clicca "Segna come contattato" su chi hai già scritto, così non lo confondi

### Venerdì sera — Prepara il weekend
1. Guarda chi ha risposto durante la settimana (WhatsApp/email)
2. Per chi ha risposto positivamente, fissa un appuntamento per sabato o domenica
3. Se serve una demo su misura (non generica) per un appuntamento fissato, lancia `clone_template.sh` con i dati del cliente e pubblicala su Netlify prima dell'incontro

---

## ROUTINE WEEKEND

### Sabato/Domenica — Appuntamenti fissati
1. Vai solo agli incontri già confermati durante la settimana (non girare a vuoto senza appuntamento, salvo la prima uscita esplorativa)
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
- Weekend solo per appuntamenti confermati, non per giri a vuoto (tranne la prima uscita esplorativa)
- Tieni traccia di ogni incasso per la questione dei 5000€/anno, e senti un commercialista prima di incassare il primo pagamento

---

## TASK PROGRAMMATA (automatica il lunedì sera)

Ho impostato una task programmata che ogni lunedì sera lancia da sola la ricerca dei lead
aggiornata (`lead_finder.py`) e la generazione delle demo (`generate_demo_batch.py`), e ti
lascia un riepilogo pronto da leggere. Non invia nessun messaggio: l'invio resta sempre una
tua azione manuale, per le ragioni di policy/reputazione già viste (rischio ban WhatsApp,
conversioni peggiori con l'automazione totale).

Quando la task gira, ricevi in chat il riepilogo di quanti nuovi lead ha trovato e quali
demo ha generato: a quel punto ti basta aprire la conversazione, controllare l'output,
pubblicare su Netlify le demo che ti servono e passare dritto alla routine di mercoledì
sera per preparare i messaggi.
