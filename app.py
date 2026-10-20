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


def logic_fallbacks(first, second, current, history, count=4):
    """Always relate both input words; extend the chosen bridge on later hops."""
    a, b = first.strip(), second.strip()
    used = {x.get("choice", "").casefold() for x in history}
    if {a, b} == {"바다", "호랑이"}:
        base = ["바닷속 호랑이", "호랑이 무늬 파도", "호랑이가 사는 섬", "호랑이처럼 줄무늬가 있는 물고기", "바다를 지키는 호랑이", "호랑이 발자국 모양 조개"]
        if history:
            base = [f"{current}의 비밀", f"{current}가 움직이는 모습", f"{current}와 만나는 친구", f"{current}에서 벌어지는 모험", f"{current}의 숨겨진 장소", f"{current}의 새로운 모습"]
    else:
        if st.session_state.lang == "한국어":
            base = ([f"{a}를 만난 {b}", f"{b}처럼 생긴 {a}", f"{a} 속에 숨은 {b}", f"{a}와 {b}의 비밀 장소", f"{a}와 {b}가 함께 하는 모험", f"{a}에서 발견한 {b}"] if not history else [f"{current}의 숨은 비밀", f"{current}가 사는 곳", f"{current}의 새로운 친구", f"{current}의 특별한 능력", f"{current}가 달라진 모습", f"{current}의 다음 모험"])
        else:
            base = ([f"{b} meets {a}", f"{a} shaped like {b}", f"{b} hidden inside {a}", f"Secret place of {a} and {b}", f"Adventure of {a} and {b}"] if not history else [f"Secret of {current}", f"Where {current} lives", f"A friend for {current}", f"A new power for {current}", f"What happens to {current} next"])
    result = [x for x in base if x.casefold() not in used and x.casefold() != current.casefold()]
    n = 1
    while len(result) < count:
        candidate = f"{current}의 상상 가지 {n}" if st.session_state.lang == "한국어" else f"{current} branch {n}"
        if candidate.casefold() not in used:
            result.append(candidate)
        n += 1
    return result[:count]


def logic_map():
    """Visible connection mind map: original pair, selected bridge, next branches."""
    ss = st.session_state
    a, b = clean(ss.seed), clean(ss.second)
    st.markdown("### " + tr("🌈 두 생각의 연결 마인드맵", "🌈 Connection mind map"))
    st.markdown(f"""<div style='display:flex;justify-content:center;align-items:center;gap:12px;flex-wrap:wrap;margin:15px 0'>
    <div style='padding:16px 26px;border-radius:35px;background:#e0f3ff;border:2px solid #9acbed;font-weight:700;color:#29577a'>🌊 {a}</div>
    <div style='font-size:24px;color:#8995c5'>＋</div>
    <div style='padding:16px 26px;border-radius:35px;background:#fff0da;border:2px solid #eac493;font-weight:700;color:#7c5832'>🐯 {b}</div></div>""", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;color:#9ca4c8;font-size:24px'>↓</div>", unsafe_allow_html=True)
    if ss.steps:
        for idx, step in enumerate(ss.steps):
            word = clean(step.get('own') or step['choice'])
            st.markdown(f"<div style='text-align:center;margin:5px auto;padding:12px;border-radius:25px;background:#f0e9ff;color:#604e89;max-width:520px'>☁️ {word}</div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align:center;color:#9ca4c8;font-size:20px'>↓</div>", unsafe_allow_html=True)
    st.caption(tr("아래 구름들은 두 단어를 연결해 뻗어 나온 가지야. 마음에 드는 가지를 골라 봐!", "These branches connect your two words. Choose one to explore!"))


def fresh_fallbacks(mode, current, history, count):
    """Context-sensitive offline clouds, never the same six generic labels."""
    import hashlib
    root = (current or "상상").strip()
    used = {str(x.get("choice", "")).strip().casefold() for x in history}
    used.add(root.casefold())
    ko = st.session_state.lang == "한국어"
    if mode == "creative":
        # Common child-friendly associations for recognizable words.
        banks = {
            "밥": ["쌀", "콩밥", "도시락", "주걱", "급식", "밥솥", "반찬", "논"],
            "콩밥": ["콩", "쌀", "도시락", "밥그릇", "농부", "콩밭", "숟가락"],
            "콩": ["콩나무", "콩밭", "두부", "새싹", "씨앗", "농부", "꼬투리", "비"],
            "콩나무": ["하늘", "거인", "구름", "사다리", "잎사귀", "성", "바람"],
            "하늘": ["구름", "비행기", "무지개", "새", "별", "바람", "노을"],
            "달": ["토끼", "우주", "별", "밤", "우주선", "달빛", "분화구"],
            "고양이": ["수염", "발바닥", "생선", "꼬리", "골골송", "호랑이", "상자"],
            "비": ["우산", "웅덩이", "무지개", "장화", "빗방울", "개구리", "구름"],
            "바다": ["파도", "고래", "산호", "조개", "모래", "등대", "배"],
            "나무": ["잎", "새", "그네", "열매", "뿌리", "숲", "다람쥐"],
            "우주": ["별", "행성", "로켓", "외계인", "달", "은하수", "우주복"],
        }
        candidates = banks.get(root, [])[:]
        for word, values in banks.items():
            if word in root and word != root:
                candidates.extend(values)
        # For unfamiliar words, build varied clouds that explicitly include the
        # selected thought, rather than returning an unrelated fixed list.
        if not candidates:
            if ko:
                candidates = [f"{root} 친구", f"{root} 마을", f"{root} 색깔", f"{root} 여행", f"{root} 비밀", f"{root} 소리", f"{root} 꿈", f"{root} 별"]
            else:
                candidates = [f"{root} friend", f"{root} town", f"{root} colors", f"{root} journey", f"{root} secret", f"{root} sounds", f"{root} dream", f"{root} stars"]
    elif mode == "logic":
        candidates = ([f"{root}의 공통점", f"{root}의 비밀", f"{root}가 만나는 곳", f"{root}의 모험", f"{root}의 특별한 능력", f"{root}의 새로운 모습", f"{root}의 친구"] if ko else [f"Similarities: {root}", f"Secret of {root}", f"Where {root} meets", f"Adventure: {root}", f"Powers of {root}", f"New form of {root}"])
    else:
        candidates = ([f"{root}의 주인공", f"{root}가 있는 곳", f"{root}에서 생긴 일", f"{root}의 비밀", f"{root}의 소리", f"{root}의 색깔", f"{root}의 다음 장면"] if ko else [f"Hero of {root}", f"Place for {root}", f"What happened to {root}", f"Secret of {root}", f"Sounds of {root}", f"Colors of {root}", f"Next scene: {root}"])
    digest = int(hashlib.sha256((root + str(len(history))).encode()).hexdigest()[:8], 16)
    # Preserve sensible word-association ordering; rotate only later steps.
    if history and candidates:
        offset = digest % len(candidates)
        candidates = candidates[offset:] + candidates[:offset]
    out = []
    for candidate in candidates:
        if candidate.casefold() not in used and candidate.casefold() not in {x.casefold() for x in out}:
            out.append(candidate)
        if len(out) == count:
            break
    index = 1
    while len(out) < count:
        candidate = (f"{root} 상상 {index}" if ko else f"{root} idea {index}")
        if candidate.casefold() not in used:
            out.append(candidate)
        index += 1
    return out


def suggestions():
    ss = st.session_state
    mode = ss.mode
    count = 6 if mode == "creative" else 4
    history = [{"cloud": x["choice"], "own_words": x["own"]} for x in ss.steps[-10:]]
    context = ss.current if mode != "logic" else f"{ss.seed} + {ss.second} → {ss.current}"
    instruction = {
        "creative": "Generate SIX DISTINCT SHORT ASSOCIATED WORDS or short noun phrases, NOT questions. Make direct and imaginative associations specifically with CURRENT thought. For example 밥→콩밥→콩→콩나무→하늘. Each option 1-3 Korean words, no generic categories.",
        "logic": "This is a CONNECTION MIND MAP, NOT a question list. On the FIRST step, every one of FOUR short concrete noun-phrase branches MUST explicitly connect BOTH input words, not just one. Example 바다 + 호랑이 => 바닷속 호랑이, 호랑이 무늬 파도, 호랑이가 사는 섬, 호랑이 줄무늬 물고기. On LATER steps, generate FOUR concrete child-friendly branches of the LATEST selected connection, keeping the two original words as the conceptual roots. No generic labels, no questions.",
        "fusion": "Generate FOUR distinct concrete scenes or story developments FROM THE LATEST chosen direction, not generic question categories. Each option short, specific and playful.",
    }[mode]
    previous = [x["choice"] for x in ss.steps]
    prompt = f"""You are Cloud Fairy, a gentle imagination companion for ages 8-10. Language: {'Korean' if ss.lang=='한국어' else 'English'}.
Circuit: {mode}. Initial word: {ss.seed!r}. Second word: {ss.get('second','')!r}. LATEST chosen thought (MOST IMPORTANT): {ss.current!r}.
Full previous path: {json.dumps(history, ensure_ascii=False)}.
{instruction}
CRITICAL: Every new choice MUST be connected to the latest chosen thought {ss.current!r}, NOT simply to the original seed. Advance the imagination in a new direction at EVERY step. Do not repeat any earlier chosen option: {json.dumps(previous, ensure_ascii=False)}. No exams, grades, personal information, scary or adult content.
Return ONLY JSON {{"options":[...]}} with exactly {count} strings."""
    raw = ai(prompt, "")
    generated = parse_items(raw, count)
    blocked = {x.casefold() for x in previous}
    blocked.add(str(ss.current).casefold())
    # If the AI repeats previous choices or cannot be reached, use context-specific
    # suggestions. Never show the same fixed generic fallback again.
    if generated and all(x.casefold() not in blocked for x in generated):
        if mode != "logic":
            return generated
        # A bridge must include BOTH inputs in its starting suggestions,
        # or explicitly grow from a bridge the child has already chosen.
        if ss.steps or all((ss.seed in x and ss.second in x) for x in generated):
            return generated
    if mode == "logic":
        return logic_fallbacks(ss.seed, ss.second, ss.current, ss.steps, count)
    return fresh_fallbacks(mode, ss.current, ss.steps, count)

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
        if ss.mode == "logic":
            logic_map()
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
