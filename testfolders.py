import imaplib

def list_folders(email_address, password, server_address):
    # Connect to the server
    mail = imaplib.IMAP4_SSL(server_address)
    mail.login(email_address, password)

    # List all folders
    result, folders = mail.list()

    if result == 'OK':
        print(f"Folders for {email_address}:")
        for folder in folders:
            print(folder.decode())
    else:
        print("Failed to list folders.")

    # Logout from the server
    mail.logout()

# Replace with your actual email credentials
email_address = 'info@stretta-music.com'
password = 'H7pbc6dC1TLVpiPVaniu'
server_address = 'w01f596d.kasserver.com'

list_folders(email_address, password, server_address)