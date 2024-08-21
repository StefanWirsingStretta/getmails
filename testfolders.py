import imaplib

def list_folders(email_address, password, server_address):
   
    mail = imaplib.IMAP4_SSL(server_address)
    mail.login(email_address, password)

    result, folders = mail.list()

    if result == 'OK':
        print(f"Folders for {email_address}:")
        for folder in folders:
            print(folder.decode())
    else:
        print("Failed to list folders.")

 
    mail.logout()


email_address = 'info@stretta-music.com'
password = '...'
server_address = 'w01f596d.kasserver.com'

list_folders(email_address, password, server_address)