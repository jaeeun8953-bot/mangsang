"""Embedded Daydream Circuit brain interface, communicating with Streamlit."""
import json
import os
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

_COMPONENT = components.declare_component(
    "daydream_brain", path=str(Path(__file__).resolve().parent)
)

def _generate(payload):
    mode = payload.get("mode", "mixed")
    language = payload.get("language", "ko")
    if mode not in ("logic", "creative", "mixed") or language not in ("ko", "en"):
        raise ValueError("Invalid mode or language")
    logic_n, creative_n = {"logic": (6, 0), "creative": (0, 6), "mixed": (0, 0)}[mode]
    history = payload.get("history", [])
    if not isinstance(history, list):
        history = []
    initial = str(payload.get("initial_thought", ""))[:500]
    current = str(payload.get("current_thought", ""))[:500]
    if not current.strip():
        raise ValueError("Missing thought")
    key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    from google import genai
    client = genai.Client(api_key=key)
    prompt = f"""You are the Daydream Circuit thought-exploration facilitator.
Generate follow-up questions, not answers, in {"Korean" if language == "ko" else "English"}.
The user's starting idea: {initial}
Current selected direction: {current}
Earlier choices: {json.dumps(history[-18:], ensure_ascii=False)}
Return JSON with exactly three arrays: "logic" ({logic_n} strings), "creative" ({creative_n} strings), "mixed" ({6 if mode == "mixed" else 0} strings).
Logical questions should focus on reasoning, causes, evidence, comparisons, conditions, constraints.
Creative questions should focus on imagination, alternative perspectives, analogies, new connections.
Mixed questions must EACH integrate both analytical reasoning and imaginative possibilities into ONE coherent question; do NOT split into 3 logical plus 3 creative questions. Each question must be brief, distinct and specific to the current thought, not generic.
Never suggest that brain hemispheres exclusively control these skills.
Do not answer the questions. No Markdown, only valid JSON."""
    result = client.models.generate_content(
        model=os.environ.get("GEMINI_MODEL", "gemini-3.8-flash"),
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    data = json.loads(result.text)
    if (not isinstance(data.get("logic"), list)
        or not isinstance(data.get("creative"), list)
        or not isinstance(data.get("mixed"), list)
        or len(data["logic"]) != logic_n or len(data["creative"]) != creative_n
        or len(data["mixed"]) != (6 if mode == "mixed" else 0)
        or not all(isinstance(x,str) and x.strip() for x in data["logic"] + data["creative"] + data["mixed"])):
        raise ValueError("Invalid AI response")
    return data

def show_brain(language):
    st.caption("🧠 3D 사고 지도 · AI-generated thought paths")
    response = st.session_state.get("brain_ai_response")
    event = _COMPONENT(
        language="en" if language == "English" else "ko",
        ai_response=response,
        key="daydream_brain_component",
        default=None,
    )
    if not isinstance(event, dict):
        return
    request_id = str(event.get("request_id", ""))
    if not request_id or request_id == st.session_state.get("brain_processed_request"):
        return
    st.session_state.brain_processed_request = request_id
    try:
        with st.spinner("새로운 생각의 갈림길 생성 중..." if language != "English" else "Generating new paths..."):
            data = _generate(event)
        st.session_state.brain_ai_response = {"request_id": request_id, **data}
    except Exception as exc:
        # Do not expose API key, secrets, or internal errors to the browser.
        st.session_state.brain_ai_response = {"request_id": request_id, "error": "AI unavailable"}
        st.warning("Gemini 연결에 실패해 기본 갈림길로 계속합니다." if language != "English"
                   else "Gemini is unavailable. Continuing with built-in prompts.")
    st.rerun()
