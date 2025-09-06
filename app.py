import streamlit as st

# ##############################################################################
# 실제 import 구문 (위 가짜 함수들을 지울 경우 주석 해제)
from m1_scraper import get_article_text
from m2_analyzer import get_keywords_from_llm
from m3_searcher import search_news_articles
from m4_estimator import estimate_trust_score
# ##############################################################################


# --- 페이지 설정 ---
st.set_page_config(layout="wide", page_title="AI 뉴스 신뢰도 분석기")

# --- CSS 파일 로드 함수 ---
def local_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"'{file_name}' 파일을 찾을 수 없습니다. app.py와 같은 경로에 있는지 확인해주세요.")

# CSS 파일 적용
local_css("main.css")

# --- 세션 상태(Session State) 초기화 ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'url' not in st.session_state:
    st.session_state.url = ""
if 'article_text' not in st.session_state:
    st.session_state.article_text = None
if 'keywords' not in st.session_state:
    st.session_state.keywords = None
if 'final_result' not in st.session_state:
    st.session_state.final_result = None
if 'show_report' not in st.session_state:
    st.session_state.show_report = False

# --- 페이지 렌더링 함수 정의 ---

def render_home_page():
    """Page 1: URL을 입력받는 메인 페이지를 렌더링합니다."""
    st.title("📰 AI 뉴스 신뢰도 분석기")
    st.subheader("분석하고 싶은 뉴스 기사의 URL을 입력해주세요.")
    url_input = st.text_input("URL 입력", placeholder="https://www.example-news.com/...", key="url_input")
    if st.button("분석 시작하기", type="primary"):
        if url_input:
            st.session_state.url = url_input
            st.session_state.page = 'article'
            # article 페이지로 넘어가기 전에 이전 상태를 초기화
            st.session_state.article_text = None
            st.session_state.final_result = None
            st.session_state.show_report = False
            st.rerun()
        else:
            st.warning("URL을 입력해주세요.")

def render_article_page():
    """Page 2, 3: 기사 본문 표시, 자동 AI 분석을 처리합니다."""
    if st.button("◀ 다른 기사 분석하기"):
        st.session_state.page = 'home'
        # 홈으로 돌아갈 때 모든 상태 초기화
        st.session_state.url = ""
        st.session_state.article_text = None
        st.session_state.keywords = None
        st.session_state.final_result = None
        st.session_state.show_report = False
        st.rerun()

    # --- 1단계: 본문 스크래핑 (아직 안했다면) ---
    if st.session_state.get('article_text') is None:
        with st.spinner("기사 본문을 추출하고 있습니다..."):
            article_text = get_article_text(st.session_state.url)
            if article_text and "오류" not in article_text:
                st.session_state.article_text = article_text
                st.rerun()
            else:
                st.error("기사 본문을 가져오는 데 실패했습니다. URL을 확인하거나 다른 기사를 시도해주세요.")
                return

    st.header("기사 본문")
    st.markdown(f"> 원문 링크: [{st.session_state.url}]({st.session_state.url})")
    
    _, col2 = st.columns([0.7, 0.3]) 
    button_placeholder = col2.empty()

    st.text_area("추출된 본문 내용", st.session_state.article_text, height=400, key="article_display")

    # --- 2단계: AI 분석 (아직 안했다면) ---
    if st.session_state.get('final_result') is None:
        with button_placeholder.container():
            with st.spinner("AI가 기사를 종합 분석하고 있습니다..."):
                keywords = get_keywords_from_llm(st.session_state.article_text)
                if keywords and "오류" not in keywords[0]:
                    st.session_state.keywords = keywords
                    similar_urls = search_news_articles(st.session_state.keywords)
                    st.session_state.final_result = estimate_trust_score(similar_urls)
                else:
                    st.session_state.final_result = {'grade': 'N/A', 'summary': '기사의 핵심 주장을 추출하는 데 실패하여 분석을 진행할 수 없습니다.'}
                
                # ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
                # 수정된 부분 1: 분석이 끝나면 바로 리포트를 표시하도록 상태 변경
                st.session_state.show_report = True 
                # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

        st.rerun()

    # --- 3단계: 분석 완료 후 버튼 표시 ---
    else:
        with button_placeholder.container():
            result = st.session_state.get('final_result', {})
            grade = result.get('grade', 'N/A')
            
            if grade == 'A':
                st.success("✅ 분석 완료: 신뢰도 높음")
            elif grade == 'B':
                st.warning("⚠️ 분석 완료: 주의 필요")
            else:
                st.error("❌ 분석 완료: 신뢰도 낮음")

            # ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
            # 수정된 부분 2: 버튼 텍스트가 바로 "숨기기"로 표시되도록 수정
            button_text = "상세 리포트 숨기기" if st.session_state.get('show_report') else "상세 리포트 보기"
            if st.button(button_text, use_container_width=True, key="toggle_report"):
                st.session_state.show_report = not st.session_state.get('show_report', False)
                st.rerun()
            # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

def render_sidebar():
    """4단계: 리포트 사이드바를 렌더링하는 함수"""
    with st.sidebar:
        st.header("🏁 최종 분석 리포트")
        result = st.session_state.get('final_result', {})
        grade = result.get('grade', 'N/A')
        
        if grade == 'A': st.success(f"## 신뢰도 등급: {grade}")
        elif grade == 'B': st.warning(f"## 신뢰도 등급: {grade}")
        elif grade == 'N/A': st.info(f"## 신뢰도 등급: {grade} (분석 불가)")
        else: st.error(f"## 신뢰도 등급: {grade}")
        
        st.info(f"**분석 요약:** {result.get('summary', '요약 정보 없음')}")

        if grade != 'N/A' and result.get('total_articles'): # 데이터가 있을 때만 표시
            st.subheader("📊 분석 핵심 지표")
            c1, c2, c3 = st.columns(3)
            c1.metric("유사 기사 수", f"{result.get('total_articles', 'N/A')} 개")
            c2.metric("신뢰도 높은 출처", f"{result.get('trusted_count', 'N/A')} 곳")
            c3.metric("출처 다양성", f"{result.get('unique_domains', 'N/A')} 곳")
            
            with st.expander("분석에 사용된 기사 출처 전체 보기"):
                st.markdown("#### ✅ 신뢰도 높은 언론사")
                st.write(result.get('trusted_urls') or ["발견되지 않음"])
                st.markdown("#### ❓ 기타 출처")
                st.write(result.get('other_urls') or ["발견되지 않음"])


# --- 메인 라우터(Router) ---
# 메인 페이지 렌더링
if st.session_state.page == 'home':
    render_home_page()
elif st.session_state.page == 'article':
    render_article_page()

# 사이드바 렌더링 로직
if st.session_state.page == 'article' and st.session_state.get('show_report'):
    render_sidebar()