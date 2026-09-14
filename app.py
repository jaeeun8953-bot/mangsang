import streamlit as st
from google import genai
from pathlib import Path
import json
import html
import time
import random


# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="망상회로",
    page_icon="☁️",
    layout="centered"
)

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

MODEL = "gemini-3.6-flash"

BASE_DIR = Path(__file__).resolve().parent
FAIRY_IMAGE = BASE_DIR / "cloud_fairy.png"
TAROT_DIR = BASE_DIR


# =========================================================
# 구름요정 타로 22장
# =========================================================
TAROT_CARDS = [
    {
        "name": "THE FOOL",
        "ko": "바보",
        "image": "00_fool.png",
        "meaning": "새로운 시작, 자유로운 발걸음, 아직 정해지지 않은 가능성을 상징해.",
        "ending": (
            "아직 모든 길을 알고 시작할 필요는 없어. "
            "오늘 떠오른 생각 중 하나가 예상하지 못한 곳으로 데려갈 수도 있으니까. "
            "조금 서툴러도 네가 가보고 싶은 방향을 응원할게. ☁️"
        ),
    },
    {
        "name": "THE MAGICIAN",
        "ko": "마법사",
        "image": "01_magician.png",
        "meaning": "가능성, 시작할 수 있는 힘, 이미 가지고 있는 자원을 상징해.",
        "ending": (
            "생각보다 네 손에는 이미 많은 것이 있을지도 몰라. "
            "오늘 떠다닌 생각들도 언젠가 무언가를 만드는 재료가 될 수 있어. "
            "네가 만들어갈 다음 장면을 응원할게. 🪄"
        ),
    },
    {
        "name": "THE HIGH PRIESTESS",
        "ko": "여사제",
        "image": "02_high_priestess.png",
        "meaning": "직감, 조용한 내면의 목소리, 아직 말로 설명하기 어려운 감각을 상징해.",
        "ending": (
            "꼭 모든 생각에 바로 이름을 붙이지 않아도 괜찮아. "
            "이유는 모르겠는데 계속 마음에 남는 생각도 있으니까. "
            "네 안에서 천천히 선명해질 때까지 지켜봐 줄게. 🌙"
        ),
    },
    {
        "name": "THE EMPRESS",
        "ko": "여황제",
        "image": "03_empress.png",
        "meaning": "풍요, 창조, 편안함과 자라나는 가능성을 상징해.",
        "ending": (
            "좋은 생각은 억지로 잡아당기지 않아도 천천히 자라나기도 해. "
            "오늘 발견한 작은 마음도 충분히 소중해. "
            "네 생각이 네 속도로 예쁘게 자라길 응원할게. 🌷"
        ),
    },
    {
        "name": "THE EMPEROR",
        "ko": "황제",
        "image": "04_emperor.png",
        "meaning": "기준, 안정감, 나만의 방향과 중심을 상징해.",
        "ending": (
            "수많은 생각 사이에서도 결국 네가 중요하게 여기는 기준이 있을 거야. "
            "오늘의 망상이 그 기준을 조금 더 알아가는 시간이었길 바라. "
            "네 중심을 믿고 걸어가도 괜찮아. ☁️"
        ),
    },
    {
        "name": "THE HIEROPHANT",
        "ko": "교황",
        "image": "05_hierophant.png",
        "meaning": "배움, 익숙한 가치, 오래 이어져 온 기준과 지혜를 상징해.",
        "ending": (
            "익숙한 길에도 이유가 있고, 새로운 길에도 이유가 있어. "
            "무엇을 따를지는 결국 네가 선택하는 거니까. "
            "배운 것과 네 생각이 멋지게 만나는 순간을 응원할게. 📜"
        ),
    },
    {
        "name": "THE LOVERS",
        "ko": "연인",
        "image": "06_lovers.png",
        "meaning": "끌림, 관계, 마음이 자연스럽게 향하는 선택을 상징해.",
        "ending": (
            "계속 마음이 가는 생각에는 작은 이유가 숨어 있을지도 몰라. "
            "그게 사람이든 꿈이든 새로운 삶이든 괜찮아. "
            "네 마음이 진짜 좋아하는 것을 만날 수 있길 응원할게. 💞"
        ),
    },
    {
        "name": "THE CHARIOT",
        "ko": "전차",
        "image": "07_chariot.png",
        "meaning": "이동, 추진력, 원하는 방향으로 나아가는 힘을 상징해.",
        "ending": (
            "오늘 생각이 꽤 멀리 달려왔네. "
            "처음과 전혀 다른 곳에 도착했어도 그 과정 자체가 네 길이야. "
            "가보고 싶은 방향이 있다면 씩씩하게 움직일 수 있길 응원할게. 🌠"
        ),
    },
    {
        "name": "STRENGTH",
        "ko": "힘",
        "image": "08_strength.png",
        "meaning": "부드러운 용기, 내면의 힘, 자신을 다루는 여유를 상징해.",
        "ending": (
            "강하다는 건 언제나 세게 밀어붙이는 것만은 아니래. "
            "때로는 기다리고, 받아들이고, 다시 시작하는 것도 힘이니까. "
            "네 방식의 용기를 응원할게. 🦁"
        ),
    },
    {
        "name": "THE HERMIT",
        "ko": "은둔자",
        "image": "09_hermit.png",
        "meaning": "혼자만의 탐색, 사색, 조용히 나만의 답을 찾아가는 시간을 상징해.",
        "ending": (
            "혼자 떠다닌 생각 속에서도 꽤 많은 걸 발견할 수 있어. "
            "오늘 잠깐 멈춰서 네 생각을 바라본 것도 충분히 의미 있는 탐험이야. "
            "네 안의 작은 등불을 응원할게. 🏮"
        ),
    },
    {
        "name": "WHEEL OF FORTUNE",
        "ko": "운명의 수레바퀴",
        "image": "10_wheel_of_fortune.png",
        "meaning": "변화, 우연한 전환, 예상하지 못했던 흐름을 상징해.",
        "ending": (
            "생각도 삶도 가끔은 예상하지 못한 방향으로 돌아가곤 하지. "
            "오늘의 별생각이 언젠가 중요한 계기가 될 수도 있어. "
            "네게 찾아올 좋은 변화들을 응원할게. 🎡"
        ),
    },
    {
        "name": "JUSTICE",
        "ko": "정의",
        "image": "11_justice.png",
        "meaning": "균형, 판단, 나에게 중요한 기준을 바라보는 것을 상징해.",
        "ending": (
            "서로 다른 마음이 동시에 존재해도 괜찮아. "
            "그 사이에서 네가 중요하게 생각하는 것을 천천히 알아가면 되니까. "
            "네가 스스로 납득할 수 있는 선택을 응원할게. ⚖️"
        ),
    },
    {
        "name": "THE HANGED MAN",
        "ko": "매달린 사람",
        "image": "12_hanged_man.png",
        "meaning": "멈춤, 다른 시선, 익숙한 것을 새로운 각도에서 바라보는 것을 상징해.",
        "ending": (
            "당장 앞으로 가지 않아도 괜찮아. "
            "잠깐 거꾸로 바라보면 전에는 보이지 않던 게 보이기도 하니까. "
            "네가 새로운 시선을 발견하는 순간을 응원할게. ✨"
        ),
    },
    {
        "name": "DEATH",
        "ko": "죽음",
        "image": "13_death.png",
        "meaning": "끝과 변화, 낡은 흐름을 보내고 새로운 장면으로 넘어가는 것을 상징해.",
        "ending": (
            "무언가가 끝난다는 건 언제나 사라진다는 뜻만은 아니야. "
            "다른 모습으로 이어질 수도 있으니까. "
            "지나간 것은 잘 보내고 새로 시작될 너의 장면을 응원할게. 🦋"
        ),
    },
    {
        "name": "TEMPERANCE",
        "ko": "절제",
        "image": "14_temperance.png",
        "meaning": "조화, 균형, 서로 다른 것들이 자연스럽게 섞이는 과정을 상징해.",
        "ending": (
            "서로 전혀 달라 보이는 생각들도 네 안에서는 하나의 흐름일 수 있어. "
            "오늘 떠다닌 생각들이 천천히 잘 섞여서 네게 맞는 방향이 되길 바라. "
            "네 속도를 응원할게. 🌈"
        ),
    },
    {
        "name": "THE DEVIL",
        "ko": "악마",
        "image": "15_devil.png",
        "meaning": "강한 끌림, 쉽게 놓이지 않는 마음, 반복해서 돌아보게 되는 것을 상징해.",
        "ending": (
            "자꾸 마음이 가는 생각이 있다고 해서 꼭 나쁜 건 아니야. "
            "그만큼 네게 강하게 남는 무언가일 수도 있으니까. "
            "네 마음을 너무 몰아붙이지 않고 바라볼 수 있길 응원할게. 🔥"
        ),
    },
    {
        "name": "THE TOWER",
        "ko": "탑",
        "image": "16_tower.png",
        "meaning": "갑작스러운 변화, 기존의 틀이 흔들리며 새롭게 보이는 순간을 상징해.",
        "ending": (
            "예상 밖의 생각 하나가 머릿속 지도를 완전히 바꾸기도 하지. "
            "조금 흔들려도 괜찮아. 그 뒤에 새로운 풍경이 보일 수도 있으니까. "
            "네가 다시 멋진 길을 찾길 응원할게. ⚡"
        ),
    },
    {
        "name": "THE STAR",
        "ko": "별",
        "image": "17_star.png",
        "meaning": "희망, 꿈, 앞으로 이어질 가능성과 마음속의 빛을 상징해.",
        "ending": (
            "그 꿈이 자유든, 취업이든, 새로운 시작이든, "
            "아직 이름 붙이지 못한 무언가든 괜찮아. "
            "오늘 떠다닌 생각들이 언젠가 하나의 별자리처럼 이어질지도 몰라. "
            "네가 바라는 방향을 응원할게. ✨"
        ),
    },
    {
        "name": "THE MOON",
        "ko": "달",
        "image": "18_moon.png",
        "meaning": "상상, 불확실함, 아직 또렷하게 설명할 수 없는 마음을 상징해.",
        "ending": (
            "지금은 선명하지 않아도 괜찮아. "
            "모든 생각이 처음부터 밝은 낮처럼 보이는 건 아니니까. "
            "흐릿한 달빛 아래에서도 네가 천천히 길을 찾아가길 응원할게. 🌙"
        ),
    },
    {
        "name": "THE SUN",
        "ko": "태양",
        "image": "19_sun.png",
        "meaning": "기쁨, 자신감, 따뜻한 에너지와 밝게 드러나는 가능성을 상징해.",
        "ending": (
            "오늘 떠다닌 생각 중에서 유난히 마음이 밝아졌던 순간이 있었을지도 몰라. "
            "그 작은 즐거움을 오래 기억했으면 좋겠어. "
            "네 하루에 따뜻한 빛이 오래 머물길 응원할게. ☀️"
        ),
    },
    {
        "name": "JUDGEMENT",
        "ko": "심판",
        "image": "20_judgement.png",
        "meaning": "깨달음, 되돌아봄, 이전과는 조금 다른 시선으로 자신을 바라보는 것을 상징해.",
        "ending": (
            "처음 떠올린 생각과 지금의 생각은 꽤 달라졌을 수도 있어. "
            "그 사이에서 발견한 작은 깨달음 하나면 충분해. "
            "네가 스스로 알아가는 모든 순간을 응원할게. 📯"
        ),
    },
    {
        "name": "THE WORLD",
        "ko": "세계",
        "image": "21_world.png",
        "meaning": "완성, 연결, 여러 조각이 하나의 흐름으로 이어지는 것을 상징해.",
        "ending": (
            "여기까지 꽤 멀리 떠다녔네. "
            "처음에는 서로 상관없어 보였던 생각도 결국 하나의 길이 되었어. "
            "오늘 만든 작은 세계를 잘 간직하길 바라. 너의 다음 여행도 응원할게. 🌍"
        ),
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
        f"'{current}'에서 떠오르는 장소",
        f"'{current}'와 연결되는 사람",
        f"이 생각의 정반대 방향",
        f"이게 현실이 된다면 생길 장면",
        f"예전에 비슷하게 떠올렸던 기억",
        f"아예 엉뚱한 곳으로 새보기",
        f"이 생각이 영화라면 다음 장면",
        f"갑자기 여행으로 연결해보기",
        f"이 생각에서 떠오르는 감정",
        f"5년 뒤의 나와 연결해보기",
        f"이 생각과 전혀 상관없는 취미",
        f"이 생각을 친구에게 말한다면",
    ]

    suggestions = random.sample(
        templates,
        6
    )

    if len(thought_path) == 1:

        comment = (
            "별가루가 잠깐 충전 중이야 ☁️ "
            "그래도 망상길은 열려 있어. "
            "어디로 한번 새볼까?"
        )

    else:

        first = thought_path[0]

        comment = (
            f"처음엔 '{first}'에서 출발했는데 "
            f"어느새 '{current}'까지 왔네. ☁️ "
            "AI 별가루는 쉬는 중이지만, "
            "생각은 계속 떠다닐 수 있어."
        )

    return comment, suggestions


# =========================================================
# Gemini 없이 숨은 연결
# =========================================================
def fallback_hidden_connection(thought_path):

    first = thought_path[0]
    last = thought_path[-1]

    if len(thought_path) >= 3:

        middle = thought_path[
            len(thought_path) // 2
        ]

        return (
            f"☁️ 지금 보이는 흐름\n\n"
            f"처음에는 '{first}'에서 시작했는데 "
            f"지금은 '{last}'까지 흘러왔네.\n\n"
            f"✨ 숨어 있던 별\n\n"
            f"중간에 '{middle}'를 지나왔다는 게 재밌어. "
            f"처음 생각과 지금 생각 사이에 놓인 "
            f"작은 다리였을지도 몰라.\n\n"
            f"🪄 구름요정의 관찰\n\n"
            f"정답이라기보다, 네 생각이 한 방향으로만 가지 않고 "
            f"여러 갈래를 지나 여기까지 왔다는 게 보여."
        )

    return (
        f"☁️ 지금 보이는 흐름\n\n"
        f"'{first}'에서 시작해서 '{last}'까지 왔네.\n\n"
        f"✨ 숨어 있던 별\n\n"
        f"두 생각은 처음에는 멀어 보일 수도 있지만, "
        f"네 머릿속에서는 이미 하나의 길로 연결됐어.\n\n"
        f"🪄 구름요정의 관찰\n\n"
        f"오늘은 그 연결 자체만 발견해도 충분해."
    )


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
            "☁️ 오늘의 AI 별가루를 다 썼어요. "
            "지금은 기본 망상 모드로 계속 탐험할게!"
        )

        return comment, suggestions


    path_text = " → ".join(
        thought_path
    )

  

    prompt = f"""
너는 AI 사고 탐험 서비스 '망상회로'의 구름요정이야.

생각 흐름:
{path_text}

할 일:
1. 흐름을 경청한 짧은 관찰 1문장.
2. 현재 생각에서 이어질 서로 다른 갈림길 정확히 6개.

갈림길은 감정, 사람, 기억, 장소, 행동, 미래,
현실적 가능성, 엉뚱한 상상 등을 다양하게 섞어.
서로 비슷하지 않게 하고 각각 짧고 흥미롭게 써.

정답 제시, 훈계, 생산성 강요, 심리진단,
사용자 성격 단정은 하지 마.
사용자의 상상회로를 존중하고 옆에서 따라가는 말투로 써.

JSON만 출력:
{{
  "fairy_comment": "짧은 관찰",
  "suggestions": [
    "갈림길1",
    "갈림길2",
    "갈림길3",
    "갈림길4",
    "갈림길5",
    "갈림길6"
  ]
}}
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
                "생각 갈림길을 충분히 생성하지 못했습니다."
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
                "☁️ 오늘의 AI 별가루를 다 썼어요. "
                "지금은 기본 망상 모드로 계속 탐험할게!"
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
            "☁️ AI 별가루는 충전 중이라 "
            "구름요정 기본 관찰 모드로 볼게."
        )

        return fallback_hidden_connection(
            thought_path
        )


    path_text = " → ".join(
        thought_path
    )

    prompt = f"""
너는 '망상회로'의 구름요정이다.

사용자가 지금까지 지나온 생각:

{path_text}

이 생각들 사이에서
사용자가 미처 눈치채지 못했을 법한
흥미로운 연결 하나를 찾아라.

하지만 사용자를 분석하거나 규정하지 않는다.

심리 진단 금지.
성격 단정 금지.
훈계 금지.
자기계발식 조언 금지.

가능성을 열어두는 말투를 사용한다.

다음 형식으로 짧게 이야기한다.

☁️ 지금 보이는 흐름

처음 생각에서 현재 생각까지
어떤 방향으로 이동했는지 설명한다.

✨ 숨어 있던 별

반복되는 주제,
비슷하게 등장한 관심사,
또는 의외의 연결 하나를 찾아낸다.

🪄 이런 생각은 어때?

사용자가 스스로 더 생각해볼 수 있는
새 질문 하나를 던진다.

짧고 위트 있지만 차분하게 말한다.
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
                "☁️ AI 별가루는 충전 중이라 "
                "구름요정 기본 관찰 모드로 볼게."
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
            "🪄 그 구름을 따라가는 중..."
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

        st.rerun()


    except Exception as e:

        # Gemini 말고 진짜 다른 오류만 표시
        st.error(
            "별가루가 잠깐 엉켰어요 ✨ "
            "한 번 더 눌러봐."
        )

        st.code(
            str(e)
        )


# =========================================================
# CSS
# =========================================================
st.markdown(
    """
<style>

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
</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# 헤더
# =========================================================
st.markdown(
    '<div class="logo">'
    '☁️ 망상회로 ✨'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="tagline">'
    '생각의 유랑이 반짝이는 별에 닿을 수도! ✨'
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
            "구름요정 이미지를 찾지 못했어요 ☁️"
        )

        st.code(
            str(FAIRY_IMAGE)
        )


    st.markdown(
        '<div class="fairy-card">'
        '<div class="fairy-name">'
        '☁️ 구름요정'
        '</div>'
        '<div class="fairy-text">'
        '머릿속에 떠다니는 생각 하나만 던져봐.<br>'
        '어디까지 흘러가는지 같이 따라가 볼게. 🪄'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


    first_thought = st.text_input(
        "첫 생각",
        placeholder=(
            "예: 그냥 다 그만두고 여행 가고 싶다"
        ),
        label_visibility="collapsed"
    )


    if st.button(
        "✨ 여기서 망상 시작하기",
        use_container_width=True
    ):

        if not first_thought.strip():

            st.warning(
                "생각 하나만 살짝 던져줘 ☁️"
            )

        else:

            try:

                first_path = [
                    first_thought.strip()
                ]

                with st.spinner(
                    "☁️ 첫 번째 생각 구름을 만드는 중..."
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

                st.rerun()


            except Exception as e:

                st.error(
                    "구름요정이 잠깐 구름 속에 숨었어요 ☁️"
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
    # API fallback 안내
    # =====================================================
    if st.session_state.api_notice:

        st.info(
            st.session_state.api_notice,
            icon="☁️"
        )


    # =====================================================
    # 구름요정 코멘트
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
            '☁️ 구름요정'
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
        '✨ 내가 지나온 생각의 별자리'
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
        '☁️ 지금 머릿속'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">'
        '끌리는 구름을 눌러서 생각을 따라가 봐.'
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
            '✨ 지금 내 생각'
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
    # 직접 딴생각
    # =====================================================
    st.markdown(
        '<div class="section-title">'
        '💭 갑자기 딴생각 났어?'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">'
        'AI가 안 보여준 길이어도 괜찮아.'
        '</div>',
        unsafe_allow_html=True
    )


    custom = st.text_input(
        "직접 생각",
        placeholder=(
            "갑자기 떠오른 생각을 그대로 적어봐"
        ),
        label_visibility="collapsed",
        key=f"custom_{len(path)}"
    )


    if st.button(
        "☁️ 이 생각으로 확 새기",
        key=f"custom_button_{len(path)}",
        use_container_width=True
    ):

        if not custom.strip():

            st.warning(
                "새로 떠오른 생각을 적어줘 ☁️"
            )

        else:

            choose_thought(
                custom.strip()
            )


    # =====================================================
    # 숨은 연결
    # =====================================================
    if len(path) >= 2:

        st.markdown(
            '<div class="section-title">'
            '✨ 슬슬 뭔가 연결되고 있을지도?'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-sub">'
            '구름요정에게 지금까지의 흐름을 보여줘.'
            '</div>',
            unsafe_allow_html=True
        )


        if st.button(
            "🪄 숨은 연결 찾기",
            key=f"connection_{len(path)}",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "✨ 생각 사이에서 별 하나 찾는 중..."
                ):

                    st.session_state.analysis = (
                        find_hidden_connection(
                            path
                        )
                    )

                st.rerun()


            except Exception as e:

                st.error(
                    "별이 잠깐 구름 뒤에 숨었어요 ☁️"
                )

                st.code(
                    str(e)
                )


    if st.session_state.analysis:

        analysis = html.escape(
            st.session_state.analysis
        ).replace(
            "\n",
            "<br>"
        )


        (
            analysis_fairy,
            analysis_text
        ) = st.columns(
            [1, 2.8],
            vertical_alignment="center"
        )


        with analysis_fairy:

            if FAIRY_IMAGE.exists():

                st.image(
                    str(FAIRY_IMAGE),
                    use_container_width=True
                )

            else:

                st.markdown(
                    "☁️🪄"
                )


        with analysis_text:

            st.markdown(
                '<div class="fairy-card">'
                '<div class="fairy-name">'
                '☁️ 구름요정의 발견 ✨'
                '</div>'
                '<div class="fairy-text">'
                f'{analysis}'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )


    # =====================================================
    # EUREKA
    # =====================================================
       # =====================================================
    # EUREKA / 생각 여행 마무리
    # =====================================================
    if len(path) >= 3:

        st.markdown(
            '<div class="section-title">'
            '💡 이제 생각 여행을 마쳐볼까요?'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-sub">'
            '충분히 떠다녔다면 여기서 마무리해도 좋아요.<br>'
            '아직 더 헤매고 싶다면 위의 구름을 계속 눌러도 돼요. ☁️'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="eureka-card">'
            '<div style="'
            'text-align:center;'
            'font-size:27px;'
            'font-weight:900;'
            '">'
            '💡 오늘 발견한 별 하나'
            '</div>'
            '<div style="'
            'text-align:center;'
            'color:#777;'
            'margin-top:10px;'
            'line-height:1.7;'
            '">'
            '처음 생각과 지금 생각을 천천히 바라봐.<br>'
            '<b>오늘 새롭게 발견한 생각을 한 줄로 남겨줘.</b><br><br>'
            '한 줄을 남기면 마지막 행운카드도 뽑을 수 있어요. 🔮'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        note = st.text_area(
            "💡 오늘 생각 여행에서 발견한 것",
            value=st.session_state.eureka_note,
            placeholder=(
                "예: 나는 취업 자체보다 새로운 환경에서 "
                "살아보고 싶은 마음이 더 큰 걸지도."
            ),
            height=110
        )

        if not st.session_state.eureka_saved:

            if st.button(
                "💡 EUREKA!로 남기고 행운카드 보기",
                key=f"save_eureka_{len(path)}",
                use_container_width=True
            ):

                if note.strip():

                    st.session_state.eureka_note = (
                        note.strip()
                    )

                    st.session_state.eureka_saved = True

                    st.success(
                        "✨ 오늘의 별을 남겼어요! "
                        "이제 아래에서 행운카드를 뽑아봐."
                    )

                    st.balloons()

                    st.rerun()

                else:

                    st.warning(
                        "오늘 발견한 생각을 한 줄만 적어줘 💡"
                    )

               else:

            saved_note = html.escape(
                st.session_state.eureka_note
            )

            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    margin:28px 0 12px 0;
                ">

                    <div style="
                        font-size:30px;
                        letter-spacing:8px;
                        margin-bottom:8px;
                    ">
                        ☁️　☁️　✨　☁️　☁️
                    </div>

                    <div style="
                        font-size:14px;
                        color:#8b86a6;
                        font-weight:700;
                        margin-bottom:8px;
                    ">
                        오늘 생각 여행에서 발견한 별
                    </div>

                    <div style="
                        max-width:520px;
                        margin:0 auto;
                        padding:28px 24px;
                        border-radius:32px;
                        background:
                            radial-gradient(
                                circle at 50% 35%,
                                #fffdf0 0%,
                                #fff8c9 55%,
                                #fff3a8 100%
                            );
                        border:1px solid #ffe795;
                        box-shadow:
                            0 0 25px rgba(255,220,100,0.35),
                            0 10px 30px rgba(120,100,50,0.10);
                    ">

                        <div style="
                            font-size:38px;
                            margin-bottom:10px;
                        ">
                            ⭐
                        </div>

                        <div style="
                            font-size:18px;
                            font-weight:850;
                            color:#514a39;
                            line-height:1.65;
                            word-break:keep-all;
                        ">
                            {saved_note}
                        </div>

                    </div>

                    <div style="
                        font-size:27px;
                        letter-spacing:7px;
                        margin-top:8px;
                    ">
                        ☁️　✨　☁️
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


    # =====================================================
    # 구름요정 타로
    # =====================================================
    if st.session_state.eureka_saved:

        st.markdown(
            '<div class="section-title">'
            '🔮 탐험 끝에 별 하나 더'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-sub">'
            '오늘의 생각 여행을 마무리해줄 카드 한 장.'
            '</div>',
            unsafe_allow_html=True
        )


        # -------------------------------------------------
        # 아직 카드 안 뽑음
        # -------------------------------------------------
        if st.session_state.tarot_card is None:

            (
                tarot_fairy,
                tarot_text
            ) = st.columns(
                [1, 2.8],
                vertical_alignment="center"
            )


            with tarot_fairy:

                if FAIRY_IMAGE.exists():

                    st.image(
                        str(FAIRY_IMAGE),
                        use_container_width=True
                    )

                else:

                    st.markdown(
                        "☁️🔮"
                    )


            with tarot_text:

                st.markdown(
                    '<div class="fairy-card">'
                    '<div class="fairy-name">'
                    '☁️ 구름요정'
                    '</div>'
                    '<div class="fairy-text">'
                    '오늘 꽤 멀리 떠다녔네.<br>'
                    '마지막으로 카드 한 장만 뽑아볼래? 🪄'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )


            if st.button(
                "🔮 오늘의 행운 카드 뽑기",
                key=f"tarot_{len(path)}",
                use_container_width=True
            ):

                with st.spinner(
                    "☁️ 구름요정이 카드를 섞는 중... ✨"
                ):

                 time.sleep(0.25)

                st.session_state.tarot_card = (
                    random.choice(
                        TAROT_CARDS
                    )
                )

                st.rerun()


        # -------------------------------------------------
        # 카드 결과
        # -------------------------------------------------
        else:

            card = (
                st.session_state.tarot_card
            )

            image_path = (
                TAROT_DIR
                / card["image"]
            )


            st.markdown(
                '<div class="tarot-stage">'
                '<div style="'
                'font-size:13px;'
                'letter-spacing:3px;'
                'color:#9b8bac;'
                'font-weight:800;'
                '">'
                '☁️ CLOUD FAIRY TAROT ☁️'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )


            if image_path.exists():

                (
                    image_left,
                    image_mid,
                    image_right
                ) = st.columns(
                    [1, 2, 1]
                )

                with image_mid:

                    st.image(
                        str(image_path),
                        use_container_width=True
                    )


            else:

                st.error(
                    "타로 카드 이미지를 찾지 못했어요 😭"
                )

                st.code(
                    str(image_path)
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
                '<b>'
                '🔮 이 카드가 전하는 의미'
                '</b>'
                '<br><br>'
                f'{html.escape(card["meaning"])}'
                '</div>',
                unsafe_allow_html=True
            )


            st.markdown(
                '<div class="ending-card">'
                '<div class="ending-label">'
                '☁️ 구름요정의 마지막 한마디'
                '</div>'
                f'{html.escape(card["ending"])}'
                '</div>',
                unsafe_allow_html=True
            )


            st.markdown(
                '<div style="'
                'text-align:center;'
                'color:#9a92ad;'
                'font-size:13px;'
                'margin-bottom:22px;'
                'line-height:1.6;'
                '">'
                '오늘의 카드는 미래를 정하는 답이 아니라, '
                '생각 여행 끝에 만난 작은 상징이에요. ✨'
                '</div>',
                unsafe_allow_html=True
            )


    # =====================================================
    # 새로운 망상
    # =====================================================
    st.divider()


    if st.button(
        "🌙 새로운 망상 시작하기",
        key="restart",
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

        st.session_state.started = False

        # API 쿼터 상태는 유지
        # 같은 브라우저 세션에서 계속 429 요청하는 것을 방지

        st.rerun()
