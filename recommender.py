import pandas as pd
import re
import os

RAW_FILE = 'data/raw/crawled_policy_news.csv'
CLEANED_FILE = 'data/processed/cleaned_policy_news.csv'
RECOMMENDED_FILE = 'data/processed/recommended_policy_news.csv'

KEYWORDS = ['AI', '생성형 AI', '자동화', '클라우드', '데이터', '보안', '디지털 전환']

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    # 광고 및 불필요 문구 제거
    ad_phrases = ['무단전재', '재배포 금지', 'Copyright', '기자', 'ⓒ', '무단 전재', '재배포금지']
    for phrase in ad_phrases:
        text = text.replace(phrase, '')
    # 연속된 공백 치환
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def calculate_score(row):
    score = 0
    title = str(row['title'])
    content = str(row['content'])
    for kw in KEYWORDS:
        # 제목 가중치 2, 본문 가중치 1
        score += title.count(kw) * 2
        score += content.count(kw) * 1
    return score

def process_data():
    if not os.path.exists(RAW_FILE):
        print(f"Error: {RAW_FILE} 파일이 존재하지 않습니다.")
        return

    df = pd.read_csv(RAW_FILE)
    initial_count = len(df)

    # 1. 결측치 및 빈 제목 제거
    # has_null이 True인 행, 혹은 title/content가 없는 행 제거
    df_null_dropped = df.dropna(subset=['title', 'content'])
    df_null_dropped = df_null_dropped[~df_null_dropped['has_null'].astype(bool)]
    df_null_dropped = df_null_dropped[df_null_dropped['title'].str.strip() != '']
    null_removed = initial_count - len(df_null_dropped)

    # 2. 텍스트 정제 (HTML, 광고문구 제거)
    df_null_dropped = df_null_dropped.copy()
    df_null_dropped['content'] = df_null_dropped['content'].apply(clean_text)
    df_null_dropped['title'] = df_null_dropped['title'].apply(clean_text)

    # 3. 너무 짧은 본문 제거 (50자 미만)
    df_length_filtered = df_null_dropped[df_null_dropped['content'].str.len() >= 50].copy()
    short_removed = len(df_null_dropped) - len(df_length_filtered)

    # 4. 중복 및 유사 기사 제거 (제목 공백 제거 후 비교, URL 비교)
    df_length_filtered['norm_title'] = df_length_filtered['title'].str.replace(r'\s+', '', regex=True)
    df_deduped = df_length_filtered.drop_duplicates(subset=['norm_title'], keep='first')
    df_deduped = df_deduped.drop_duplicates(subset=['source_url'], keep='first').copy()
    duplicates_removed = len(df_length_filtered) - len(df_deduped)
    
    # 임시 컬럼 제거
    df_deduped = df_deduped.drop(columns=['norm_title'])

    # 정제된 파일 저장
    os.makedirs(os.path.dirname(CLEANED_FILE), exist_ok=True)
    df_deduped.to_csv(CLEANED_FILE, index=False, encoding='utf-8-sig')

    # 5. 추천 점수 계산
    df_deduped['score'] = df_deduped.apply(calculate_score, axis=1)
    
    # 점수 순, 그 다음 최신 순으로 정렬
    df_sorted = df_deduped.sort_values(by=['score', 'collected_at'], ascending=[False, False])
    
    # 상위 20건 추출 및 저장
    df_top20 = df_sorted.head(20)
    os.makedirs(os.path.dirname(RECOMMENDED_FILE), exist_ok=True)
    df_top20.to_csv(RECOMMENDED_FILE, index=False, encoding='utf-8-sig')

    # 평가 결과 출력
    print(f"[정제 및 추천 평가 결과]")
    print(f"- 원본 기사 수: {initial_count}건")
    print(f"- 결측 및 빈 제목으로 제거된 수: {null_removed}건")
    print(f"- 짧은 본문으로 제거된 수: {short_removed}건")
    print(f"- 중복/유사 기사로 제거된 수: {duplicates_removed}건")
    print(f"- 최종 정제된 기사 수: {len(df_deduped)}건\n")
    
    print("[추천 상위 5건]")
    for idx, row in df_top20.head(5).iterrows():
        print(f"점수: {row['score']} | 제목: {row['title']}")

if __name__ == '__main__':
    process_data()
