# AI Act — Biblioteca unificata: design

Data: 2026-07-29

## Obiettivo

Fondere `ai-act-explorer.html` e `eu_ai_act_guida_vademecum.html` in un unico file HTML
autosufficiente, consultabile come una biblioteca completa sul Regolamento (UE) 2024/1689
(AI Act) e sul Digital Omnibus (Regolamento (UE) 2026/1744), con forte enfasi su UI/UX.

## Stato di partenza

- **ai-act-explorer.html** (106 KB): design editoriale bilingue IT/EN (Fraunces/Inter/IBM
  Plex Mono), sidebar sticky, ricerca, toggle lingua. Copre: livelli di rischio, timeline,
  sanzioni, obblighi per ruolo (provider/deployer/importer/distributor), tool di
  classificazione del rischio, sintesi di tutti i 113 articoli per capitolo, sintesi dei
  13 allegati, casi pratici. Nessun testo verbatim.
- **eu_ai_act_guida_vademecum.html** (22 KB): Tailwind + Chart.js da CDN, 3 tab (Analisi/
  Vademecum/Sanzioni), grafico a barre sanzioni, checklist filtrabile per ruolo. Contenuto
  sostanzialmente ridondante rispetto all'explorer, meno approfondito.

Decisione: **ai-act-explorer.html è la base**. Il vademecum viene ritirato; l'unica idea
recuperata è il grafico a barre delle sanzioni, riprodotto come SVG inline (niente CDN
aggiuntivi, per restare un file singolo autosufficiente).

## Fonti per il testo verbatim

EUR-Lex (eur-lex.europa.eu) blocca il fetch diretto (AWS WAF, `x-amzn-waf-action: challenge`)
sia via curl sia via WebFetch. Soluzione: recuperati via Wayback Machine (web.archive.org)
snapshot HTML strutturati semanticamente (classi `oj-ti-art`, `oj-sti-art`, `eli-subdivision`,
`eli-container`, id `art_N` / `rct_N` / `anx_N`):

- Reg. 2024/1689 IT: snapshot 2026-07-27, confermati 113 articoli, 180 considerando, 13 allegati.
- Reg. 2024/1689 EN: snapshot 2026-07-25, stessa struttura, stessi conteggi.
- Reg. 2026/1744 (Digital Omnibus) EN: snapshot 2026-07-28, 11 articoli. Verificato reale
  (pubblicato in GU UE il 24/7/2026, in vigore dal 27/7/2026).
- Reg. 2026/1744 IT: **non disponibile** — non ancora archiviato su Wayback Machine, EUR-Lex
  live bloccato. Decisione utente: includere l'Omnibus solo in EN nella libreria, con nota
  esplicita che la versione IT ufficiale non era disponibile al momento della creazione.

## Architettura dell'informazione

Due modalità, selezionabili da un tab in header (accanto al toggle IT/EN):

1. **Guida** — il contenuto attuale dell'explorer (tiers, timeline, sanzioni con nuovo
   grafico SVG, ruoli, classificatore, sintesi capitoli/articoli, sintesi allegati, scenari).
2. **Biblioteca** (nuova) — testo integrale:
   - Considerando (180), collassati per default, ricercabili/espandibili.
   - Capi e Articoli (113), navigazione per capitolo con vista "un articolo alla volta" +
     Precedente/Successivo, indice sempre cliccabile a sinistra.
   - Allegati (13) verbatim, inclusi contenuti tabellari dove presenti nel testo originale.
   - Digital Omnibus 2026/1744 come documento separato (EN, con nota sulla mancanza dell'IT).

Motivazione: evitare di appesantire la Guida con centinaia di migliaia di parole di testo
legale; dare alla richiesta esplicita dell'utente ("una sezione per leggere tutti gli
articoli alla lettera") un'identità propria da vera biblioteca.

## UI/UX della Biblioteca

- Sidebar sinistra sticky con indice a gruppi: Considerando / Capi e Articoli (espandibili
  per capitolo) / Allegati / Digital Omnibus.
- Pannello di lettura a destra con tipografia serif dedicata alla lettura lunga (font Google
  aggiuntivo, es. Source Serif 4), distinta dal sans-serif dell'interfaccia.
- Vista articolo singolo con navigazione Precedente/Successivo.
- Considerando e allegati in pannelli `<details>` collassati per default (prestazioni).
- Stesso toggle IT/EN globale del resto del sito (testo verbatim bilingue reale, non
  traduzione automatica).
- Ricerca in header estesa al testo integrale: un risultato in un articolo porta
  direttamente alla Biblioteca, sull'articolo giusto, con termine evidenziato.
- Collegamento bidirezionale: ogni card-articolo nella Guida ha un link "→ Testo integrale"
  che apre la Biblioteca sull'articolo corrispondente.

## Implementazione tecnica

- Script Python locale estrae da ciascuno snapshot HTML: articoli (numero, titolo, testo),
  considerando (numero, testo), allegati (numero, titolo, testo/tabelle) → JSON puliti,
  uno per lingua/documento.
- I JSON vengono incorporati come dati JS nel file HTML finale, stesso pattern già usato
  dall'explorer per `CHAPTERS`, `TIMELINE`, ecc. Risultato: un unico file HTML autosufficiente,
  apribile offline, senza nuove dipendenze esterne oltre a Google Fonts (già in uso).
- Dimensione finale attesa: ~1,5–2,5 MB (da 106 KB attuali). Accettabile: file locale, non
  servito ad alto traffico.

## Fuori scope

- Consolidamento giuridico del testo (fondere le modifiche dell'Omnibus dentro il testo
  degli articoli del regolamento base): le modifiche dell'Omnibus sono istruzioni di modifica
  (es. "l'articolo 5, paragrafo 1, è così modificato..."), non testo sostitutivo pronto.
  Restano un documento verbatim separato, collegato ma non fuso.
- Nuove dipendenze CDN (Tailwind, Chart.js): il grafico sanzioni del vademecum viene
  riprodotto come SVG inline.
