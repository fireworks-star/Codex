import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone
import sys


def _parse_iso_datetime(value: str):
    if not value or not isinstance(value, str):
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _load_auth_dir(config_path: str):
    if not os.path.exists(config_path):
        return None
    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("auth-dir:"):
                value = stripped.split(":", 1)[1].strip()
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]
                return os.path.expanduser(value)
    return None


def _load_proxy_url(config_path: str):
    if not os.path.exists(config_path):
        return None
    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("proxy-url:"):
                value = stripped.split(":", 1)[1].strip()
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]
                return value
    return None


def _find_expired_key(payload: dict):
    for key in ("expired", "expires_at", "expiresAt", "expiry", "expires"):
        if key in payload:
            return payload[key]
    return None


def _is_token_invalidated(access_token: str, proxy_url: str | None):
    if not access_token:
        return False
    url = "https://api.openai.com/v1/models"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    request = urllib.request.Request(url, headers=headers, method="GET")

    handlers = []
    if proxy_url and proxy_url.lower().startswith(("http://", "https://")):
        handlers.append(
            urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
        )
    opener = urllib.request.build_opener(*handlers)

    try:
        with opener.open(request, timeout=5) as resp:
            return False
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", errors="ignore")
            data = json.loads(body)
            error = data.get("error") if isinstance(data, dict) else None
            code = error.get("code") if isinstance(error, dict) else None
            if exc.code == 401 and code == "token_invalidated":
                return True
        except Exception:
            return False
    except urllib.error.URLError:
        return False
    except Exception:
        return False
    return False


def _load_lines(file_path: str):
    if not os.path.isfile(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def _save_lines(file_path: str, lines: list[str]):
    with open(file_path, "w", encoding="utf-8") as f:
        if lines:
            f.write("\n".join(lines) + "\n")
        else:
            f.write("")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.yaml")
    auth_dir = _load_auth_dir(config_path)
    proxy_url = _load_proxy_url(config_path)
    if not auth_dir:
        auth_dir = os.path.join(
            base_dir, "codex_auto_register", "codex", "codex_accounts_tokens"
        )

    if not os.path.isdir(auth_dir):
        print(f"[清理] 未找到认证目录: {auth_dir}")
        return

    print(f"[清理] 开始扫描认证目录: {auth_dir}")
    
    # 获取所有需要检查的文件
    all_entries = [entry for entry in os.listdir(auth_dir) if entry.lower().endswith(".json")]
    total_files = len(all_entries)
    
    if total_files == 0:
        print("[清理] 没有需要检查的认证文件")
        return
    
    print(f"[清理] 发现 {total_files} 个认证文件需要检查")

    now_aware = datetime.now(timezone.utc)
    removed = 0
    checked = 0
    expired_emails: set[str] = set()
    expired_access_tokens: set[str] = set()
    expired_refresh_tokens: set[str] = set()
    
    # 收集失效的认证文件信息
    expired_files_info = []
    # 批量读取所有JSON文件内容，减少文件打开次数
    file_contents = {}
    for idx, entry in enumerate(all_entries, 1):
        # 显示进度条
        progress = idx / total_files
        bar_length = 30
        filled_length = int(bar_length * progress)
        bar = '=' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f"\r[进度] [{bar}] {idx}/{total_files} ({progress:.1%})")
        sys.stdout.flush()
        
        file_path = os.path.join(auth_dir, entry)
        if not os.path.isfile(file_path):
            continue
        checked += 1
        
        # 批量读取文件内容
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
                file_contents[file_path] = payload
        except Exception:
            continue

        expired_value = _find_expired_key(payload)
        if not expired_value:
            continue

        expires_at = _parse_iso_datetime(expired_value)
        if not expires_at:
            continue

        if expires_at.tzinfo is None:
            now = datetime.now()
        else:
            now = now_aware
        access_token = (
            payload.get("access_token") if isinstance(payload, dict) else None
        )
        refresh_token = (
            payload.get("refresh_token") if isinstance(payload, dict) else None
        )

        is_expired = False
        is_invalidated = False
        
        if expires_at <= now:
            is_expired = True
        
        # 主动验证 token 是否已被服务端吊销
        if isinstance(access_token, str) and access_token:
            if _is_token_invalidated(access_token, proxy_url):
                is_invalidated = True
        
        if is_expired or is_invalidated:
            email = payload.get("email")
            expired_files_info.append({
                "file_path": file_path,
                "email": email,
                "expires_at": expires_at.isoformat() if expires_at else None,
                "is_expired": is_expired,
                "is_invalidated": is_invalidated,
                "access_token": access_token,
                "refresh_token": refresh_token
            })
            if isinstance(email, str) and email:
                expired_emails.add(email.strip())
            if isinstance(access_token, str) and access_token:
                expired_access_tokens.add(access_token.strip())
            if isinstance(refresh_token, str) and refresh_token:
                expired_refresh_tokens.add(refresh_token.strip())
    
    # 进度条完成
    print()
    
    # 生成失效邮箱记录文件
    if expired_files_info:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        expired_log_path = os.path.join(base_dir, "expired_auth_files.txt")
        print(f"[清理] 正在生成失效记录文件...")
        try:
            with open(expired_log_path, "a", encoding="utf-8") as f:
                timestamp = datetime.now(timezone.utc).isoformat()
                f.write(f"\n{'=' * 60}\n")
                f.write(f"[{timestamp}] 发现 {len(expired_files_info)} 个失效认证文件\n")
                f.write(f"{'=' * 60}\n")
                for info in expired_files_info:
                    f.write(f"邮箱: {info['email']}\n")
                    f.write(f"文件: {os.path.basename(info['file_path'])}\n")
                    f.write(f"过期时间: {info['expires_at']}\n")
                    f.write(f"过期: {'是' if info['is_expired'] else '否'}\n")
                    f.write(f"被吊销: {'是' if info['is_invalidated'] else '否'}\n")
                    f.write(f"{'-' * 40}\n")
            print(f"[清理] 已生成失效认证文件记录: {expired_log_path}")
        except Exception as e:
            print(f"[清理] 生成失效记录文件失败: {e}")
    
    # 删除失效的认证文件
    print(f"[清理] 正在删除 {len(expired_files_info)} 个失效认证文件...")
    # 批量删除文件，提升性能
    for idx, info in enumerate(expired_files_info, 1):
        progress = idx / len(expired_files_info)
        bar_length = 30
        filled_length = int(bar_length * progress)
        bar = '=' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f"\r[删除] [{bar}] {idx}/{len(expired_files_info)} ({progress:.1%})")
        sys.stdout.flush()
        
        try:
            os.remove(info["file_path"])
            removed += 1
        except Exception:
            continue
    
    print()

    # 同步清理账号与 token 文件
    base_dir = os.path.dirname(os.path.abspath(__file__))
    accounts_path = os.path.join(base_dir, "accounts.txt")
    registered_path = os.path.join(base_dir, "registered_accounts.csv")
    ak_path = os.path.join(base_dir, "ak.txt")
    rk_path = os.path.join(base_dir, "rk.txt")

    # 清理 accounts.txt
    accounts_removed = 0
    if expired_emails and os.path.isfile(accounts_path):
        print(f"[清理] 正在清理 accounts.txt...")
        lines = _load_lines(accounts_path) or []
        total_lines = len(lines)
        kept = []
        
        for idx, line in enumerate(lines, 1):
            progress = idx / total_lines
            bar_length = 20
            filled_length = int(bar_length * progress)
            bar = '=' * filled_length + '-' * (bar_length - filled_length)
            sys.stdout.write(f"\r[清理] [{bar}] {idx}/{total_lines} ({progress:.1%})")
            sys.stdout.flush()
            
            if not line.strip():
                continue
            email = line.split(":", 1)[0].strip()
            if email in expired_emails:
                accounts_removed += 1
                continue
            kept.append(line)
        _save_lines(accounts_path, kept)
        print()

    # 清理 registered_accounts.csv
    registered_removed = 0
    if expired_emails and os.path.isfile(registered_path):
        print(f"[清理] 正在清理 registered_accounts.csv...")
        lines = _load_lines(registered_path) or []
        total_lines = len(lines)
        
        for idx, line in enumerate(lines, 1):
            progress = idx / total_lines
            bar_length = 20
            filled_length = int(bar_length * progress)
            bar = '=' * filled_length + '-' * (bar_length - filled_length)
            sys.stdout.write(f"\r[清理] [{bar}] {idx}/{total_lines} ({progress:.1%})")
            sys.stdout.flush()
            
            if not line.strip():
                continue
            email = line.split(",", 1)[0].strip()
            if email in expired_emails:
                registered_removed += 1
                continue
            kept.append(line)
        _save_lines(registered_path, kept)
        print()

    # 清理 ak.txt
    ak_removed = 0
    if expired_access_tokens and os.path.isfile(ak_path):
        print(f"[清理] 正在清理 ak.txt...")
        lines = _load_lines(ak_path) or []
        total_lines = len(lines)
        
        for idx, line in enumerate(lines, 1):
            progress = idx / total_lines
            bar_length = 20
            filled_length = int(bar_length * progress)
            bar = '=' * filled_length + '-' * (bar_length - filled_length)
            sys.stdout.write(f"\r[清理] [{bar}] {idx}/{total_lines} ({progress:.1%})")
            sys.stdout.flush()
            
            token = line.strip()
            if token in expired_access_tokens:
                ak_removed += 1
                continue
            kept.append(line)
        _save_lines(ak_path, kept)
        print()

    # 清理 rk.txt
    rk_removed = 0
    if expired_refresh_tokens and os.path.isfile(rk_path):
        print(f"[清理] 正在清理 rk.txt...")
        lines = _load_lines(rk_path) or []
        total_lines = len(lines)
        
        for idx, line in enumerate(lines, 1):
            progress = idx / total_lines
            bar_length = 20
            filled_length = int(bar_length * progress)
            bar = '=' * filled_length + '-' * (bar_length - filled_length)
            sys.stdout.write(f"\r[清理] [{bar}] {idx}/{total_lines} ({progress:.1%})")
            sys.stdout.flush()
            
            token = line.strip()
            if token in expired_refresh_tokens:
                rk_removed += 1
                continue
            kept.append(line)
        _save_lines(rk_path, kept)
        print()

    print(
        f"[清理] 检查 {checked} 个认证文件，删除 {removed} 个已失效文件。"
        f" 账号: -{accounts_removed}, 注册表: -{registered_removed},"
        f" access token: -{ak_removed}, refresh token: -{rk_removed}"
    )


if __name__ == "__main__":
    main()
