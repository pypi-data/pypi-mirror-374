# autoi18n

Runtime HTML i18n with OpenAI: translate the page on first request, cache results to JSON, reuse on subsequent requests, and auto-sync when the source changes.

**PyPI name:** `autoi18n` | **Import:** `autoi18n`

---

## Features

- 🔁 On-the-fly translation of raw HTML strings  
- 🗂️ JSON cache per target language (on disk)  
- 🔄 Auto-sync: stale entries removed when source changes  
- 🧩 Chunking for model context limits (long pages split safely)  
- 🛡️ Preserves `<script>`/`<style>` as-is  
- 🎛️ Concise UI translation (e.g., buttons)  
- 🌐 Helpers: detect browser lang, pick alternate lang

---

## Installation

```bash
    pip install autoi18n
```
## Quick start
``` 
from autoi18n import Translator

html_in = "<h1>Добро пожаловать</h1><p>Это тест.</p>"
tr = Translator(
    source_lang="ru",
    cache_dir="./translations",   # JSON cache folder
    # api_key="sk-..."            # or use OPENAI_API_KEY env var
)

html_out = tr.translate_html(html_in, target_lang="en", page_name="page")
print(html_out)
First call translates via OpenAI and writes ./translations/page.en.json.
Next calls reuse the cache and only translate new/changed strings.
```
## Environment
``` 
OPENAI_API_KEY — used if api_key not passed to Translator.
```
## API

``` 
Translator(source_lang="ru", cache_dir="./translations", api_key=None)
translate_html(html: str, target_lang: str, page_name: str = "page") -> str
```

## Translates visible text nodes, preserves script/style, chunks long text, updates cache JSON.

```
translate_text(text: str, target_lang: str, page_name: str = "page") -> str
```

## Low-level single-string translation with caching.

```

detect_browser_lang(accept_language_header: str) -> str
```

## Parses Accept-Language → short code like ru, en, fr.

```
get_alternative_lang(current: str, browser_lang: str) -> str
```

## Returns alternate code for a language toggle.
Cache layout

translations/
└─ page.en.json   # UTF-8 JSON: { "source": "translated", ... }
Example:

``` json (example)
{
  "Добро пожаловать": "Welcome",
  "Выберите язык:": "Choose a language:"
}
```
## Minimal FastAPI wiring (example) python
```
from fastapi import FastAPI, Request
from autoi18n import Translator
from pathlib import Path

app = FastAPI()
tr = Translator(source_lang="ru", cache_dir="./translations")
HTML_PATH = Path("index.html")

@app.get("/")
def home():
    return HTML_PATH.read_text(encoding="utf-8")

@app.get("/detect_lang")
def detect_lang(request: Request):
    return {"lang": tr.detect_browser_lang(request.headers.get("accept-language", ""))}

@app.get("/alt_lang")
def alt_lang(request: Request, current: str = "ru"):
    browser = tr.detect_browser_lang(request.headers.get("accept-language", ""))
    return {"lang": tr.get_alternative_lang(current, browser)}

@app.get("/translate")
def translate(lang: str = "en"):
    html = HTML_PATH.read_text(encoding="utf-8")
    return tr.translate_html(html, target_lang=lang, page_name="page")
```
# Notes & limits
You control OpenAI usage/billing.

Chunking keeps requests within model limits; HTML structure preserved.

Short labels (buttons) use a concise prompt to avoid verbose text.

This package is for runtime translation with caching; static catalogs are out of scope.

# Versioning
Semantic Versioning: MAJOR.MINOR.PATCH.

# License
MIT © BONA

# Support
Issues & feature requests → GitHub Issues (see project URLs in metadata).

