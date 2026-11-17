# PRD: AI 번역기 (Streamlit)

## 1. 개요
사용자가 텍스트를 입력하고 **[영어] / [일본어] / [베트남어]** 버튼 중 하나를 누르면, AI 모델이 해당 언어로 번역한 결과를 보여주는 간단한 웹 애플리케이션.

## 2. 목표 및 비목표
### 목표
- 최소한의 클릭으로 3개 언어(영어, 일본어, 베트남어) 번역 제공
- Streamlit(Python)으로 구현하고 웹에 배포
- API 키와 모델명은 `.env`로 관리 (코드에 하드코딩 금지)

### 비목표 (v1 제외)
- 로그인/회원가입, 번역 기록 저장
- 음성 입력/출력, 파일(문서) 번역
- 3개 외 언어 지원, 원문 언어 선택 (자동 감지만 사용)

## 3. 대상 사용자
- 짧은 문장/문단을 빠르게 번역하고 싶은 일반 사용자 (한국어 입력 중심, 다른 언어 입력도 허용)

## 4. 사용자 시나리오
1. 사용자가 앱에 접속한다.
2. 텍스트 입력창에 번역할 글을 입력한다.
3. [영어] / [일본어] / [베트남어] 중 하나의 버튼을 누른다.
4. 로딩 표시 후 번역 결과가 결과 영역에 표시된다.
5. 사용자는 결과를 복사하거나, 다른 언어 버튼을 눌러 다시 번역한다.

## 5. 기능 요구사항
| ID | 요구사항 | 우선순위 |
|----|----------|----------|
| F1 | 여러 줄 텍스트 입력창 제공 (최대 글자 수 제한, 기본 2,000자) | Must |
| F2 | 번역 버튼 3개: 영어, 일본어, 베트남어 (가로 배치) | Must |
| F3 | 버튼 클릭 시 해당 언어로 AI 번역 호출 후 결과 표시 | Must |
| F4 | 번역 중 스피너 표시 | Must |
| F5 | 빈 입력 시 "텍스트를 입력해 주세요" 경고 표시, API 호출 안 함 | Must |
| F6 | API 오류/타임아웃 시 사용자 친화적 에러 메시지 표시 | Must |
| F7 | 결과 복사 기능 (`st.code` 블록의 복사 아이콘 활용) | Should |
| F8 | 번역 결과에는 번역문만 출력 (설명/따옴표/머리말 없음) | Must |

## 6. AI 번역 사양
- **모델**: `gpt-6.1-sol` (환경변수 `OPENAI_MODEL`로 지정, 기본값으로 위 모델명 사용)
- **환경변수 (`.env`)**
  ```
  OPENAI_API_KEY=sk-...
  OPENAI_MODEL=gpt-6.1-sol
  ```
- **로딩**: `python-dotenv`의 `load_dotenv()`로 로컬 개발 시 `.env` 로드. 배포 환경에서는 플랫폼의 Secrets/환경변수 사용.
- **프롬프트 (예시)**
  - System: "You are a professional translator. Translate the user's text into {target_language}. Output only the translated text, with no explanations, notes, or quotation marks. Preserve line breaks and tone."
  - User: 입력 원문
- **파라미터**: 요청 타임아웃 30초. `gpt-6.1-sol`은 `temperature` 파라미터를 지원하지 않아(400 `unsupported_value`) 지정하지 않는다.
- 모델은 코드 상수가 아니라 환경변수에서 읽어 교체 가능하게 한다.

## 7. UI 구성
```
┌──────────────────────────────┐
│  🌐 AI 번역기                 │
│  [ 텍스트 입력창 (여러 줄) ]   │
│  [영어] [일본어] [베트남어]    │
│  ── 번역 결과 ──              │
│  (결과 텍스트 / 복사 버튼)     │
└──────────────────────────────┘
```
- `st.title`, `st.text_area`, `st.columns(3)` + `st.button`, `st.spinner`, `st.code`/`st.success`
- 모바일에서도 사용 가능한 반응형 기본 레이아웃(Streamlit 기본 제공)

## 8. 기술 스택 및 구조
- **언어/프레임워크**: Python 3.10+, Streamlit
- **라이브러리**: `streamlit`, `openai`, `python-dotenv`
- **파일 구조**
  ```
  번역기/
  ├─ app.py              # Streamlit 앱
  ├─ requirements.txt
  ├─ .env                # 로컬 전용 (Git 제외)
  ├─ .env.example        # 키 이름만 담은 템플릿
  ├─ .gitignore          # .env 포함
  └─ PRD.md
  ```

## 9. 배포
- **권장**: Streamlit Community Cloud (GitHub 저장소 연결, 무료)
  1. 코드를 GitHub에 push (`.env`는 제외)
  2. Streamlit Cloud에서 저장소/`app.py` 선택
  3. App settings → Secrets에 `OPENAI_API_KEY`, `OPENAI_MODEL` 등록
  4. Deploy
- 대안: Render, Railway, Hugging Face Spaces 등

## 10. 비기능 요구사항
- **보안**: API 키를 코드/저장소/클라이언트에 노출하지 않음. `.env`는 `.gitignore`에 포함.
- **성능**: 일반적인 짧은 문장 기준 응답 5초 이내 목표
- **비용 관리**: 입력 글자 수 제한으로 과다 호출 방지
- **가용성**: 키 누락 시 앱 시작 단계에서 명확한 오류 안내

## 11. 예외 처리
| 상황 | 처리 |
|------|------|
| 입력 비어있음 | 경고 메시지, 호출 안 함 |
| 글자 수 초과 | 경고 및 호출 차단 |
| API 키/모델 미설정 | "환경변수를 확인하세요" 오류 표시 |
| 네트워크/API 오류, 타임아웃 | "번역에 실패했습니다. 잠시 후 다시 시도해 주세요" 표시 |

## 12. 성공 지표
- 버튼 클릭 → 결과 표시까지 성공률 ≥ 95%
- 평균 응답 시간 ≤ 5초
- 배포된 URL로 외부 접속 가능

## 13. 마일스톤
1. **M1** 로컬 구현: `app.py`, 번역 함수, UI
2. **M2** 에러 처리 및 입력 검증
3. **M3** GitHub 업로드 및 Streamlit Cloud 배포, Secrets 설정
4. **M4** 동작 확인 및 마무리

## 14. 오픈 이슈
- `gpt-6.1-sol` 모델명이 사용하는 API 제공자에서 유효한지 배포 전 확인 필요 (무효 시 `OPENAI_MODEL` 값만 교체)
- 사용량이 늘 경우 접근 제한(비밀번호 등) 또는 호출 횟수 제한 도입 검토
