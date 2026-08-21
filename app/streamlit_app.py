import streamlit as st
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="IT/정책 뉴스 대시보드", page_icon="📰", layout="wide")

# 커스텀 CSS (흰색 배경, 남색 헤더, 회색 카드, 초록 배지)
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1, h2, h3 { color: #003366; }
    
    /* 카드 스타일 */
    .st-emotion-cache-1wivap2, .css-1wivap2, div[data-testid="stVerticalBlock"] > div > div > div > div { 
        background-color: #f4f6f9; 
        border-radius: 8px; 
        padding: 20px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
        border-left: 5px solid #003366; 
        margin-bottom: 20px; 
    }
    
    .success-badge { 
        display: inline-block; 
        background-color: #28a745; 
        color: white; 
        padding: 4px 10px; 
        border-radius: 12px; 
        font-size: 13px; 
        font-weight: bold; 
        margin-bottom: 10px; 
    }
    .article-title { font-size: 20px; font-weight: bold; color: #003366; margin-bottom: 10px; }
    .article-meta { font-size: 14px; color: #666666; margin-bottom: 10px; }
    .article-summary { font-size: 15px; color: #333333; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.title("📰 주요 IT/정책 뉴스 대시보드")
st.markdown("실무 보고용 핵심 추천 기사 모음")

DATA_FILE = 'data/processed/recommended_policy_news.csv'

if not os.path.exists(DATA_FILE):
    st.error(f"데이터 파일이 없습니다. 크롤러와 추천 스크립트를 먼저 실행해주세요: {DATA_FILE}")
else:
    df = pd.read_csv(DATA_FILE)
    top10_df = df.head(10)
    
    st.success(f"총 {len(df)}건의 추천 기사 중 상위 TOP 10을 보여줍니다.")
    
    # 카드 형태로 TOP 10 출력
    for idx, row in top10_df.iterrows():
        title = row.get('title', '제목 없음')
        score = row.get('score', 0)
        source_name = row.get('source_name', '알 수 없음')
        date = row.get('date', '')
        url = row.get('source_url', '#')
        summary = row.get('summary', '')
        
        if pd.isna(summary) or str(summary).strip() == '':
            content = str(row.get('content', ''))
            summary = content[:200] + '...' if len(content) > 200 else content

        with st.container():
            st.markdown('<hr style="margin: 0; border: none;">', unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background-color: #f4f6f9; border-radius: 8px; padding: 20px; border-left: 5px solid #003366; margin-bottom: 20px;">
                    <span class="success-badge">추천 점수: {score}점</span>
                    <div class="article-title">{idx + 1}. <a href="{url}" target="_blank" style="color: #003366; text-decoration: none;">{title}</a></div>
                    <div class="article-meta">출처: {source_name} | 발행일: {date}</div>
                    <div class="article-summary">{summary}</div>
                </div>
            """, unsafe_allow_html=True)
