import os

import openai
import streamlit as st
from dotenv import load_dotenv

# 로컬 개발 시 .env 로드 (배포 환경에서는 플랫폼의 Secrets/환경변수 사용)
load_dotenv()

DEFAULT_MODEL = "gpt-6.1-sol"
MAX_CHARS = 2000
TIMEOUT_SEC = 30

LANGUAGES = {
    "영어": "English",
    "일본어": "Japanese",
    "베트남어": "Vietnamese",
}

SYSTEM_PROMPT = (
    "You are a professional translator. Translate the user's text into {lang}. "
    "Output only the translated text, with no explanations, notes, or quotation marks. "
    "Preserve line breaks and tone."
)

MSG_EMPTY = "텍스트를 입력해 주세요."
MSG_TOO_LONG = f"글자 수가 너무 많습니다. {MAX_CHARS:,}자 이하로 입력해 주세요."
MSG_CONFIG = "환경변수(OPENAI_API_KEY, OPENAI_MODEL)를 확인하세요."
MSG_FAIL = "번역에 실패했습니다. 잠시 후 다시 시도해 주세요."


class TranslationError(Exception):
    """사용자에게 그대로 보여줄 수 있는 메시지를 담는 예외."""


def translate(text: str, target_language: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL") or DEFAULT_MODEL
    if not api_key or not model:
        raise TranslationError(MSG_CONFIG)

    try:
        client = openai.OpenAI(api_key=api_key, timeout=TIMEOUT_SEC)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.format(lang=target_language)},
                {"role": "user", "content": text},
            ],
        )
        result = (response.choices[0].message.content or "").strip()
    except (
        openai.AuthenticationError,
        openai.PermissionDeniedError,
        openai.NotFoundError,
        openai.BadRequestError,
    ):
        # 키 오류 / 모델 없음·권한 없음 / 모델이 거부하는 요청 → 설정 문제로 안내 (상세 내용은 노출하지 않음)
        raise TranslationError(MSG_CONFIG) from None
    except Exception:
        # 네트워크, 타임아웃, 기타 API 오류 (예외 상세·키는 화면에 노출하지 않음)
        raise TranslationError(MSG_FAIL) from None

    if not result:
        raise TranslationError(MSG_FAIL)
    return result


def validate(text: str) -> str | None:
    """문제가 있으면 사용자용 메시지를, 없으면 None을 반환."""
    if not text.strip():
        return MSG_EMPTY
    if len(text) > MAX_CHARS:
        return MSG_TOO_LONG
    return None


FLAGS = {"영어": "🇺🇸", "일본어": "🇯🇵", "베트남어": "🇻🇳"}

# Streamlit 테마 변수를 쓰므로 밝은/어두운 테마 모두에서 글자가 잘 보인다.
CSS = """
<style>
.block-container { padding-top: 2.5rem; max-width: 760px; }
h1 { text-align: center; margin-bottom: 0.25rem; }
.subtitle { text-align: center; opacity: 0.7; margin-bottom: 1.5rem; }
.char-count { text-align: right; font-size: 0.85rem; opacity: 0.7; margin-top: -0.5rem; }
.char-count.over { color: #e5484d; opacity: 1; font-weight: 600; }
div[data-testid="stTextArea"] textarea { font-size: 1.05rem; line-height: 1.5; }
.stButton > button { height: 3rem; font-size: 1.05rem; font-weight: 600; border-radius: 0.6rem; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 0.8rem; }
/* 모바일에서도 버튼 3개를 한 줄로 유지 */
@media (max-width: 640px) {
    div[data-testid="stHorizontalBlock"] { flex-wrap: nowrap; gap: 0.5rem; }
    div[data-testid="stColumn"] { min-width: 0 !important; width: auto !important; flex: 1 1 0 !important; }
}
@media (max-width: 480px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1.5rem; }
    .stButton > button { font-size: 0.95rem; padding-left: 0.25rem; padding-right: 0.25rem; }
}
</style>
"""


def main():
    st.set_page_config(page_title="AI 번역기", page_icon="🌐", layout="centered")
    st.markdown(CSS, unsafe_allow_html=True)
    st.title("🌐 AI 번역기")
    st.markdown(
        '<div class="subtitle">글을 입력하고 번역할 언어를 선택하세요</div>',
        unsafe_allow_html=True,
    )

    text = st.text_area(
        "번역할 텍스트",
        height=200,
        placeholder="번역할 글을 입력하세요. (최대 2,000자)",
        label_visibility="collapsed",
    )
    over = len(text) > MAX_CHARS
    st.markdown(
        f'<div class="char-count{" over" if over else ""}">{len(text):,} / {MAX_CHARS:,}</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(len(LANGUAGES))
    clicked = None
    for col, label in zip(cols, LANGUAGES):
        if col.button(f"{FLAGS[label]} {label}", use_container_width=True, key=f"btn_{label}"):
            clicked = label

    if not clicked:
        return

    problem = validate(text)
    if problem:
        st.warning(problem)
        return

    try:
        with st.spinner("번역 중..."):
            result = translate(text, LANGUAGES[clicked])
    except TranslationError as e:
        st.error(str(e))
        return

    with st.container(border=True):
        st.caption(f"{FLAGS[clicked]} {clicked} 번역 결과")
        # st.code 블록의 복사 아이콘으로 복사 가능
        st.code(result, language=None, wrap_lines=True)


if __name__ == "__main__":
    main()
