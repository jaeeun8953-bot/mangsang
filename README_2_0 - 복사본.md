# 망상회로 2.0

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit Community Cloud에서 **Main file path**는 `app.py`로 지정합니다. 기존 앱과 동일하게 앱의 Secrets에 `GEMINI_API_KEY`를 설정하세요. 필요하면 `GEMINI_MODEL = "gemini-3.8-flash"`를 추가할 수 있습니다. 모델 사용 가능 여부는 Google 계정 및 API 설정에 따라 달라질 수 있습니다.

## 기능

- 논리/발상/융합 회로 선택 (여행 시작 후 고정)
- 사용자 생각에 맞춘 6가지 질문, 직접 답변, Gemini 코칭
- 기존 `cloud_fairy.png` 캐릭터, 생각 경로 표시와 짧은 점프 효과
- 탐험 종료 후 생각노트와 22장 중 타로카드 1장 및 성찰 조언
- 생각노트 Markdown 다운로드 (타로 이미지 파일 자체는 문서에 내장되지 않음)
- 한국어/영어 전환

## 참고

이 버전은 Streamlit 기본 UI를 사용한 **기능 중심 MVP**입니다. 구름 징검다리는 클릭 가능한 구름 선택지와 경로 표시로 구현되었으며, 캐릭터가 특정 구름 좌표까지 실제로 이동하는 고급 애니메이션은 아직 구현되지 않았습니다. 노트는 브라우저 세션 중 유지되며, 앱 서버의 영구 저장소에는 자동 저장되지 않습니다. 다운로드로 보관해 주세요. Gemini 호출이 실패하면 기본 질문/코칭 문구가 표시될 수 있습니다.

원본 `daydream_ko.py`, `daydream_en.py`, 타로 카드 이미지와 기타 이미지는 보존되어 있습니다. 기존 3D 뇌 관련 `brain_mode.py`, `index.html`, `assets/brain.glb`는 새 앱 실행에 사용하지 않으므로 배포 ZIP에서는 제외했습니다.
