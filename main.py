import imaplib
import email
import os
import re
import time
from email import policy
from email.parser import BytesParser
from datetime import datetime, timedelta


def sanitize_filename(subject, max_length=100):

    sanitized_subject = re.sub(r'\s+', ' ', subject)

    sanitized_subject = re.sub(r'[_]', ' ', sanitized_subject)

    sanitized_subject = re.sub(r'[\\/*?:"<>|]', '_', sanitized_subject)
    

    sanitized_subject = re.sub(r'https?__\S+', '', sanitized_subject)
    

    return sanitized_subject[:max_length].strip()


def fetch_emails_from_folder(mail, folder_name, save_dir, start_date, end_date):
    mail.select(folder_name)
    result, data = mail.search(None, f'(SINCE {start_date} BEFORE {end_date})')
    email_ids = data[0].split()
    
    for email_id in email_ids:
        result, msg_data = mail.fetch(email_id, '(RFC822)')
        raw_email = msg_data[0][1]
        msg = BytesParser(policy=policy.default).parsebytes(raw_email)
        
        subject = msg.get('subject', 'no_subject')
        sanitized_subject = sanitize_filename(subject)
        email_filename = os.path.join(save_dir, f"{sanitized_subject}.eml")
        
        with open(email_filename, 'wb') as f:
            f.write(raw_email)


def fetch_emails_for_accounts(accounts, server_address):
    for account in accounts:
        email_address = account['email']
        password = account['password']

        print(f"Fetching emails for {email_address}...")

        mail = imaplib.IMAP4_SSL(server_address)
        mail.login(email_address, password)
        
        local_part = email_address.split('@')[0]
        base_save_dir = os.path.join(os.getcwd(), local_part)
        os.makedirs(base_save_dir, exist_ok=True)
        

        end_date = datetime.now()
        for i in range(6):
            start_date = (end_date - timedelta(days=30)).strftime("%d-%b-%Y")
            end_date_str = end_date.strftime("%d-%b-%Y")
            
            inbox_save_dir = os.path.join(base_save_dir, f'Inbox_{end_date.year}_{end_date.month}')
            os.makedirs(inbox_save_dir, exist_ok=True)
            fetch_emails_from_folder(mail, "inbox", inbox_save_dir, start_date, end_date_str)
            
            sent_folders = ["Gesendet", "Sent", "Sent Items", "INBOX.Sent"]
            for folder in sent_folders:
                try:
                    sent_save_dir = os.path.join(base_save_dir, f'Sent_{end_date.year}_{end_date.month}')
                    os.makedirs(sent_save_dir, exist_ok=True)
                    fetch_emails_from_folder(mail, folder, sent_save_dir, start_date, end_date_str)
                    break
                except imaplib.IMAP4.error:
                    continue
            

            time.sleep(3)


            end_date = end_date - timedelta(days=30)
        
        mail.logout()


        time.sleep(5)


accounts = [
    {'email': 'wirsing@stretta-music.com', 'password': '...'},

]

server_address = "server25.zoks.net"
fetch_emails_for_accounts(accounts, server_address)
