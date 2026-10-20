import streamlit as st
from google import genai
from pathlib import Path
import json
import html
import time
import random
import base64


# =========================================================
# 기본 설정
# =========================================================
# Page configuration is handled by app.py

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

MODEL = "gemini-3.6-flash"

BASE_DIR = Path(__file__).resolve().parent
FAIRY_IMAGE = BASE_DIR / "cloud_fairy.png"
TAROT_DIR = BASE_DIR
EUREKA_CLOUD_IMAGE = BASE_DIR / "eureka_cloud.svg"
EUREKA_STAR_IMAGE = BASE_DIR / "eureka_star.svg"


def asset_data_uri(path):
    if not path.exists():
        return ""

    mime = "image/svg+xml" if path.suffix.lower() == ".svg" else "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"



# =========================================================
# Cloud Fairy 타로 22장
# =========================================================
TAROT_CARDS = [
    {
        "name": "THE FOOL",
        "ko": "The Fool",
        "image": "00_fool.png",
        "meaning": "This card represents new beginnings, freedom, and possibilities yet to unfold.",
        "ending": "You do not need to know every road before taking the first step. A small thought today might lead somewhere wonderful. Keep exploring! ☁️",
    },
    {
        "name": "THE MAGICIAN",
        "ko": "The Magician",
        "image": "01_magician.png",
        "meaning": "This card represents potential, initiative, and the resources already within reach.",
        "ending": "You may already have more to work with than you realize. Even your wandering thoughts can become the seeds of something new. 🪄",
    },
    {
        "name": "THE HIGH PRIESTESS",
        "ko": "The High Priestess",
        "image": "02_high_priestess.png",
        "meaning": "This card represents intuition, inner wisdom, and feelings not yet put into words.",
        "ending": "Not every feeling needs a name right away. Give the thoughts that linger a little room to grow clearer. 🌙",
    },
    {
        "name": "THE EMPRESS",
        "ko": "The Empress",
        "image": "03_empress.png",
        "meaning": "This card represents creativity, abundance, and possibilities growing naturally.",
        "ending": "Good ideas sometimes grow at their own pace. Treasure the small things you discovered today. 🌷",
    },
    {
        "name": "THE EMPEROR",
        "ko": "The Emperor",
        "image": "04_emperor.png",
        "meaning": "This card represents stability, personal values, and a sense of direction.",
        "ending": "Among so many possibilities, your own values can be your compass. Trust the direction that feels right to you. ☁️",
    },
    {
        "name": "THE HIEROPHANT",
        "ko": "The Hierophant",
        "image": "05_hierophant.png",
        "meaning": "This card represents learning, tradition, and wisdom passed down over time.",
        "ending": "Both familiar paths and new ones have something to teach. The next choice is yours. 📜",
    },
    {
        "name": "THE LOVERS",
        "ko": "The Lovers",
        "image": "06_lovers.png",
        "meaning": "This card represents connection, attraction, and choices guided by the heart.",
        "ending": "The thoughts you keep returning to might be pointing toward something meaningful. Follow your curiosity. 💞",
    },
    {
        "name": "THE CHARIOT",
        "ko": "The Chariot",
        "image": "07_chariot.png",
        "meaning": "This card represents momentum, movement, and the courage to move forward.",
        "ending": "Your thoughts have traveled far today. Even an unexpected destination can be part of your journey. 🌠",
    },
    {
        "name": "STRENGTH",
        "ko": "Strength",
        "image": "08_strength.png",
        "meaning": "This card represents gentle courage, inner resilience, and patience.",
        "ending": "Courage can also mean waiting, accepting, and beginning again. Find your own way forward. 🦁",
    },
    {
        "name": "THE HERMIT",
        "ko": "The Hermit",
        "image": "09_hermit.png",
        "meaning": "This card represents quiet reflection, solitude, and discovering your own answers.",
        "ending": "Even quiet moments of reflection can reveal something new. Keep your inner lantern glowing. 🏮",
    },
    {
        "name": "WHEEL OF FORTUNE",
        "ko": "Wheel of Fortune",
        "image": "10_wheel_of_fortune.png",
        "meaning": "This card represents change, unexpected turns, and the surprises of life.",
        "ending": "Sometimes an ordinary thought becomes the start of an extraordinary change. Stay open to surprises. 🎡",
    },
    {
        "name": "JUSTICE",
        "ko": "Justice",
        "image": "11_justice.png",
        "meaning": "This card represents balance, sound judgment, and what matters most to you.",
        "ending": "Different feelings can coexist. Take your time discovering what matters most to you. ⚖️",
    },
    {
        "name": "THE HANGED MAN",
        "ko": "The Hanged Man",
        "image": "12_hanged_man.png",
        "meaning": "This card represents pausing to see familiar things from a new perspective.",
        "ending": "You do not always need to move forward. A different angle may reveal something you missed. ✨",
    },
    {
        "name": "DEATH",
        "ko": "Death",
        "image": "13_death.png",
        "meaning": "This card represents endings, transformation, and the beginning of a new chapter.",
        "ending": "An ending can also be a transformation. Make room for the next chapter. 🦋",
    },
    {
        "name": "TEMPERANCE",
        "ko": "Temperance",
        "image": "14_temperance.png",
        "meaning": "This card represents harmony, balance, and bringing different ideas together.",
        "ending": "Even unrelated thoughts can become part of the same story. Let them find their own balance. 🌈",
    },
    {
        "name": "THE DEVIL",
        "ko": "The Devil",
        "image": "15_devil.png",
        "meaning": "This card represents strong attachments and thoughts that keep drawing you back.",
        "ending": "A thought that keeps coming back may be worth exploring gently, without judging yourself. 🔥",
    },
    {
        "name": "THE TOWER",
        "ko": "The Tower",
        "image": "16_tower.png",
        "meaning": "This card represents sudden change and a fresh perspective after disruption.",
        "ending": "An unexpected idea can redraw your entire mental map. New views may appear after the shake-up. ⚡",
    },
    {
        "name": "THE STAR",
        "ko": "The Star",
        "image": "17_star.png",
        "meaning": "This card represents hope, dreams, and the light of future possibilities.",
        "ending": "Whether your dream is freedom, a new beginning, or something unnamed, let it shine. ✨",
    },
    {
        "name": "THE MOON",
        "ko": "The Moon",
        "image": "18_moon.png",
        "meaning": "This card represents imagination, uncertainty, and feelings still taking shape.",
        "ending": "You do not need complete clarity right now. Even moonlight can help you find your way. 🌙",
    },
    {
        "name": "THE SUN",
        "ko": "The Sun",
        "image": "19_sun.png",
        "meaning": "This card represents joy, confidence, and bright possibilities.",
        "ending": "Remember the little moments of joy you discovered today. May that warmth stay with you. ☀️",
    },
    {
        "name": "JUDGEMENT",
        "ko": "Judgement",
        "image": "20_judgement.png",
        "meaning": "This card represents awakening, reflection, and seeing yourself differently.",
        "ending": "Your thoughts may have changed since the beginning. Even one small realization is worth celebrating. 📯",
    },
    {
        "name": "THE WORLD",
        "ko": "The World",
        "image": "21_world.png",
        "meaning": "This card represents completion, connection, and separate pieces coming together.",
        "ending": "Look how far your thoughts have traveled! Keep the little world you created, and enjoy the next journey. 🌍",
    },
]


# =========================================================
# 세션 상태
# =========================================================
defaults = {
    "thought_path": [],
    "started": False,
    "suggestions": [],
    "fairy_comment": "",
    "analysis": "",
    "eureka_mode": False,
    "eureka_note": "",
    "eureka_saved": False,
    "tarot_card": None,

    # 생각 여행 마무리 체크포인트
    "journey_checkpoint": 3,
    "journey_finish_mode": False,
    "train_boarded": False,
    "train_flow_open": False,

    # Gemini 상태
    "quota_fallback": False,
    "api_notice": "",
    "ai_disabled": False,

    # 같은 생각 경로 API 재호출 방지
    "thought_cache": {},
    "connection_cache": {},
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# Gemini 호출
# =========================================================
def generate_with_retry(prompt, retries=2):

    if st.session_state.ai_disabled:
        raise RuntimeError("GEMINI_QUOTA_EXHAUSTED")

    last_error = None

    for attempt in range(retries):
        try:
            return client.models.generate_content(
                model=MODEL,
                contents=prompt
            )

        except Exception as e:

            last_error = e
            error_text = str(e).lower()

            # -------------------------------------------------
            # 쿼터 초과
            # -------------------------------------------------
            if (
                "429" in error_text
                or "resource_exhausted" in error_text
                or "quota exceeded" in error_text
                or "free_tier_requests" in error_text
            ):
                st.session_state.ai_disabled = True
                st.session_state.quota_fallback = True

                raise RuntimeError(
                    "GEMINI_QUOTA_EXHAUSTED"
                )

            # -------------------------------------------------
            # Gemini 서버 일시 과부하
            # -------------------------------------------------
            if (
                "503" in error_text
                or "unavailable" in error_text
                or "high demand" in error_text
            ):
                time.sleep(
                    1 * (attempt + 1)
                )
                continue

            raise

    raise last_error

# =========================================================
# Gemini JSON 정리
# =========================================================
def clean_json(text):

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


# =========================================================
# Gemini 없이도 돌아가는 기본 망상 모드
# =========================================================
def fallback_explore(thought_path):

    current = thought_path[-1]

    templates = [
        f"'{current}' — a place it brings to mind",
        f"'{current}' — someone it reminds you of",
        f"The complete opposite of this idea",
        f"Imagine this idea becoming real",
        f"A memory of a similar thought",
        f"Take a wildly unexpected turn",
        f"If this were a movie, what happens next?",
        f"Turn this thought into a journey",
        f"The feeling this thought brings up",
        f"Connect it to your future self in five years",
        f"An unrelated hobby to explore",
        f"What if you told a friend?",
    ]

    suggestions = random.sample(
        templates,
        6
    )

    if len(thought_path) == 1:

        comment = (
            "The AI stardust is recharging ☁️ "
            "But the imagination trail is still open. "
            "Which way shall we wander?"
        )

    else:

        first = thought_path[0]

        comment = (
            f"We started with '{first}' and somehow reached '{current}'. ☁️ "
            "The AI stardust is taking a break, but "
            "your thoughts can keep floating."
        )

    return comment, suggestions


# =========================================================
# Gemini 없이 숨은 연결
# =========================================================
def fallback_hidden_connection(thought_path):
    first = thought_path[0]
    last = thought_path[-1]
    middle = thought_path[len(thought_path) // 2] if len(thought_path) >= 3 else None
    middle_line = (f"Along the way, '{middle}' was an interesting stop. It might be a bridge between the first and latest ideas.\n\n" if middle else "")
    return (
        f"☁️ The Journey So Far\n\nWe started with '{first}' and arrived at '{last}'.\n\n"
        f"✨ A Hidden Connection\n\n{middle_line}Even ideas that seem far apart can connect through your imagination.\n\n"
        "🪄 The Cloud Fairy's Observation\n\nThere is no single right answer. Noticing how your ideas connect is a discovery in itself."
    )


# =========================================================
# EUREKA 구름에 보여줄 짧은 생각 라벨
# =========================================================
def compact_thought_label(text, max_len=14):
    cleaned = " ".join(str(text).replace("\n", " ").split())

    if len(cleaned) <= max_len:
        return cleaned

    words = cleaned.split()
    result = ""

    for word in words:
        candidate = word if not result else f"{result} {word}"

        if len(candidate) > max_len:
            break

        result = candidate

    if result:
        return result + "…"

    return cleaned[:max_len].rstrip() + "…"


# =========================================================
# 생각 갈림길 생성
# =========================================================
def explore_thoughts(thought_path):

    # -----------------------------------------------------
    # 같은 경로면 Gemini 다시 호출하지 않음
    # -----------------------------------------------------
    cache_key = " → ".join(
        thought_path
    )

    if cache_key in st.session_state.thought_cache:

        cached = (
            st.session_state.thought_cache[
                cache_key
            ]
        )

        return (
            cached["comment"],
            cached["suggestions"]
        )

    # -----------------------------------------------------
    # 이미 쿼터가 끝났다면 바로 fallback
    # -----------------------------------------------------
    if st.session_state.ai_disabled:

        comment, suggestions = (
            fallback_explore(
                thought_path
            )
        )

        st.session_state.api_notice = (
            "☁️ The AI stardust has run out for now. "
            "You can keep exploring in offline imagination mode!"
        )

        return comment, suggestions


    path_text = " → ".join(
        thought_path
    )

  

    prompt = f"""
You are the friendly Cloud Fairy in Daydream Circuit, an AI thought-exploration app.
Thought journey: {path_text}
Provide one short, thoughtful observation and exactly six different directions to explore next.
Vary the suggestions across emotions, people, memories, places, actions, the future, realistic possibilities, and playful imagination. Keep them short and distinct.
Never lecture, diagnose, judge the user's personality, or force a single correct answer.
Be warm, curious, and respectful of the user's imagination.
All output must be in natural English, even when the user's input is in another language.
Return ONLY valid JSON:
{{"fairy_comment":"Short observation","suggestions":["Direction 1","Direction 2","Direction 3","Direction 4","Direction 5","Direction 6"]}}
"""

    try:

        response = generate_with_retry(
            prompt
        )

        result = json.loads(
            clean_json(
                response.text
            )
        )

        suggestions = result.get(
            "suggestions",
            []
        )

        if len(suggestions) < 6:

            raise ValueError(
                "Could not generate six directions."
            )

        comment = result.get(
            "fairy_comment",
            ""
        )

        suggestions = suggestions[:6]

        st.session_state.quota_fallback = False
        st.session_state.api_notice = ""

        # 캐시 저장
        st.session_state.thought_cache[
            cache_key
        ] = {
            "comment": comment,
            "suggestions": suggestions,
        }

        return comment, suggestions


    except RuntimeError as e:

        if str(e) == "GEMINI_QUOTA_EXHAUSTED":

            st.session_state.quota_fallback = True

            st.session_state.api_notice = (
                "☁️ The AI stardust has run out for now. "
                "You can keep exploring in offline imagination mode!"
            )

            return fallback_explore(
                thought_path
            )

        raise


# =========================================================
# 숨은 연결 찾기
# =========================================================
def find_hidden_connection(
    thought_path
):

    cache_key = " → ".join(
        thought_path
    )

    # 같은 경로면 API 재호출 안 함
    if (
        cache_key
        in st.session_state.connection_cache
    ):
        return (
            st.session_state.connection_cache[
                cache_key
            ]
        )

    # 이미 쿼터 소진
    if st.session_state.ai_disabled:

        st.session_state.api_notice = (
            "☁️ The AI stardust is recharging, so "
            "the Cloud Fairy will use its offline observations."
        )

        return fallback_hidden_connection(
            thought_path
        )


    path_text = " → ".join(
        thought_path
    )

    prompt = f"""
You are the Cloud Fairy in Daydream Circuit.
The user's thought journey: {path_text}
Identify one surprising or interesting connection between these thoughts, without analyzing or defining the person.
Do not diagnose, make personality assumptions, lecture, or give self-help advice. Use a curious, gentle tone.
Respond briefly, in natural English, with these sections:
☁️ The Journey So Far — How the ideas evolved.
✨ A Hidden Connection — A recurring theme or unexpected connection.
🪄 What If? — One open-ended question to inspire further thought.
"""

    try:

        response = generate_with_retry(
            prompt
        )

        result = response.text

        st.session_state.connection_cache[
            cache_key
        ] = result

        return result


    except RuntimeError as e:

        if str(e) == "GEMINI_QUOTA_EXHAUSTED":

            st.session_state.quota_fallback = True

            st.session_state.api_notice = (
                "☁️ The AI stardust is recharging, so "
                "the Cloud Fairy will use its offline observations."
            )

            return fallback_hidden_connection(
                thought_path
            )

        raise


# =========================================================
# 생각 선택
# =========================================================
def choose_thought(thought):

    try:

        new_path = (
            st.session_state.thought_path
            + [thought]
        )

        with st.spinner(
            "🪄 Following that cloud..."
        ):

            comment, suggestions = (
                explore_thoughts(
                    new_path
                )
            )

        st.session_state.thought_path = (
            new_path
        )

        st.session_state.fairy_comment = (
            comment
        )

        st.session_state.suggestions = (
            suggestions
        )

        st.session_state.analysis = ""
        st.session_state.eureka_mode = False
        st.session_state.eureka_saved = False
        st.session_state.eureka_note = ""
        st.session_state.tarot_card = None
        st.session_state.journey_finish_mode = False
        st.session_state.train_boarded = False
        st.session_state.train_flow_open = False

        st.rerun()


    except Exception as e:

        # Gemini 말고 진짜 다른 오류만 표시
        st.error(
            "The stardust got a little tangled ✨ "
            "Please try again."
        )

        st.code(
            str(e)
        )



# =========================================================
# 전용 EUREKA / 타로 화면
# =========================================================
def render_eureka_screen(path):

    if not st.session_state.eureka_saved:

        st.markdown(
            '<div style="height:18px;"></div>'
            '<div class="section-title">'
            '⭐ EUREKA! You found a star!'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-sub">'
            'From your thought journey, save '
            '<b>one keyword or short phrase</b>that stands out.<br>'
            'e.g., Little joys · New beginnings · Freedom'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="eureka-card">'
            '<div style="text-align:center;font-size:31px;">☁️　✨　☁️</div>'
            '<div style="text-align:center;color:#68647e;font-size:16px;'
            'font-weight:800;line-height:1.65;margin-top:8px;">'
            'No need to write a long summary.<br>'
            'Just one phrase that stayed with you is enough.'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        note = st.text_input(
            "Today’s EUREKA",
            value=st.session_state.eureka_note,
            placeholder="e.g., Little joys",
            max_chars=24,
            label_visibility="collapsed",
            key="eureka_dedicated_input"
        )

        if st.button(
            "⭐ Save this thought as today’s star",
            key="save_eureka_dedicated",
            use_container_width=True
        ):
            if note.strip():
                st.session_state.eureka_note = note.strip()
                st.session_state.eureka_saved = True
                st.rerun()
            else:
                st.warning(
                    "Enter one keyword that stayed with you ✨"
                )

        return


    saved_note = html.escape(
        st.session_state.eureka_note
    )

    recent_thoughts = path[-4:]

    cloud_labels = [
        html.escape(
            compact_thought_label(
                item
            )
        )
        for item in recent_thoughts
    ]

    while len(cloud_labels) < 4:
        cloud_labels.insert(
            0,
            "☁️"
        )

    cloud_uri = asset_data_uri(
        EUREKA_CLOUD_IMAGE
    )

    star_uri = asset_data_uri(
        EUREKA_STAR_IMAGE
    )

    eureka_star_html = (
        '<div class="eureka-celebration">'
        '<div class="eureka-celebration-title">'
        '✨ A star discovered on today’s thought journey ✨'
        '</div>'

        f'<div class="big-labeled-cloud blc1">'
        f'<img src="{cloud_uri}">'
        f'<div class="big-cloud-word">{cloud_labels[0]}</div>'
        '</div>'

        f'<div class="big-labeled-cloud blc2">'
        f'<img src="{cloud_uri}">'
        f'<div class="big-cloud-word">{cloud_labels[1]}</div>'
        '</div>'

        f'<div class="big-labeled-cloud blc3">'
        f'<img src="{cloud_uri}">'
        f'<div class="big-cloud-word">{cloud_labels[2]}</div>'
        '</div>'

        f'<div class="big-labeled-cloud blc4">'
        f'<img src="{cloud_uri}">'
        f'<div class="big-cloud-word">{cloud_labels[3]}</div>'
        '</div>'

        f'<img class="asset-cloud ac5" src="{cloud_uri}">'
        f'<img class="asset-cloud ac6" src="{cloud_uri}">'
        f'<img class="asset-cloud ac7" src="{cloud_uri}">'
        f'<img class="asset-cloud ac8" src="{cloud_uri}">'
        f'<img class="asset-cloud ac9" src="{cloud_uri}">'

        '<div class="celebration-glow"></div>'
        '<div class="celebration-spark cs1">✦</div>'
        '<div class="celebration-spark cs2">✧</div>'
        '<div class="celebration-spark cs3">✦</div>'
        '<div class="celebration-spark cs4">✧</div>'

        '<div class="asset-star-wrap">'
        f'<img class="asset-star-img" src="{star_uri}">'
        f'<div class="asset-star-note">{saved_note}</div>'
        '</div>'
        '</div>'

        '<div class="eureka-reveal">'
        '<div class="eureka-reveal-title">'
        '✨ A star discovered on today’s thought journey ✨'
        '</div>'

        f'<div class="final-labeled-cloud flc1">'
        f'<img src="{cloud_uri}">'
        f'<div class="final-cloud-word">{cloud_labels[0]}</div>'
        '</div>'

        f'<div class="final-labeled-cloud flc2">'
        f'<img src="{cloud_uri}">'
        f'<div class="final-cloud-word">{cloud_labels[1]}</div>'
        '</div>'

        f'<div class="final-labeled-cloud flc3">'
        f'<img src="{cloud_uri}">'
        f'<div class="final-cloud-word">{cloud_labels[2]}</div>'
        '</div>'

        f'<div class="final-labeled-cloud flc4">'
        f'<img src="{cloud_uri}">'
        f'<div class="final-cloud-word">{cloud_labels[3]}</div>'
        '</div>'

        '<div class="final-asset-star">'
        f'<img src="{star_uri}">'
        f'<div class="final-asset-star-note">{saved_note}</div>'
        '</div>'

        '<div class="eureka-caption">'
        'Even small thoughts can become brilliant ideas one day. ☁️'
        '</div>'
        '</div>'
    )

    st.markdown(
        eureka_star_html,
        unsafe_allow_html=True
    )

    if st.session_state.tarot_card is None:

        if st.button(
            "✨🔮 Draw a tarot card for a little inspiration ✨",
            key="tarot_dedicated",
            use_container_width=True,
            type="primary"
        ):

            with st.spinner(
                "☁️ The Cloud Fairy is shuffling the cards... ✨"
            ):
                time.sleep(
                    0.25
                )

            st.session_state.tarot_card = (
                random.choice(
                    TAROT_CARDS
                )
            )

            st.rerun()

    else:

        card = st.session_state.tarot_card

        image_path = (
            TAROT_DIR
            / card["image"]
        )

        st.markdown(
            '<div class="tarot-stage">'
            '<div style="font-size:13px;letter-spacing:3px;'
            'color:#9b8bac;font-weight:800;">'
            '☁️ CLOUD FAIRY TAROT ☁️'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        if image_path.exists():

            left, mid, right = st.columns(
                [1, 2, 1]
            )

            with mid:
                st.image(
                    str(
                        image_path
                    ),
                    use_container_width=True
                )

        else:

            st.error(
                "Tarot card image not found 😭"
            )

        st.markdown(
            '<div class="tarot-title">'
            f'{html.escape(card["name"])}'
            '</div>'
            '<div class="tarot-korean">'
            f'{html.escape(card["ko"])}'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="tarot-meaning">'
            '<b>🔮 What this card represents</b><br><br>'
            f'{html.escape(card["meaning"])}'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="ending-card">'
            '<div class="ending-label">'
            '☁️ A final note from the Cloud Fairy'
            '</div>'
            f'{html.escape(card["ending"])}'
            '</div>',
            unsafe_allow_html=True
        )

    st.divider()

    # =====================================================
    # EUREKA 이후 선택
    # 1) 같은 흐름에서 EUREKA 다시 쓰기
    # 2) 완전히 새로운 망상 시작
    # 3) 하던 망상 흐름으로 돌아가기
    # =====================================================

    if st.button(
        "⭐ Save a different EUREKA",
        key="rewrite_eureka",
        use_container_width=True
    ):

        st.session_state.eureka_note = ""
        st.session_state.eureka_saved = False
        st.session_state.tarot_card = None

        st.session_state.journey_finish_mode = True
        st.session_state.train_boarded = False
        st.session_state.train_flow_open = False

        st.rerun()


    new_train_col, continue_train_col = st.columns(2)

    with new_train_col:

        if st.button(
            "🚂 Board a new thought train",
            key="restart_dedicated",
            use_container_width=True
        ):

            st.session_state.thought_path = []
            st.session_state.suggestions = []
            st.session_state.fairy_comment = ""
            st.session_state.analysis = ""

            st.session_state.eureka_mode = False
            st.session_state.eureka_note = ""
            st.session_state.eureka_saved = False
            st.session_state.tarot_card = None

            st.session_state.journey_checkpoint = 3
            st.session_state.journey_finish_mode = False
            st.session_state.train_boarded = False
            st.session_state.train_flow_open = False

            st.session_state.started = False

            st.rerun()


    with continue_train_col:

        if st.button(
            "☁️ Return to your thought train",
            key="continue_old_train",
            use_container_width=True
        ):

            # 지금까지의 생각 경로와 현재 6갈래는 그대로 유지
            # EUREKA/타로 화면만 닫고 탐험 화면으로 복귀
            selections_count = max(
                0,
                len(st.session_state.thought_path) - 1
            )

            st.session_state.eureka_mode = False
            st.session_state.eureka_note = ""
            st.session_state.eureka_saved = False
            st.session_state.tarot_card = None

            st.session_state.journey_finish_mode = False
            st.session_state.train_boarded = False
            st.session_state.train_flow_open = False
            st.session_state.analysis = ""

            # 복귀하자마자 체크포인트가 다시 뜨지 않도록
            # 3개의 생각 구름을 더 탄 뒤 다시 제안
            st.session_state.journey_checkpoint = (
                selections_count + 3
            )

            st.rerun()


# =========================================================
# CSS
# =========================================================
st.markdown(
    """
<style>
/* Daydream Circuit — refined bilingual typography and components */
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp, .stApp button, .stApp input, .stApp textarea, .stApp p, .stApp label {
    font-family: 'Pretendard', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}
.stApp { color: #34384a; }
.logo { font-size: clamp(32px, 6vw, 42px) !important; font-weight: 800 !important; letter-spacing: -0.045em !important; line-height: 1.2 !important; }
.tagline { font-size: 16px !important; font-weight: 400 !important; line-height: 1.65 !important; }
.section-title { font-size: 22px !important; font-weight: 750 !important; letter-spacing: -0.025em !important; }
.section-sub { font-size: 15px !important; line-height: 1.7 !important; }
.fairy-name, .current-label { font-weight: 700 !important; }
.fairy-text { font-size: 16px !important; line-height: 1.75 !important; }
.fairy-card, .current-thought, .eureka-card, .ending-card, .tarot-meaning, .constellation-box {
    border-radius: 22px !important;
    box-shadow: 0 5px 20px rgba(94, 103, 147, 0.075) !important;
}
div.stButton > button, div[data-testid="stButton"] > button {
    border-radius: 16px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    box-shadow: 0 3px 12px rgba(105,115,165,0.07) !important;
    transition: transform .15s ease, box-shadow .15s ease !important;
}
div.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 16px rgba(105,115,165,.11) !important; }
div.stTextInput input { border-radius: 14px !important; font-size: 16px !important; }
div.stTextArea textarea { border-radius: 14px !important; font-size: 15px !important; }


.stApp {
    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(255,255,255,0.98) 0px,
            rgba(255,255,255,0) 250px
        ),
        radial-gradient(
            circle at 90% 15%,
            rgba(255,255,255,0.88) 0px,
            rgba(255,255,255,0) 280px
        ),
        linear-gradient(
            180deg,
            #eaf7ff 0%,
            #f2f0ff 52%,
            #fff8fc 100%
        );
}

.block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

.logo {
    text-align: center;
    font-size: 48px;
    font-weight: 900;
    letter-spacing: -2px;
    margin-bottom: 2px;
}

.tagline {
    text-align: center;
    font-size: 19px;
    color: #73798a;
    margin-bottom: 24px;
}

.fairy-card {
    background: rgba(255,255,255,0.87);
    border: 1px solid rgba(255,255,255,0.98);
    border-radius: 28px;
    padding: 20px 22px;
    margin: 14px 0;
    box-shadow: 0 12px 35px rgba(94,110,160,0.10);
}

.fairy-name {
    font-weight: 850;
    font-size: 14px;
    color: #7772aa;
    margin-bottom: 7px;
}

.fairy-text {
    font-size: 17px;
    line-height: 1.65;
    color: #34384a;
}

.section-title {
    text-align: center;
    font-size: 23px;
    font-weight: 850;
    margin-top: 28px;
}

.section-sub {
    text-align: center;
    color: #808596;
    margin: 5px 0 18px 0;
}

.current-thought {
    background: rgba(255,255,255,0.98);
    border-radius: 32px;
    padding: 17px 20px;
    text-align: center;
    box-shadow: 0 10px 28px rgba(103,110,160,0.14);
    margin: 7px 0 12px 0;
}

.current-label {
    font-size: 12px;
    font-weight: 800;
    color: #9992c7;
    margin-bottom: 4px;
}

.current-text {
    font-size: 18px;
    font-weight: 850;
    color: #34384a;
    line-height: 1.45;
}

div[data-testid="stButton"] > button {
    border-radius: 30px !important;
    min-height: 72px;
    padding: 12px 14px;
    background: rgba(255,255,255,0.89);
    border: 1px solid rgba(255,255,255,0.98);
    box-shadow: 0 8px 25px rgba(105,115,165,0.11);
    font-weight: 700;
    white-space: normal;
    line-height: 1.35;
    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease;
}

div[data-testid="stButton"] > button:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(100,110,170,0.17);
    border: 1px solid rgba(180,175,230,0.45);
}


/* =========================================================
   별자리
   ========================================================= */

.constellation-box {
    position: relative;
    overflow: hidden;

    background:
        radial-gradient(
            circle at 20% 30%,
            rgba(255,255,255,0.85),
            rgba(255,255,255,0.16)
        ),
        linear-gradient(
            135deg,
            rgba(223,232,255,0.85),
            rgba(242,230,255,0.70)
        );

    border-radius: 32px;
    padding: 24px 18px;
    margin: 22px 0;

    box-shadow:
        0 12px 32px
        rgba(93,105,160,0.09);
}

.constellation-title {
    text-align: center;
    font-size: 14px;
    font-weight: 850;
    color: #74708f;
    margin-bottom: 20px;
}

.constellation {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    gap: 4px;
    line-height: 2.2;
}

.star-node {
    display: inline-block;
    background: rgba(255,255,255,0.94);
    padding: 7px 12px;
    border-radius: 999px;
    color: #65677c;
    font-size: 13px;

    box-shadow:
        0 0 0 3px rgba(255,255,255,0.24),
        0 5px 16px rgba(82,91,145,0.08);
}

.star-current {
    display: inline-block;

    background:
        linear-gradient(
            135deg,
            #fff7c9,
            #ffffff
        );

    padding: 8px 14px;
    border-radius: 999px;

    color: #67571d;
    font-size: 13px;
    font-weight: 850;

    box-shadow:
        0 0 18px rgba(255,221,105,0.50),
        0 6px 18px rgba(120,100,40,0.10);
}

.star-line {
    display: inline-block;
    color: rgba(119,112,165,0.60);
    font-size: 17px;
    padding: 0 3px;
}

.sparkles {
    text-align: center;
    font-size: 19px;
    color: #d2ae47;
    letter-spacing: 14px;
    margin: 2px 0 8px 0;

    animation:
        sparkle 2s ease-in-out infinite;
}

@keyframes sparkle {

    0%, 100% {
        opacity: 0.35;
    }

    50% {
        opacity: 1;
    }
}


/* =========================================================
   EUREKA
   ========================================================= */

.eureka-card {
    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.98),
            rgba(255,249,215,0.95)
        );

    border:
        1px solid #ffeaa0;

    border-radius: 28px;

    padding: 27px;

    margin-top: 20px;

    box-shadow:
        0 14px 38px
        rgba(160,130,60,0.12);
}


/* =========================================================
   실제 타로
   ========================================================= */

.tarot-stage {
    background:
        radial-gradient(
            circle at 50% 15%,
            rgba(255,255,255,0.96),
            rgba(255,255,255,0.45)
        ),
        linear-gradient(
            180deg,
            rgba(239,235,255,0.75),
            rgba(255,248,237,0.78)
        );

    border-radius: 36px;

    padding:
        26px 20px;

    margin:
        20px 0;

    box-shadow:
        0 16px 45px
        rgba(91,84,145,0.10);

    text-align: center;
}

.tarot-title {
    text-align: center;
    font-size: 25px;
    font-weight: 900;
    color: #514c72;
    margin-top: 9px;
}

.tarot-korean {
    text-align: center;
    font-size: 15px;
    color: #8b829d;
    margin-top: 3px;
}

.tarot-meaning {
    background:
        rgba(255,255,255,0.87);

    border-radius: 24px;

    padding:
        20px 22px;

    line-height: 1.7;

    color: #464859;

    margin:
        17px 0
        12px 0;

    box-shadow:
        0 8px 25px
        rgba(95,95,145,0.06);

    text-align: center;
}

.ending-card {
    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.97),
            rgba(255,250,229,0.94)
        );

    border:
        1px solid
        rgba(233,207,132,0.50);

    border-radius: 28px;

    padding:
        23px 24px;

    margin:
        16px 0
        24px 0;

    line-height: 1.75;

    color: #3f4151;

    box-shadow:
        0 12px 35px
        rgba(150,125,70,0.08);
}

.ending-label {
    font-weight: 900;
    color: #7772aa;
    margin-bottom: 10px;
}


/* =========================================================
   입력창
   ========================================================= */

div.stTextInput input {
    border-radius: 999px;
}

div.stTextArea textarea {
    border-radius: 18px;
}
/* =========================================================
   최종 UI 보정
   1. 화면 위쪽 여백
   2. 갈림길 버튼 긴 글 전체 표시
   ========================================================= */

/* 제목이 화면 맨 위에 붙지 않도록 */
.block-container {
    max-width: 820px !important;
    padding-top: 4rem !important;
    padding-bottom: 5rem !important;
}

/* 모든 Streamlit 버튼 기본 */
div.stButton > button {
    border-radius: 999px !important;

    /* 고정 높이 대신 내용에 따라 늘어나게 */
    height: auto !important;
    min-height: 56px !important;

    padding: 12px 18px !important;

    /* 긴 문장 줄바꿈 */
    white-space: normal !important;
    word-break: keep-all !important;
    overflow-wrap: break-word !important;

    /* ... 말줄임 제거 */
    overflow: visible !important;
    text-overflow: unset !important;

    line-height: 1.45 !important;
}

/* Streamlit이 버튼 글자 내부에 넣는 p 태그 */
div.stButton > button p {
    margin: 0 !important;

    white-space: normal !important;
    word-break: keep-all !important;
    overflow-wrap: break-word !important;

    overflow: visible !important;
    text-overflow: unset !important;

    display: block !important;
    -webkit-line-clamp: unset !important;
    -webkit-box-orient: initial !important;

    line-height: 1.45 !important;
}

/* =========================================================
   EUREKA - full screen cloud celebration
   ========================================================= */

/* 저장 직후 화면 전체를 덮는 축하 모션.
   pointer-events:none 이라 버튼/스크롤을 막지 않음 */
.eureka-celebration {
    position: fixed;
    inset: 0;
    z-index: 999999;
    overflow: hidden;
    pointer-events: none;
    background:
        radial-gradient(circle at 50% 52%, rgba(255,245,190,.70) 0%, rgba(255,245,190,0) 27%),
        linear-gradient(180deg, rgba(238,244,255,.88) 0%, rgba(249,241,255,.90) 52%, rgba(255,244,250,.94) 100%);
    opacity: 0;
    animation: celebrationScene 5.8s ease forwards;
}

.eureka-celebration-title {
    position: absolute;
    z-index: 40;
    top: 8vh;
    left: 0;
    right: 0;
    padding: 0 20px;
    text-align: center;
    color: #7772aa;
    font-size: clamp(16px, 4vw, 25px);
    font-weight: 950;
    letter-spacing: -.02em;
    opacity: 0;
    transform: translateY(10px);
    animation: celebrationTitle .7s ease .45s forwards;
}

/* 큰 몽실 구름: 모두 같은 색 */
.big-cloud {
    position: absolute;
    z-index: 15;
    width: clamp(210px, 42vw, 430px);
    height: clamp(78px, 14vw, 145px);
    border-radius: 999px;
    background: linear-gradient(180deg, rgba(255,255,255,1), rgba(238,237,255,.98));
    box-shadow:
        0 18px 42px rgba(111,103,166,.15),
        inset 0 -12px 25px rgba(213,209,243,.24);
    opacity: 0;
    transform: translateY(40vh) scale(.76);
    filter: blur(.1px);
}

.big-cloud::before,
.big-cloud::after {
    content: "";
    position: absolute;
    bottom: 15%;
    border-radius: 50%;
    background: inherit;
    box-shadow: inherit;
}
.big-cloud::before {
    width: 48%;
    aspect-ratio: 1;
    left: 10%;
}
.big-cloud::after {
    width: 58%;
    aspect-ratio: 1;
    right: 8%;
}

.bc1 { left:-10%; bottom:3%; animation: cloudBurst 2.15s cubic-bezier(.16,.82,.24,1.06) .05s forwards, cloudDriftA 3.2s ease-in-out 2.2s infinite; }
.bc2 { left:13%; bottom:-1%; animation: cloudBurst 2.30s cubic-bezier(.16,.82,.24,1.06) .14s forwards, cloudDriftB 3.5s ease-in-out 2.4s infinite; }
.bc3 { right:13%; bottom:0%; animation: cloudBurst 2.25s cubic-bezier(.16,.82,.24,1.06) .22s forwards, cloudDriftA 3.4s ease-in-out 2.5s infinite; }
.bc4 { right:-11%; bottom:4%; animation: cloudBurst 2.20s cubic-bezier(.16,.82,.24,1.06) .30s forwards, cloudDriftB 3.1s ease-in-out 2.5s infinite; }
.bc5 { left:34%; bottom:-8%; width:clamp(250px,48vw,480px); animation: cloudBurstCenter 2.35s cubic-bezier(.16,.82,.24,1.06) .08s forwards, cloudDriftA 3.8s ease-in-out 2.5s infinite; }

/* 생각 키워드가 적힌 작은 구름 */
.memory-cloud {
    position: absolute;
    z-index: 28;
    min-width: 120px;
    max-width: min(190px, 38vw);
    padding: 16px 18px;
    border-radius: 999px;
    text-align: center;
    color: #66637f;
    font-size: clamp(12px, 3vw, 15px);
    font-weight: 900;
    line-height: 1.35;
    word-break: keep-all;
    background: linear-gradient(180deg, #ffffff, #f0efff);
    border: 1px solid rgba(255,255,255,.96);
    box-shadow: 0 12px 28px rgba(117,108,172,.14);
    opacity: 0;
}
.mem1 { left:5%; top:27%; animation: memoryPop .8s cubic-bezier(.18,.85,.28,1.15) .72s forwards; }
.mem2 { right:5%; top:29%; animation: memoryPop .8s cubic-bezier(.18,.85,.28,1.15) .88s forwards; }
.mem3 { left:7%; top:61%; animation: memoryPop .8s cubic-bezier(.18,.85,.28,1.15) 1.04s forwards; }
.mem4 { right:7%; top:62%; animation: memoryPop .8s cubic-bezier(.18,.85,.28,1.15) 1.18s forwards; }

/* 별 뒤 빛 */
.celebration-glow {
    position: absolute;
    z-index: 20;
    left: 50%;
    top: 48%;
    width: min(72vw, 500px);
    aspect-ratio: 1;
    border-radius: 50%;
    transform: translate(-50%,-50%) scale(.15);
    opacity: 0;
    background: radial-gradient(circle, rgba(255,232,113,.78) 0%, rgba(255,242,177,.32) 43%, rgba(255,255,255,0) 72%);
    animation: celebrationGlow 1.2s ease 1.18s forwards;
}

/* 구름 사이에서 떠오르는 큰 별 */
.celebration-star {
    position: absolute;
    z-index: 35;
    left: 50%;
    top: 48%;
    width: min(54vw, 350px);
    aspect-ratio: 1;
    transform: translate(-50%, 45vh) scale(.18) rotate(-7deg);
    opacity: 0;
    animation: celebrationStar 1.35s cubic-bezier(.17,.88,.26,1.20) 1.20s forwards;
}

.celebration-star-glyph {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: Georgia, "Times New Roman", serif;
    font-size: min(52vw, 345px);
    line-height: 1;
    font-weight: 900;
    background: linear-gradient(145deg, #fff6b9 4%, #ffe37c 34%, #f5c845 68%, #fff0a0 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    filter: drop-shadow(0 14px 28px rgba(196,151,36,.25));
    animation: celebrationStarPulse 2.2s ease-in-out 2.55s infinite;
}

.celebration-star-note {
    position: absolute;
    z-index: 36;
    left: 50%;
    top: 51%;
    width: 47%;
    transform: translate(-50%,-50%);
    text-align: center;
    color: #5b4b20;
    font-size: clamp(15px, 4vw, 24px);
    font-weight: 950;
    line-height: 1.3;
    word-break: keep-all;
}

.celebration-spark {
    position: absolute;
    z-index: 38;
    color: #ffd65d;
    opacity: 0;
    filter: drop-shadow(0 0 10px rgba(255,214,93,.72));
    animation: celebrationSpark .8s ease forwards;
}
.cs1 { left:25%; top:19%; font-size:30px; animation-delay:1.45s; }
.cs2 { right:23%; top:21%; font-size:23px; animation-delay:1.58s; }
.cs3 { left:27%; top:49%; font-size:20px; animation-delay:1.72s; }
.cs4 { right:27%; top:52%; font-size:29px; animation-delay:1.84s; }

/* 모션이 끝난 뒤 남는 결과 카드 */
.eureka-reveal {
    position: relative;
    min-height: 380px;
    margin: 24px 0 10px 0;
    overflow: hidden;
    border-radius: 38px;
    text-align: center;
    background:
        radial-gradient(circle at 50% 48%, rgba(255,240,166,.56) 0%, rgba(255,240,166,0) 33%),
        linear-gradient(180deg, rgba(244,247,255,.96), rgba(255,246,252,.96));
    box-shadow: inset 0 0 60px rgba(255,255,255,.65);
}

.eureka-reveal-title {
    position: relative;
    z-index: 20;
    padding-top: 22px;
    color: #7772aa;
    font-size: 16px;
    font-weight: 950;
}

.final-cloud-sea {
    position: absolute;
    left: -5%;
    right: -5%;
    bottom: -30px;
    height: 155px;
    background:
        radial-gradient(circle at 8% 62%, #fff 0 58px, transparent 60px),
        radial-gradient(circle at 23% 45%, #f6f4ff 0 78px, transparent 80px),
        radial-gradient(circle at 42% 66%, #fff 0 68px, transparent 70px),
        radial-gradient(circle at 60% 42%, #f5f2ff 0 82px, transparent 84px),
        radial-gradient(circle at 79% 64%, #fff 0 72px, transparent 74px),
        radial-gradient(circle at 96% 45%, #f4f2ff 0 74px, transparent 76px);
    filter: drop-shadow(0 -6px 16px rgba(126,117,174,.08));
}

.final-star {
    position: absolute;
    z-index: 18;
    left: 50%;
    top: 49%;
    width: 230px;
    height: 220px;
    transform: translate(-50%,-50%);
}
.final-star-glyph {
    position: absolute;
    inset: 0;
    display:flex;
    align-items:center;
    justify-content:center;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 210px;
    font-weight: 900;
    line-height:1;
    background: linear-gradient(145deg, #fff6b9, #ffd95d 52%, #efbf3b 78%, #fff1a3);
    -webkit-background-clip:text;
    background-clip:text;
    color:transparent;
    filter:drop-shadow(0 12px 22px rgba(194,149,38,.20));
}
.final-star-note {
    position:absolute;
    z-index:20;
    left:50%;
    top:51%;
    width:122px;
    transform:translate(-50%,-50%);
    color:#5b4b20;
    font-size:16px;
    font-weight:950;
    line-height:1.3;
    word-break:keep-all;
    text-align:center;
}

.final-memory {
    position:absolute;
    z-index:17;
    min-width:105px;
    max-width:145px;
    padding:12px 14px;
    border-radius:999px;
    background:linear-gradient(180deg,#fff,#f0efff);
    box-shadow:0 9px 20px rgba(117,108,172,.11);
    color:#6b6882;
    font-size:12px;
    font-weight:850;
    line-height:1.3;
    word-break:keep-all;
}
.fm1 { left:4%; top:30%; }
.fm2 { right:4%; top:31%; }
.fm3 { left:7%; top:65%; }
.fm4 { right:7%; top:65%; }

.eureka-caption {
    position:absolute;
    z-index:25;
    left:0;
    right:0;
    bottom:15px;
    color:#8b86a6;
    font-size:12px;
}

@keyframes celebrationScene {
    0%   { opacity:0; visibility:visible; }
    6%   { opacity:1; }
    82%  { opacity:1; }
    100% { opacity:0; visibility:hidden; }
}
@keyframes celebrationTitle {
    from { opacity:0; transform:translateY(10px); }
    to   { opacity:1; transform:translateY(0); }
}
@keyframes cloudBurst {
    0%   { opacity:0; transform:translateY(42vh) scale(.72); }
    58%  { opacity:1; }
    82%  { opacity:1; transform:translateY(-12vh) scale(1.08); }
    100% { opacity:1; transform:translateY(-8vh) scale(1); }
}
@keyframes cloudBurstCenter {
    0%   { opacity:0; transform:translateY(45vh) scale(.72); }
    58%  { opacity:1; }
    82%  { opacity:1; transform:translateY(-7vh) scale(1.08); }
    100% { opacity:1; transform:translateY(-4vh) scale(1); }
}
@keyframes cloudDriftA {
    0%,100% { margin-left:0; margin-top:0; }
    50% { margin-left:9px; margin-top:-7px; }
}
@keyframes cloudDriftB {
    0%,100% { margin-left:0; margin-top:0; }
    50% { margin-left:-9px; margin-top:-5px; }
}
@keyframes memoryPop {
    0%   { opacity:0; transform:translateY(45px) scale(.65); }
    72%  { opacity:1; transform:translateY(-4px) scale(1.05); }
    100% { opacity:1; transform:translateY(0) scale(1); }
}
@keyframes celebrationGlow {
    0% { opacity:0; transform:translate(-50%,-50%) scale(.15); }
    100% { opacity:1; transform:translate(-50%,-50%) scale(1.35); }
}
@keyframes celebrationStar {
    0%   { opacity:0; transform:translate(-50%,45vh) scale(.18) rotate(-7deg); }
    65%  { opacity:1; transform:translate(-50%,-10px) scale(1.08) rotate(2deg); }
    82%  { opacity:1; transform:translate(-50%,4px) scale(.98) rotate(-1deg); }
    100% { opacity:1; transform:translate(-50%,0) scale(1) rotate(0); }
}
@keyframes celebrationStarPulse {
    0%,100% { transform:scale(1); }
    50% { transform:scale(1.045); }
}
@keyframes celebrationSpark {
    0% { opacity:0; transform:scale(.1) rotate(-25deg); }
    58% { opacity:1; transform:scale(1.35) rotate(8deg); }
    100% { opacity:.95; transform:scale(1) rotate(0); }
}



/* =========================================================
   EUREKA asset-based visual polish
   ========================================================= */
.eureka-celebration,
.eureka-reveal {
    font-family: "Pretendard", "Apple SD Gothic Neo", "Noto Sans KR", system-ui, sans-serif;
}

.asset-cloud {
    position: absolute;
    z-index: 15;
    width: clamp(260px, 48vw, 520px);
    height: auto;
    opacity: 0;
    transform: translateY(45vh) scale(.72);
    filter: drop-shadow(0 18px 28px rgba(111,103,166,.11));
    will-change: transform, opacity;
}
.ac1 { left:-14%; bottom:-6%; animation: assetCloudRiseA 2.20s cubic-bezier(.16,.82,.24,1.06) .02s forwards, assetCloudFloatA 4.4s ease-in-out 2.3s infinite; }
.ac2 { left:8%; bottom:-11%; animation: assetCloudRiseB 2.35s cubic-bezier(.16,.82,.24,1.06) .10s forwards, assetCloudFloatB 4.8s ease-in-out 2.5s infinite; }
.ac3 { left:33%; bottom:-14%; width:clamp(300px,54vw,590px); animation: assetCloudRiseC 2.45s cubic-bezier(.16,.82,.24,1.06) .16s forwards, assetCloudFloatA 5.0s ease-in-out 2.6s infinite; }
.ac4 { right:7%; bottom:-10%; animation: assetCloudRiseB 2.32s cubic-bezier(.16,.82,.24,1.06) .22s forwards, assetCloudFloatB 4.6s ease-in-out 2.55s infinite; }
.ac5 { right:-15%; bottom:-5%; animation: assetCloudRiseA 2.24s cubic-bezier(.16,.82,.24,1.06) .28s forwards, assetCloudFloatA 4.3s ease-in-out 2.55s infinite; }

.asset-star-wrap {
    position:absolute;
    z-index:34;
    left:50%;
    top:46%;
    width:min(55vw, 390px);
    aspect-ratio:1;
    transform:translate(-50%, 48vh) scale(.2);
    opacity:0;
    animation:assetStarRise 1.38s cubic-bezier(.17,.88,.26,1.20) 1.12s forwards;
    will-change: transform, opacity;
}
.asset-star-img {
    position:absolute;
    inset:0;
    width:100%;
    height:100%;
    object-fit:contain;
    animation:assetStarBreathe 3.0s ease-in-out 2.6s infinite;
}
.asset-star-note {
    position:absolute;
    z-index:40;
    left:50%;
    top:50.5%;
    width:48%;
    transform:translate(-50%,-50%);
    text-align:center;
    color:#665022;
    font-size:clamp(16px,4.2vw,25px);
    font-weight:850;
    letter-spacing:-.03em;
    line-height:1.28;
    word-break:keep-all;
    text-shadow:0 1px 0 rgba(255,255,255,.34);
}

.memory-cloud {
    background:rgba(255,255,255,.88) !important;
    backdrop-filter:blur(10px);
    -webkit-backdrop-filter:blur(10px);
    border:1px solid rgba(255,255,255,.92) !important;
    color:#6d6888 !important;
    box-shadow:0 12px 30px rgba(107,98,160,.10) !important;
    font-weight:800 !important;
}
.eureka-celebration-title {
    color:#706aa6 !important;
    font-weight:850 !important;
    letter-spacing:-.025em !important;
    text-shadow:0 1px 10px rgba(255,255,255,.82);
}

.final-asset-cloud {
    position:absolute;
    z-index:8;
    width:260px;
    height:auto;
    opacity:.96;
    filter:drop-shadow(0 10px 20px rgba(111,103,166,.10));
}
.fac1 { left:-50px; bottom:-25px; }
.fac2 { left:100px; bottom:-42px; }
.fac3 { right:90px; bottom:-38px; }
.fac4 { right:-55px; bottom:-22px; }

.final-asset-star {
    position:absolute;
    z-index:20;
    left:50%;
    top:48%;
    width:250px;
    height:250px;
    transform:translate(-50%,-50%);
}
.final-asset-star img {
    width:100%;
    height:100%;
    object-fit:contain;
}
.final-asset-star-note {
    position:absolute;
    left:50%;
    top:50.5%;
    width:48%;
    transform:translate(-50%,-50%);
    color:#665022;
    font-size:17px;
    font-weight:850;
    line-height:1.28;
    word-break:keep-all;
    text-align:center;
}

@keyframes assetCloudRiseA {
    0% { opacity:0; transform:translateY(46vh) scale(.72); }
    62% { opacity:1; }
    84% { opacity:1; transform:translateY(-12vh) scale(1.06); }
    100% { opacity:1; transform:translateY(-8vh) scale(1); }
}
@keyframes assetCloudRiseB {
    0% { opacity:0; transform:translateY(48vh) scale(.70); }
    62% { opacity:1; }
    84% { opacity:1; transform:translateY(-6vh) scale(1.05); }
    100% { opacity:1; transform:translateY(-3vh) scale(1); }
}
@keyframes assetCloudRiseC {
    0% { opacity:0; transform:translateY(50vh) scale(.72); }
    62% { opacity:1; }
    84% { opacity:1; transform:translateY(-2vh) scale(1.07); }
    100% { opacity:1; transform:translateY(1vh) scale(1); }
}
@keyframes assetCloudFloatA {
    0%,100% { margin-top:0; margin-left:0; }
    50% { margin-top:-9px; margin-left:7px; }
}
@keyframes assetCloudFloatB {
    0%,100% { margin-top:0; margin-left:0; }
    50% { margin-top:-7px; margin-left:-7px; }
}
@keyframes assetStarRise {
    0% { opacity:0; transform:translate(-50%,48vh) scale(.20) rotate(-8deg); }
    66% { opacity:1; transform:translate(-50%,-12px) scale(1.08) rotate(2deg); }
    84% { opacity:1; transform:translate(-50%,4px) scale(.98) rotate(-1deg); }
    100% { opacity:1; transform:translate(-50%,0) scale(1) rotate(0); }
}
@keyframes assetStarBreathe {
    0%,100% { transform:scale(1); filter:drop-shadow(0 12px 22px rgba(206,164,48,.18)); }
    50% { transform:scale(1.035); filter:drop-shadow(0 16px 32px rgba(255,217,90,.36)); }
}

@media (max-width: 640px) {
    .eureka-celebration-title { top:7vh; font-size:18px !important; }
    .memory-cloud { min-width:104px; max-width:142px; padding:13px 14px; font-size:12px !important; }
    .mem1 { left:3%; top:25%; }
    .mem2 { right:3%; top:27%; }
    .mem3 { left:4%; top:63%; }
    .mem4 { right:4%; top:64%; }
    .asset-star-wrap { width:min(72vw, 330px); top:47%; }
}


/* =========================================================
   생각 키워드를 '구름 위'에 표시
   ========================================================= */
.memory-cloud {
    position:absolute !important;
    z-index:30 !important;
    width:clamp(130px, 24vw, 200px) !important;
    min-width:0 !important;
    max-width:none !important;
    padding:0 !important;
    border:0 !important;
    border-radius:0 !important;
    background:transparent !important;
    box-shadow:none !important;
    opacity:0;
    transform:translateY(48px) scale(.72);
    animation-name:memoryCloudAssetPop;
    animation-duration:.85s;
    animation-timing-function:cubic-bezier(.18,.85,.28,1.15);
    animation-fill-mode:forwards;
}
.memory-cloud img {
    display:block;
    width:100%;
    height:auto;
    filter:drop-shadow(0 12px 24px rgba(109,99,163,.12));
}
.memory-cloud .cloud-word {
    position:absolute;
    z-index:3;
    left:50%;
    top:57%;
    width:66%;
    transform:translate(-50%,-50%);
    text-align:center;
    color:#625f7b;
    font-size:clamp(12px,2.8vw,15px);
    font-weight:850;
    letter-spacing:-.03em;
    line-height:1.22;
    word-break:keep-all;
    text-shadow:0 1px 5px rgba(255,255,255,.92);
}

.mem1 { left:1%;  top:21%; animation-delay:.55s; }
.mem2 { right:1%; top:22%; animation-delay:.70s; }
.mem3 { left:3%;  top:53%; animation-delay:.88s; }
.mem4 { right:3%; top:54%; animation-delay:1.03s; }

/* 더 많은 뭉게구름 레이어 */
.asset-cloud.ac6 {
    left:-4%;
    bottom:20%;
    width:clamp(190px,35vw,360px);
    animation:assetCloudRiseB 2.20s cubic-bezier(.16,.82,.24,1.06) .34s forwards,
              assetCloudFloatA 4.6s ease-in-out 2.5s infinite;
}
.asset-cloud.ac7 {
    right:-5%;
    bottom:22%;
    width:clamp(190px,35vw,360px);
    animation:assetCloudRiseB 2.26s cubic-bezier(.16,.82,.24,1.06) .40s forwards,
              assetCloudFloatB 4.7s ease-in-out 2.6s infinite;
}
.asset-cloud.ac8 {
    left:21%;
    bottom:16%;
    width:clamp(190px,34vw,350px);
    animation:assetCloudRiseA 2.32s cubic-bezier(.16,.82,.24,1.06) .28s forwards,
              assetCloudFloatA 4.9s ease-in-out 2.5s infinite;
}
.asset-cloud.ac9 {
    right:21%;
    bottom:15%;
    width:clamp(190px,34vw,350px);
    animation:assetCloudRiseA 2.28s cubic-bezier(.16,.82,.24,1.06) .36s forwards,
              assetCloudFloatB 4.8s ease-in-out 2.6s infinite;
}

@keyframes memoryCloudAssetPop {
    0%   { opacity:0; transform:translateY(48px) scale(.70); }
    72%  { opacity:1; transform:translateY(-5px) scale(1.05); }
    100% { opacity:1; transform:translateY(0) scale(1); }
}

/* 3번째 선택 뒤 나타나는 여행 체크포인트 */
.journey-checkpoint {
    margin:30px 0 18px 0;
    padding:26px 22px;
    border-radius:30px;
    text-align:center;
    background:
        radial-gradient(circle at 50% 0%, rgba(255,255,255,.98), rgba(255,255,255,.72)),
        linear-gradient(135deg, rgba(235,242,255,.92), rgba(250,239,255,.92));
    border:1px solid rgba(255,255,255,.96);
    box-shadow:0 14px 38px rgba(104,96,155,.10);
}
.journey-checkpoint .train {
    font-size:34px;
    margin-bottom:6px;
}
.journey-checkpoint .title {
    color:#56536e;
    font-size:22px;
    font-weight:900;
    letter-spacing:-.04em;
}
.journey-checkpoint .sub {
    color:#858197;
    font-size:14px;
    line-height:1.65;
    margin-top:8px;
}

@media (max-width:640px) {
    .memory-cloud {
        width:132px !important;
    }
    .memory-cloud .cloud-word {
        width:62%;
        font-size:11.5px;
    }
    .mem1 { left:-2%; top:20%; }
    .mem2 { right:-2%; top:22%; }
    .mem3 { left:-1%; top:57%; }
    .mem4 { right:-1%; top:58%; }

    .journey-checkpoint {
        padding:22px 16px;
    }
    .journey-checkpoint .title {
        font-size:19px;
    }
}


/* =========================================================
   EUREKA 구름 밀도/크기 강화
   ========================================================= */
.asset-cloud {
    width: clamp(320px, 58vw, 680px) !important;
    filter: drop-shadow(0 22px 34px rgba(111,103,166,.12)) !important;
}
.ac1 { left:-24% !important; bottom:-3% !important; }
.ac2 { left:0% !important; bottom:-10% !important; }
.ac3 { left:24% !important; bottom:-14% !important; width:clamp(380px,66vw,760px) !important; }
.ac4 { right:-1% !important; bottom:-9% !important; }
.ac5 { right:-25% !important; bottom:-2% !important; }

.asset-cloud.ac6 {
    left:-10% !important;
    bottom:23% !important;
    width:clamp(280px,50vw,560px) !important;
}
.asset-cloud.ac7 {
    right:-10% !important;
    bottom:25% !important;
    width:clamp(280px,50vw,560px) !important;
}
.asset-cloud.ac8 {
    left:16% !important;
    bottom:18% !important;
    width:clamp(280px,48vw,540px) !important;
}
.asset-cloud.ac9 {
    right:16% !important;
    bottom:18% !important;
    width:clamp(280px,48vw,540px) !important;
}

/* 키워드 구름도 조금 키우기 */
.memory-cloud {
    width:clamp(150px, 28vw, 220px) !important;
}
.memory-cloud .cloud-word {
    font-size:clamp(13px, 3.2vw, 16px) !important;
    width:68% !important;
}

/* 모바일에서 구름이 화면을 더 꽉 채우도록 */
@media (max-width: 640px) {
    .asset-cloud {
        width: 76vw !important;
    }
    .ac1 { left:-28% !important; }
    .ac2 { left:-5% !important; }
    .ac3 { left:12% !important; width:86vw !important; }
    .ac4 { right:-5% !important; }
    .ac5 { right:-28% !important; }

    .asset-cloud.ac6,
    .asset-cloud.ac7,
    .asset-cloud.ac8,
    .asset-cloud.ac9 {
        width:66vw !important;
    }

    .memory-cloud {
        width:145px !important;
    }
}


/* =========================================================
   생각 흐름 기차
   ========================================================= */
.train-flow-card {
    margin:16px 0 20px 0;
    padding:20px 18px;
    border-radius:26px;
    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,.96),
            rgba(245,240,255,.93)
        );
    border:1px solid rgba(255,255,255,.98);
    box-shadow:0 12px 30px rgba(101,93,152,.09);
}

.train-flow-label {
    text-align:center;
    color:#716ca1;
    font-size:14px;
    font-weight:900;
    margin-bottom:14px;
}

.train-flow-track {
    display:flex;
    flex-wrap:wrap;
    justify-content:center;
    align-items:center;
    gap:7px;
}

.train-thought {
    display:inline-block;
    padding:9px 13px;
    border-radius:999px;
    background:
        linear-gradient(
            180deg,
            #ffffff,
            #f1efff
        );
    color:#626078;
    font-size:13px;
    font-weight:800;
    line-height:1.3;
    box-shadow:0 6px 15px rgba(101,93,152,.08);
}

.train-arrow {
    color:#b09bd8;
    font-size:18px;
    font-weight:900;
}

@media (max-width:640px) {
    .train-flow-card {
        padding:18px 12px;
    }

    .train-thought {
        font-size:12px;
        padding:8px 10px;
    }
}


/* =========================================================
   EUREKA: 큰 구름 자체에 키워드 표시
   ========================================================= */
.big-labeled-cloud {
    position:absolute;
    z-index:28;
    width:clamp(280px, 48vw, 520px);
    opacity:0;
    transform:translateY(44vh) scale(.72);
    will-change:transform, opacity;
}
.big-labeled-cloud img {
    display:block;
    width:100%;
    height:auto;
    filter:drop-shadow(0 18px 30px rgba(111,103,166,.13));
}
.big-cloud-word {
    position:absolute;
    z-index:4;
    left:50%;
    top:58%;
    width:54%;
    transform:translate(-50%,-50%);
    text-align:center;
    color:#625f7b;
    font-size:clamp(15px,3.4vw,21px);
    font-weight:900;
    letter-spacing:-.035em;
    line-height:1.25;
    word-break:keep-all;
    text-shadow:0 1px 7px rgba(255,255,255,.95);
}

.blc1 {
    left:-13%;
    top:18%;
    animation:assetCloudRiseA 2.20s cubic-bezier(.16,.82,.24,1.06) .18s forwards,
              assetCloudFloatA 4.5s ease-in-out 2.4s infinite;
}
.blc2 {
    right:-13%;
    top:19%;
    animation:assetCloudRiseA 2.25s cubic-bezier(.16,.82,.24,1.06) .28s forwards,
              assetCloudFloatB 4.7s ease-in-out 2.5s infinite;
}
.blc3 {
    left:-10%;
    top:54%;
    animation:assetCloudRiseB 2.28s cubic-bezier(.16,.82,.24,1.06) .38s forwards,
              assetCloudFloatA 4.8s ease-in-out 2.6s infinite;
}
.blc4 {
    right:-10%;
    top:55%;
    animation:assetCloudRiseB 2.30s cubic-bezier(.16,.82,.24,1.06) .48s forwards,
              assetCloudFloatB 4.6s ease-in-out 2.7s infinite;
}

/* 결과 화면도 한 구름 = 한 키워드 */
.final-labeled-cloud {
    position:absolute;
    z-index:16;
    width:230px;
}
.final-labeled-cloud img {
    display:block;
    width:100%;
    height:auto;
    filter:drop-shadow(0 10px 20px rgba(111,103,166,.10));
}
.final-cloud-word {
    position:absolute;
    left:50%;
    top:58%;
    width:56%;
    transform:translate(-50%,-50%);
    text-align:center;
    color:#66627f;
    font-size:13px;
    font-weight:900;
    line-height:1.25;
    word-break:keep-all;
}
.flc1 { left:-38px; top:21%; }
.flc2 { right:-38px; top:22%; }
.flc3 { left:-26px; top:58%; }
.flc4 { right:-26px; top:59%; }

/* 타로 primary CTA를 더 강조 */
div[data-testid="stButton"] > button[kind="primary"] {
    min-height:72px !important;
    font-size:17px !important;
    font-weight:900 !important;
    border-radius:999px !important;
    box-shadow:
        0 14px 34px rgba(153,104,205,.28),
        0 0 0 4px rgba(255,255,255,.35) !important;
    transform:translateY(0);
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    transform:translateY(-3px) scale(1.01);
    box-shadow:
        0 18px 40px rgba(153,104,205,.34),
        0 0 0 5px rgba(255,255,255,.42) !important;
}

@media (max-width:640px) {
    .big-labeled-cloud {
        width:68vw;
    }
    .big-cloud-word {
        width:52%;
        font-size:14px;
    }
    .blc1 { left:-25%; top:18%; }
    .blc2 { right:-25%; top:20%; }
    .blc3 { left:-22%; top:58%; }
    .blc4 { right:-22%; top:59%; }

    .final-labeled-cloud {
        width:170px;
    }
    .final-cloud-word {
        font-size:11.5px;
    }
    .flc1 { left:-45px; }
    .flc2 { right:-45px; }
    .flc3 { left:-38px; }
    .flc4 { right:-38px; }
}


/* =========================================================
   타로 CTA - 보라색 강조
   ========================================================= */
div[data-testid="stButton"] button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
    min-height: 74px !important;
    border-radius: 999px !important;
    border: 1px solid rgba(190,155,255,.85) !important;
    background:
        linear-gradient(
            135deg,
            #8d63ff 0%,
            #a66cff 48%,
            #c77dff 100%
        ) !important;
    color: #ffffff !important;
    font-size: 17px !important;
    font-weight: 900 !important;
    box-shadow:
        0 14px 34px rgba(126,82,210,.30),
        0 0 0 4px rgba(255,255,255,.38) !important;
}

div[data-testid="stButton"] button[kind="primary"] p,
button[data-testid="stBaseButton-primary"] p {
    color: #ffffff !important;
    font-weight: 900 !important;
}

div[data-testid="stButton"] button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-3px) scale(1.01) !important;
    background:
        linear-gradient(
            135deg,
            #7f55ef 0%,
            #995ff4 48%,
            #bd70f4 100%
        ) !important;
    box-shadow:
        0 18px 40px rgba(126,82,210,.38),
        0 0 0 5px rgba(255,255,255,.42) !important;
}


/* =========================================================
   EUREKA 구름 간격 보정 - 화면 밖 잘림 방지
   ========================================================= */
.big-labeled-cloud {
    width: clamp(250px, 34vw, 430px) !important;
}

.blc1 {
    left: 4% !important;
    top: 20% !important;
}
.blc2 {
    right: 4% !important;
    top: 21% !important;
}
.blc3 {
    left: 6% !important;
    top: 57% !important;
}
.blc4 {
    right: 6% !important;
    top: 58% !important;
}

.big-cloud-word {
    width: 58% !important;
    font-size: clamp(15px, 2.3vw, 20px) !important;
}

.final-labeled-cloud {
    width: 205px !important;
}
.flc1 { left: 2% !important; top: 23% !important; }
.flc2 { right: 2% !important; top: 24% !important; }
.flc3 { left: 4% !important; top: 59% !important; }
.flc4 { right: 4% !important; top: 60% !important; }

@media (max-width: 640px) {
    .big-labeled-cloud {
        width: 56vw !important;
    }

    .blc1 { left: -2% !important; top: 20% !important; }
    .blc2 { right: -2% !important; top: 21% !important; }
    .blc3 { left: 0% !important; top: 58% !important; }
    .blc4 { right: 0% !important; top: 59% !important; }

    .big-cloud-word {
        width: 56% !important;
        font-size: 13px !important;
    }

    .final-labeled-cloud {
        width: 150px !important;
    }

    .flc1 { left: -4% !important; }
    .flc2 { right: -4% !important; }
    .flc3 { left: -2% !important; }
    .flc4 { right: -2% !important; }
}


/* Readability update: larger selectable thought paths and action labels */
div[data-testid="stButton"] > button,
div.stButton > button {
    font-size: 18px !important;
    line-height: 1.55 !important;
    padding: 15px 20px !important;
    min-height: 64px !important;
}
div[data-testid="stButton"] > button p,
div.stButton > button p {
    font-size: inherit !important;
    line-height: inherit !important;
}
.section-title { font-size: 25px !important; }
.section-sub { font-size: 16px !important; line-height: 1.65 !important; }
.fairy-text { font-size: 18px !important; }
.current-text { font-size: 20px !important; }
@media (max-width: 640px) {
    div[data-testid="stButton"] > button,
    div.stButton > button {
        font-size: 17px !important;
        padding: 13px 16px !important;
    }
}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# 헤더
# =========================================================
st.markdown(
    '<div class="logo">'
    '☁️ Daydream Circuit ✨'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="tagline">'
    'A wandering thought might lead to a shining star! ✨'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# 시작 화면
# =========================================================
if not st.session_state.started:

    if FAIRY_IMAGE.exists():

        left, middle, right = st.columns(
            [1, 2.2, 1]
        )

        with middle:

            st.image(
                str(FAIRY_IMAGE),
                use_container_width=True
            )

    else:

        st.warning(
            "Cloud Fairy image not found ☁️"
        )

        st.code(
            str(FAIRY_IMAGE)
        )


    st.markdown(
        '<div class="fairy-card">'
        '<div class="fairy-name">'
        '☁️ Cloud Fairy'
        '</div>'
        '<div class="fairy-text">'
        'Share one thought floating through your mind.<br>'
        '<b>Your cloud train of thoughts is leaving now! 🚂☁️</b>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


    first_thought = st.text_input(
        "First thought",
        placeholder=(
            "e.g., I wish I could drop everything and travel"
        ),
        label_visibility="collapsed"
    )


    if st.button(
        "✨ Start exploring",
        use_container_width=True
    ):

        if not first_thought.strip():

            st.warning(
                "Share just one little thought ☁️"
            )

        else:

            try:

                first_path = [
                    first_thought.strip()
                ]

                with st.spinner(
                    "☁️ Creating your first thought cloud..."
                ):

                    comment, suggestions = (
                        explore_thoughts(
                            first_path
                        )
                    )

                st.session_state.thought_path = (
                    first_path
                )

                st.session_state.fairy_comment = (
                    comment
                )

                st.session_state.suggestions = (
                    suggestions
                )

                st.session_state.started = True
                st.session_state.analysis = ""
                st.session_state.eureka_mode = False
                st.session_state.eureka_note = ""
                st.session_state.eureka_saved = False
                st.session_state.tarot_card = None
                st.session_state.journey_checkpoint = 3
                st.session_state.journey_finish_mode = False
                st.session_state.train_boarded = False
                st.session_state.train_flow_open = False

                st.rerun()


            except Exception as e:

                st.error(
                    "The Cloud Fairy is hiding in a cloud for a moment ☁️"
                )

                st.code(
                    str(e)
                )


# =========================================================
# 탐험 화면
# =========================================================
else:

    current = (
        st.session_state.thought_path[-1]
    )

    path = (
        st.session_state.thought_path
    )


    # =====================================================
    # 전용 화면 모드
    # 기차/EUREKA를 누른 뒤에는 탐험 화면을 쌓지 않고
    # 화면 자체를 전환한다.
    # =====================================================

    if (
        st.session_state.journey_finish_mode
        or st.session_state.eureka_saved
    ):

        render_eureka_screen(
            path
        )

        st.stop()


    if st.session_state.train_boarded:

        # -------------------------------------------------
        # 생각 흐름 긴 글 화면
        # -------------------------------------------------
        if st.session_state.train_flow_open:

            st.markdown(
                '<div style="height:12px;"></div>'
                '<div class="section-title">'
                '✨ Ready to connect the dots?'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="section-sub">'
                'Here is how your thoughts wandered from the beginning. '
                'The Cloud Fairy connected the dots.'
                '</div>',
                unsafe_allow_html=True
            )

            if not st.session_state.analysis:

                with st.spinner(
                    "🪄 Finding connections in your thought journey..."
                ):

                    try:

                        st.session_state.analysis = (
                            find_hidden_connection(
                                path
                            )
                        )

                    except Exception:

                        st.session_state.analysis = (
                            fallback_hidden_connection(
                                path
                            )
                        )

            analysis = html.escape(
                st.session_state.analysis
            ).replace(
                "\\n",
                "<br>"
            )

            flow_left, flow_right = st.columns(
                [1, 3],
                vertical_alignment="center"
            )

            with flow_left:

                if FAIRY_IMAGE.exists():

                    st.image(
                        str(
                            FAIRY_IMAGE
                        ),
                        use_container_width=True
                    )

                else:

                    st.markdown(
                        "☁️🪄"
                    )

            with flow_right:

                st.markdown(
                    '<div class="fairy-card">'
                    '<div class="fairy-name">'
                    '☁️ The Cloud Fairy’s discovery ✨'
                    '</div>'
                    '<div class="fairy-text">'
                    f'{analysis}'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

            flow_eureka_col, flow_more_col = st.columns(2)

            with flow_eureka_col:

                if st.button(
                    "⭐ EUREKA! You found a star!",
                    key="flow_screen_eureka",
                    use_container_width=True
                ):

                    st.session_state.journey_finish_mode = True
                    st.session_state.train_boarded = False
                    st.session_state.train_flow_open = False
                    st.rerun()

            with flow_more_col:

                if st.button(
                    "☁️ Keep exploring",
                    key="flow_screen_continue",
                    use_container_width=True
                ):

                    # 탐험 화면으로 돌아가되,
                    # 같은 체크포인트가 즉시 다시 뜨지 않도록
                    # 다음 3번 선택 후 다시 제안
                    st.session_state.journey_checkpoint = (
                        max(
                            st.session_state.journey_checkpoint,
                            max(0, len(path) - 1) + 3
                        )
                    )

                    st.session_state.train_boarded = False
                    st.session_state.train_flow_open = False
                    st.session_state.journey_finish_mode = False
                    st.session_state.analysis = ""
                    st.rerun()

            st.stop()


        # -------------------------------------------------
        # 기차 탑승 직후 화면
        # -------------------------------------------------
        st.markdown(
            '<div style="height:18px;"></div>'
            '<div class="journey-checkpoint">'
            '<div class="train">🚂✨</div>'
            '<div class="title">On the way to finding a star ✨</div>'
            '<div class="sub">'
            'Choose one option for your next step.<br>'
            'Review your thought journey or save an EUREKA right away.'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        train_flow_col, train_eureka_col = st.columns(
            2
        )

        with train_flow_col:

            if st.button(
                "🛤️ Review your thought journey",
                key="dedicated_train_flow",
                use_container_width=True
            ):

                st.session_state.analysis = ""

                with st.spinner(
                    "🪄 Finding connections in your thought journey..."
                ):

                    try:

                        st.session_state.analysis = (
                            find_hidden_connection(
                                path
                            )
                        )

                    except Exception:

                        st.session_state.analysis = (
                            fallback_hidden_connection(
                                path
                            )
                        )

                st.session_state.train_flow_open = True
                st.rerun()

        with train_eureka_col:

            if st.button(
                "⭐ EUREKA! You found a star!",
                key="dedicated_train_eureka",
                use_container_width=True
            ):

                st.session_state.journey_finish_mode = True
                st.session_state.train_boarded = False
                st.session_state.train_flow_open = False
                st.rerun()

        st.stop()


    # =====================================================
    # API fallback 안내
    # =====================================================
    if st.session_state.api_notice:

        st.info(
            st.session_state.api_notice,
            icon="☁️"
        )


    # =====================================================
    # Cloud Fairy 코멘트
    # =====================================================
    fairy_col, comment_col = st.columns(
        [1, 2.8],
        vertical_alignment="center"
    )


    with fairy_col:

        if FAIRY_IMAGE.exists():

            st.image(
                str(FAIRY_IMAGE),
                use_container_width=True
            )

        else:

            st.markdown(
                "☁️🪄"
            )


    with comment_col:

        comment = html.escape(
            st.session_state.fairy_comment
        )

        st.markdown(
            '<div class="fairy-card">'
            '<div class="fairy-name">'
            '☁️ Cloud Fairy'
            '</div>'
            f'<div class="fairy-text">'
            f'{comment}'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )


    # =====================================================
    # 별자리 사고 궤적
    # =====================================================
    constellation_html = ""


    for i, thought in enumerate(
        path
    ):

        safe_thought = html.escape(
            thought
        )


        if i == len(path) - 1:

            constellation_html += (
                '<span class="star-current">'
                f'⭐ {safe_thought}'
                '</span>'
            )

        else:

            constellation_html += (
                '<span class="star-node">'
                f'✦ {safe_thought}'
                '</span>'
            )


        if i < len(path) - 1:

            constellation_html += (
                '<span class="star-line">'
                '⋯ ✧ ⋯'
                '</span>'
            )


    st.markdown(
        '<div class="constellation-box">'
        '<div class="constellation-title">'
        '✨ My constellation of thoughts'
        '</div>'
        '<div class="constellation">'
        f'{constellation_html}'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


    # =====================================================
    # 망상지도
    # =====================================================
    st.markdown(
        '<div class="section-title">'
        '☁️ On your mind now'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">'
        'Choose a cloud that catches your eye.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sparkles">'
        '✦ ✧ ⋆ ✦'
        '</div>',
        unsafe_allow_html=True
    )


    # 위 2개
    top_left, top_gap, top_right = (
        st.columns(
            [1.35, 0.35, 1.35]
        )
    )


    with top_left:

        if st.button(
            f"☁️\n\n"
            f"{st.session_state.suggestions[0]}",
            key=f"cloud_{len(path)}_0",
            use_container_width=True
        ):

            choose_thought(
                st.session_state.suggestions[0]
            )


    with top_right:

        if st.button(
            f"☁️\n\n"
            f"{st.session_state.suggestions[1]}",
            key=f"cloud_{len(path)}_1",
            use_container_width=True
        ):

            choose_thought(
                st.session_state.suggestions[1]
            )


    # 가운데
    (
        left_cloud,
        center_cloud,
        right_cloud
    ) = st.columns(
        [1.15, 1.5, 1.15],
        vertical_alignment="center"
    )


    with left_cloud:

        if st.button(
            f"☁️\n\n"
            f"{st.session_state.suggestions[2]}",
            key=f"cloud_{len(path)}_2",
            use_container_width=True
        ):

            choose_thought(
                st.session_state.suggestions[2]
            )


    with center_cloud:

        safe_current = html.escape(
            current
        )

        st.markdown(
            '<div class="current-thought">'
            '<div class="current-label">'
            '✨ My current thought'
            '</div>'
            '<div class="current-text">'
            f'{safe_current}'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )


    with right_cloud:

        if st.button(
            f"☁️\n\n"
            f"{st.session_state.suggestions[3]}",
            key=f"cloud_{len(path)}_3",
            use_container_width=True
        ):

            choose_thought(
                st.session_state.suggestions[3]
            )


    # 아래 2개
    (
        bottom_left,
        bottom_gap,
        bottom_right
    ) = st.columns(
        [1.35, 0.35, 1.35]
    )


    with bottom_left:

        if st.button(
            f"☁️\n\n"
            f"{st.session_state.suggestions[4]}",
            key=f"cloud_{len(path)}_4",
            use_container_width=True
        ):

            choose_thought(
                st.session_state.suggestions[4]
            )


    with bottom_right:

        if st.button(
            f"☁️\n\n"
            f"{st.session_state.suggestions[5]}",
            key=f"cloud_{len(path)}_5",
            use_container_width=True
        ):

            choose_thought(
                st.session_state.suggestions[5]
            )


    # =====================================================
    # 생각 여행 체크포인트
    # First thought 이후 구름을 3번 누를 때마다 등장
    # =====================================================
    selections_count = max(0, len(path) - 1)

    if (
        selections_count >= st.session_state.journey_checkpoint
        and not st.session_state.eureka_saved
    ):

        # -------------------------------------------------
        # 아직 기차에 타기 전
        # -------------------------------------------------
        if not st.session_state.train_boarded:

            st.markdown(
                '<div class="journey-checkpoint">'
                '<div class="train">🚂☁️</div>'
                '<div class="title">Ready to hop off the cloud train and catch a star?</div>'
                '<div class="sub">'
                'Take a moment to look back at where your thoughts have traveled.<br>'
                'Or keep wandering if you are not ready to stop. ☁️'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )

            train_col, more_col = st.columns(2)

            with train_col:
                if st.button(
                    "⭐ Catch today’s star",
                    key=f"board_train_{len(path)}",
                    use_container_width=True
                ):
                    st.session_state.train_boarded = True
                    st.session_state.train_flow_open = False
                    st.rerun()

            with more_col:
                if st.button(
                    "☁️ Keep riding the cloud train",
                    key=f"more_thoughts_{len(path)}",
                    use_container_width=True
                ):
                    st.session_state.journey_checkpoint += 3
                    st.session_state.train_boarded = False
                    st.session_state.train_flow_open = False
                    st.rerun()


    # =====================================================
    # 직접 딴생각
    # =====================================================
    st.markdown(
        '<div class="section-title">'
        '💭 A new thought popped up?'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">'
        'It is okay to take a path the AI did not suggest.'
        '</div>',
        unsafe_allow_html=True
    )


    custom = st.text_input(
        "Your own thought",
        placeholder=(
            "Write down the thought that just popped into your mind"
        ),
        label_visibility="collapsed",
        key=f"custom_{len(path)}"
    )


    if st.button(
        "☁️ Explore this new thought",
        key=f"custom_button_{len(path)}",
        use_container_width=True
    ):

        if not custom.strip():

            st.warning(
                "Enter your new thought ☁️"
            )

        else:

            choose_thought(
                custom.strip()
            )

    # =====================================================
    # 언제든 Next step로 넘어가기
    # '딴 생각으로 새기' 바로 아래
    # =====================================================
    next_spacer, next_button_col = st.columns(
        [2.6, 1.4]
    )

    with next_button_col:

        if st.button(
            "Next step →",
            key=f"next_step_{len(path)}",
            use_container_width=True
        ):

            st.session_state.train_boarded = True
            st.session_state.train_flow_open = False
            st.session_state.journey_finish_mode = False
            st.rerun()