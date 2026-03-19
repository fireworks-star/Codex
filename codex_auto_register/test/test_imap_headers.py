import imaplib
import email
from email.header import decode_header
import json
import os

def check_recent_emails():
    # Load config
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
        mail.select("inbox")
        
        # Search for all emails
        status, messages = mail.search(None, 'ALL')
        if status != "OK":
            print("Failed to search emails.")
            return
            
        email_ids = messages[0].split()
        print(f"Total emails in inbox: {len(email_ids)}")
        
        # Fetch the last 5 emails
        recent_ids = email_ids[-5:]
        recent_ids.reverse() # Newest first
        
        for eid in recent_ids:
            print(f"\n--- Email ID: {eid.decode()} ---")
            status, msg_data = mail.fetch(eid, '(RFC822)')
            if status != "OK":
                print("Failed to fetch email.")
                continue
                
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Decrypt headers
                    def get_header(header_name):
                        val = msg.get(header_name, "")
                        if not val: return ""
                        decoded_parts = decode_header(val)
                        res = ""
                        for part, encoding in decoded_parts:
                            if isinstance(part, bytes):
                                try:
                                    res += part.decode(encoding or "utf-8", errors="ignore")
                                except:
                                    res += part.decode("utf-8", errors="ignore")
                            else:
                                res += part
                        return res
                        
                    print(f"From: {get_header('From')}")
                    print(f"To: {get_header('To')}")
                    print(f"Subject: {get_header('Subject')}")
                    print(f"Date: {get_header('Date')}")
                    
        mail.close()
        mail.logout()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_recent_emails()
