import streamlit as st
from urllib.parse import urlparse

# 신뢰할 수 있는 언론사 도메인 리스트 (필요에 따라 추가/수정 가능)
# 주요 일간지, 통신사, 방송사, IT 전문지 등을 포함
TRUSTED_SOURCES = [
    'chosun.com', 'joongang.co.kr', 'donga.com', # 주요 일간지
    'hani.co.kr', 'khan.co.kr', 'kyunghyang.com', # 주요 일간지
    'seoul.co.kr', 'hankookilbo.com', 'munhwa.com', # 주요 일간지
    'yna.co.kr', 'newsis.com', 'news1.kr', # 통신사
    'sbs.co.kr', 'kbs.co.kr', 'mbc.co.kr', 'ytn.co.kr', # 방송사
    'zdnet.co.kr', 'etnews.com', 'it.chosun.com', # IT 전문
    'hankyung.com', 'mk.co.kr' # 경제지
]

@st.cache_data(ttl=3600) # 1시간 동안 결과 캐싱
def estimate_trust_score(similar_urls):
    """
    유사 기사 URL 리스트를 받아 신뢰도 등급과 분석 결과를 반환합니다.
    새로운 규칙에 따라 등급을 결정합니다.
    """
    if not similar_urls:
        return {
            'grade': 'N/A',
            'summary': '분석할 유사 기사를 찾지 못했습니다.',
            'total_articles': 0,
            'trusted_count': 0,
            'unique_domains': 0,
            'trusted_urls': [],
            'other_urls': []
        }

    # 1. 지표 계산: 전체 기사 수, 신뢰 출처 수, 도메인 다양성 등
    total_articles = len(similar_urls)
    unique_domains = set()
    trusted_urls = []
    other_urls = []

    for url in similar_urls:
        try:
            domain = urlparse(url).netloc.replace('www.', '')
            unique_domains.add(domain)
            # 도메인 리스트 중 하나라도 포함되면 신뢰 출처로 간주
            if any(trusted_domain in domain for trusted_domain in TRUSTED_SOURCES):
                trusted_urls.append(url)
            else:
                other_urls.append(url)
        except Exception:
            # URL 파싱 오류 시 건너뜀
            continue
            
    trusted_count = len(trusted_urls)
    
    # 2. 새로운 규칙에 따라 등급 및 요약 결정
    grade = ''
    summary = ''
    
    # 규칙 1: 기사 개수가 9개 이상이면 'C'
    if total_articles >= 9:
        grade = 'C'
        summary = f"유사 기사가 {total_articles}건으로 과도하게 많아 어뷰징 또는 스팸성 이슈일 수 있습니다. 신뢰도를 낮게 평가합니다."
    
    # 규칙 2: 기사 개수가 2개 이하면 무조건 'B'
    elif total_articles <= 2:
        grade = 'B'
        summary = f"유사 기사가 {total_articles}건으로 매우 적어 교차 검증이 어렵습니다. 주장의 신뢰성을 단정하기 힘들어 주의가 필요합니다."
    
    # 규칙 3: 기사 개수가 3개 ~ 8개 사이일 때
    else:
        # 신뢰성 있는 출처가 1개 이상이면 'A'
        if trusted_count >= 1:
            grade = 'A'
            summary = f"신뢰도 높은 언론사 {trusted_count}곳을 포함해 총 {total_articles}곳에서 해당 내용을 다루고 있어 신뢰도가 높습니다."
        # 신뢰성 있는 출처가 없으면 'C'
        else:
            grade = 'C'
            summary = f"총 {total_articles}곳에서 관련 내용을 다루고 있지만, 신뢰도 높은 주요 언론사가 없어 사실 확인이 필요합니다."

    # 3. 최종 결과 딕셔너리 구성
    result = {
        'grade': grade,
        'summary': summary,
        'total_articles': total_articles,
        'trusted_count': trusted_count,
        'unique_domains': len(unique_domains),
        'trusted_urls': trusted_urls,
        'other_urls': other_urls
    }

    return result