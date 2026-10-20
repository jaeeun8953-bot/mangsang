"""아이디어 회로: 8–10세를 위한 구름요정과 생각 여행."""
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
st.set_page_config(page_title="아이디어 회로 | 생각이 깨어나는 시간", page_icon="☁️", layout="wide")

MODES = {
    "creative": ("발상회로", "Word Clouds", "☁️", "생각이 퐁퐁!", "단어 하나에서 또 다른 단어로"),
    "logic": ("논리회로", "Connection Bridge", "🌈", "생각이 찌릿!", "서로 다른 두 생각 사이에 다리 놓기"),
    "fusion": ("구체화 회로", "Story Explorer", "📖", "생각이 몽글몽글!", "한 생각에서 장면과 이야기로"),
}
CARDS = [
    ("00_fool.png", "새로운 시작", "낯선 길로 한 걸음 가 볼까?"),
    ("01_magician.png", "마법의 도구", "내가 가진 상상으로 무엇을 만들까?"),
    ("02_high_priestess.png", "비밀", "아직 발견하지 못한 것은 무엇일까?"),
    ("03_empress.png", "자라나는 씨앗", "이 생각이 자라면 어떤 모습일까?"),
    ("04_emperor.png", "멋진 건축가", "내 상상 속 세계에는 어떤 규칙이 있을까?"),
    ("05_hierophant.png", "새로운 배움", "처음 보는 것을 만나면 무엇이 궁금할까?"),
    ("06_lovers.png", "친구", "서로 다른 두 친구가 만나면?"),
    ("07_chariot.png", "모험", "다음에는 어디로 떠나 볼까?"),
    ("08_strength.png", "용기", "조금 더 용기를 낸다면?"),
    ("09_hermit.png", "작은 발견", "조용히 살펴보면 무엇이 보일까?"),
    ("10_wheel_of_fortune.png", "깜짝 변화", "모든 것이 거꾸로 바뀐다면?"),
    ("11_justice.png", "서로 다른 마음", "친구는 이걸 어떻게 생각할까?"),
    ("12_hanged_man.png", "거꾸로 보기", "반대편에서 바라보면?"),
    ("13_death.png", "새로운 모습", "낡은 생각이 새 모습으로 바뀐다면?"),
    ("14_temperance.png", "섞어 보기", "두 가지를 섞으면 무엇이 될까?"),
    ("15_devil.png", "엉뚱한 장난", "말도 안 되는 상상을 해 볼까?"),
    ("16_tower.png", "와르르!", "모든 규칙이 사라지면?"),
    ("17_star.png", "반짝이는 별", "내가 가장 좋아하는 상상은?"),
    ("18_moon.png", "달빛", "밤이 되면 무엇이 달라질까?"),
    ("19_sun.png", "햇살", "이 생각을 환하게 비춰 보면?"),
    ("20_judgement.png", "다시 발견", "처음 생각과 지금 생각은 어떻게 다를까?"),
    ("21_world.png", "넓은 세상", "이 상상을 다른 세상으로 가져가면?"),
]

st.markdown("""<style>
.stApp{background:linear-gradient(150deg,#eef8ff 0%,#fbf5ff 55%,#fff9f1 100%)}
.block-container{max-width:1050px;padding-top:1.3rem}
.hero{text-align:center;padding:10px 12px}.hero h1{font-size:3rem;color:#394f82;margin:.2rem}
.hero p{color:#61769b;font-size:1.14rem}.eyebrow{letter-spacing:.15em;color:#8a9ac1;font-size:.8rem;font-weight:700}
div.stButton>button{border-radius:22px;min-height:3.2rem;white-space:normal;height:auto;padding:12px;border:1px solid #dce5f7;background:#fff;color:#465b86}
div.stButton>button:hover{background:#f3f4ff;border-color:#9e9bdd}
div.stButton>button[kind=primary]{background:#7467c7;color:white;border-color:#7467c7}
.cloud-box{border:1px solid #dce6f7;border-radius:24px;background:#fff;padding:15px;margin:6px 0 16px;text-align:center;color:#4b628d}
.path{background:#fff;border-radius:18px;padding:12px 16px;line-height:2.2;color:#465b86}
.fairy img{max-width:270px;width:100%;display:block;margin:auto;animation:float 3s ease-in-out infinite}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
.small-note{color:#7181a0;font-size:.9rem}.journal{background:#fffaf0;border:1px solid #e7d9bd;padding:20px;border-radius:22px}
</style>""", unsafe_allow_html=True)


def tr(ko, en):
    return ko if st.session_state.lang == "한국어" else en


def clean(value):
    return html.escape(str(value))


def img_uri(path):
    if not path.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def ai(prompt, fallback):
    try:
        key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("No Gemini API key")
        model = st.secrets.get("GEMINI_MODEL") or os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
        result = genai.Client(api_key=key).models.generate_content(model=model, contents=prompt)
        text = (result.text or "").strip()
        if not text:
            raise ValueError("Empty response")
        return text
    except Exception as exc:
        print("AI fallback:", type(exc).__name__)
        st.caption(tr("☁️ 잠깐 구름요정이 준비한 생각을 보여줄게!", "☁️ Here are some ideas from Cloud Fairy!"))
        return fallback


def parse_items(text, count):
    try:
        match = re.search(r"\{.*\}", text, re.S)
        obj = json.loads(match.group() if match else text)
        items = obj.get("options", [])
        items = [str(x).strip() for x in items if isinstance(x, str) and x.strip()]
        if len(items) == count and len(set(items)) == count:
            return items
    except (ValueError, TypeError, AttributeError):
        pass
    return None


def fallbacks(mode):
    if mode == "creative":
        return (["친구", "하늘", "색깔", "모험", "맛", "비밀"] if st.session_state.lang == "한국어" else ["Friend", "Sky", "Color", "Adventure", "Taste", "Secret"])
    if mode == "logic":
        return (["모양이 닮았을까?", "쓰임새가 비슷할까?", "함께 여행한다면?", "서로 도와준다면?"] if st.session_state.lang == "한국어" else ["Similar shapes?", "Similar uses?", "Travel together?", "Help each other?"])
    return (["누가 등장할까?", "어디에서 일어날까?", "어떤 소리가 날까?", "깜짝 사건이 생긴다면?"] if st.session_state.lang == "한국어" else ["Who appears?", "Where is it?", "What sounds?", "A surprise happens?"])


def suggestions():
    ss = st.session_state
    mode = ss.mode
    count = 6 if mode == "creative" else 4
    history = [{"cloud": x["choice"], "own_words": x["own"]} for x in ss.steps[-8:]]
    context = ss.current if mode != "logic" else f"{ss.seed} + {ss.second}"
    instruction = {
        "creative": "Generate SIX DISTINCT SHORT ASSOCIATED WORDS or short noun phrases, NOT questions. Mix direct associations, surprising connections, senses, nature, daily life. Each option max 1-3 Korean words. Follow the current word, not only the first word.",
        "logic": "Generate FOUR distinct short playful CONNECTION HINTS or questions that bridge the TWO original words, based on the child's chosen path. Include analogies, shared features, imaginative relationships. No demands for explanations or correctness.",
        "fusion": "Generate FOUR different playful short scene/story directions from the current thought and the child's earlier selections: character, place, event, sensory detail. Do not write a whole story or ask for a mandatory answer.",
    }[mode]
    prompt = f"""You are Cloud Fairy, a gentle imaginative companion for children aged 8-10. Language: {'Korean' if ss.lang=='한국어' else 'English'}.
Circuit: {mode}. Initial word/thought: {ss.seed!r}. Second word (if any): {ss.get('second','')!r}. Current thought: {context!r}. Path: {json.dumps(history, ensure_ascii=False)}.
{instruction}
Child safety: age-appropriate, warm, no scary/sexual/violent content, no personal information, no grades or tests. Encourage free imagination and agency. Avoid repetition. Return ONLY JSON {{"options":[...]}} with exactly {count} strings."""
    return parse_items(ai(prompt, ""), count) or fallbacks(mode)


def fairy_comment(choice):
    ss = st.session_state
    if ss.mode == "creative":
        fallback = tr(f"'{ss.seed}'에서 시작해 '{choice}'까지 왔네! 다음엔 어디로 갈까?", f"From '{ss.seed}' to '{choice}'! Where next?")
    else:
        fallback = tr("오, 그런 방향도 있구나! 다음 구름에는 뭐가 있을까?", "What a fun direction! What's on the next cloud?")
    prompt = f"""You are a playful, safe cloud fairy talking to an 8-10 year old in {'Korean' if ss.lang=='한국어' else 'English'}. Start: {ss.seed!r}; mode: {ss.mode}; child chose: {choice!r}; child optional words: {ss.get('own_saved','')!r}. React with ONE brief, specific, curious sentence, not a grade, lesson, demand or test. Never ask for personal information. Do not claim the child has written something they haven't."""
    return ai(prompt, fallback)


def reset():
    for k in ["stage", "mode", "seed", "second", "current", "options", "selected", "steps", "own_draft", "own_saved", "comment", "card", "mode_choice", "seed_input", "second_input", "card_note"]:
        st.session_state.pop(k, None)
    st.session_state.stage = "start"
    st.session_state.mode_choice = "creative"


def record_step():
    ss = st.session_state
    ss.steps.append({"choice": ss.selected, "own": ss.get("own_saved", ""), "comment": ss.get("comment", "")})
    ss.current = ss.get("own_saved", "").strip() or ss.selected


def note_text():
    ss = st.session_state
    title = MODES[ss.mode][0] if ss.lang == "한국어" else MODES[ss.mode][1]
    lines = ["# " + tr("나의 상상노트", "My Imagination Journal"), "", f"- {datetime.now():%Y-%m-%d}", f"- {title}", "", tr("## 첫 생각", "## Starting thought"), ss.seed]
    if ss.mode == "logic":
        lines.append(ss.second)
    lines += ["", tr("## 구름을 건넌 길", "## My cloud journey")]
    for i, step in enumerate(ss.steps, 1):
        lines += [f"{i}. {step['choice']}"]
        if step["own"]:
            lines.append(tr("   - 내가 덧붙인 생각: ", "   - My words: ") + step["own"])
    if ss.get("card") is not None:
        card = CARDS[ss.card]
        lines += ["", tr("## 오늘의 상상 카드", "## Today's imagination card"), card[1], card[2]]
    lines += ["", tr("*정답도 점수도 없는 나만의 생각 여행*", "*My journey has no grades or right answers*")]
    return "\n".join(lines)


if "lang" not in st.session_state:
    st.session_state.lang = "한국어"
if "stage" not in st.session_state:
    reset()

with st.sidebar:
    st.markdown("### ☁️ " + tr("아이디어 회로", "Idea Circuit"))
    st.radio("Language / 언어", ["한국어", "English"], key="lang", horizontal=True)
    st.caption(tr("말랑말랑, 생각이 깨어나는 시간!", "Wake up your imagination!"))
    if st.session_state.stage != "start":
        if st.button(tr("🏠 처음으로", "🏠 Home"), use_container_width=True):
            reset()
            st.rerun()
    st.caption(tr("실명, 학교, 주소, 연락처는 적지 않아요. 보호자와 함께 이용해 주세요.", "Do not enter names, school, addresses or contact details. Use with a caregiver."))

st.markdown(f'<div class="hero"><div class="eyebrow">IDEA CIRCUIT · IMAGINATION FRIEND</div><h1>☁️ {tr("아이디어 회로", "Idea Circuit")}</h1><p><b>{tr("말랑말랑, 생각이 깨어나는 시간!", "Wake up your imagination!")}</b></p><p>{tr("구름요정과 함께 생각을 퐁퐁 이어 보자!", "Follow the clouds and see where your thoughts go!")}</p></div>', unsafe_allow_html=True)
if (BASE / "cloud_fairy.png").exists():
    st.markdown(f'<div class="fairy"><img src="{img_uri(BASE / "cloud_fairy.png")}" alt="Cloud Fairy"></div>', unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align:center'>☁️✨</h1>", unsafe_allow_html=True)

ss = st.session_state
if ss.stage == "start":
    st.markdown("### " + tr("오늘은 어떤 생각 여행을 떠날까?", "Which cloud journey today?"))
    cols = st.columns(3)
    for col, (mid, data) in zip(cols, MODES.items()):
        with col:
            st.markdown(f'<div class="cloud-box"><h3>{data[2]} {clean(data[0] if ss.lang=="한국어" else data[1])}</h3><b>{clean(data[3])}</b><p>{clean(data[4])}</p></div>', unsafe_allow_html=True)
            if st.button(tr("✓ 선택했어!" if ss.mode_choice == mid else "이 구름으로!", "✓ Selected" if ss.mode_choice == mid else "Choose"), key=f"choose_{mid}", use_container_width=True):
                ss.mode_choice = mid
                st.rerun()
    mode = ss.mode_choice
    if mode == "logic":
        a, b = st.columns(2)
        with a:
            seed = st.text_input(tr("첫 번째 단어", "First word"), placeholder=tr("예: 고양이", "e.g. Cat"), key="seed_input")
        with b:
            second = st.text_input(tr("두 번째 단어", "Second word"), placeholder=tr("예: 우주", "e.g. Space"), key="second_input")
        ready = bool(seed.strip() and second.strip())
    else:
        seed = st.text_input(tr("첫 생각을 하나만 꺼내 볼까?", "What's your first thought?"), placeholder=tr("예: 밥, 달, 비밀의 문", "e.g. Rice, Moon, Secret door"), key="seed_input")
        second = ""
        ready = bool(seed.strip())
    st.caption(tr("단어 하나여도 괜찮아. 틀린 생각은 없어!", "One word is enough. There are no wrong ideas!"))
    if st.button(tr("☁️ 구름 여행 출발!", "☁️ Let's fly!"), type="primary", disabled=not ready, use_container_width=True):
        ss.mode, ss.seed, ss.second = mode, seed.strip()[:200], second.strip()[:200]
        ss.current = ss.seed
        ss.steps = []
        with st.spinner(tr("구름을 불러오는 중…", "Gathering clouds…")):
            ss.options = suggestions()
        ss.stage = "explore"
        st.rerun()

elif ss.stage in ("explore", "reflect"):
    st.markdown(f"### {MODES[ss.mode][2]} {MODES[ss.mode][0] if ss.lang == '한국어' else MODES[ss.mode][1]}")
    origin = ss.seed + (" + " + ss.second if ss.mode == "logic" else "")
    path = " → ".join([origin] + [x["choice"] for x in ss.steps])
    st.markdown(f'<div class="path">☁️ {clean(path)}</div>', unsafe_allow_html=True)
    if ss.stage == "explore":
        st.markdown("#### " + tr("어떤 구름이 끌려?", "Which cloud catches your eye?"))
        st.caption(tr("골라 보기만 해도 돼! 직접 떠오른 생각을 적어도 좋아.", "Just choose a cloud, or add your own thought!"))
        cols = st.columns(3 if ss.mode == "creative" else 2)
        for i, option in enumerate(ss.options):
            with cols[i % len(cols)]:
                if st.button(f"☁️ {option}", key=f"option_{len(ss.steps)}_{i}", use_container_width=True):
                    ss.selected = option
                    ss.own_saved = ""
                    ss.stage = "reflect"
                    st.rerun()
        if ss.steps and st.button(tr("📖 여기서 상상노트 보기", "📖 Open imagination journal"), use_container_width=True):
            ss.stage = "journal"
            st.rerun()
    else:
        st.markdown(f'<div class="cloud-box"><h3>☁️ {clean(ss.selected)}</h3></div>', unsafe_allow_html=True)
        st.caption(tr("이 구름에서 또 다른 생각이 떠올랐니? 안 적어도 괜찮아!", "Any new thought? It's okay to leave this blank!"))
        st.text_input(tr("내가 만든 구름 (선택)", "My own cloud (optional)"), key=f"own_draft_{len(ss.steps)}", placeholder=tr("나만의 단어나 짧은 생각", "My own word or thought"))
        if st.button(tr("✨ 다음 구름으로 폴짝!", "✨ Hop to the next cloud!"), type="primary", use_container_width=True):
            ss.own_saved = ss.get(f"own_draft_{len(ss.steps)}", "").strip()[:300]
            record_step()
            with st.spinner(tr("새 구름을 만드는 중…", "Making new clouds…")):
                ss.options = suggestions()
            ss.stage = "explore"
            st.rerun()
        if st.button(tr("📖 이 구름에서 여행 마치기", "📖 Finish here"), use_container_width=True):
            ss.own_saved = ss.get(f"own_draft_{len(ss.steps)}", "").strip()[:300]
            record_step()
            ss.stage = "journal"
            st.rerun()
        if st.button(tr("← 다른 구름 고르기", "← Choose another cloud")):
            ss.stage = "explore"
            st.rerun()

elif ss.stage == "journal":
    st.markdown("## 📖 " + tr("나의 상상노트", "My Imagination Journal"))
    st.caption(tr("내 생각이 어디까지 여행했는지 살펴보자!", "Look how far your thoughts have traveled!"))
    st.markdown(f'<div class="journal"><h3>🌱 {tr("첫 생각", "Starting thought")}</h3><p>{clean(ss.seed + (" + " + ss.second if ss.mode == "logic" else ""))}</p></div>', unsafe_allow_html=True)
    if not ss.steps:
        st.info(tr("아직 건넌 구름이 없어. 하나를 골라 보자!", "No clouds crossed yet!"))
    else:
        st.markdown("### ☁️ " + tr("내가 건넌 구름", "Clouds I crossed"))
        for i, step in enumerate(ss.steps, 1):
            st.markdown(f"**{i}. ☁️ {step['choice']}**")
            if step["own"]:
                st.write(tr("내가 덧붙인 생각: ", "My words: ") + step["own"])
    st.markdown("### 🃏 " + tr("오늘의 상상 카드", "Today's imagination card"))
    st.caption(tr("운세가 아니라 다음 상상을 떠올리게 해 주는 카드야.", "A card to spark imagination, not a prediction."))
    if ss.get("card") is None:
        if st.button(tr("✨ 상상 카드 한 장 뽑기", "✨ Pick an imagination card"), use_container_width=True):
            ss.card = random.randrange(len(CARDS))
            st.rerun()
    else:
        filename, name, question = CARDS[ss.card]
        left, right = st.columns([1, 2])
        with left:
            if (BASE / filename).exists():
                st.image(str(BASE / filename), use_container_width=True)
            else:
                st.markdown("### 🃏")
        with right:
            st.markdown(f"**{name}**")
            st.write(question)
            st.caption(tr("카드 그림은 상상을 위한 그림이야.", "This picture is for imagination."))
    st.download_button(tr("📥 상상노트 저장하기", "📥 Save imagination journal"), note_text(), file_name=f"idea_circuit_{datetime.now():%Y%m%d}.md", mime="text/markdown", use_container_width=True)
    if st.button(tr("☁️ 새로운 여행 떠나기", "☁️ Start another journey"), type="primary", use_container_width=True):
        reset()
        st.rerun()
