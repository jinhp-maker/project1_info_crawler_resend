import feedparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
import uuid
import time
from datetime import datetime
import logging
import os

# 로그 설정 (logs 폴더 내에 저장)
logging.basicConfig(filename='logs/crawler_error_log.txt', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 크롤링 설정
KEYWORDS = [
    'AI', '인공지능', '자동화', 'RPA', '클라우드', 'Cloud', 
    '빅데이터', '데이터분석', '사이버보안', '정보보안', 
    '디지털전환', 'DX', '머신러닝', '딥러닝', 'LLM', 
    '생성형 AI', '데이터센터', 'SaaS', 'IoT', '블록체인'
]
MAX_PER_KEYWORD = 30 # 키워드당 수집 목표
OUTPUT_FILE = 'data/raw/crawled_policy_news.csv'

def get_article_text(url):
    """
    주어진 URL에서 뉴스 본문을 추출합니다.
    (간단한 규칙: <p> 태그의 텍스트를 모으고, 안되면 전체 텍스트 일부를 가져옴)
    """
    try:
        # 안전한 요청을 위해 timeout과 일반 브라우저 User-Agent 설정
        res = requests.get(url, timeout=7, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        res.raise_for_status()
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 스크립트, 스타일 태그 등 불필요한 요소 제거
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.extract()
            
        # 1차 시도: <p> 태그 텍스트 결합 (주로 본문이 이 안에 있음)
        paragraphs = soup.find_all('p')
        content = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
        
        # 2차 시도: 만약 내용이 너무 짧거나 없다면, 일반 텍스트 추출 (최대 2000자)
        if len(content) < 100:
            content = soup.get_text(separator=' ', strip=True)[:2000]
            
        return content
    except Exception as e:
        logging.error(f"본문 파싱 오류 - {url}: {e}")
        return ""

import urllib.parse

def crawl():
    print("크롤링을 시작합니다. (Bing News RSS 활용)")
    all_articles = []
    urls_seen = set()
    
    for keyword in KEYWORDS:
        print(f"[{keyword}] 키워드로 뉴스 수집 중...")
        # URL 안전하게 인코딩 (공백 등 처리)
        encoded_keyword = urllib.parse.quote(keyword)
        # Bing News RSS URL
        rss_url = f"https://www.bing.com/news/search?q={encoded_keyword}&format=rss"
        feed = feedparser.parse(rss_url)
        
        count = 0
        for entry in feed.entries:
            if count >= MAX_PER_KEYWORD:
                break
                
            source_url = entry.link
            
            # 중복 URL 체크
            if source_url in urls_seen:
                continue
            urls_seen.add(source_url)
            
            title = entry.title
            date = entry.published if hasattr(entry, 'published') else ''
            summary = entry.description if hasattr(entry, 'description') else ''
            # 출처명 추출 시도
            source_name = entry.source.title if hasattr(entry, 'source') else 'Unknown'
            
            # 본문 추출
            content = get_article_text(source_url)
            
            # 결측치 확인
            has_null = not bool(title and content)
            
            all_articles.append({
                'article_id': str(uuid.uuid4()),
                'title': title,
                'date': date,
                'content': content,
                'summary': summary,
                'source_url': source_url,
                'source_name': source_name,
                'collected_at': datetime.now().isoformat(),
                'has_null': has_null
            })
            
            count += 1
            # 서버 부하 방지를 위해 짧게 대기
            time.sleep(0.1)
            
    print("크롤링 완료. 데이터를 CSV로 저장합니다.")
    df = pd.DataFrame(all_articles)
    
    # 디렉토리 존재 확인
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    # 데이터 저장
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    
    # 평가 지표 산출
    total_count = len(df)
    null_titles = df['title'].isnull().sum() + (df['title'] == '').sum()
    null_contents = df['content'].isnull().sum() + (df['content'] == '').sum()
    
    print("\n[수집 결과 평가 요약]")
    print(f"- 총 수집 건수: {total_count}건")
    print(f"- 결측 제목 수: {null_titles}건")
    print(f"- 결측 본문 수: {null_contents}건")
    print("\n- 소스별 상위 10개 건수:")
    
    source_counts = df['source_name'].value_counts().head(10)
    for name, cnt in source_counts.items():
        print(f"  * {name}: {cnt}건")
    
    if total_count < 200:
        print("\n[주의] 목표한 200건 미만입니다. 대체 소스나 키워드를 추가하여 재실행이 필요할 수 있습니다.")
    else:
        print("\n[성공] 목표한 200건 이상의 데이터를 확보했습니다.")

if __name__ == "__main__":
    crawl()
