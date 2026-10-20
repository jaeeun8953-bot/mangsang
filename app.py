"""아이디어 회로 — original cloud fairy, guided idea development, and reflective tarot."""
import base64
import html
import json
import os
import random
import re
from datetime import datetime
from pathlib import Path

import streamlit as st
from google import genai

BASE = Path(__file__).resolve().parent
st.set_page_config(page_title="아이디어 회로 | Idea Circuit", page_icon="☁️", layout="wide")

MODES = {
    "logic": {"ko": "논리회로", "en": "Logic Circuit", "emoji": "🔍", "ko_desc": "아이디어는 있지만 설득력이 부족해요 · 필요성과 근거를 탄탄하게", "en_desc": "I have an idea, but need stronger reasons and evidence"},
    "creative": {"ko": "발상회로", "en": "Ideation Circuit", "emoji": "✨", "ko_desc": "아직 아이디어가 막연해요 · 새로운 가능성을 발견하기", "en_desc": "My idea is still vague; help me discover possibilities"},
    "fusion": {"ko": "구체화 회로", "en": "Development Circuit", "emoji": "🧩", "ko_desc": "방향과 근거는 있지만 실행 방법이 막막해요", "en_desc": "I know the direction but need an actionable plan"},
}
CARDS = [
    ("00_fool.png", "The Fool", "바보", "새로운 시작과 열린 가능성"),
    ("01_magician.png", "The Magician", "마법사", "자원과 실행의 힘"),
    ("02_high_priestess.png", "The High Priestess", "여사제", "직관과 내면의 질문"),
    ("03_empress.png", "The Empress", "여황제", "성장과 돌봄"),
    ("04_emperor.png", "The Emperor", "황제", "구조와 책임"),
    ("05_hierophant.png", "The Hierophant", "교황", "배움과 관습"),
    ("06_lovers.png", "The Lovers", "연인", "가치와 선택"),
    ("07_chariot.png", "The Chariot", "전차", "방향과 추진력"),
    ("08_strength.png", "Strength", "힘", "용기와 인내"),
    ("09_hermit.png", "The Hermit", "은둔자", "성찰과 탐색"),
    ("10_wheel_of_fortune.png", "Wheel of Fortune", "운명의 수레바퀴", "변화와 기회"),
    ("11_justice.png", "Justice", "정의", "균형과 근거"),
    ("12_hanged_man.png", "The Hanged Man", "매달린 사람", "관점의 전환"),
    ("13_death.png", "Death", "죽음", "끝과 새로운 시작"),
    ("14_temperance.png", "Temperance", "절제", "조화와 통합"),
    ("15_devil.png", "The Devil", "악마", "고정관념과 집착"),
    ("16_tower.png", "The Tower", "탑", "기존 가정의 재검토"),
    ("17_star.png", "The Star", "별", "희망과 영감"),
    ("18_moon.png", "The Moon", "달", "불확실성과 상상"),
    ("19_sun.png", "The Sun", "태양", "명료함과 활력"),
    ("20_judgement.png", "Judgement", "심판", "되돌아봄과 새 판단"),
    ("21_world.png", "The World", "세계", "완성과 연결"),
]

IDEATION_LENSES = [
    ("관점 바꾸기", "Shift perspective"), ("반대로 생각하기", "Reverse assumptions"),
    ("이질적 연결", "Unexpected connections"), ("제약 없애기", "Remove constraints"),
    ("상황 바꾸기", "Change the setting"), ("문제 재정의", "Reframe the problem"),
]

CSS = """
<style>
.stApp {background: linear-gradient(155deg,#f4f8ff 0%,#f9f5ff 52%,#fdf8f3 100%);}
.block-container {max-width:1080px;padding-top:2rem;}
.hero {text-align:center;padding:22px 14px 12px;}
.hero h1 {font-size:3.25rem;color:#38456f;margin:5px 0 0;letter-spacing:-.04em;}
.hero-eyebrow {font-size:.82rem;letter-spacing:.14em;color:#7987ad;font-weight:700;}
.hero .hero-tagline {font-size:1.48rem;font-weight:750;color:#425987;margin:12px 0 6px;}
.hero .hero-subtitle {font-size:1.02rem;color:#727b9a;margin:4px 0 10px;}
.hero p {color:#727b9a;font-size:1.08rem;margin:8px 0;}
.cloud-label {background:white;border:1px solid #e2e7fa;border-radius:25px;padding:14px 20px;box-shadow:0 10px 30px #9ca8d526;text-align:center;margin:8px 0 18px;color:#505d86;}
.step-line {display:flex;justify-content:center;align-items:center;gap:10px;margin:12px auto;flex-wrap:wrap;}
.step-cloud {padding:9px 15px;border-radius:30px;background:#fff;box-shadow:0 5px 16px #a8b6d73a;color:#53618c;font-size:.87rem;}
.step-arrow {color:#a6add1;}
section[data-testid="stSidebar"] {background:#f4f3fd;}
div.stButton > button {border-radius:18px;min-height:3rem;border:1px solid #d8dff5;background:white;color:#45517d;white-space:normal;height:auto;padding:12px 14px;}
div.stButton > button:hover {border-color:#a58bda;color:#6853a6;background:#f9f5ff;}
div.stButton > button[kind="primary"] {background:#7465c8;color:white;border-color:#7465c8;}
@keyframes cloudHop {0%{transform:translateY(0) scale(1)}35%{transform:translateY(-18px) scale(1.035)}70%{transform:translateY(-4px)}100%{transform:translateY(0)}}
.fairy-hop img {animation:cloudHop 1.1s ease-in-out;}
.journal {background:#fffaf0;border:1px solid #e9dbc2;border-radius:22px;padding:24px;color:#574d45;}
.journal h2 {color:#63513f;margin-top:0;}
.journal .thought {padding:10px 0;border-bottom:1px solid #e7dccd;}
.journal .note {font-size:.9rem;color:#806c5c;}
.mode-selected {border:2px solid #a894ed!important;background:#f3efff!important;}
.cloud-kicker {font-size:.84rem;color:#7d72aa;font-weight:700;margin-bottom:5px;}
.idea-journey {background:#fff;border:1px solid #e2e7fa;border-radius:18px;padding:14px 18px;margin-bottom:16px;}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def tr(ko, en):
    return ko if st.session_state.lang == "한국어" else en

def esc(s):
    return html.escape(str(s))

def img_uri(path):
    if not path.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()

def ask_ai(task, fallback):
    """Use existing Streamlit secret, but don't expose it in logs or UI."""
    try:
        key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY is not configured")
        model = st.secrets.get("GEMINI_MODEL") or os.getenv("GEMINI_MODEL") or "gemini-3.8-flash"
        client = genai.Client(api_key=key)
        result = client.models.generate_content(model=model, contents=task)
        value = (result.text or "").strip()
        if not value:
            raise ValueError("Empty AI response")
        return value
    except Exception as e:
        # Avoid leaking secrets or raw prompts in user-visible exceptions.
        st.warning(tr("AI 연결이 원활하지 않아 임시 내용을 보여줘요. 모델 설정을 확인해 주세요.", "AI is temporarily unavailable. Showing a fallback; please check model settings."))
        print("Gemini generation error type:", type(e).__name__)
        return fallback

def parse_suggestions(raw):
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.I)
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            data = data.get("options", [])
        if isinstance(data, list):
            out = [str(x.get("text", x.get("question", "")) if isinstance(x, dict) else x).strip() for x in data]
            out = [x for x in out if x]
            if len(out) == 6 and len(set(out)) == 6:
                return out
    except (ValueError, TypeError):
        pass
    return None

def make_options():
    mode = st.session_state.mode
    lang = "Korean" if st.session_state.lang == "한국어" else "English"
    mode_instruction = {
        "logic": "Generate analytical, causal, evidence-seeking, counterargument or reasoning questions. Avoid leading questions.",
        "creative": "Use these SIX DIFFERENT ideation lenses IN THIS EXACT ORDER: (1) shift perspective (2) reverse a common assumption (3) connect with a distant domain (4) remove a constraint (5) change situation or context (6) reframe the underlying problem. Each lens must produce exactly one concrete question anchored to the user's current thought. Do not provide answers or completed ideas. Avoid repeating prior paths. Adapt every question to the user's latest own answer.",
        "fusion": "Each option should help DEVELOP the user’s idea: clarify its purpose, identify who benefits, consider constraints, test assumptions, design feasible steps, or improve the concept. Offer six different development directions, not six answers.",
    }[mode]
    history = [{"question":x["question"], "user_thought":x["answer"]} for x in st.session_state.steps]
    prompt = f"""You are a supportive thinking-training coach, not an answer machine.
Language: {lang}. Original thought: {st.session_state.seed!r}
Selected thinking circuit: {mode}. Rule: {mode_instruction}
User's prior thought journey: {json.dumps(history, ensure_ascii=False)}
Produce EXACTLY SIX distinct, open-ended, concise thought prompts that naturally extend the latest user's OWN thought and accumulated context. These are six alternative directions, not a quiz and not six answers. Never repeat previous questions. Avoid vague generic prompts.
Return ONLY valid JSON: {{"options":["question 1", "question 2", "question 3", "question 4", "question 5", "question 6"]}}"""
    raw = ask_ai(prompt, "")
    options = parse_suggestions(raw)
    if options:
        return options
    if mode == "creative":
        return (["이 생각을 전혀 다른 사람이 바라본다면 어떤 기회가 보일까?", "지금 당연하다고 여기는 규칙을 거꾸로 바꾸면?", "이 생각을 게임이나 예술 같은 다른 분야와 결합하면?", "비용과 시간의 제약이 사라지면 어떤 모습일까?", "이 아이디어를 완전히 다른 장소나 상황에 적용하면?", "우리가 정말 해결하려는 문제를 다시 정의하면?"] if st.session_state.lang == "한국어" else ["How would someone very different see this opportunity?", "What if you reversed a basic assumption?", "What happens when you connect this with games or art?", "What if time and budget constraints vanished?", "What changes in an entirely different context?", "What is the deeper problem worth solving?"])
    if mode == "fusion":
        return (["누가 가장 먼저 이 아이디어를 필요로 할까?", "사용자가 경험할 핵심 변화는 무엇일까?", "가장 작은 핵심 기능 하나만 만든다면?", "현실적으로 필요한 자원과 제약은 무엇일까?", "실제로 작동하는지 어떻게 시험할까?", "이번 주에 할 수 있는 첫 단계는 무엇일까?"] if st.session_state.lang == "한국어" else ["Who needs this first?", "What should change for the user?", "What is the smallest essential feature?", "What resources and constraints matter?", "How can you test the idea?", "What is the first step this week?"])
    return (["그렇게 생각하게 된 가장 중요한 이유는 무엇일까?", "반대되는 사례를 찾는다면 무엇이 있을까?", "숨겨진 전제는 무엇일까?", "다른 사람은 이 상황을 어떻게 볼까?", "어떤 정보가 있으면 판단이 달라질까?", "이 생각의 다음 결과는 무엇일까?"] if st.session_state.lang == "한국어" else ["What is the strongest reason for this?", "What might be a counterexample?", "What assumption is hidden here?", "How might someone else see this?", "What evidence could change your mind?", "What follows from this idea?"])

def coach_for(question, answer):
    mode = st.session_state.mode
    lang = "Korean" if st.session_state.lang == "한국어" else "English"
    prompt = f"""You are a friendly AI thinking coach. Respond in {lang} to the USER'S OWN thinking, without grading, flattery or telling them what to believe. Selected mode: {mode}. Original thought: {st.session_state.seed!r}. Selected question: {question!r}. User's answer: {answer!r}. Give (1) one concrete observation of the reasoning or new perspective the user introduced, and (2) ONE short, meaningful follow-up question that stretches their thinking. 2-3 short sentences total. No markdown headings. For logic: examine assumptions/evidence; creative: point out the user’s original connection and ask one divergent question without giving a ready-made idea; fusion: connect imagination to a practical first step."""
    return ask_ai(prompt, tr("이 생각의 근거를 한 번 더 살펴보거나, 다른 관점에서 질문해 보면 어떨까?", "What if you examined the reasoning or tried another perspective?"))

def reset():
    for k in ["stage", "mode", "seed", "options", "selected", "steps", "answer_draft", "answer_saved", "coach", "tarot", "tarot_advice", "journey_date", "idea_title", "idea_connection", "idea_next", "mode_choice", "starting_thought"]:
        st.session_state.pop(k, None)
    st.session_state.stage = "start"

def markdown_journal():
    ss = st.session_state
    label = MODES[ss.mode]["ko"] if ss.lang == "한국어" else MODES[ss.mode]["en"]
    journal_name = "아이디어 발상노트 / Ideation Journal" if ss.mode == "creative" else ("아이디어 검증노트 / Logic Journal" if ss.mode == "logic" else "아이디어 실행노트 / Development Journal")
    lines = [f"# {journal_name}", "", f"- Date: {ss.journey_date}", f"- Circuit: {label}", "", "## 처음 생각 / My starting thought", ss.seed]
    if ss.mode == "creative":
        lines += ["", "## 내가 발견한 아이디어 / My developed idea", ss.get("idea_title", ""), "", "## 가장 흥미로웠던 연결 / Favorite connection", ss.get("idea_connection", ""), "", "## 다음에 발전시킬 질문 / Next question", ss.get("idea_next", "")]
    else:
        lines += ["", "## 핵심 정리 / My takeaway", ss.get("idea_title", ""), "", "## 배운 점 / Key insight", ss.get("idea_connection", ""), "", "## 다음 단계 / Next step", ss.get("idea_next", "")]
    lines += ["", "## 생각의 길 / My thought journey"]
    for i, step in enumerate(ss.steps, 1):
        lines += ["", f"### {i}. {step['question']}", f"**My thought:** {step['answer']}", f"**AI coach:** {step['coach']}"]
    if ss.get("tarot") is not None:
        card = CARDS[ss.tarot]
        lines += ["", "## 오늘의 성찰 카드 / Reflection tarot", f"**{card[1]} / {card[2]}** — {card[3]}", "", ss.get("tarot_advice", "")]
    lines += ["", "---", "*Tarot is used as a reflective prompt, not a prediction.*"]
    return "\n".join(lines)

if "lang" not in st.session_state:
    st.session_state.lang = "한국어"
if "stage" not in st.session_state:
    reset()
if "answer_draft" not in st.session_state:
    st.session_state.answer_draft = ""
if "answer_saved" not in st.session_state:
    st.session_state.answer_saved = ""

with st.sidebar:
    st.markdown("### ✨ 아이디어 회로")
    st.radio("Language / 언어", ["한국어", "English"], key="lang", horizontal=True)
    st.caption(tr("작은 생각을 탄탄한 아이디어로", "Grow a spark of thought into a strong idea"))
    if st.session_state.stage != "start":
        st.info(tr("회로는 탐험을 시작한 후 고정돼요.", "Your circuit stays fixed during this journey."))
        if st.button(tr("새로운 여행 시작", "Start a new journey"), use_container_width=True):
            reset()
            st.rerun()

st.markdown(f'<div class="hero"><div class="hero-eyebrow">IDEA CIRCUIT · AI IDEA COACH</div><h1>✨ {tr("아이디어 회로", "Idea Circuit")}</h1><p class="hero-tagline">{tr("작은 생각의 불씨를, 탄탄한 아이디어로.", "From a small spark of thought to a stronger idea.")}</p><p class="hero-subtitle">{tr("내 생각에서 출발해 질문하고, 상상하고, 구체화하는 AI 아이디어 코치", "An AI idea coach to question, imagine, and develop ideas starting from your own thoughts.")}</p></div>', unsafe_allow_html=True)
# Show the ORIGINAL character prominently at the top, including before selecting a mode.
if (BASE / "cloud_fairy.png").exists():
    _, hero_character, _ = st.columns([1.1, 1, 1.1])
    with hero_character:
        st.image(str(BASE / "cloud_fairy.png"), use_container_width=True)


if st.session_state.stage == "start":
    st.markdown(f"### {tr('지금 내 아이디어는 어떤 상태인가요?', 'Where is your idea right now?')}")
    st.caption(tr("현재 가장 도움이 필요한 단계를 선택해 주세요. 발상회로가 기본으로 선택되어 있어요.", "Choose the stage where you need the most help. Ideation is selected by default."))
    cols = st.columns(3)
    if "mode_choice" not in st.session_state:
        st.session_state.mode_choice = "creative"
    for col, (mid, info) in zip(cols, MODES.items()):
        with col:
            selected = st.session_state.mode_choice == mid
            st.markdown(f"<div class='cloud-label'>{info['emoji']} <b>{info['ko'] if st.session_state.lang == '한국어' else info['en']}</b><br><small>{info['ko_desc'] if st.session_state.lang == '한국어' else info['en_desc']}</small></div>", unsafe_allow_html=True)
            if st.button(("✓ " if selected else "☁️ ") + tr("선택됨" if selected else "선택하기", "Selected" if selected else "Choose"), key=f"choose_{mid}", use_container_width=True):
                st.session_state.mode_choice = mid
                st.rerun()
    if st.session_state.mode_choice == "creative":
        st.info(tr("💡 발상회로에서는 관점 전환·반대 발상·이질적 연결 등 6가지 방향을 따라 생각을 직접 키워요. AI는 정답 대신 질문을 건네요.", "💡 Ideation explores six different creative lenses. You build the idea; AI guides with questions, not answers."))
    st.markdown(f"### {tr('나의 첫 생각', 'My first thought')}")
    thought = st.text_area(tr("아이디어의 출발점이 될 작은 생각을 적어 줘", "Write a small thought to grow into an idea"), placeholder=tr("예: 사람들이 책을 더 재미있게 읽을 방법이 없을까?", "e.g. How might we make reading more engaging?"), height=110, key="starting_thought")
    if st.button(tr("☁️ 아이디어 키우기 시작", "☁️ Start developing my idea"), type="primary", use_container_width=True, disabled=not thought.strip()):
        st.session_state.seed = thought.strip()
        st.session_state.mode = st.session_state.mode_choice
        st.session_state.steps = []
        st.session_state.journey_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        with st.spinner(tr("여섯 개의 구름을 만들고 있어요…", "Creating six clouds…")):
            st.session_state.options = make_options()
        st.session_state.stage = "explore"
        st.rerun()

elif st.session_state.stage in ("explore", "write", "feedback"):
    mode_info = MODES[st.session_state.mode]
    st.caption(f"{mode_info['emoji']} {mode_info['ko'] if st.session_state.lang == '한국어' else mode_info['en']} · {tr('완료한 구름', 'Clouds crossed')}: {len(st.session_state.steps)}")
    st.markdown(f"<div class='cloud-label'>☁️ <b>{esc(st.session_state.seed)}</b></div>", unsafe_allow_html=True)
    if st.session_state.steps:
        nodes = [tr("시작", "Start")] + [f"☁️ {i}" for i in range(1, len(st.session_state.steps)+1)]
        st.markdown('<div class="step-line">' + '<span class="step-arrow">➜</span>'.join(f'<span class="step-cloud">{esc(x)}</span>' for x in nodes) + '</div>', unsafe_allow_html=True)
    left, center, right = st.columns([1, 2, 1])
    with center:
        st.markdown(f'<div class="fairy-hop"><img src="{img_uri(BASE / "cloud_fairy.png")}" alt="Cloud Fairy" style="width:100%;max-width:370px;border-radius:22px;display:block;margin:auto;"></div>', unsafe_allow_html=True)
    if st.session_state.stage == "explore":
        st.markdown(f"### {tr('다음에는 어느 구름으로 건너갈까?', 'Which cloud will you step onto next?')}")
        st.caption(tr("6개의 구름 중 하나를 골라 내 생각을 펼쳐 봐.", "Choose one of six clouds to develop your own thought."))
        columns = st.columns(2)
        for i, question in enumerate(st.session_state.options):
            with columns[i % 2]:
                if st.session_state.mode == "creative":
                    lens = IDEATION_LENSES[i]
                    st.markdown(f"<div class='cloud-kicker'>☁️ {esc(lens[0] if st.session_state.lang == '한국어' else lens[1])}</div>", unsafe_allow_html=True)
                if st.button(f"☁️ {i+1}. {question}", key=f"cloud_{len(st.session_state.steps)}_{i}", use_container_width=True):
                    st.session_state.selected = question
                    st.session_state.answer_draft = ""
                    st.session_state.answer_saved = ""
                    st.session_state.stage = "write"
                    st.rerun()
        if st.session_state.steps and st.button(tr("📖 여기서 탐험 마치고 노트 만들기", "📖 Finish and create my journal"), type="primary", use_container_width=True):
            st.session_state.stage = "journal"
            st.rerun()
    elif st.session_state.stage == "write":
        st.markdown(f"### ☁️ {st.session_state.selected}")
        st.caption(tr("정답은 없어. 내 생각을 직접 적어 보자.", "There's no single right answer. Write what you think."))
        answer = st.text_area(tr("나의 생각", "My thinking"), key="answer_draft", height=160)
        if st.button(tr("✨ 내 생각 완성하고 AI 코칭 받기", "✨ Finish my thought and get coaching"), disabled=not answer.strip(), type="primary", use_container_width=True):
            with st.spinner(tr("AI 코치가 내 생각을 읽고 있어요…", "Your AI coach is reading your thought…")):
                st.session_state.answer_saved = answer.strip()
                st.session_state.coach = coach_for(st.session_state.selected, answer.strip())
            st.session_state.stage = "feedback"
            st.rerun()
        if st.button(tr("← 다른 구름 고르기", "← Choose another cloud")):
            st.session_state.stage = "explore"
            st.rerun()
    else:
        st.markdown(f"### {tr('내 생각', 'My thought')}")
        st.write(st.session_state.get("answer_saved", ""))
        st.markdown(f"### ✨ {tr('AI 코치의 질문', 'Your AI coach')}")
        st.info(st.session_state.coach)
        st.caption(tr("코칭은 정답이나 능력 점수가 아니라, 생각을 확장하기 위한 질문이야.", "Coaching offers prompts to reflect, not grades or ability scores."))
        if st.button(tr("☁️ 다음 구름으로 점프하기", "☁️ Jump to the next cloud"), type="primary", use_container_width=True):
            st.session_state.steps.append({"question": st.session_state.selected, "answer": st.session_state.get("answer_saved", ""), "coach": st.session_state.coach})
            with st.spinner(tr("다음 생각의 구름을 만들고 있어요…", "Creating your next thought clouds…")):
                st.session_state.options = make_options()
            st.session_state.stage = "explore"
            st.rerun()
        if st.button(tr("📖 여기서 마치고 생각노트 만들기", "📖 Finish and make my journal"), use_container_width=True):
            st.session_state.steps.append({"question": st.session_state.selected, "answer": st.session_state.get("answer_saved", ""), "coach": st.session_state.coach})
            st.session_state.stage = "journal"
            st.rerun()

elif st.session_state.stage == "journal":
    notebook_title = (tr("나의 아이디어 발상노트", "My Ideation Journal") if st.session_state.mode == "creative" else (tr("나의 아이디어 검증노트", "My Logic Journal") if st.session_state.mode == "logic" else tr("나의 아이디어 실행노트", "My Development Journal")))
    st.markdown(f"## 📖 {notebook_title}")
    st.caption(st.session_state.journey_date)
    st.markdown(f"<div class='journal'><h2>{tr('나의 첫 생각', 'My first thought')}</h2><p>{esc(st.session_state.seed)}</p></div>", unsafe_allow_html=True)
    st.markdown(f"### {tr('내가 걸어온 생각의 길', 'My thought journey')}")
    for i, step in enumerate(st.session_state.steps, 1):
        with st.expander(f"☁️ {i}. {step['question']}", expanded=True):
            st.markdown(f"**{tr('내 생각', 'My thought')}**")
            st.write(step["answer"])
            st.markdown(f"**✨ {tr('AI 코치', 'AI coach')}**")
            st.write(step["coach"])
    st.markdown(f"### {tr('오늘 발전시킨 아이디어 정리', 'Capture your developed idea')}")
    if st.session_state.mode == "creative":
        st.text_input(tr("오늘 발견한 아이디어 한 문장", "My idea in one sentence"), key="idea_title", placeholder=tr("예: 독서와 게임을 결합한 인터랙티브 리딩 서비스", "e.g. Interactive reading meets game progression"))
        st.text_area(tr("가장 흥미로웠던 새로운 연결", "My most interesting new connection"), key="idea_connection", height=90)
        st.text_area(tr("다음에 더 발전시키고 싶은 질문", "Question to explore next"), key="idea_next", height=90)
    else:
        st.text_input(tr("오늘 정리한 핵심 아이디어", "My key idea"), key="idea_title")
        st.text_area(tr("이번 탐험에서 발견한 점", "What I discovered"), key="idea_connection", height=90)
        st.text_area(tr("다음에 확인하거나 실행할 것", "What to test or do next"), key="idea_next", height=90)
    st.caption(tr("위 내용은 직접 작성한 생각으로 기록돼요. AI의 질문과 코칭은 아래 탐험 기록에 따로 남겨요.", "These are your own words. AI questions and coaching are stored separately below."))
    st.markdown(f"### 🔮 {tr('오늘의 생각에 붙일 타로카드', 'A tarot card for today’s thought')}")
    st.caption(tr("미래 예측이 아닌, 오늘의 생각을 다른 시선으로 돌아보는 성찰 카드야.", "A reflection prompt, not a prediction of the future."))
    if st.session_state.get("tarot") is None:
        st.markdown(tr("마음속으로 카드를 한 장 골라 봐.", "Pick a card that speaks to you."))
        cols = st.columns(3)
        for i, col in enumerate(cols):
            with col:
                if st.button(f"🃏 {tr('카드', 'Card')} {i+1}", key=f"tarot_pick_{i}", use_container_width=True):
                    # Pick a random card after the user chooses a face-down card.
                    st.session_state.tarot = random.randrange(len(CARDS))
                    card = CARDS[st.session_state.tarot]
                    context = [{"question": x["question"], "user_thought": x["answer"]} for x in st.session_state.steps]
                    prompt = f"""Write in {'Korean' if st.session_state.lang == '한국어' else 'English'}. You are a gentle reflection coach. The user started with {st.session_state.seed!r} and explored {json.dumps(context, ensure_ascii=False)}. They drew the tarot card {card[1]} (symbolic theme: {card[3]}). Write a personalized reflection of 3-4 sentences that connects the SYMBOLISM to one specific thread of the user's own thinking, plus one open-ended question for next time. Do not predict events, claim supernatural certainty, or grade the user."""
                    with st.spinner(tr("생각에 어울리는 조언을 적고 있어요…", "Writing a reflection for your journal…")):
                        st.session_state.tarot_advice = ask_ai(prompt, tr(f"{card[3]}의 의미를 오늘의 생각에 비춰 보면 어떨까? 다음에는 어떤 관점을 더 살펴보고 싶어?", f"How might the theme of {card[1]} help you reflect on today's thought?"))
                    st.rerun()
    else:
        card = CARDS[st.session_state.tarot]
        col_img, col_text = st.columns([1, 2])
        with col_img:
            if (BASE / card[0]).exists():
                st.image(str(BASE / card[0]), use_container_width=True)
            else:
                st.caption(card[1])
        with col_text:
            st.markdown(f"### {card[1]} · {card[2]}")
            st.caption(card[3])
            st.write(st.session_state.tarot_advice)
            st.success(tr("타로카드와 조언을 생각노트에 붙였어!", "The tarot card and reflection have been added to your journal!"))
    st.download_button(tr("📥 나의 생각노트 다운로드 (.md)", "📥 Download my journal (.md)"), data=markdown_journal(), file_name=f"idea_circuit_journal_{datetime.now():%Y%m%d}.md", mime="text/markdown", use_container_width=True)
    if st.button(tr("☁️ 새로운 생각으로 다시 시작하기", "☁️ Begin a new thought journey"), use_container_width=True):
        reset()
        st.rerun()
