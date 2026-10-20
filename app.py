"""Daydream Circuit bilingual launcher. Run: streamlit run app.py"""
import runpy
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Daydream Circuit | 망상회로", page_icon="🧠", layout="wide")

if "app_language" not in st.session_state:
    st.session_state.app_language = "English"

with st.sidebar:
    st.markdown("### 🌐 Language / 언어")
    language = st.radio(
        "Choose a language / 언어 선택",
        ["English", "한국어"],
        key="app_language",
        horizontal=True,
        label_visibility="collapsed",
    )

# Clear language-dependent app data when switching to avoid mixed-language
# AI suggestions, cached outputs, and the previous language's UI state.
if st.session_state.get("_active_language") != language:
    keep = {"app_language", "_active_language", "app_view", "brain_ai_response", "brain_processed_request"}
    for key in list(st.session_state.keys()):
        if key not in keep:
            del st.session_state[key]
    st.session_state["_active_language"] = language

with st.sidebar:
    view = st.radio(
        "Experience / 화면 선택",
        ["🧠 3D Brain Explorer", "☁️ Original Daydream Circuit"],
        key="app_view",
    )

if view == "🧠 3D Brain Explorer":
    from brain_mode import show_brain
    show_brain(language)
else:
    script = "daydream_en.py" if language == "English" else "daydream_ko.py"
    runpy.run_path(str(Path(__file__).resolve().parent / script), run_name="__main__")
