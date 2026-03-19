import imaplib

def check_first_account():
    imap_server = "imap.qq.com"
    imap_user = "1964055097@qq.com"
    imap_pass = "vycvoxxecqwmbjch"
    
    print(f"Connecting to {imap_server} with user {imap_user}...")
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(imap_user, imap_pass)
        
        status, folders = mail.list()
        if status == "OK":
            for folder_info in folders:
                folder_str = folder_info.decode('utf-8')
                parts = folder_str.split('"" ')
                if len(parts) > 1:
                    folder_name = parts[-1].strip('"')
                else:
                    parts = folder_str.split('"/" ')
                    if len(parts) > 1:
                        folder_name = parts[-1].strip('"')
                    else:
                        folder_name = folder_str.split()[-1].strip('"')
                
                print(f"Checking folder: {folder_name}")
                try:
                    s, msg_count_info = mail.select(folder_name, readonly=True)
                    if s == "OK":
                        count = msg_count_info[0].decode()
                        print(f"  -> Total emails: {count}")
                except Exception as e:
                    print(f"  -> Error selecting folder: {e}")
                    
        mail.close()
        mail.logout()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_first_account()
