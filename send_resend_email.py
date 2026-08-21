import os
import re
import csv
import logging
from datetime import datetime
import resend
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

HTML_FILE = 'reports/email_preview.html'
LOG_FILE = 'reports/resend_send_log.csv'
ERROR_LOG_FILE = 'logs/resend_error_log.txt'

os.makedirs(os.path.dirname(ERROR_LOG_FILE), exist_ok=True)
logging.basicConfig(filename=ERROR_LOG_FILE, level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def validate_env():
    api_key = os.getenv('RESEND_API_KEY', '')
    sender = os.getenv('SENDER_EMAIL', '')
    receiver = os.getenv('RECEIVER_EMAIL', '')
    enable_send = str(os.getenv('ENABLE_REAL_EMAIL_SEND', 'false')).lower()

    errors = []
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    if not api_key.startswith('re_'):
        errors.append("- RESEND_API_KEY가 올바르지 않습니다. 're_'로 시작하는 키를 발급받아 입력해주세요.")
    if not re.match(email_regex, sender):
        errors.append("- SENDER_EMAIL 형식이 올바르지 않습니다. 정확한 이메일 주소를 입력해주세요.")
    if not re.match(email_regex, receiver):
        errors.append("- RECEIVER_EMAIL 형식이 올바르지 않습니다. 정확한 이메일 주소를 입력해주세요.")
    if enable_send != 'true':
        errors.append("- ENABLE_REAL_EMAIL_SEND가 'true'가 아닙니다. 실제 발송을 원하시면 'true'로 변경해주세요.")

    if errors:
        print("❌ [환경 변수 설정 오류]")
        for err in errors:
            print(err)
        print("\n.env 파일을 수정한 후 다시 실행해주세요.")
        return False
    return True

def check_already_sent(receiver_email, subject, today_str):
    if not os.path.exists(LOG_FILE):
        return False
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sent_date = row.get('sent_at', '')[:10]
            if sent_date == today_str and row.get('receiver_email') == receiver_email and row.get('subject') == subject and row.get('status') == 'SUCCESS':
                return True
    return False

def send_email():
    print("이메일 발송 준비 중...")
    
    if not validate_env():
        return
        
    api_key = os.getenv('RESEND_API_KEY')
    sender_email = os.getenv('SENDER_EMAIL')
    receiver_email = os.getenv('RECEIVER_EMAIL')
        
    if not os.path.exists(HTML_FILE):
        print(f"Error: {HTML_FILE} 파일이 존재하지 않습니다. 먼저 email_report_builder.py를 실행하세요.")
        return
        
    # HTML 리포트 읽기
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    resend.api_key = api_key
    
    subject = "📰 주요 IT/정책 뉴스 일일 브리핑"
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    if check_already_sent(receiver_email, subject, today_str):
        print("💡 [중복 발송 방지] 오늘 이미 동일한 수신자와 제목으로 발송된 기록이 있습니다. 발송을 건너뜁니다.")
        return

    try:
        print(f"수신자({receiver_email})에게 이메일을 발송합니다...")
        
        params = {
            "from": sender_email,
            "to": receiver_email,
            "subject": subject,
            "html": html_content
        }
        
        # Resend API 호출
        email_response = resend.Emails.send(params)
        resend_email_id = email_response.get('id', 'Unknown')
        print(f"[SUCCESS] 이메일 발송 성공! (ID: {resend_email_id})")
        
        # 로그 기록
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        file_exists = os.path.exists(LOG_FILE)
        with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['sent_at', 'receiver_email', 'subject', 'status', 'resend_email_id'])
            writer.writerow([datetime.now().isoformat(), receiver_email, subject, 'SUCCESS', resend_email_id])
        
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] 이메일 발송 실패: {error_msg}")
        logging.error(f"Failed to send email to {receiver_email}: {error_msg}")
        
        if '403' in error_msg or 'forbidden' in error_msg.lower():
            print("\n[!] 403 Forbidden 오류가 발생했습니다.")
            print("발신 도메인이 Resend에 등록 및 검증(Verified)되지 않았거나 권한이 부족할 수 있습니다.")
            print("해결 방법: Resend 대시보드(Domains 메뉴)에서 발신 도메인(SENDER_EMAIL의 도메인)의 DNS 레코드를 추가하고 검증을 완료하세요.")

if __name__ == '__main__':
    send_email()
