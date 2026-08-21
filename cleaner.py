import pandas as pd
import logging
import os

# 로그 설정
logging.basicConfig(filename='logs/crawler_error_log.txt', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

INPUT_FILE = 'data/raw/crawled_policy_news.csv'
OUTPUT_FILE = 'data/processed/cleaned_policy_news.csv'

def clean_data():
    print("데이터 정제 및 중복 제거를 시작합니다...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"오류: 입력 파일({INPUT_FILE})이 존재하지 않습니다.")
        return

    # 1. 데이터 로드
    df = pd.read_csv(INPUT_FILE)
    initial_count = len(df)
    
    # 2. 결측치 처리 (has_null이 True이거나 제목/본문이 없는 경우 제외)
    df = df.dropna(subset=['title', 'content'])
    # boolean 컬럼 처리 보완
    df = df[~df['has_null'].astype(bool)]
    
    # 3. 중복 제거 (제목 또는 URL 기준 중복 제거)
    df = df.drop_duplicates(subset=['title'], keep='first')
    df = df.drop_duplicates(subset=['source_url'], keep='first')
    
    # 본문 텍스트 정제 (연속된 공백 제거 등)
    df['content'] = df['content'].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
    
    # 길이가 너무 짧은 기사 제외 (최소 50자 이상)
    df = df[df['content'].str.len() >= 50]
    
    final_count = len(df)
    removed_count = initial_count - final_count
    
    # 4. 저장
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    
    # 5. 결과 출력
    print("\n[정제 결과 요약]")
    print(f"- 원본 데이터 건수: {initial_count}건")
    print(f"- 제외된 데이터 건수: {removed_count}건 (중복, 결측, 짧은 본문)")
    print(f"- 최종 유효 데이터 건수: {final_count}건")
    
    if final_count < 150:
        print("\n[알림] 정제 후 데이터가 예상보다 적습니다. 필요 시 크롤링을 추가 진행할 수 있습니다.")
    else:
        print("\n[성공] 데이터 정제 및 중복 제거가 성공적으로 완료되었습니다.")

if __name__ == "__main__":
    clean_data()
