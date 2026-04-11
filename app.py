"""
Streamlit UI for the multi-agent sunglasses campaign lab (Gemini-only models).
Run: streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from google import genai

from config import (
    GEMINI_IMAGE_MODEL,
    GEMINI_TEXT_MODEL,
    USE_TAVILY_SEARCH,
    describe_api_key_problem,
    hint_if_only_truncated_keys_in_env,
    normalize_api_key,
    resolve_google_api_key,
)
from gemini_agents import run_sunglasses_campaign_pipeline


def _api_key_from_streamlit_secrets() -> str:
    try:
        sec = st.secrets
        return normalize_api_key(sec.get("GOOGLE_API_KEY", "") or sec.get("GEMINI_API_KEY", ""))
    except Exception:
        return ""

st.set_page_config(
    page_title="Campaign lab — multi-agent (Gemini)",
    page_icon="🕶️",
    layout="wide",
)

st.title("Summer sunglasses campaign — multi-agent lab")
st.caption(
    "Teaching demo: Market Research → Graphic Designer → Copywriter → Packaging. "
    "All LLM steps use Gemini; images use a Nano Banana image model."
)

st.markdown(
    """
**Pipeline**

1. **Market Research** — Google Search grounding *or* Tavily + `product_catalog_tool` (function calling).  
2. **Graphic Designer** — Gemini text → JSON prompt + caption; **Nano Banana** image model → hero image.  
3. **Copywriter** — Multimodal Gemini: image + trends → quote + justification.  
4. **Packaging** — Gemini polishes copy; app writes an executive Markdown report.
"""
)

with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input(
        "Google API key (optional if set in .env)",
        type="password",
        value="",
        placeholder="Leave empty to use GOOGLE_API_KEY or GEMINI_API_KEY",
        help=(
            "Create one at https://aistudio.google.com/apikey — or set GOOGLE_API_KEY "
            "or GEMINI_API_KEY in a .env file next to app.py."
        ),
    )
    _from_env = resolve_google_api_key("")
    _from_secrets = _api_key_from_streamlit_secrets()
    if not api_key.strip() and (_from_env or _from_secrets):
        src = "`.streamlit/secrets.toml`" if _from_secrets and not _from_env else "`.env`"
        st.caption(f"Using API key from {src} (`GOOGLE_API_KEY` or `GEMINI_API_KEY`).")
    text_model = st.text_input("Text model (Gemini Flash)", value=GEMINI_TEXT_MODEL)
    image_model = st.text_input("Image model (Nano Banana)", value=GEMINI_IMAGE_MODEL)
    use_tavily = st.toggle(
        "Use Tavily instead of Google Search",
        value=USE_TAVILY_SEARCH,
        help="Requires TAVILY_API_KEY in environment. Default uses Google Search grounding.",
    )
    if use_tavily:
        st.info("Set `TAVILY_API_KEY` in `.env` for web search.")
    st.markdown(
        "Each full run performs several billed API calls (text + image). "
        "Use a test project key for class demos."
    )
    run = st.button("Run full pipeline", type="primary")

if "last_error" not in st.session_state:
    st.session_state.last_error = None
if "result" not in st.session_state:
    st.session_state.result = None


if "trace" not in st.session_state:
    st.session_state.trace = []

if run:
    st.session_state.last_error = None
    st.session_state.result = None
    st.session_state.trace = []
    resolved_key = resolve_google_api_key(api_key) or _api_key_from_streamlit_secrets()
    if not resolved_key:
        truncated = hint_if_only_truncated_keys_in_env()
        st.session_state.last_error = truncated or (
            "No usable API key: add a full `GOOGLE_API_KEY` or `GEMINI_API_KEY` to `.env` "
            "(next to `app.py`) or paste it in the sidebar. Restart Streamlit after editing `.env`."
        )
    else:
        trace: list[str] = []

        def log_step(msg: str) -> None:
            trace.append(msg)

        try:
            prob = describe_api_key_problem(resolved_key)
            if prob:
                st.session_state.last_error = prob
            else:
                # Force Gemini Developer API (Google AI Studio key). Vertex uses different auth.
                client = genai.Client(api_key=resolved_key, vertexai=False)
                with st.spinner("Running multi-agent pipeline (may take a minute)…"):
                    result = run_sunglasses_campaign_pipeline(
                        client,
                        text_model=text_model.strip() or GEMINI_TEXT_MODEL,
                        image_model=image_model.strip() or GEMINI_IMAGE_MODEL,
                        use_tavily=use_tavily,
                        log_step=log_step,
                    )
                st.session_state.result = result
                st.session_state.trace = trace
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            if "API_KEY_INVALID" in str(e) or "API key not valid" in str(e):
                err += (
                    "\n\n**Tip:** Create the key in [Google AI Studio](https://aistudio.google.com/apikey) "
                    "and paste the **full** key (about 39 characters). "
                    "If both `GOOGLE_API_KEY` and `GEMINI_API_KEY` exist in `.env`, remove the wrong or truncated one."
                )
            st.session_state.last_error = err

if st.session_state.last_error:
    st.error(st.session_state.last_error)

res = st.session_state.result
if res:
    st.success("Pipeline completed.")

    with st.expander("1 — Market research", expanded=True):
        st.markdown("**Trend brief**")
        st.markdown(res["trend_summary"])
        steps = res.get("research_steps") or []
        if steps:
            st.markdown("**Orchestration notes**")
            for s in steps:
                st.text(s)
        trace = st.session_state.get("trace") or []
        if trace:
            st.markdown("**Agent trace (tool + model steps)**")
            st.code("\n".join(trace[-200:]), language=None)

    with st.expander("2 — Graphic designer", expanded=True):
        vis = res["visual"]
        st.image(vis["image_path"], caption="Campaign visual", use_container_width=True)
        st.markdown("**Caption**")
        st.write(vis.get("caption", ""))
        st.markdown("**Image prompt**")
        st.code(vis.get("prompt", ""), language="text")

    with st.expander("3 — Copywriter", expanded=True):
        q = res["quote"]
        st.markdown(f"**Quote:** {q.get('quote', '')}")
        st.markdown(f"**Justification:** {q.get('justification', '')}")

    with st.expander("4 — Packaging", expanded=True):
        md_path = res["markdown_path"]
        st.markdown(f"Report saved to `{md_path}`")
        p = Path(md_path)
        if p.is_file():
            md_text = p.read_text(encoding="utf-8")
            img_p = Path(res["visual"]["image_path"])
            if img_p.is_file():
                md_text = md_text.replace(
                    f"![Campaign visual]({img_p.name})",
                    f"![Campaign visual]({img_p.as_posix()})",
                )
            st.markdown(md_text)
            st.download_button(
                label="Download Markdown report",
                data=md_text,
                file_name=p.name,
                mime="text/markdown",
            )
