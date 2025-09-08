from __future__ import annotations

import os, io, re, json, base64
from typing import Any, Dict, List, Optional

from syntaxmatrix import profiles as _prof
from syntaxmatrix.settings.model_map import GPT_MODELS_LATEST 
from syntaxmatrix.gpt_models_latest import extract_output_text as _out, set_args
from google.genai import types


# Axes/labels/legend (read-only; no plotting changes)
MPL_PROBE_SNIPPET = r"""
    import json
    import matplotlib.pyplot as plt

    out=[]
    for num in plt.get_fignums():
        fig = plt.figure(num)
        for ax in fig.get_axes():
            info = {
                "title": (ax.get_title() or "").strip(),
                "x_label": (ax.get_xlabel() or "").strip(),
                "y_label": (ax.get_ylabel() or "").strip(),
                "legend": []
            }
            try:
                leg = ax.get_legend()
                if leg:
                    info["legend"] = [t.get_text().strip() for t in leg.get_texts() if t.get_text().strip()]
            except Exception:
                pass
            out.append(info)
    print("SMX_VIS_SUMMARY::" + json.dumps(out))
"""

# 2) Figure images to base64 (tight bbox, high DPI)
MPL_IMAGE_PROBE_SNIPPET = r"""
    import json, io, base64
    import matplotlib.pyplot as plt

    payload=[]
    for num in plt.get_fignums():
        fig = plt.figure(num)
        axes=[]
        for ax in fig.get_axes():
            info={"title": (ax.get_title() or "").strip(),
                "x_label": (ax.get_xlabel() or "").strip(),
                "y_label": (ax.get_ylabel() or "").strip(),
                "legend": []}
            try:
                leg = ax.get_legend()
                if leg:
                    info["legend"] = [t.get_text().strip() for t in leg.get_texts() if t.get_text().strip()]
            except Exception:
                pass
            axes.append(info)

        b64 = ""
        try:
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=192, bbox_inches="tight", facecolor="white")
            buf.seek(0)
            b64 = base64.b64encode(buf.read()).decode("ascii")
        except Exception:
            b64 = ""
        payload.append({"png_b64": b64, "axes": axes})
    print("SMX_FIGS_B64::" + json.dumps(payload))
"""


def _json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), indent=2)


def parse_mpl_probe_output(text_blocks: List[str]) -> List[Dict[str, Any]]:
    joined = "\n".join(text_blocks)
    m = re.search(r"SMX_VIS_SUMMARY::(\[.*\]|\{.*\})", joined, re.DOTALL)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
        return data if isinstance(data, list) else []
    except Exception:
        return []
    
def parse_image_probe_output(text_blocks: List[str]) -> List[Dict[str, Any]]:
    joined = "\n".join(text_blocks)
    m = re.search(r"SMX_FIGS_B64::(\[.*\])", joined, re.DOTALL)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
        return data if isinstance(data, list) else []
    except Exception:
        return []

# 3) Table headers (from already-rendered HTML) — optional but helps context
def _strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", " ", s).strip()

def sniff_tables_from_html(html: str) -> List[Dict[str, Any]]:
    tables=[]
    for tbl in re.findall(r"<table[^>]*class=[\"'][^\"']*smx-table[^\"']*[\"'][^>]*>(.*?)</table>",
                          html, re.DOTALL|re.IGNORECASE):
        ths = re.findall(r"<th[^>]*>(.*?)</th>", tbl, re.DOTALL|re.IGNORECASE)
        headers = [_strip_tags(h) for h in ths][:50]
        trs = re.findall(r"<tr[^>]*>", tbl, re.IGNORECASE)
        tables.append({
            "columns": headers,
            "columns_count": len(headers),
            "rows_approx": max(0, len(trs)-1)
        })
    return tables


def build_display_summary(question: str,
                          mpl_axes: List[Dict[str, Any]],
                          html_blocks: List[str]) -> Dict[str, Any]:
    html_joined = "\n".join(str(b) for b in html_blocks)
    tables = sniff_tables_from_html(html_joined)

    axes_clean=[]
    for ax in mpl_axes:
        axes_clean.append({
            "title": ax.get("title",""),
            "x_label": ax.get("x_label",""),
            "y_label": ax.get("y_label",""),
            "legend": ax.get("legend", []),
        })

    return {
        "question": (question or "").strip(),
        "axes": axes_clean,
        "tables": tables
    }

def _context_strings(context: Dict[str, Any]) -> List[str]:
    s = [context.get("question","")]
    for ax in context.get("axes", []) or []:
        s += [ax.get("title",""), ax.get("x_label",""), ax.get("y_label","")]
        s += (ax.get("legend", []) or [])
    for t in context.get("tables", []) or []:
        s += (t.get("columns", []) or [])
    # de-dup
    seen=set(); out=[]
    for it in s:
        it=(it or "").strip()
        if not it: continue
        k=it.lower()
        if k in seen: continue
        seen.add(k); out.append(it)
    return out




# --- C) LLM prompts ---

_SYSTEM_VISION = (
    "You are a data analyst. Write a short, precise commentary in UK English that explains what the "
    "already-rendered visuals mean for the user's question. "
    "Use information visible in the attached figures and the provided context strings (field names, labels). "
    "Do not invent numbers. If the figures/context are insufficient, say: 'Insufficient context to comment usefully.'"
)

_USER_TMPL_VISION = """\
Question:
{q}

Visible context strings (titles, axes, legends, headers):
{ctx}

Write a concise conclusion (~140-200 words) with:
- Headline (one sentence answering the question).
- Evidence (4-5 bullets referencing panels/axes/legend groups seen in the figures).
- Limitations (1-2 bullets; avoid quoting numbers unless present in context).
- Next step (1 bullet).
"""

def phrase_commentary_vision(context: Dict[str, Any], images_b64: List[str]) -> str:
    """
    Use the project's 'vision2text' profile (profiles.py). If the provider supports images,
    send figures + text; otherwise fall back to a text-only prompt grounded by labels.
    """
  
    visible = _context_strings(context)
    user = _USER_TMPL_VISION.format(
        q=context.get("question",""),
        ctx=json.dumps(visible, ensure_ascii=False, indent=2)
    )

    # Always try 'vision2text' first, then fall back to 'admin'
    prof = _prof.get_profile("vision2text") or _prof.get_profile("admin")
    if not prof:
        return "Insufficient context to comment usefully."
    client = _prof.get_client(prof)
    provider = (prof.get("provider") or "").lower()
    model = prof.get("model") or ""

    # Google GenAI (Gemini) — multimodal
    if provider == "google":
        try:
            from google.genai import types
            parts = [types.Part.from_text(text=user)]
            for b64 in images_b64[:4]:
                if b64:
                    parts.append(types.Part.from_bytes(data=base64.b64decode(b64), mime_type="image/png"))
            contents = [types.Content(role="user", parts=parts)]
            resp = client.models.generate_content(
                model=model,
                contents=contents,
                system_instruction=_SYSTEM_VISION
            )
            txt = getattr(resp, "text", "") or ""
            if txt.strip():
                return txt.strip()
        except Exception:
            pass  # fall through to text-only
    
    elif provider == "openai" and model in GPT_MODELS_LATEST:
        # Use the Responses API with multimodal input (text + up to 4 images)
        try:
            parts = [{"type": "input_text", "text": user}]
            for b64 in (images_b64 or [])[:4]:
                if b64:
                    parts.append({"type": "input_image", "image_url": f"data:image/png;base64,{b64}"})

            args = set_args(
                model=model,
                instructions=_SYSTEM_VISION,
                input=[{"role": "user", "content": parts}],
                previous_id=None,
                store=False,
                reasoning_effort="minimal",
                verbosity="low",
            )
            resp = client.responses.create(**args)
            txt = _out(resp) or ""
            if txt.strip():
                return txt.strip()
        except Exception:
            # If the Responses path fails for any reason, fall through to the
            # chat.completions fallback implemented below.
            pass

    # OpenAI (gpt-4o / gpt-4o-mini) — chat.completions with image parts
    else: # provider in {"openai","xai","deepseek","moonshotai","alibaba"}:
        try:
            parts = [{"type":"text","text": user}]
            for b64 in images_b64[:4]:
                if b64:
                    parts.append({"type":"image_url","image_url":{"url": f"data:image/png;base64,{b64}"}})
            resp = client.chat.completions.create(
                model=model,
                temperature=0.2,
                messages=[
                    {"role":"system","content":_SYSTEM_VISION},
                    {"role":"user","content":parts},
                ],
                max_tokens=600,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception:
            pass  # fall through

    # Text-only fallback via Responses API
    try:
        args = set_args(model=model, instructions=_SYSTEM_VISION,
                        input=user, previous_id=None, store=False,
                        reasoning_effort="minimal", verbosity="low")
        resp = client.responses.create(**args)
        return _out(resp)
    except Exception:
        # Classic chat fallback
        try:
            resp = client.chat.completions.create(
                model=model,
                temperature=0.2,
                messages=[{"role":"system","content":_SYSTEM_VISION},
                          {"role":"user","content":user}],
                max_tokens=600,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception:
            return "Insufficient context to comment usefully."


def wrap_html(card_text: str) -> str:
    return f"""
        <div class="smx-commentary-card" style="margin-top:1rem;padding:1rem;border:1px solid #e5e7eb;border-radius:0.75rem;background:#fafafa">
        <div style="font-weight:600;margin-bottom:0.5rem;">Commentary</div>
        <div class="prose" style="white-space:pre-wrap;line-height:1.45">{card_text}</div>
        </div>
    """.strip()
