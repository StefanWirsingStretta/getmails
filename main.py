import imaplib
import email
import os
import re
import time
import logging
from email import policy
from email.parser import BytesParser
from datetime import datetime, timedelta

logging.basicConfig(
    filename='email_fetch.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

report_lines = []

def sanitize_filename(subject, max_length=100):
    sanitized_subject = re.sub(r'\s+', ' ', subject)
    sanitized_subject = re.sub(r'[_]', ' ', sanitized_subject)
    sanitized_subject = re.sub(r'[\\/*?:"<>|]', '_', sanitized_subject)
    sanitized_subject = re.sub(r'https?__\S+', '', sanitized_subject)
    return sanitized_subject[:max_length].strip()

def fetch_emails_from_folder(mail, folder_name, save_dir, start_date, end_date):
    try:
        mail.select(folder_name)
        result, data = mail.search(None, f'(SINCE {start_date} BEFORE {end_date})')
        if result != 'OK':
            logging.error(f"Failed to search emails in folder {folder_name}. Result: {result}")
            report_lines.append(f"Failed to search emails in folder {folder_name}. Result: {result}")
            return
        
        email_ids = data[0].split()
        logging.info(f"Found {len(email_ids)} emails in {folder_name} between {start_date} and {end_date}.")
        report_lines.append(f"Folder: {folder_name}, Emails found: {len(email_ids)} between {start_date} and {end_date}")
        
        for email_id in email_ids:
            result, msg_data = mail.fetch(email_id, '(RFC822)')
            if result != 'OK':
                logging.error(f"Failed to fetch email {email_id} from folder {folder_name}. Result: {result}")
                report_lines.append(f"Failed to fetch email {email_id} from folder {folder_name}. Result: {result}")
                continue
            
            raw_email = msg_data[0][1]
            msg = BytesParser(policy=policy.default).parsebytes(raw_email)
            
            subject = msg.get('subject', 'no_subject')
            sanitized_subject = sanitize_filename(subject)
            email_filename = os.path.join(save_dir, f"{sanitized_subject}.eml")
            
            with open(email_filename, 'wb') as f:
                f.write(raw_email)
            logging.info(f"Saved email: {email_filename}")
            report_lines.append(f"Saved email: {email_filename}")
    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP error while accessing folder {folder_name}: {e}")
        report_lines.append(f"Error accessing folder {folder_name}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error while fetching emails from {folder_name}: {e}")
        report_lines.append(f"Unexpected error while fetching emails from {folder_name}: {e}")

def fetch_emails_for_accounts(accounts, server_address):
    report_start_time = datetime.now()
    report_lines.append(f"Email Fetch Report - Started at {report_start_time}\n")

    for account in accounts:
        email_address = account['email']
        password = account['password']

        logging.info(f"Starting email fetch for {email_address}...")
        report_lines.append(f"\nFetching emails for {email_address}...")

        try:
            mail = imaplib.IMAP4_SSL(server_address)
            mail.login(email_address, password)
        except imaplib.IMAP4.error as e:
            logging.error(f"Failed to log in to {email_address}: {e}")
            report_lines.append(f"Failed to log in to {email_address}: {e}")
            continue

        local_part = email_address.split('@')[0]
        base_save_dir = os.path.join(os.getcwd(), local_part)
        os.makedirs(base_save_dir, exist_ok=True)

        end_date = datetime.now()
        for i in range(3):
            start_date = (end_date - timedelta(days=30)).strftime("%d-%b-%Y")
            end_date_str = end_date.strftime("%d-%b-%Y")

            inbox_save_dir = os.path.join(base_save_dir, f'Inbox_{end_date.year}_{end_date.month}')
            os.makedirs(inbox_save_dir, exist_ok=True)
            fetch_emails_from_folder(mail, "inbox", inbox_save_dir, start_date, end_date_str)

            sent_folders = ["Sent", "Sent Items", "INBOX.Sent", "Gesendet"]
            folder_accessed = False
            for folder in sent_folders:
                try:
                    logging.info(f"Attempting to select folder: {folder}")
                    result, _ = mail.select(folder, readonly=True)
                    
                    if result != 'OK':
                        logging.error(f"Failed to select folder {folder}. Skipping...")
                        report_lines.append(f"Failed to select folder {folder}. Skipping...")
                        continue
                    
                    sent_save_dir = os.path.join(base_save_dir, f'Sent_{end_date.year}_{end_date.month}')
                    os.makedirs(sent_save_dir, exist_ok=True)
                    fetch_emails_from_folder(mail, folder, sent_save_dir, start_date, end_date_str)
                    folder_accessed = True
                    break 
                except imaplib.IMAP4.error as e:
                    logging.error(f"IMAP error while accessing sent folder {folder}: {e}")
                    report_lines.append(f"IMAP error while accessing sent folder {folder}: {e}")
                    continue
                except Exception as e:
                    logging.error(f"Unexpected error while selecting sent folder {folder}: {e}")
                    report_lines.append(f"Unexpected error while selecting sent folder {folder}: {e}")
                    continue
                finally:
                    try:
                        mail.select('INBOX')
                    except Exception as e:
                        logging.error(f"Failed to deselect folder {folder}: {e}")
                        report_lines.append(f"Failed to deselect folder {folder}: {e}")
                        
            if not folder_accessed:
                logging.warning(f"None of the sent folders were accessible for {email_address}.")
                report_lines.append(f"None of the sent folders were accessible for {email_address}.")

            time.sleep(3)

            end_date = end_date - timedelta(days=30)
        
        try:
            mail.logout()
            logging.info(f"Completed email fetch for {email_address}.")
            report_lines.append(f"Completed email fetch for {email_address}.")
        except Exception as e:
            logging.error(f"Failed to log out from {email_address}: {e}")
            report_lines.append(f"Failed to log out from {email_address}: {e}")

        time.sleep(5)

    report_end_time = datetime.now()
    report_lines.append(f"\nEmail Fetch Report - Completed at {report_end_time}")
    report_lines.append(f"Total time taken: {report_end_time - report_start_time}\n")

    with open('email_fetch_report.txt', 'w', encoding='utf-8') as report_file:
        report_file.write("\n".join(report_lines))



accounts = [
    {'email': 'wirsing@stretta-music.com', 'password': 'dTOdz56yFPz66huGMddK'},

]

server_address = "server25.zoks.net"
fetch_emails_for_accounts(accounts, server_address)
