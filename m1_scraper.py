# m1_scraper.py (하이브리드 최종 버전)
import requests
import re
import json
from bs4 import BeautifulSoup

def get_article_text(url: str) -> str:
    """
    URL을 입력받아 두 가지 방식으로 기사 본문을 추출하는 함수
    1순위: JavaScript 변수(JSON) 파싱 시도
    2순위: HTML 태그 직접 검색 시도
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- 1순위: JSON 파싱 시도 ---
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'Fusion.globalContent' in script.string:
                match = re.search(r'Fusion\.globalContent\s*=\s*({.*?});', script.string)
                if match:
                    json_data_str = match.group(1)
                    data = json.loads(json_data_str)
                    content_list = [
                        element.get('content', '')
                        for element in data.get('content_elements', [])
                        if element.get('type') == 'text'
                    ]
                    if content_list:
                        # 성공 시 여기서 함수 종료
                        return '\n\n'.join(content_list)

        # --- 2순위: HTML 태그 직접 검색 시도 (1순위 실패 시 실행) ---
        article_body = soup.find('div', class_='article-body')
        if article_body:
            # 성공 시 여기서 함수 종료
            return article_body.get_text(separator='\n', strip=True)

        # --- 최종 실패 ---
        return "두 가지 방법 모두 본문 추출에 실패했습니다. 사이트 구조를 확인해주세요."

    except requests.exceptions.RequestException as e:
        return f"URL 요청 중 오류 발생: {e}"
    except Exception as e:
        return f"알 수 없는 오류 발생: {e}"