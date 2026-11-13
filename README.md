# simonenota.github.io

Sito personale di Simone Nota, costruito con [Hugo](https://gohugo.io) e pubblicato con GitHub Pages su https://simonenota.github.io.

Ogni modifica salvata sul ramo `main` ripubblica il sito da sola in circa un minuto (scheda **Actions**).

## Dove stanno i contenuti

| Cosa | File |
|---|---|
| Testi della pagina principale, inglese | `content/_index.en.md` |
| Testi della pagina principale, italiano | `content/_index.it.md` |
| Pubblicazioni (con riassunto EN/IT) | `data/publications.yaml` |
| Galleria AI & Philosophy | `data/aifun.yaml` e `content/ai-philosophy.*.md` |
| PDF di articoli, tesi e CV | `static/papers/` |
| Foto e immagini | `static/images/` |
| Scritte dei pulsanti e del menu | `i18n/en.yaml`, `i18n/it.yaml` |
| Aspetto (colori, caratteri) | `assets/css/main.css` |

## Modificare dal browser

Il file `.pages.yml` configura [Pages CMS](https://app.pagescms.org), un pannello web gratuito: accedi con GitHub, scegli questo repository e modifichi i testi tramite moduli, senza toccare il codice.

Nei campi di testo si può usare il Markdown: `**grassetto**`, `*corsivo*`, `[testo](indirizzo)`.

## Anteprima in locale (facoltativa)

```
hugo server
```

## Traduzione italiana automatica

Quando modifichi un testo in inglese (pagina principale, pubblicazioni, galleria), il workflow `.github/workflows/translate.yml` lo traduce in italiano con DeepL e apre una pull request "Traduzione italiana da rivedere". Rileggila, correggila se serve e premi **Merge pull request**: solo allora va online.

- Vengono ritradotti solo i testi inglesi cambiati; le correzioni fatte a mano all'italiano restano finché non cambi l'originale inglese.
- Serve il secret `DEEPL_API_KEY` (Settings → Secrets and variables → Actions). Senza, il workflow non fa nulla.
- `.translation-base` ricorda a quale versione inglese corrisponde l'italiano: non modificarlo a mano.
