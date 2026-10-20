import streamlit as st
from google import genai
import json
import re
import random
import html

EN = st.session_state.get("app_language", "English") == "English"
def t(en, ko):
    return en if EN else ko

ACTIVITIES = [
    ("association", "☁️ Free Association", "☁️ 자유 연상"),
    ("uses", "💡 Alternative Uses", "💡 새로운 용도 찾기"),
    ("connection", "🔗 Random Connection", "🔗 엉뚱한 연결"),
]
MISSIONS = {
    "association": [
        ("Start with 'rain'. What does it remind you of?", "‘비’를 떠올리면 무엇이 생각나나요?"),
        ("What comes to mind when you hear 'a train station'?", "‘기차역’ 하면 어떤 생각이 떠오르나요?"),
        ("Start with 'the moon'. Where does your mind wander?", "‘달’을 떠올리면 생각이 어디로 이어지나요?"),
    ],
    "uses": [
        ("Imagine a surprising new use for a paper cup.", "종이컵의 색다른 용도를 상상해 보세요."),
        ("What else could you do with a shoebox?", "신발 상자를 다른 용도로 쓴다면?"),
        ("Invent an unusual use for an umbrella.", "우산의 엉뚱한 새로운 용도를 만들어 보세요."),
    ],
    "connection": [
        ("Combine a library and an amusement park into one new idea.", "도서관과 놀이공원을 결합해 새로운 아이디어를 만들어 보세요."),
        ("Combine a cloud and a bicycle into something unexpected.", "구름과 자전거를 결합해 색다른 무언가를 만들어 보세요."),
        ("Combine a garden and a smartphone into one idea.", "정원과 스마트폰을 결합해 새로운 아이디어를 만들어 보세요."),
    ],
}
def reset(mission=None):
    st.session_state.creative_mission = mission or random.choice(MISSIONS[st.session_state.creative_activity])
    st.session_state.creative_history = []
    st.session_state.creative_suggestions = []
    st.session_state.creative_observation = ""
    st.session_state.creative_finish = False
    st.session_state.creative_fallback = False

def make_directions(activity, mission, history):
    prompt = f"""You are the gentle, playful creative thinking partner for Daydream Circuit.
Respond in {"English" if EN else "Korean"} only.
Activity: {activity}
Mission: {mission}
User's actual ideas in order: {json.dumps(history, ensure_ascii=False)}
The user has already contributed their own idea. Encourage divergent thinking without judging intelligence.
Give ONE short, specific observation about the most recent user idea.
Then provide exactly SIX short, distinct follow-up creative prompts/questions that invite the user to create
their own next idea. Do not supply completed solutions. Mix changes of perspective, surprising
combinations, scale, senses, narrative and unusual constraints. Avoid repeated prompts.
Return only JSON with fields "observation" (string) and "directions" (array of six strings)."""
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
        raw = response.text.strip()
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw).strip()
        result = json.loads(raw)
        directions = result["directions"]
        if not isinstance(directions,list) or len(directions)!=6 or not all(isinstance(x,str) and x.strip() for x in directions):
            raise ValueError("Invalid directions")
        st.session_state.creative_fallback = False
        return str(result.get("observation","")), directions
    except Exception:
        st.session_state.creative_fallback = True
        if EN:
            return ("Your idea can go in many directions. Pick a new lens to explore.",
                ["What if it were ten times bigger?", "What would a child imagine?",
                 "What if it existed in the future?", "Could you combine it with music?",
                 "What is the opposite approach?", "What if it worked underwater?"])
        return ("이 생각도 여러 방향으로 확장할 수 있어요. 새로운 관점을 골라 보세요.",
                ["크기가 열 배 커진다면?", "어린이라면 어떻게 상상할까요?",
                 "미래에 존재한다면?", "음악과 결합한다면?",
                 "정반대 방법은 무엇일까요?", "물속에서 작동한다면?"])

st.markdown("""
<style>
.creative-title {font-size:35px;font-weight:800;letter-spacing:-.035em;text-align:center;margin:8px 0}
.creative-sub {font-size:17px;color:#74758a;text-align:center;margin-bottom:20px}
div[data-testid="stButton"] button {font-size:18px!important;line-height:1.5!important;
min-height:62px!important;border-radius:17px!important;white-space:normal!important}
div[data-testid="stButton"] button p {font-size:inherit!important;line-height:inherit!important}
</style>""",unsafe_allow_html=True)
st.markdown('<div class="creative-title">🎨 Creative Mode</div>',unsafe_allow_html=True)
st.markdown('<div class="creative-sub">'+t("Practice thinking beyond the obvious.","익숙한 생각에서 벗어나는 연습")+'</div>',unsafe_allow_html=True)

labels=[x[1] if EN else x[2] for x in ACTIVITIES]
selected=st.radio(t("Choose a creative exercise","창의력 훈련 선택"),labels,horizontal=False)
activity=ACTIVITIES[labels.index(selected)][0]
if st.session_state.get("creative_activity")!=activity or st.session_state.get("creative_language")!=EN:
    st.session_state.creative_activity=activity
    st.session_state.creative_language=EN
    reset()

mission=st.session_state.creative_mission[0 if EN else 1]
st.info("🎯 "+mission)
if st.button(t("🎲 New mission","🎲 새로운 미션"),use_container_width=True):
    reset()
    st.rerun()

history=st.session_state.creative_history
st.caption(t("First, share your own idea. AI will help you explore six different directions.",
             "먼저 직접 생각을 적어보세요. AI가 서로 다른 6가지 방향으로 확장을 도와줘요."))

if history:
    st.markdown("#### "+t("Your thought journey","나의 생각 여행"))
    for i,idea in enumerate(history,1):
        st.markdown(f"**{i}.** {html.escape(idea)}")

if not st.session_state.creative_finish:
    if st.session_state.creative_suggestions:
        st.markdown("#### ☁️ "+t("Six paths to explore","6가지 생각 갈림길"))
        st.write(st.session_state.creative_observation)
        if st.session_state.creative_fallback:
            st.caption(t("AI is temporarily unavailable. You can continue with built-in prompts.",
                         "AI 연결이 잠시 어려워 기본 질문으로 계속할 수 있어요."))
        for i,direction in enumerate(st.session_state.creative_suggestions):
            if st.button(f"{i+1}. {direction}",key=f"creative_direction_{i}",use_container_width=True):
                st.session_state.creative_selected_direction=direction
                st.rerun()
        if st.session_state.get("creative_selected_direction"):
            st.success(t("Your chosen direction: ","선택한 방향: ")+st.session_state.creative_selected_direction)

    with st.form("creative_idea_form",clear_on_submit=True):
        idea=st.text_area(t("What is your idea?","어떤 생각이 떠올랐나요?"),
                          placeholder=t("Write your own idea here...","나만의 생각을 적어보세요..."),
                          max_chars=600,height=110)
        submit=st.form_submit_button(t("✨ Explore my idea","✨ 내 생각 확장하기"),use_container_width=True)
    if submit:
        if not idea.strip():
            st.warning(t("Please write an idea first.","먼저 생각을 입력해 주세요."))
        else:
            history.append(idea.strip())
            with st.spinner(t("Exploring new directions...","새로운 방향을 찾고 있어요...")):
                obs,dirs=make_directions(activity,mission,history)
            st.session_state.creative_observation=obs
            st.session_state.creative_suggestions=dirs
            st.session_state.creative_selected_direction=""
            st.rerun()
    if history and st.button(t("⭐ Finish & see my journey","⭐ 마무리하고 생각 기록 보기"),use_container_width=True):
        st.session_state.creative_finish=True
        st.rerun()
else:
    st.markdown("### ⭐ EUREKA!")
    st.write(t("Here are the ideas you created during this exercise.",
               "이번 훈련에서 직접 만들어 낸 생각들이에요."))
    st.metric(t("Ideas explored","탐색한 생각"),len(history))
    st.text_area(t("Copy your journey","생각 기록 복사하기"),
                 value="\n".join(f"{i}. {x}" for i,x in enumerate(history,1)),height=170)
    st.caption(t("This summary is available in the current session. Copy it to save it elsewhere.",
                 "이 기록은 현재 세션에서 확인할 수 있어요. 보관하려면 복사해 주세요."))
    if st.button(t("☁️ Try another journey","☁️ 새로운 생각 여행"),use_container_width=True):
        reset()
        st.rerun()
