# 📰 IT/정책 뉴스 크롤링 및 자동화 리포트 시스템

초보자도 쉽게 실행할 수 있는 뉴스 크롤링, 정제, 추천 및 이메일 자동 발송 시스템입니다. 
Streamlit 대시보드를 통해 수집된 뉴스를 시각적으로 확인할 수도 있습니다.

## 📁 최종 산출물 목록
*   `data/` : 크롤링된 원본 데이터(`raw/`) 및 정제/추천 데이터(`processed/`)
*   `reports/` : 실무 보고용 HTML/TXT 이메일 미리보기 파일 및 발송 이력 로그 CSV
*   `logs/` : 시스템 오류 및 상태 로그 기록
*   `app/` : Streamlit 기반 웹 대시보드 (`streamlit_app.py`)
*   `.env.example` : 이메일 발송에 필요한 환경 변수 템플릿 파일
*   `README.md` : 프로젝트 실행 가이드 문서
*   기타 파이썬 스크립트 (`crawler.py`, `cleaner.py`, `recommender.py`, `email_report_builder.py`, `send_resend_email.py`)

---

## 🚀 실행 방법 (초보자용 가이드)

### 1. 환경 설정
```bash
# 1) 패키지 설치
pip install -r requirements.txt

# 2) .env 설정
# .env.example 파일을 복사하여 .env 파일을 만들고 Resend API Key를 입력하세요.
```

### 2. 데이터 수집 및 정제
```bash
# 1) 뉴스 크롤링 진행
python crawler.py

# 2) 데이터 정제 및 추천 점수 계산
python recommender.py
```

### 3. 리포트 생성 및 이메일 발송
```bash
# 1) 이메일 HTML/TXT 템플릿 생성 (보고용 디자인 적용)
python email_report_builder.py

# 2) 이메일 발송 (Resend API 연동)
python send_resend_email.py
```

### 4. 대시보드 확인
```bash
# Streamlit 대시보드 실행
streamlit run app/streamlit_app.py
```
