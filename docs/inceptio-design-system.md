# Inceptio Solutions — Design System Reference

> **Scopo di questo documento**: dare a un agente che NON conosce questo codebase tutto ciò che serve per costruire o riadattare una pagina HTML standalone (landing page, pagina di atterraggio per una campagna, pagina legale, ecc.) in modo che sia visivamente indistinguibile dal resto di Inceptio Solutions. Ogni valore qui sotto è preso letteralmente dal codice sorgente (`tailwind.config.js`, `index.html`, componenti in `/components`) — non sono interpretazioni, sono i token reali in uso.
>
> Se stai costruendo una pagina HTML pura (no build step Tailwind), scorri fino alla sezione **"Starter kit copy-paste"** in fondo: contiene un `<head>` pronto e le classi tradotte in CSS puro dove serve.

---

## 1. Stack e assunzioni

- **Font**: Google Fonts **Inter**, pesi 300/400/500/600/700.
- **CSS**: Tailwind CSS (`darkMode: 'class'`), nessun plugin custom installato (vedi §9 sulle animazioni per un'eccezione importante).
- **Icone**: [lucide-react](https://lucide.dev) esclusivamente (o l'equivalente SVG set "Lucide" se la pagina non è React).
- **Lingua**: sito bilingue IT/EN, IT è la lingua di default (`<html lang="it">`). Se la pagina target non usa lo stesso sistema di i18n, non è un problema — ma evita di "ingessare" il testo in contenitori a larghezza fissa, per coerenza con lo stile del resto del sito.

---

## 2. Colori (token primari)

Questi sono i colori brand definiti in `tailwind.config.js`:

| Token | Hex | Uso |
|---|---|---|
| `brand-orange` | `#C35C3B` | Colore primario/CTA. Bottoni, link, accenti, focus ring |
| `brand-orange-light` | `#D97D5E` | Gradient highlight, badge, hover chiaro |
| `brand-orange-dark` | `#A64B2E` | Hover su elementi arancioni, scrollbar thumb hover |
| `brand-dark` | `#333C44` | Sfondo scuro / superfici in dark mode / bottoni primari su sfondo chiaro |
| `brand-dark-light` | `#454F59` | Superficie scura secondaria (spesso a opacità `/10`–`/50`) |
| `brand-dark-soft` | `#F4F5F6` | Sfondo neutro chiaro (input, badge footer) |

**Sfondi pagina** (non tokenizzati in Tailwind, usati come hex letterali):
- Light mode: pagina `#eaecf0`, card/sezioni `#ffffff` o `#fafbfc`
- Dark mode: pagina `#0f1215`, sezioni `#333C44` / `#181E24` / `#101417` (mai nero puro — è un "navy-charcoal premium")

**Neutrali**: scala Tailwind default `slate-*` (50→900) per testo secondario, bordi, stati disabilitati.

**Colori semantici** (Tailwind default, nessun token custom):
- Successo: `green-500`/`green-600`/`green-100`
- Errore/destructive: `red-500`/`red-600`/`red-50`/`red-200`
- Stato "live/online": `orange-500` (⚠️ nota: è l'arancione Tailwind default, NON `brand-orange` — un'inconsistenza esistente nel sito originale, da non correggere silenziosamente ma da poter uniformare se richiesto)

**Gradient ricorrenti** (copia questi esattamente, sono la firma visiva del sito):
```
from-brand-orange via-brand-orange-light to-transparent   /* hairline top accent su card */
from-brand-orange to-brand-orange-dark                     /* badge icona, step numerati */
from-brand-dark to-brand-dark-light                        /* header banner modali */
from-brand-orange to-brand-dark                             /* badge trust/shield */
from-brand-dark via-transparent to-brand-dark/20            /* scrim overlay su video */
```

Glow radiale decorativo (via `style` inline, non classe Tailwind):
```css
background: radial-gradient(620px 380px at 50% 0%, rgba(195,92,59,0.10), transparent 65%);
```

---

## 3. Tipografia

- Font family unica: **Inter** per tutto (titoli e body) — la gerarchia si costruisce solo con size/weight/tracking, non cambiando font.
- Import: `<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">`

Pattern d'uso reali (classi Tailwind osservate nei componenti):

| Elemento | Classi |
|---|---|
| H1 Hero | `text-4xl md:text-6xl font-extrabold leading-tight tracking-tight` |
| H2 Sezione | `text-3xl md:text-4xl font-bold leading-tight` |
| H2 "founder" grande | `text-3xl md:text-5xl font-extrabold tracking-tight` |
| H3/H4 card | `text-xl font-bold` |
| Body intro (grande) | `text-lg text-slate-600 dark:text-slate-300 leading-relaxed` |
| Body secondario | `text-sm text-slate-500` |
| Eyebrow/kicker | `text-[11px] font-bold text-brand-orange uppercase tracking-[0.25em]` |
| Micro-label (badge, timestamp) | `text-[9px]`/`text-[10px] font-bold uppercase tracking-widest` |
| Bottoni CTA | `font-bold` (`font-black` riservato a stati ad alta enfasi: success screen, headline Alina) |

Peso dominante: `font-bold` è di gran lunga il più usato. `font-black`/`font-extrabold` solo per momenti "hero" o di forte enfasi.

---

## 4. Spacing e layout

- **Container dominante**: `max-w-6xl` per la maggior parte delle sezioni. `max-w-5xl` per hero, `max-w-3xl`/`max-w-2xl` per colonne di testo strette (FAQ, testi lunghi).
- **Pattern "sezione come card fluttuante"**: il sito NON è a sezioni edge-to-edge, ma una pila di grandi card arrotondate che galleggiano sullo sfondo pagina:
  ```
  mx-4 md:mx-8 lg:mx-auto max-w-6xl my-10 rounded-[2.5rem] bg-white dark:bg-brand-dark border shadow-xl
  px-6 py-16 md:py-20   /* padding interno */
  ```
  Questo è IL pattern strutturale più riconoscibile del sito — replicalo per ogni sezione principale.
- **Grid comuni**: `grid md:grid-cols-2`, `grid md:grid-cols-3`, `grid lg:grid-cols-2 gap-12 items-center` (split testo+immagine).
- **Breakpoint**: mobile-first. `md:` è il più usato, poi `lg:`, poi `sm:` (soprattutto per compattare la chat su mobile). `xl:`/`2xl:` praticamente mai usati — non introdurli senza motivo.
- **Elementi fissi**: navbar `fixed top-4 z-40`, toggle tema `fixed bottom-6 right-6 z-50`, modali `fixed inset-0 z-50`.

---

## 5. Border radius (scala "soft premium")

Dal più grande al più piccolo, uso reale nel codice:

| Radius | Uso |
|---|---|
| `rounded-[2.5rem]` | Contenitore di sezione principale (la "pill card" della homepage) |
| `rounded-3xl` | Card grandi, modali |
| `rounded-2xl` | Card medie, bolle chat, accordion FAQ, bottoni primari |
| `rounded-xl` | Bottoni, input, badge icona |
| `rounded-lg` / `rounded-md` | Tag/pill piccoli |
| `rounded-full` | Avatar, dot di stato, badge pillola, contenitori icona circolari |

Bolle chat con "coda" asimmetrica: `rounded-2xl rounded-br-none` (utente) / `rounded-2xl rounded-bl-none` (bot).

---

## 6. Ombre (shadow)

- `shadow-xl`/`shadow-2xl` per card elevate, modali, pannelli di sezione — **quasi ogni sezione della homepage usa `shadow-xl`**.
- Ombre "colorate" sotto elementi arancioni: `shadow-lg shadow-brand-orange/20` (o `/25`, `/30`) — un bagliore arancione soffuso sotto bottoni CTA e badge icona.
- `shadow-sm` per elevazione sottile (card, bolle chat).
- `shadow-inner` sul contenitore input della chat.
- Ombre custom arbitrarie osservate: `shadow-[0_16px_48px_-12px_rgba(15,23,42,0.28)]` (banner cookie), `shadow-[0_-5px_20px_rgba(0,0,0,0.02)]` (barra input chat).

---

## 7. Componenti chiave

### Bottoni

**Primario scuro** (pattern CTA più diffuso — hover che passa a arancione):
```html
<button class="bg-brand-dark dark:bg-white text-white dark:text-brand-dark
  hover:bg-brand-orange dark:hover:bg-brand-orange hover:text-white
  rounded-2xl font-bold px-8 py-4
  transition-all hover:-translate-y-1 hover:scale-[1.02] active:scale-[0.98]
  shadow-lg">
  Testo bottone
</button>
```

**Primario arancione** (usato per invio chat, CTA finali):
```html
<button class="bg-brand-orange text-white hover:bg-brand-orange-dark
  rounded-xl font-bold px-5 py-3.5 transition-all
  hover:scale-[1.02] active:scale-[0.98]">
  Invia
</button>
```

**Secondario/outline**:
```html
<button class="bg-white text-brand-dark border-2 border-slate-200
  hover:border-brand-orange rounded-2xl font-bold px-8 py-4 transition-all">
  Testo
</button>
```

**Link testuale terziario**:
```html
<a class="text-brand-orange font-bold hover:text-brand-orange-dark">Scopri di più →</a>
```

**Micro-interazione universale** (da applicare a QUALSIASI elemento cliccabile): `transition-all hover:scale-[1.02] active:scale-[0.98]` — è la "sensazione elastica" firma del sito. Non ometterla.

### Card/pannelli
- Padding interno: `p-6` a `p-8`.
- Bordo hairline top a gradiente arancione su card in evidenza: `<div class="h-1 bg-gradient-to-r from-brand-orange via-brand-orange-light to-transparent">`.
- Card scure (dark mode / sezioni "servizi"): `bg-brand-dark-light/50 backdrop-blur-sm border border-slate-700`.

### Form/input
```html
<input class="w-full px-4 py-3 rounded-xl border border-slate-200
  focus:outline-none focus:ring-2 focus:ring-brand-orange focus:border-transparent
  transition-all" />
```
Pattern "pillola" per input chat: contenitore `flex items-center bg-brand-dark-soft rounded-2xl p-1 border border-slate-200 focus-within:border-brand-orange/40 focus-within:ring-2 focus-within:ring-brand-orange/5 shadow-inner` con input trasparente + bottone invio circolare arancione.

### Navbar (glassmorphism flottante)
```html
<nav class="fixed top-4 left-4 right-4 lg:max-w-6xl lg:mx-auto z-40
  bg-white/40 dark:bg-brand-dark/40 backdrop-blur-md
  border border-slate-200/30 dark:border-white/5
  rounded-2xl shadow-lg">
```

### Modali
Overlay: `fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm`
Pannello: `bg-white rounded-3xl shadow-2xl max-w-md overflow-hidden`
Header banner con cerchio decorativo sfocato: `<div class="w-32 h-32 bg-brand-orange/20 rounded-full blur-3xl">`
Bottone chiusura: `w-8 h-8 rounded-full bg-white/10 hover:bg-white/20` in alto a destra.

### Icone
Solo **lucide-react** (o SVG Lucide equivalenti). Non mischiare con altri set di icone (Font Awesome, Heroicons, ecc.) — l'omogeneità del set è parte dello stile.

---

## 8. Dark mode

- Toggle utente reale (non solo `prefers-color-scheme`), classe `dark` su `<html>`, persistito in `localStorage`.
- Default: **light mode** (non rileva l'OS al primo avvio).
- Pattern testo ricorrente su quasi ogni elemento: `text-brand-dark dark:text-white` oppure `text-slate-600 dark:text-slate-300`.
- Sfondo light `#eaecf0` / dark `#0f1215`. Mai bianco/nero puro.

Se la pagina target non ha bisogno di dark mode, va bene ometterlo — ma se lo implementi, usa questi identici valori, non improvvisare una nuova scala di grigi.

---

## 9. Animazioni e micro-interazioni

⚠️ **Attenzione — gotcha reale nel codice sorgente**: alcune classi tipo `animate-in`, `fade-in`, `zoom-in-95`, `slide-in-from-bottom-4` compaiono nel JSX del sito ma il plugin che le rende funzionanti (`tailwindcss-animate`) **non è installato**. Sono di fatto no-op nel sito live. Non copiarle pensando che facciano qualcosa, a meno di installare tu stesso il plugin.

**Il vero motore di animazione del sito** è CSS + IntersectionObserver, definito inline in `index.html`:
```css
@keyframes reveal-fade-up {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}
.reveal { opacity: 0; transform: translateY(24px); }
.reveal.revealed { animation: reveal-fade-up 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
.reveal-delay-1 { animation-delay: 0.1s; }
.reveal-delay-2 { animation-delay: 0.2s; }
.reveal-delay-3 { animation-delay: 0.3s; }
```
Con un `IntersectionObserver` (threshold `0.15`) che aggiunge `.revealed` una sola volta per elemento quando entra in viewport. Questo è il pattern da replicare per un "fade-up on scroll" coerente con il resto del sito.

Altri elementi di movimento:
- Micro-interazioni hover/click: `transition-all`, `hover:scale-[1.02]`/`hover:scale-105`, `active:scale-95`/`active:scale-[0.98]`, `hover:-translate-y-1`, `group-hover:translate-x-1` (icone freccia).
- Utility Tailwind native (funzionano senza plugin): `animate-pulse`, `animate-bounce`, `animate-ping`, `animate-spin` — usate per dot di stato "live" e indicatori di caricamento.
- `framer-motion` è nel `package.json` ma **non è usato in nessun componente** — non è il motore reale delle animazioni, ignoralo come riferimento.

---

## 10. Cose da NON fare (inconsistenze esistenti, non da propagare)

- Non usare `orange-500` di Tailwind pensando che sia lo stesso brand color: il brand è `#C35C3B` (`brand-orange`). Se possibile, uniforma tutto a `brand-orange` anche dove il sito originale usa l'arancione default per errore.
- Non copiare le classi `animate-in`/`fade-in`/ecc. senza installare `tailwindcss-animate` — altrimenti sono inerti.
- Non introdurre `xl:`/`2xl:` breakpoint a meno che il layout lo richieda davvero — non fanno parte del vocabolario visivo attuale.
- Non usare nero/bianco puro per gli sfondi dark/light — usa sempre i toni "navy-charcoal" (`#0f1215`, `#333C44`) e "grigio caldo" (`#eaecf0`, `#F4F5F6`).

---

## 11. Starter kit copy-paste (pagina HTML standalone, senza build Tailwind)

Se la pagina target non ha una pipeline Tailwind, includi il CDN e questo `<head>`:

```html
<head>
  <meta charset="UTF-8">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: {
              orange: '#C35C3B',
              'orange-light': '#D97D5E',
              'orange-dark': '#A64B2E',
              dark: '#333C44',
              'dark-light': '#454F59',
              'dark-soft': '#F4F5F6',
            },
          },
          fontFamily: { sans: ['Inter', 'sans-serif'] },
        },
      },
    }
  </script>
  <style>
    body { font-family: 'Inter', sans-serif; margin: 0; padding: 0; }
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { background: #C35C3B; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #A64B2E; }

    @keyframes reveal-fade-up {
      from { opacity: 0; transform: translateY(24px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .reveal { opacity: 0; transform: translateY(24px); }
    .reveal.revealed { animation: reveal-fade-up 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
    .reveal-delay-1 { animation-delay: 0.1s; }
    .reveal-delay-2 { animation-delay: 0.2s; }
    .reveal-delay-3 { animation-delay: 0.3s; }
  </style>
</head>
<body class="bg-[#eaecf0] dark:bg-[#0f1215] text-brand-dark dark:text-white overflow-x-hidden">
```

Script minimo per il reveal-on-scroll:
```html
<script>
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
</script>
```

Struttura sezione tipo (il pattern "card fluttuante" da riusare ovunque):
```html
<section class="mx-4 md:mx-8 lg:mx-auto max-w-6xl my-10 rounded-[2.5rem]
  bg-white dark:bg-brand-dark border border-slate-200 dark:border-slate-700
  shadow-xl px-6 py-16 md:py-20 reveal">
  <p class="text-[11px] font-bold text-brand-orange uppercase tracking-[0.25em] mb-3">Eyebrow</p>
  <h2 class="text-3xl md:text-4xl font-bold leading-tight tracking-tight mb-4">Titolo sezione</h2>
  <p class="text-lg text-slate-600 dark:text-slate-300 leading-relaxed">Testo introduttivo.</p>
</section>
```

---

## 12. Checklist rapida per un agente che deve "uniformare" una pagina esistente

1. Sostituisci font a **Inter** (300–700), rimuovi altri font.
2. Sostituisci ogni colore primario/CTA con `#C35C3B` (+ hover `#A64B2E`).
3. Sfondo pagina: `#eaecf0` (light) / `#0f1215` (dark) — mai bianco/nero puro.
4. Avvolgi le sezioni principali nel pattern "card fluttuante": `rounded-[2.5rem]`, `shadow-xl`, margini `mx-4 md:mx-8 lg:mx-auto max-w-6xl my-10`.
5. Bottoni: applica sempre `transition-all hover:scale-[1.02] active:scale-[0.98]` + radius `rounded-xl`/`rounded-2xl`.
6. Icone: converti tutto a Lucide.
7. Se serve dark mode: aggiungi toggle con classe `dark` su `<html>`, persistenza `localStorage`, default light.
8. Aggiungi `.reveal` + IntersectionObserver per il fade-up on scroll, se la pagina ha più sezioni scrollabili.
9. Non introdurre breakpoint `xl`/`2xl` se non strettamente necessario.
10. Verifica che i colori "semantici" (successo/errore) restino sui default Tailwind (`green-*`/`red-*`) — non serve tokenizzarli.
