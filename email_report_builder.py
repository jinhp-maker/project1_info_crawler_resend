import pandas as pd
import os
from datetime import datetime

INPUT_FILE = 'data/processed/recommended_policy_news.csv'
HTML_OUTPUT = 'reports/email_preview.html'
TXT_OUTPUT = 'reports/email_preview.txt'

def build_email_reports():
    print("이메일 리포트 생성을 시작합니다... (실무 보고용 디자인 적용 및 TOP 10 반영)")
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} 파일이 존재하지 않습니다.")
        return

    # TOP 10건만 추출
    df = pd.read_csv(INPUT_FILE).head(10)
    
    today_str = datetime.now().strftime('%Y년 %m월 %d일')
    
    # --- HTML 리포트 생성 (디자인 개선) ---
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; line-height: 1.6; color: #333; background-color: #ffffff; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; }}
            .header {{ background-color: #003366; color: #ffffff; padding: 25px 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .header p {{ margin: 10px 0 0 0; font-size: 14px; opacity: 0.9; }}
            .content {{ padding: 30px 20px; background-color: #ffffff; }}
            .card {{ background-color: #f4f6f9; border-left: 5px solid #003366; margin-bottom: 25px; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
            .card-title {{ font-size: 18px; font-weight: bold; color: #003366; margin: 0 0 12px 0; }}
            .badge {{ display: inline-block; background-color: #28a745; color: white; padding: 4px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; margin-bottom: 15px; }}
            .meta {{ font-size: 13px; color: #555; margin-bottom: 12px; }}
            .summary {{ font-size: 14px; color: #444; margin-bottom: 15px; }}
            .link-btn {{ display: inline-block; padding: 10px 18px; background-color: #003366; color: white; text-decoration: none; border-radius: 4px; font-size: 13px; font-weight: bold; }}
            .footer {{ text-align: center; margin-top: 10px; font-size: 12px; color: #999; padding: 20px; background-color: #f9f9f9; border-top: 1px solid #eee; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📰 주요 IT/정책 뉴스 일일 브리핑</h1>
                <p>{today_str} 기준 핵심 추천 기사 TOP 10</p>
            </div>
            <div class="content">
    """
    
    # --- TXT 리포트 생성 ---
    txt_content = f"주요 IT/정책 뉴스 일일 브리핑 ({today_str} 기준 TOP 10)\n"
    txt_content += "=" * 50 + "\n\n"
    
    for idx, row in df.iterrows():
        title = row.get('title', '제목 없음')
        score = row.get('score', 0)
        source_url = row.get('source_url', '#')
        source_name = row.get('source_name', '알 수 없음')
        date = row.get('date', '')
        
        summary = row.get('summary')
        if pd.isna(summary) or str(summary).strip() == '':
            content = str(row.get('content', ''))
            summary = content[:150] + '...' if len(content) > 150 else content
        else:
            summary = str(summary)
            
        # HTML 덧붙이기
        html_content += f"""
                <div class="card">
                    <div class="badge">추천 점수: {score}점</div>
                    <h2 class="card-title">{idx + 1}. {title}</h2>
                    <div class="meta">출처: {source_name} | {date}</div>
                    <div class="summary">{summary}</div>
                    <a href="{source_url}" class="link-btn" target="_blank">기사 원문 보기</a>
                </div>
        """
        
        # TXT 덧붙이기
        txt_content += f"[{idx + 1}] {title}\n"
        txt_content += f"- 추천 점수: {score}점 | 출처: {source_name} | {date}\n"
        txt_content += f"- 요약: {summary}\n"
        txt_content += f"- 링크: {source_url}\n"
        txt_content += "-" * 50 + "\n"
        
    html_content += """
            </div>
            <div class="footer">
                <p>본 메일은 자동화된 시스템에 의해 발송되었습니다.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # 디렉토리 생성 및 저장
    os.makedirs(os.path.dirname(HTML_OUTPUT), exist_ok=True)
    os.makedirs(os.path.dirname(TXT_OUTPUT), exist_ok=True)
    
    with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    with open(TXT_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(txt_content)
        
    print(f"디자인 반영 미리보기 파일 생성 완료!\n- HTML: {HTML_OUTPUT}\n- TXT: {TXT_OUTPUT}")

if __name__ == '__main__':
    build_email_reports()
