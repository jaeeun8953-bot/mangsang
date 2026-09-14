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
EUREKA_CLOUD_IMAGE = BASE_DIR / "eureka_cloud.svg"
EUREKA_STAR_IMAGE = BASE_DIR / "eureka_star.svg"


def asset_data_uri(path):
    if not path.exists():
        return ""

    mime = "image/svg+xml" if path.suffix.lower() == ".svg" else "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"



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
        st.session_state.journey_finish_mode = False
        st.session_state.train_boarded = False
        st.session_state.train_flow_open = False

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
# 전용 EUREKA / 타로 화면
# =========================================================
def render_eureka_screen(path):

    if not st.session_state.eureka_saved:

        st.markdown(
            '<div style="height:18px;"></div>'
            '<div class="section-title">'
            '💡 오늘의 EUREKA'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-sub">'
            '지나온 생각에서 오늘 건져 올린 '
            '<b>키워드나 짧은 표현 하나</b>만 남겨봐요.<br>'
            '예: 소소한 행복 · 새로운 시작 · 자유'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="eureka-card">'
            '<div style="text-align:center;font-size:31px;">☁️　✨　☁️</div>'
            '<div style="text-align:center;color:#68647e;font-size:16px;'
            'font-weight:800;line-height:1.65;margin-top:8px;">'
            '길게 정리하지 않아도 괜찮아요.<br>'
            '지금 가장 마음에 남는 말 하나면 충분해요.'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        note = st.text_input(
            "오늘의 EUREKA",
            value=st.session_state.eureka_note,
            placeholder="예: 소소한 행복",
            max_chars=24,
            label_visibility="collapsed",
            key="eureka_dedicated_input"
        )

        if st.button(
            "⭐ 이 생각을 오늘의 별로 남기기",
            key="save_eureka_dedicated",
            use_container_width=True
        ):
            if note.strip():
                st.session_state.eureka_note = note.strip()
                st.session_state.eureka_saved = True
                st.rerun()
            else:
                st.warning(
                    "오늘 마음에 남은 키워드 하나만 적어줘 ✨"
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
        '✨ 오늘 생각 여행에서 발견한 별 ✨'
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
        '✨ 오늘 생각 여행에서 발견한 별 ✨'
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
        '작은 생각도 언젠가 반짝이는 아이디어가 될 수 있어요 ☁️'
        '</div>'
        '</div>'
    )

    st.markdown(
        eureka_star_html,
        unsafe_allow_html=True
    )

    if st.session_state.tarot_card is None:

        if st.button(
            "✨🔮 오늘의 운세를 타로로 조언 얻기 ✨",
            key="tarot_dedicated",
            use_container_width=True,
            type="primary"
        ):

            with st.spinner(
                "☁️ 구름요정이 카드를 섞는 중... ✨"
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
                "타로 카드 이미지를 찾지 못했어요 😭"
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
            '<b>🔮 이 카드가 전하는 의미</b><br><br>'
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

    st.divider()

    if st.button(
        "🌙 새로운 망상 시작하기",
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


    if st.button(
        "💡 EUREKA 다시 기록하기",
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
                st.session_state.journey_checkpoint = 3
                st.session_state.journey_finish_mode = False
                st.session_state.train_boarded = False
                st.session_state.train_flow_open = False

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
                '✨ 이제 슬슬 정리될 수도?'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="section-sub">'
                '처음 생각에서 여기까지 어떻게 흘러왔는지 '
                '구름요정이 한 번 이어봤어요.'
                '</div>',
                unsafe_allow_html=True
            )

            if not st.session_state.analysis:

                with st.spinner(
                    "🪄 지나온 생각 사이에서 연결을 찾는 중..."
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
                    '☁️ 구름요정의 발견 ✨'
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
                    "💡 EUREKA 기록하기",
                    key="flow_screen_eureka",
                    use_container_width=True
                ):

                    st.session_state.journey_finish_mode = True
                    st.session_state.train_boarded = False
                    st.session_state.train_flow_open = False
                    st.rerun()

            with flow_more_col:

                if st.button(
                    "☁️ 망상구름 이어가기",
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
            '<div class="title">생각 흐름 기차에 탑승했어요</div>'
            '<div class="sub">'
            '다음 단계에서 하나만 골라봐요.<br>'
            '지나온 생각 흐름을 살펴보거나, 바로 EUREKA를 남길 수 있어요.'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        train_flow_col, train_eureka_col = st.columns(
            2
        )

        with train_flow_col:

            if st.button(
                "🛤️ 생각 흐름 살펴보기",
                key="dedicated_train_flow",
                use_container_width=True
            ):

                st.session_state.analysis = ""

                with st.spinner(
                    "🪄 지나온 생각 사이에서 연결을 찾는 중..."
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
                "💡 EUREKA 기록하기",
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
    # 생각 여행 체크포인트
    # 첫 생각 이후 구름을 3번 누를 때마다 등장
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
                '<div class="title">이제 생각 흐름 기차를 타볼까요?</div>'
                '<div class="sub">'
                '지금까지 떠다닌 생각들을 한 번 이어서 바라볼 수 있어요.<br>'
                '아직 더 헤매고 싶다면 망상을 계속 이어가도 좋아요. ☁️'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )

            train_col, more_col = st.columns(2)

            with train_col:
                if st.button(
                    "🚂 생각 흐름 기차 타기",
                    key=f"board_train_{len(path)}",
                    use_container_width=True
                ):
                    st.session_state.train_boarded = True
                    st.session_state.train_flow_open = False
                    st.rerun()

            with more_col:
                if st.button(
                    "☁️ 망상 더 해보기",
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
    # 언제든 다음 단계로 넘어가기
    # '딴 생각으로 새기' 바로 아래
    # =====================================================
    next_spacer, next_button_col = st.columns(
        [2.6, 1.4]
    )

    with next_button_col:

        if st.button(
            "다음 단계 →",
            key=f"next_step_{len(path)}",
            use_container_width=True
        ):

            st.session_state.train_boarded = True
            st.session_state.train_flow_open = False
            st.session_state.journey_finish_mode = False
            st.rerun()
