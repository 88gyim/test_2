# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

사용자가 텍스트를 입력하고 [영어]/[일본어]/[베트남어] 버튼을 누르면 AI가 그 언어로 번역해 주는 Streamlit 단일 페이지 앱. 요구사항의 기준은 `PRD.md`(한국어), 단계별 개발 프롬프트는 `PROMPTS.md`다. 1~4단계(뼈대, 기능, UI, 검토)는 끝났고 다음은 Streamlit Community Cloud 배포다.

## 명령어

```
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

테스트 코드와 린트 설정은 저장소에 없다. 로직 검증은 `streamlit.testing.v1.AppTest`에 `openai.OpenAI`를 mock으로 바꿔서 했다.

## 아키텍처

모든 코드는 `app.py` 한 파일이다.

- `translate(text, target_language)`: OpenAI chat completions 호출. 실패는 `TranslationError`(사용자에게 그대로 보여줄 메시지)로 바꿔 던진다. 키 오류, 모델 없음, 권한 오류, 400은 "환경변수를 확인하세요", 그 외는 "번역에 실패했습니다"로 나눈다. 예외 상세와 키는 화면에 노출하지 않는다.
- `validate(text)`: 빈 입력과 2,000자 초과를 API 호출 전에 막는다.
- `main()`: UI. 버튼을 누른 그 실행에서만 결과를 그리며, 결과를 세션에 저장하지 않는다. 그래서 원문을 고치면 결과가 사라진다.
- 모델명과 키는 환경변수 `OPENAI_MODEL`(없으면 `gpt-6.1-sol`), `OPENAI_API_KEY`에서 읽는다. `load_dotenv()`는 로컬 개발용이고, 배포에서는 Streamlit Cloud Secrets가 같은 이름의 환경변수로 쓰인다.

## 주의사항

- `gpt-6.1-sol`은 `temperature` 파라미터를 지원하지 않는다 (넣으면 400 `unsupported_value`). 호출에 넣지 않는다.
- 설치된 `openai` 3.x는 HTTP 라이브러리로 `httpx2`를 쓴다. 예외 클래스 이름과 호출 방식은 이전과 같다.
- `.env`는 사용자의 비밀 파일이다. 내용을 읽거나 수정하거나 출력하지 않는다. 키가 있는지 확인할 때도 값은 출력하지 않는다.
- `.gitignore`에 `.env`, `.venv/`, `프롬프트.txt`(개인 메모)가 들어 있다. 커밋 전에 `git status`로 `.env`가 없는지 확인한다.
- 국기 이모지는 Windows 브라우저에서 `US`/`JP`/`VN` 글자로 보인다 (폰트 한계, 코드 문제 아님).
- 글자 수 카운터는 Streamlit 특성상 입력창을 벗어나거나 Ctrl+Enter를 눌러야 갱신된다.
