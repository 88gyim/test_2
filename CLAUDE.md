# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 현재 상태

아직 코드가 없는 기획 단계다. 저장소에는 문서만 있다.

- `PRD.md`: 요구사항의 기준 문서 (한국어). 기능 요구사항 F1~F8, AI 사양, 예외 처리, 배포 방식이 정의되어 있다.
- `PROMPTS.md`: 개발을 1단계 뼈대, 2단계 기능, 3단계 UI, 4단계 Playwright 검토로 나눈 프롬프트 모음. 구현은 이 순서를 따른다.
- `프롬프트.txt`: 사용자의 메모. 구현 근거로 쓰기 전에 내용을 확인한다.
- `.env`: 사용자가 직접 관리하는 비밀 파일. 내용을 읽거나 수정하거나 출력하지 않는다.

## 프로젝트 개요

사용자가 텍스트를 입력하고 [영어]/[일본어]/[베트남어] 버튼을 누르면 AI가 그 언어로 번역해 주는 Streamlit 단일 페이지 앱. Python 3.10+, `streamlit`, `openai`, `python-dotenv`를 사용한다.

## 명령어 (PRD 기준, 구현 후 적용)

```
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

테스트와 린트 도구는 아직 정해지지 않았다.

## 아키텍처 주의사항

- 앱은 `app.py` 한 파일로 시작한다 (PRD 8장). 번역은 `translate(text, target_language)` 함수 하나로 모은다.
- 모델명과 API 키는 반드시 환경변수 `OPENAI_MODEL`, `OPENAI_API_KEY`에서 읽는다. PRD의 모델은 `gpt-6.1-sol`이며 코드에 상수로 박지 않는다. 이 모델명이 제공자에서 유효한지는 아직 확인되지 않았다 (PRD 14장).
- `.env`는 `load_dotenv()`로 로컬 개발에서만 읽는다. 배포(Streamlit Community Cloud)에서는 Secrets에 같은 키를 등록한다.
- 번역 응답은 번역문만 출력해야 한다 (설명, 따옴표, 머리말 금지). 이는 system 프롬프트로 강제한다.
- 입력 검증 기준: 빈 입력은 API를 호출하지 않고, 최대 2,000자로 제한한다.
- 오류 화면에는 API 키와 예외 상세를 노출하지 않는다.
- `.gitignore`에 `.env`가 반드시 들어 있어야 한다.
