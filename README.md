# 망상회로 2.0 — 구름 배경 수정판

## 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

Gemini 사용 시 Streamlit secrets 또는 환경변수에 `GEMINI_API_KEY` 설정.

## 변경 사항
- 실제 UI가 포함되지 않은 별도 구름 배경 이미지 사용 (이전 버전의 확대된 회색 구름 문제 해결)
- 시작 화면 상단 여백 확보 및 캐릭터 잘림 방지
- 캐릭터 왼쪽 / 제목 오른쪽 배치 유지
- 기존 논리·발상·융합 회로, AI 코칭, 노트, 타로 로직 유지
- 화면 크기에 따라 이미지와 배경이 달라질 수 있음
