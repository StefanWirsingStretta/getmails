import imaplib
import email
import os
from email import policy
from email.parser import BytesParser
from datetime import datetime, timedelta


def fetch_emails(email_address, password, server_address):

    mail = imaplib.IMAP4_SSL(server_address)
    mail.login(email_address, password)
    

    mail.select("inbox")
    

    date = (datetime.now() - timedelta(1)).strftime("%d-%b-%Y")
    

    result, data = mail.search(None, f'(SINCE {date})')
    

    email_ids = data[0].split()
    for email_id in email_ids:
        result, msg_data = mail.fetch(email_id, '(RFC822)')
        
       
        raw_email = msg_data[0][1]
        msg = BytesParser(policy=policy.default).parsebytes(raw_email)
        
        
        local_part = email_address.split('@')[0]
        
        
        save_dir = os.path.join(os.getcwd(), local_part)
        os.makedirs(save_dir, exist_ok=True)
        
        
        subject = msg.get('subject', 'no_subject').replace(' ', '_').replace('/', '_')
        email_filename = f"{save_dir}/{subject}.eml"
        
        with open(email_filename, 'wb') as f:
            f.write(raw_email)
        
        
        for part in msg.iter_parts():
            if part.get_content_disposition() == 'attachment':
        
                attachment_filename = part.get_filename()
                if attachment_filename:
        
                    attachment_path = os.path.join(save_dir, attachment_filename)
                    with open(attachment_path, 'wb') as attachment_file:
                        attachment_file.write(part.get_payload(decode=True))
    
    
    mail.logout()


email_address = ""
password = ""
server_address = ""

fetch_emails(email_address, password, server_address)
