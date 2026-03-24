"""
自动获取 2925.com 的 Cookie 并保存到 cookie.txt
使用方法：
  1. 安装依赖: pip install selenium webdriver-manager
  2. 运行脚本: python get_cookie.py
  3. 在打开的浏览器中登录 2925.com
  4. 登录成功后按回车，脚本会自动保存 Cookie
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def get_cookie_manual():
    """手动输入 Cookie"""
    print("=" * 60)
    print("手动获取 Cookie 模式")
    print("=" * 60)
    print("\n请按以下步骤操作：")
    print("1. 打开浏览器，访问 https://www.2925.com")
    print("2. 登录你的 2925 邮箱账号")
    print("3. 按 F12 打开开发者工具")
    print("4. 切换到 Network（网络）标签")
    print("5. 刷新页面，点击任意请求")
    print("6. 在请求头中找到 Cookie 字段")
    print("7. 复制 Cookie 字符串\n")
    
    cookie = input("请粘贴 Cookie 字符串: ").strip()
    
    if cookie:
        save_cookie(cookie)
        print("✅ Cookie 已保存到 cookie.txt")
    else:
        print("❌ Cookie 为空，未保存")


def get_cookie_auto():
    """自动获取 Cookie（使用 Selenium）"""
    print("=" * 60)
    print("自动获取 Cookie 模式")
    print("=" * 60)
    
    # 配置 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # 可选：使用已有用户数据（保持登录状态）
    # chrome_options.add_argument("--user-data-dir=C:/Users/YourName/AppData/Local/Google/Chrome/User Data")
    
    try:
        print("正在启动浏览器...")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # 隐藏 webdriver 属性
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 打开 2925.com
        print("正在打开 https://www.2925.com ...")
        driver.get("https://www.2925.com")
        
        print("\n" + "=" * 60)
        print("请在浏览器中完成登录")
        print("登录成功后，回到这里按回车键继续...")
        print("=" * 60 + "\n")
        
        input("按回车键获取 Cookie...")
        
        # 获取 Cookie
        cookies = driver.get_cookies()
        
        # 转换为 Cookie 字符串
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        
        if cookie_str:
            save_cookie(cookie_str)
            print("✅ Cookie 已保存到 cookie.txt")
            print(f"\nCookie 内容（前 100 字符）: {cookie_str[:100]}...")
        else:
            print("❌ 未获取到 Cookie，请确保已登录")
        
        driver.quit()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("\n建议：")
        print("1. 确保已安装 Chrome 浏览器")
        print("2. 运行: pip install selenium webdriver-manager")
        print("3. 或者使用手动模式")


def save_cookie(cookie_str):
    """保存 Cookie 到文件"""
    with open("cookie.txt", "w", encoding="utf-8") as f:
        f.write(cookie_str)


def test_cookie():
    """测试 Cookie 是否有效"""
    try:
        with open("cookie.txt", "r", encoding="utf-8") as f:
            cookie = f.read().strip()
        
        if not cookie:
            print("❌ cookie.txt 为空")
            return False
        
        print("\n" + "=" * 60)
        print("测试 Cookie 有效性...")
        print("=" * 60)
        
        import requests
        
        headers = {
            "Host": "www.2925.com",
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
        }
        
        # 尝试获取 token
        res = requests.post(
            "https://www.2925.com/mailv2/auth/token",
            json={"timeout": 5000},
            headers=headers,
            timeout=10
        )
        
        data = res.json()
        if data.get("code") == 200:
            print("✅ Cookie 有效！")
            print(f"Token: {data['result'][:50]}...")
            return True
        else:
            print(f"❌ Cookie 无效: {data}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def main():
    print("=" * 60)
    print("2925.com Cookie 获取工具")
    print("=" * 60)
    print("\n选择模式：")
    print("1. 自动模式（使用 Selenium 浏览器）")
    print("2. 手动模式（手动复制 Cookie）")
    print("3. 测试现有 Cookie")
    print("4. 退出")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == "1":
        get_cookie_auto()
    elif choice == "2":
        get_cookie_manual()
    elif choice == "3":
        test_cookie()
    elif choice == "4":
        print("退出")
    else:
        print("无效选项")


if __name__ == "__main__":
    main()