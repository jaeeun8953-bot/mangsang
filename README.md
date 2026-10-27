# 망상회로 2.0 — 레퍼런스 이미지 반영 버전

## 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

Gemini API 키는 Streamlit secrets 또는 환경변수 `GEMINI_API_KEY`에 설정합니다.

## 디자인 구현
- `hero_reference.png`: 승인된 시안의 **상단 구름 요정·제목 부분을 그대로** 사용합니다. 시작 화면 상단이 잘리지 않도록 전체 너비로 표시합니다.
- `cloud_sky_background.jpg`: 시안의 구름·별 테두리를 살리되 **가운데에 그려져 있던 가짜 버튼과 글자를 제거**한 배경입니다.
- 회로 선택, 텍스트 입력, 여행 시작 버튼은 모두 실제 Streamlit 위젯으로 동작합니다.
- 한국어 시작 화면에만 시안 상단을 적용합니다. 다른 화면과 영어 모드는 기존 동적 제목을 사용합니다.

참고: 시안은 정적인 그림이므로 브라우저·화면 비율에 따라 카드 크기와 줄바꿈이 픽셀 단위로 같지는 않을 수 있습니다.
