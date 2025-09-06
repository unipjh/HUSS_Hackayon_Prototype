# m3_searcher.py (반환 형태 수정)
import streamlit as st
import requests

def search_news_articles(claims: list[str]) -> dict[str, list[str]]:
    """
    핵심 주장을 받아 네이버 검색 API로 '주장: URL 리스트' 딕셔너리를 반환하는 함수
    """
    client_id = st.secrets.get("NAVER_CLIENT_ID")
    client_secret = st.secrets.get("NAVER_CLIENT_SECRET")

    if not client_id or not client_secret:
        st.error("🔑 네이버 API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일을 확인해주세요.")
        return {}

    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    
    # [수정] 결과를 담을 자료구조를 딕셔너리로 변경
    search_results = {}

    for query in claims:
        params = {"query": query, "display": 5, "sort": "sim"}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # [수정] 현재 쿼리에 대한 URL만 추출
            urls_for_query = []
            for item in data.get("items", []):
                if "news.naver.com" in item.get("link", ""):
                    urls_for_query.append(item["link"])
            
            # [수정] 쿼리를 key로, URL 리스트를 value로 저장
            if urls_for_query: # 검색 결과가 있을 때만 추가
                search_results[query] = urls_for_query

        except requests.exceptions.RequestException as e:
            st.error(f"'{query}' 검색 중 API 오류: {e}")
            continue

    return search_results