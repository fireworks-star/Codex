import imaplib
import json
import os

def check_all_folders():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    imap_server = config.get("imap_server", "imap.qq.com")
    imap_user = config.get("imap_user", "2792535037@qq.com")
    imap_pass = config.get("imap_pass", "nznubeelqvdfdgec")
    
    print(f"Connecting to {imap_server} with user {imap_user}...")
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(imap_user, imap_pass)
        
        # List all folders
        status, folders = mail.list()
        if status == "OK":
            for folder_info in folders:
                # Format is usually: (\HasNoChildren) "/" "INBOX"
                folder_str = folder_info.decode('utf-8')
                # Extract folder name (last quoted string)
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
                        
                        if int(count) > 0:
                            s, msg_ids = mail.search(None, "ALL")
                            if s == "OK":
                                ids = msg_ids[0].split()
                                latest = ids[-1]
                                s, msg_data = mail.fetch(latest, '(BODY[HEADER.FIELDS (SUBJECT FROM TO)])')
                                if s == "OK":
                                    header_str = msg_data[0][1].decode('utf-8', errors='ignore')
                                    print(f"  -> Latest email header snippet:\n{header_str.strip()}")
                except Exception as e:
                    print(f"  -> Error selecting folder: {e}")
                    
        mail.close()
        mail.logout()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_all_folders()
