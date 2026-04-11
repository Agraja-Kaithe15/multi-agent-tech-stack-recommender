# Multi-agent marketing campaign lab

A small **multi-agent workflow** that simulates a marketing studio for a **summer sunglasses** campaign. Each stage is handled by a different Gemini-powered “role”: research, visual design, copy, and final packaging into a client-ready report.

The app is a **Streamlit** front end; orchestration and prompts live in Python using the **Google GenAI SDK** ([Gemini](https://ai.google.dev/gemini-api/docs)) with optional **Tavily** search.

## What the pipeline does

| Stage | Role | What happens |
|--------|------|----------------|
| 1 | **Market research** | Trend brief using **Google Search grounding** (default) or **Tavily** + a **product catalog** tool (`data/catalog.json`) via function calling. |
| 2 | **Graphic designer** | Text model proposes a JSON image prompt and caption; a **Gemini image** model generates a hero image saved under `outputs/`. |
| 3 | **Copywriter** | Multimodal step: image + trends → campaign **quote** and **justification**. |
| 4 | **Packaging** | Polished **Markdown** executive report written to `outputs/`, downloadable from the UI. |

This is framed as a teaching / demo lab: several billed API calls (text + image) run per full pipeline execution.

## Tech stack

- **Python 3.11+** (3.12 or 3.13 recommended)
- **Streamlit** — UI and configuration sidebar
- **`google-genai`** — Gemini text + image generation (Google AI Studio / API key auth, not Vertex by default)
- **`python-dotenv`** — loads `.env` from the project root
- **Pillow**, **requests** — images and optional Tavily HTTP calls

## Quick start

1. **Clone the repository**

   ```bash
   git clone https://github.com/thisislokesh/multi-agentic-system-marketing-agency.git
   cd multi-agentic-system-marketing-agency
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Copy the example file and add your keys (never commit `.env`):

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set at least **`GOOGLE_API_KEY`** or **`GEMINI_API_KEY`** from [Google AI Studio](https://aistudio.google.com/apikey).

4. **Run the app**

   ```bash
   streamlit run app.py
   ```

   Open the URL Streamlit prints (usually `http://localhost:8501`). You can paste an API key in the sidebar instead of using `.env`, or use [Streamlit secrets](https://docs.streamlit.io/develop/concepts/connections/secrets-management) (`.streamlit/secrets.toml`) with `GOOGLE_API_KEY` / `GEMINI_API_KEY`.

## Configuration reference

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` or `GEMINI_API_KEY` | Yes (for real runs) | Google AI Studio API key for the Gemini API. |
| `GEMINI_TEXT_MODEL` | No | Text model id (default in `.env.example`: `gemini-3-flash-preview`). |
| `GEMINI_IMAGE_MODEL` | No | Image model id (default: `gemini-3.1-flash-image-preview`). |
| `USE_TAVILY_SEARCH` | No | Set to `true` to use Tavily instead of Google Search grounding for research. |
| `TAVILY_API_KEY` | If Tavily enabled | Required when `USE_TAVILY_SEARCH=true`. |

Restart Streamlit after changing `.env`.

## Project layout

```text
.
├── app.py                 # Streamlit UI
├── config.py              # Env loading, API key helpers, model defaults
├── gemini_agents.py       # Multi-step campaign pipeline
├── tools/                 # Function-calling tools (catalog, Tavily search)
├── data/catalog.json      # Demo product catalog for the researcher agent
├── outputs/               # Generated images + Markdown (gitignored except .gitkeep)
├── requirements.txt
├── .env.example           # Template only — copy to `.env` locally
└── README.md
```

## Security notes

- **Do not commit `.env`.** It is listed in `.gitignore` and should stay on your machine (or use CI secrets / Streamlit Cloud secrets in deployment).
- Use a **dedicated API key** with usage limits for experiments and teaching.

## Repository

Upstream project: [thisislokesh/multi-agentic-system-marketing-agency](https://github.com/thisislokesh/multi-agentic-system-marketing-agency).
