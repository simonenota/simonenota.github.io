# simonenota.github.io

Sito personale di Simone Nota, costruito con [Hugo](https://gohugo.io) e pubblicato con GitHub Pages su https://simonenota.github.io.

Ogni modifica salvata sul ramo `main` ripubblica il sito da sola in circa un minuto (scheda **Actions**).

## Dove stanno i contenuti

| Cosa | File |
|---|---|
| Testi della pagina principale, inglese | `content/_index.en.md` |
| Testi della pagina principale, italiano | `content/_index.it.md` |
| Pubblicazioni (con riassunto EN/IT) | `data/publications.yaml` |
| Galleria AI Fun | `data/aifun.yaml` e `content/ai-fun.*.md` |
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
