# m2_analyzer.py (프롬프트 개선 버전)
import streamlit as st
from openai import OpenAI
import re

# st.secrets에서 API 키를 안전하게 불러옵니다.
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error("OPENAI_API_KEY가 설정되지 않았습니다. .streamlit/secrets.toml 파일을 확인해주세요.")
    st.stop()


def get_keywords_from_llm(text: str) -> list[str]:
    """
    본문 텍스트를 LLM API로 보내 검색에 용이한 핵심 주장을 추출하는 함수
    """
    # [수정] 프롬프트를 더 구체적이고 명확하게 변경
    system_prompt = """
    당신은 뉴스 기사의 핵심 사실을 추출하는 AI 팩트체커입니다.
    사용자가 제공하는 기사 본문에서, 다른 기사와 교차 검증이 가능한 '핵심 주장(Key Claims)'을 찾아야 합니다.

    아래의 규칙을 반드시 따르세요:
    1. 주관적인 의견이나 감정적인 표현은 모두 제외하고, 객관적인 사실에만 집중하세요.
    2. '누가, 무엇을, 언제, 어디서, 왜, 어떻게' 육하원칙에 해당하는 내용을 중심으로 추출하세요.
    3. 각 주장은 다른 뉴스 기사에서 검색으로 찾을 수 있을 만한 내용이어야 합니다.
    4. 가장 중요한 순서대로 3개에서 5개 사이의 주장을 완전한 문장 형태로 추출해주세요.
    5. 번호를 매겨 목록으로 제시해주세요. (예: 1. OOO가 XXX를 발표했습니다.)
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # 더 최신이고 효율적인 모델로 변경
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.2, # 사실 추출이므로 온도를 약간 낮춤
        )
        
        content = response.choices[0].message.content
        
        # LLM의 답변(번호 매겨진 문자열)을 파이썬 리스트로 변환
        keywords = [line.strip() for line in content.split('\n') if line.strip()]
        # "1. ", "2. " 같은 번호 부분을 제거
        cleaned_keywords = [re.sub(r'^\d+\.\s*', '', keyword) for keyword in keywords]
        
        if not cleaned_keywords:
            st.warning("AI가 기사에서 핵심 주장을 추출하지 못했습니다. 기사 내용이 너무 짧거나 분석이 어려울 수 있습니다.")
            return []

        return cleaned_keywords

    except Exception as e:
        st.error(f"OpenAI API 호출 중 오류가 발생했습니다: {e}")
        return ["오류"]
