# Storybook Agent

Turns one prompt into an illustrated five-page children's picture book as a downloadable PDF, with a hero who looks identical on every page.

## How it works

1. `story_planner` writes the title and a five-beat outline.
2. `character_designer` picks the hero's look from fixed options (skin, hair, outfit colors, signature item).
3. `scene_planner` writes each page's text plus a structured scene plan (setting, time of day, elements, pose, expression).
4. `quality_gate` checks the pages and loops back to `scene_planner` with feedback, up to 2 retries.
5. `page_composer` draws every page as vector art. The hero comes from one Python function, so the character is identical by construction.
6. `pdf_assembler` builds a landscape A4 PDF: cover plus five pages, illustration on top, text below.

No image-generation model is used, so there is no image cost. Only text calls go to `openai/gpt-6-luna` through AIRouter.

## Setup

Requires Python 3.10 or newer.

```bash
cd storybook-agent
python -m venv .venv
```

Activate the environment:

- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- Windows cmd: `.venv\Scripts\activate.bat`
- macOS / Linux: `source .venv/bin/activate`

Install and configure:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` (`copy .env.example .env` on Windows, `cp .env.example .env` elsewhere) and set your key:

```
AIROUTER_API_KEY=sk-air-v1-your-real-key
```

## Verify the connection

```bash
python check_connection.py
```

It should print the model's reply and `Connection OK`.

## Try it without spending credits

```bash
python generate.py --demo
```

This builds a complete PDF from built-in story data. The path of the PDF is printed, inside `outputs/<job_id>/storybook.pdf`.

## Run the app

Option A, one command:

```bash
python run_all.py
```

Option B, two terminals (activate the virtual environment in each):

```bash
uvicorn app.main:app --port 8000
streamlit run ui/streamlit_app.py
```

Open http://localhost:8501, type a story idea, click **Create my storybook**, then **Download PDF**.

## Generate from the command line

```bash
python generate.py "A brave boy named Leo finds a hidden magical garden behind his school"
```

## API

| Method | Path | Purpose |
|---|---|---|
| POST | `/books` with `{"prompt": "..."}` | Start a job, returns `job_id` |
| GET | `/books/{job_id}` | Status, progress, title, page texts |
| GET | `/books/{job_id}/pdf` | Download the PDF |
| GET | `/books/{job_id}/pages/{0-5}` | SVG of the cover (0) or a page |
| GET | `/health` | Configuration check |

Interactive docs are at http://localhost:8000/docs.

## Configuration (.env)

| Variable | Default | Meaning |
|---|---|---|
| `AIROUTER_API_KEY` | none | Your AIRouter key |
| `AIROUTER_BASE_URL` | `https://api.airouter.in/v1` | OpenAI-compatible endpoint |
| `LLM_MODEL` | `openai/gpt-6-luna` | Model name |
| `REASONING_EFFORT` | empty | Set `low` to reduce cost and latency if AIRouter accepts it |
| `LLM_MAX_ATTEMPTS` | `3` | Retries when the model returns invalid JSON |
| `DEMO_MODE` | `false` | Use built-in data, no model calls |
| `OUTPUT_DIR` | `outputs` | Where jobs are stored |
| `API_URL` | `http://127.0.0.1:8000` | Where Streamlit finds the API |

## Tests

```bash
pytest
```

## Troubleshooting

- **"AIROUTER_API_KEY is not set"**: the `.env` file must be in the project root and contain the key.
- **Streamlit says it cannot reach the API**: start the FastAPI server first, and check the API URL in the sidebar.
- **Model errors about an unsupported parameter**: leave `REASONING_EFFORT` empty.
- **A story fails after several attempts**: the model returned invalid JSON repeatedly. Run again, or raise `LLM_MAX_ATTEMPTS`.
- **Port already in use**: pass a different port to uvicorn and update `API_URL`.

## Customizing the hero and scenery

- Palettes and allowed values: `app/art/vocab.py`
- Hero drawing: `app/art/hero.py`
- Backgrounds and decorations: `app/art/scene.py`
- PDF layout and fonts: `app/services/layout.py`, `app/services/pdf_builder.py`
