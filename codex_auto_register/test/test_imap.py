import imaplib
import email
from email.header import decode_header
import re
import time

IMAP_SERVER = "imap.qq.com"
EMAIL_ACCOUNT = "1964055097@qq.com"
EMAIL_PASSWORD = "vycvoxxecqwmbjch"

def get_openai_verification_code(target_email, max_retries=5, delay_seconds=10):
    """
    通过 IMAP 登录 QQ 邮箱，并在收件箱中查找发往 target_email 的最新 OpenAI 验证码
    """
    print(f"[*] 正在登录 IMAP 服务器 {IMAP_SERVER}...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        print("[+] 登录成功！")
    except Exception as e:
        print(f"[-] 登录失败: {e}")
        return None

    for attempt in range(max_retries):
        print(f"[*] 尝试获取 OpenAI 邮件 (第 {attempt + 1}/{max_retries} 次)...")
        try:
            # 选择收件箱
            mail.select("inbox")
            
            # 搜索发件人是 noreply@tm.openai.com，且收件人是我们指定的 target_email
            # 为了更好的兼容性，有时候转发邮件收件人可能是 qq 邮箱，但邮件正文或 To 字段包含目标邮箱
            # 先搜索来自 openai 的未读邮件
            status, messages = mail.search(None, '(FROM "noreply@tm.openai.com" UNSEEN)')
            
            if status != "OK" or not messages[0]:
                print("[-] 未找到来自 OpenAI 的新邮件，等待重试...")
                time.sleep(delay_seconds)
                continue
                
            # 获取最新的邮件列表（按 ID 降序）
            email_ids = messages[0].split()
            email_ids.reverse()
            
            for eid in email_ids:
                status, msg_data = mail.fetch(eid, "(RFC822)")
                if status != "OK":
                    continue
                    
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # 解析邮件内容
                        content = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() in ["text/plain", "text/html"]:
                                    try:
                                        content += part.get_payload(decode=True).decode(errors="ignore")
                                    except:
                                        pass
                        else:
                            try:
                                content += msg.get_payload(decode=True).decode(errors="ignore")
                            except:
                                pass
                                
                        # 如果目标邮箱不在内容或收件人中（这里简单过滤）
                        headers_to = str(msg.get("To", ""))
                        if target_email.lower() not in headers_to.lower() and target_email.lower() not in content.lower():
                            continue
                            
                        # 提取6位数字验证码
                        patterns = [
                            r"(\d{6})",
                            r"code.*?(\d{6})",
                            r">(\d{6})<"
                        ]
                        
                        code = None
                        for pattern in patterns:
                            match = re.search(pattern, content)
                            if match:
                                code = match.group(1)
                                break
                                
                        if code:
                            print(f"[+] 成功提取到验证码: {code}")
                            # 标记已读 (可选，调试时可以注释掉方便再次读取)
                            mail.store(eid, '+FLAGS', '\\Seen')
                            mail.close()
                            mail.logout()
                            return code
                            
            print("[-] 找到相关邮件，但未提取到验证码或不匹配目标邮箱。")
            
        except Exception as e:
            print(f"[-] 检索邮件时出错: {e}")
            
        time.sleep(delay_seconds)

    print("[-] 达到最大重试次数，未获取到验证码。")
    try:
        mail.close()
        mail.logout()
    except:
        pass
    return None

if __name__ == "__main__":
    # 测试连接，为了避免一直阻塞，把 target_email 随便设一个，仅测试登录是否畅通
    print("=" * 40)
    print("IMAP 连接测试工具")
    print("=" * 40)
    get_openai_verification_code("test_nobody@qianxi7988.ggff.net", max_retries=1)
