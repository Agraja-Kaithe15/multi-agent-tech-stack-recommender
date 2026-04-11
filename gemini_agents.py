"""
Multi-agent campaign pipeline using Gemini (Flash text + Nano Banana image models).
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path

from google import genai
from PIL import Image
from google.genai import types

from config import GEMINI_IMAGE_MODEL, GEMINI_TEXT_MODEL, USE_TAVILY_SEARCH
from tools.catalog import product_catalog_tool
from tools.search import tavily_search_tool

OUTPUTS_DIR = Path(__file__).resolve().parent / "outputs"

_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)


def _ensure_outputs() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def _iter_response_parts(response: types.GenerateContentResponse) -> list[types.Part]:
    if response.parts:
        return list(response.parts)
    cand = (response.candidates or [None])[0]
    if cand and cand.content and cand.content.parts:
        return list(cand.content.parts)
    return []


def _parse_json_object(text: str) -> dict:
    match = _JSON_BLOCK.search(text.strip())
    if not match:
        return {"error": "No JSON object found", "raw": text}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse error: {e}", "raw": text}


def _execute_tool(name: str, args: object) -> str:
    args = args if isinstance(args, dict) else {}
    if name == "product_catalog_tool":
        return product_catalog_tool()
    if name == "tavily_search_tool":
        q = args.get("query", "")
        return tavily_search_tool(str(q))
    return json.dumps({"error": f"Unknown tool: {name}"})


def _market_research_tool_config(use_tavily: bool) -> types.GenerateContentConfig:
    catalog_decl = types.FunctionDeclaration(
        name="product_catalog_tool",
        description=(
            "Returns the internal sunglasses product catalog (JSON): id, name, "
            "description, stock, price. Call this to match trends to real products."
        ),
        parameters=types.Schema(type="object", properties={}),
    )
    if use_tavily:
        tavily_decl = types.FunctionDeclaration(
            name="tavily_search_tool",
            description=(
                "Search the public web for current fashion trends, sunglasses styles, "
                "or seasonal retail signals. Pass a focused query string."
            ),
            parameters=types.Schema(
                type="object",
                properties={
                    "query": types.Schema(
                        type="string",
                        description="Web search query, e.g. 'summer 2026 sunglasses fashion trends'",
                    )
                },
                required=["query"],
            ),
        )
        tools = [
            types.Tool(function_declarations=[tavily_decl, catalog_decl]),
        ]
    else:
        tools = [
            types.Tool(
                google_search=types.GoogleSearch(),
                function_declarations=[catalog_decl],
            ),
        ]

    return types.GenerateContentConfig(
        tools=tools,
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(
                mode=types.FunctionCallingConfigMode.AUTO,
            )
        ),
    )


def market_research_agent(
    client: genai.Client,
    text_model: str = GEMINI_TEXT_MODEL,
    *,
    use_tavily: bool | None = None,
    log_step=None,
) -> dict:
    """
    Web trends (Google Search grounding or Tavily) + catalog via function calling.
    Returns {"summary": str, "steps": list[str]}.
    """
    use_tavily = USE_TAVILY_SEARCH if use_tavily is None else use_tavily
    cfg = _market_research_tool_config(use_tavily)
    steps: list[str] = []
    steps.append(
        "Search mode: Tavily (function)"
        if use_tavily
        else "Search mode: Google Search grounding + catalog (function)"
    )

    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""You are a fashion market research agent preparing a trend analysis for a summer sunglasses campaign.

Goals:
1. Discover current sunglasses / eyewear fashion trends (use web search when needed).
2. Call product_catalog_tool to load our internal catalog.
3. Recommend one or more catalog products that fit the trends.

Today's date: {today}.

When finished, reply with a clear final message (no more tool calls) that includes:
- Top 2–3 trends you found
- Which catalog product(s) you recommend (by name and id)
- Why they fit a summer campaign
"""
    contents: list[types.Content] = [
        types.Content(role="user", parts=[types.Part.from_text(text=prompt)]),
    ]

    max_turns = 16
    for turn in range(max_turns):
        response = client.models.generate_content(
            model=text_model,
            contents=contents,
            config=cfg,
        )
        cand = response.candidates[0] if response.candidates else None
        if not cand or not cand.content or not cand.content.parts:
            msg = "No model output (blocked or empty)."
            steps.append(msg)
            if log_step:
                log_step(msg)
            return {"summary": msg, "steps": steps}

        model_content = cand.content
        contents.append(model_content)

        calls: list[types.FunctionCall] = []
        text_chunks: list[str] = []
        for part in model_content.parts:
            if part.function_call:
                calls.append(part.function_call)
            if part.text:
                text_chunks.append(part.text)

        if not calls:
            summary = (response.text or "\n".join(text_chunks)).strip()
            steps.append(f"Final answer after {turn + 1} model turn(s).")
            if log_step:
                log_step(f"Final answer (turn {turn + 1})")
            return {"summary": summary, "steps": steps}

        step_lines = [f"Turn {turn + 1}: executing {len(calls)} tool call(s)"]
        steps.extend(step_lines)
        if log_step:
            log_step("\n".join(step_lines))

        response_parts: list[types.Part] = []
        for fc in calls:
            name = fc.name or ""
            raw_args = fc.args
            args_dict = raw_args if isinstance(raw_args, dict) else {}
            if log_step:
                log_step(f"Tool `{name}` args={args_dict!r}")
            result = _execute_tool(name, args_dict)
            if log_step:
                preview = result[:1200] + ("…" if len(result) > 1200 else "")
                log_step(f"Tool `{name}` result preview:\n{preview}")
            response_parts.append(
                types.Part.from_function_response(
                    name=name,
                    response={"result": result},
                )
            )
        contents.append(types.Content(role="user", parts=response_parts))

    if log_step:
        log_step("Stopped: max turns reached without final text.")
    return {
        "summary": "[Stopped: max tool-calling turns reached — try again or increase limit.]",
        "steps": steps,
    }


def graphic_designer_agent(
    client: genai.Client,
    trend_insights: str,
    *,
    text_model: str = GEMINI_TEXT_MODEL,
    image_model: str = GEMINI_IMAGE_MODEL,
    caption_style: str = "short punchy",
    log_step=None,
) -> dict:
    """LLM writes image prompt + caption; Nano Banana image model renders the image."""
    system_message = (
        "You are a visual marketing assistant. Based on trend insights, write a creative "
        "prompt for an AI image model and a marketing caption."
    )
    user_prompt = f"""Trend insights:
{trend_insights}

Output exactly one JSON object with keys "prompt" and "caption" only.
Caption style: {caption_style}.

The image prompt should describe a single campaign hero image: summer sunglasses, on-brand, suitable for social and print.
"""
    if log_step:
        log_step("Graphic designer: requesting prompt + caption (text model).")

    chat_response = client.models.generate_content(
        model=text_model,
        contents=[types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)])],
        config=types.GenerateContentConfig(system_instruction=system_message),
    )
    raw = (chat_response.text or "").strip()
    parsed = _parse_json_object(raw)
    if "prompt" not in parsed or "caption" not in parsed:
        raise ValueError(f"Graphic designer did not return prompt/caption JSON: {parsed}")

    prompt = str(parsed["prompt"])
    caption = str(parsed["caption"])

    if log_step:
        log_step("Graphic designer: generating image (Nano Banana / image model).")

    img_response = client.models.generate_content(
        model=image_model,
        contents=[prompt],
    )

    _ensure_outputs()
    stem = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_path = OUTPUTS_DIR / f"{stem}.png"

    saved = False
    for part in _iter_response_parts(img_response):
        if part.inline_data is not None:
            img = part.as_image()
            img.save(str(out_path))
            saved = True
            break

    if not saved:
        raise RuntimeError(
            "Image model returned no inline image data. Check GEMINI_IMAGE_MODEL and billing."
        )

    return {
        "image_path": str(out_path),
        "prompt": prompt,
        "caption": caption,
    }


def copywriter_agent(
    client: genai.Client,
    image_path: str,
    trend_summary: str,
    *,
    text_model: str = GEMINI_TEXT_MODEL,
    log_step=None,
) -> dict:
    """Multimodal: image + trend text → quote + justification."""
    if log_step:
        log_step("Copywriter: multimodal quote generation.")

    with open(image_path, "rb") as f:
        img_bytes = f.read()

    fmt = (Image.open(BytesIO(img_bytes)).format or "PNG").lower()
    mime = f"image/{fmt}"

    user_text = f"""Here is a campaign visual and a trend analysis.

Trend summary:
\"\"\"{trend_summary}\"\"\"

Return a single JSON object with keys "quote" and "justification" only.
- quote: short elegant campaign phrase (max 12 words)
- justification: one short paragraph on why it matches the image and trends
"""
    response = client.models.generate_content(
        model=text_model,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(data=img_bytes, mime_type=mime),
                    types.Part.from_text(text=user_text),
                ],
            )
        ],
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a copywriter that creates elegant campaign quotes from an image "
                "and a marketing trend summary. Reply only with the requested JSON."
            ),
        ),
    )
    raw = (response.text or "").strip()
    parsed = _parse_json_object(raw)
    if "quote" not in parsed or "justification" not in parsed:
        raise ValueError(f"Copywriter did not return quote JSON: {parsed}")
    parsed["image_path"] = image_path
    return parsed


def packaging_agent(
    client: genai.Client,
    trend_summary: str,
    image_ref: str,
    quote: str,
    justification: str,
    *,
    text_model: str = GEMINI_TEXT_MODEL,
    output_path: str | None = None,
    log_step=None,
) -> str:
    """Beautify summary via Gemini, then write executive markdown."""
    if log_step:
        log_step("Packaging: refining trend copy for executives.")

    polish = client.models.generate_content(
        model=text_model,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=(
                            "Rewrite the following trend summary to be clear, professional, "
                            "and engaging for a CEO audience. Use short paragraphs.\n\n"
                            f"\"\"\"{trend_summary.strip()}\"\"\""
                        )
                    ),
                ],
            )
        ],
    )
    beautified = (polish.text or "").strip()

    _ensure_outputs()
    if output_path is None:
        output_path = str(
            OUTPUTS_DIR / f"campaign_summary_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
        )

    image_name = Path(image_ref).name
    md = f"""# Summer Sunglasses Campaign – Executive Summary

## Refined trend insights

{beautified}

## Campaign visual

![Campaign visual]({image_name})

## Campaign quote

{quote.strip()}

## Why this works

{justification.strip()}

---

*Report generated on {datetime.now().strftime("%Y-%m-%d")}*
"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)

    return output_path


def run_sunglasses_campaign_pipeline(
    client: genai.Client,
    *,
    text_model: str = GEMINI_TEXT_MODEL,
    image_model: str = GEMINI_IMAGE_MODEL,
    use_tavily: bool | None = None,
    log_step=None,
) -> dict:
    """Run all four agents in sequence; return intermediate results and report path."""
    research = market_research_agent(
        client,
        text_model=text_model,
        use_tavily=use_tavily,
        log_step=log_step,
    )
    trend_summary = research["summary"]

    visual = graphic_designer_agent(
        client,
        trend_summary,
        text_model=text_model,
        image_model=image_model,
        log_step=log_step,
    )

    quote_result = copywriter_agent(
        client,
        image_path=visual["image_path"],
        trend_summary=trend_summary,
        text_model=text_model,
        log_step=log_step,
    )

    md_path = packaging_agent(
        client,
        trend_summary=trend_summary,
        image_ref=visual["image_path"],
        quote=str(quote_result.get("quote", "")),
        justification=str(quote_result.get("justification", "")),
        text_model=text_model,
        log_step=log_step,
    )

    return {
        "trend_summary": trend_summary,
        "research_steps": research.get("steps", []),
        "visual": visual,
        "quote": quote_result,
        "markdown_path": md_path,
    }
