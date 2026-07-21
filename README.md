# Valdarno Demo Templates

Repo unico con template demo e script per il side-hustle "siti porta a porta" nel Valdarno fiorentino.

## Struttura

- `ristorante/index.html` — demo per ristoranti/trattorie ("Osteria della Torre")
- `eventi/index.html` — demo per location matrimoni/eventi ("Villa delle Ginestre")
- `scripts/lead_finder.py` — cerca su OpenStreetMap attività locali senza sito o con sito scadente
- `scripts/generate_demo_batch.py` — genera automaticamente una demo personalizzata per ogni lead, con stile visivo diverso (mai ripetuto nello stesso comune)
- `scripts/outreach_dashboard.py` — genera una pagina con link WhatsApp precompilati per ogni lead (invio sempre manuale, un click per messaggio)
- `scripts/clone_template.sh` — clona il template S.Maria (agriturismi/B&B) con l'identità del nuovo cliente
- `scripts/style_variants.json` — le 6 varianti di stile (palette/font/hero) usate per differenziare le demo
- `scripts/run_weekly.sh` — orchestratore usato dalla task programmata: clona questo repo + il repo S.Maria, lancia ricerca lead e generazione demo
- `runbook.md` — la routine operativa settimanale passo per passo
- `script_contatto.md` — testi per WhatsApp/email di primo contatto e follow-up
- `prompt_claude_code.md` — prompt da incollare in Claude Code per completare lo stile delle demo S.Maria (React)

## Uso rapido

```
pip install requests --break-system-packages
bash scripts/run_weekly.sh
```

Genera `lead_valdarno.csv` (lista contatti) e `output_demo/` (demo pronte, una cartella per cliente).

Nota: gli script di ricerca dipendono dall'API pubblica gratuita di Overpass (OpenStreetMap) — può
richiedere alcuni minuti per completare tutte le categorie, è normale.

## Come personalizzare a mano una demo (ristorante/eventi)

1. Apri il file `index.html` della variante che vuoi usare
2. Cerca e sostituisci: nome attività, numero WhatsApp (cerca "390000000000"), indirizzo/orari/telefono
3. Sostituisci le immagini placeholder (da Unsplash) con foto vere della struttura
4. Carica il file su Netlify (drag & drop) per generare la demo online da mostrare

## Nota

Per strutture ricettive (agriturismi, B&B) il template base è nel repo separato
[S.Maria](https://github.com/Fuchs665/S.Maria), basato su React/Vite. `run_weekly.sh` lo clona
automaticamente ad ogni esecuzione.
