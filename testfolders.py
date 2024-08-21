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


email_address = 'wirsing@stretta-music.com'
password = "dTOdz56yFPz66huGMddK"
server_address = 'server25.zoks.net'

list_folders(email_address, password, server_address)