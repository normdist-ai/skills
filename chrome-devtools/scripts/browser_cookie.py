import asyncio
import json
import subprocess
import time
import websocket
from pathlib import Path
from playwright.async_api import async_playwright

USER_DATA_DIR = Path(__file__).parent / "browser_data"
COOKIES_FILE = Path(__file__).parent / "cookies.json"
CDP_PORT = 9222

def get_chrome_debug_url():
    """获取 Chrome 调试 URL"""
    import requests
    try:
        resp = requests.get(f"http://127.0.0.1:{CDP_PORT}/json", timeout=2)
        targets = resp.json()
        for target in targets:
            if target.get("type") == "page":
                return target.get("webSocketDebuggerUrl")
        return None
    except:
        return None

def get_cookies_from_running_chrome(domain_filter: str = None):
    """从运行中的 Chrome 通过 CDP 获取 cookies"""
    debug_url = get_chrome_debug_url()
    if not debug_url:
        print(f"[X] 未检测到运行中的 Chrome (端口 {CDP_PORT})")
        print("\n请使用以下方式之一启动 Chrome:")
        print(f'  1. 快捷方式添加参数: --remote-debugging-port={CDP_PORT}')
        print(f'  2. 命令行启动: chrome.exe --remote-debugging-port={CDP_PORT}')
        return None
    
    print(f"✅ 检测到 Chrome 调试端口: {CDP_PORT}")
    
    ws = websocket.create_connection(debug_url)
    
    ws.send(json.dumps({
        "id": 1,
        "method": "Network.enable"
    }))
    ws.recv()
    
    ws.send(json.dumps({
        "id": 2,
        "method": "Network.getAllCookies"
    }))
    result = json.loads(ws.recv())
    
    ws.close()
    
    cookies = result.get("result", {}).get("cookies", [])
    
    if domain_filter:
        cookies = [c for c in cookies if domain_filter in c.get("domain", "")]
    
    return cookies

def launch_chrome_with_debug():
    """启动带调试端口的 Chrome"""
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    
    chrome_exe = None
    for path in chrome_paths:
        if Path(path).exists():
            chrome_exe = path
            break
    
    if not chrome_exe:
        print("❌ 未找到 Chrome")
        return False
    
    print(f"🚀 启动 Chrome (调试端口: {CDP_PORT})...")
    subprocess.Popen([
        chrome_exe,
        f"--remote-debugging-port={CDP_PORT}",
        "--remote-allow-origins=*",
        "--user-data-dir=" + str(Path(__file__).parent / "chrome_debug_profile")
    ])
    
    print("⏳ 等待 Chrome 启动...")
    time.sleep(3)
    return True

async def login_and_save():
    """打开浏览器让用户手动登录，然后保存状态"""
    async with async_playwright() as p:
        print("=" * 50)
        print("浏览器将打开，请手动登录")
        print("登录成功后，回到此窗口按 Enter 保存状态")
        print("=" * 50)
        
        context = await p.chromium.launch_persistent_context(
            str(USER_DATA_DIR),
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://www.zhihu.com/signin")
        
        print("\n等待您登录...")
        input("\n登录成功后，按 Enter 保存状态并关闭浏览器...")
        
        cookies = await context.cookies()
        with open(COOKIES_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 已保存 {len(cookies)} 个 cookies")
        print(f"   文件位置: {COOKIES_FILE}")
        
        await context.close()

async def browse_with_cookies(url: str = "https://www.zhihu.com"):
    """使用保存的 cookies 访问网站"""
    async with async_playwright() as p:
        if USER_DATA_DIR.exists():
            context = await p.chromium.launch_persistent_context(
                str(USER_DATA_DIR),
                headless=False,
                channel="chrome"
            )
        else:
            browser = await p.chromium.launch(headless=False, channel="chrome")
            context = await browser.new_context()
            
            if COOKIES_FILE.exists():
                with open(COOKIES_FILE, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
                await context.add_cookies(cookies)
                print(f"已加载 {len(cookies)} 个 cookies")
        
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto(url)
        
        print(f"\n已访问: {url}")
        print("按 Enter 关闭浏览器...")
        input()
        
        await context.close()

def sync_from_running_chrome(domain: str = None):
    """从运行中的 Chrome 同步 cookies"""
    cookies = get_cookies_from_running_chrome(domain)
    if cookies:
        with open(COOKIES_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 已从 Chrome 同步 {len(cookies)} 个 cookies")
        if domain:
            print(f"   过滤域名: {domain}")
        print(f"   文件位置: {COOKIES_FILE}")
        return True
    return False

if __name__ == "__main__":
    import sys
    
    print("\n[工具] 浏览器 Cookie 管理")
    print("-" * 40)
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "login":
            asyncio.run(login_and_save())
        elif cmd == "browse":
            url = sys.argv[2] if len(sys.argv) > 2 else "https://www.zhihu.com"
            asyncio.run(browse_with_cookies(url))
        elif cmd == "sync":
            domain = sys.argv[2] if len(sys.argv) > 2 else None
            sync_from_running_chrome(domain)
        elif cmd == "launch":
            launch_chrome_with_debug()
        else:
            print(f"未知命令: {cmd}")
    else:
        print("用法:")
        print("  py browser_cookie.py login        - 手动登录并保存状态")
        print("  py browser_cookie.py browse [url] - 使用保存的状态浏览")
        print("  py browser_cookie.py sync [domain]- 从运行中的 Chrome 同步 cookies")
        print("  py browser_cookie.py launch       - 启动带调试端口的 Chrome")
        print()
        print("说明:")
        print("  sync 命令使用 CDP 协议，无需关闭 Chrome")
        print("  需要先用 --remote-debugging-port=9222 启动 Chrome")
