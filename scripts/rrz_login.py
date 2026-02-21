#!/usr/bin/env python3
"""
人人租登录模块 v2.0
提供登录功能，返回浏览器页面对象供后续操作

功能:
1. Cookie 登录（优先，无头模式）
2. 手动登录（有头模式，Cookie失效时使用）

使用示例:
    from rrz_login import login
    
    # 登录并获取页面（自动尝试Cookie，失败则手动）
    page, browser = await login()
    
    # 执行后续操作
    await page.goto('https://admin.rrzu.com')
"""

import asyncio
import json
import os
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# ============== 配置 ==============
CDP_URL = "http://127.0.0.1:18800"  # Chrome调试端口
LOGIN_URL = "https://www.rrzu.com/auth/server-login"
ADMIN_URL = "https://admin.rrzu.com/"
ACCOUNT = "15162152584"
PASSWORD = "152584"
COOKIE_FILE = os.path.expanduser("~/.openclaw/workspace/rrz_cookies.json")

# ============== 登录类 ==============
class RRZLogin:
    """人人租登录控制器"""
    
    def __init__(self, cdp_url: str = CDP_URL):
        self.cdp_url = cdp_url
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
    
    async def login_with_cookie(self) -> bool:
        """
        使用 Cookie 登录（无头模式）
        注意：人人租有复杂验证，Cookie 方式可能不稳定
        
        Returns:
            bool: Cookie 登录是否成功
        """
        if not os.path.exists(COOKIE_FILE):
            print("❌ Cookie 文件不存在")
            return False
    
    async def _login_with_cookie_raw(self) -> bool:
        """Cookie 登录的内部实现"""
        with open(COOKIE_FILE, 'r') as f:
            cookies = json.load(f)
        
        if not cookies:
            print("❌ Cookie 为空")
            return False
        
        async with async_playwright() as p:
            print("🔷 启动无头浏览器（Cookie模式）")
            self.browser = await p.chromium.launch(headless=True)
            self.context = await self.browser.new_context()
            await self.context.add_cookies(cookies)
            
            self.page = await self.context.new_page()
            
            await self.page.goto('https://admin.rrzu.com/', timeout=30000)
            await self.page.wait_for_timeout(2000)
            
            if 'admin' in self.page.url:
                print("✅ Cookie 登录成功！")
                return True
            else:
                print("❌ Cookie 已失效")
                await self.browser.close()
                return False
        
        # 尝试通过 CDP 连接已登录的浏览器
        try:
            async with async_playwright() as p:
                print("🔗 尝试连接已登录的浏览器...")
                self.browser = await p.chromium.connect_over_cdp(self.cdp_url)
                
                # 获取现有上下文
                contexts = self.browser.contexts
                if contexts:
                    self.context = contexts[0]
                    self.page = await self.context.new_page()
                    print("✅ 已连接到浏览器")
                    return True
        except Exception as e:
            print(f"⚠️ CDP 连接失败: {e}")
        
        # CDP 失败，尝试 Cookie
        print("🔄 尝试 Cookie 登录...")
        return await self._login_with_cookie_raw()
    
    async def login_manual(self) -> Page:
        """
        手动登录（有头模式）
        登录后自动保存 Cookie
        
        Returns:
            Page: 登录后的页面对象
        """
        async with async_playwright() as p:
            # 启动有头浏览器
            print("🔶 启动有头浏览器（手动登录）")
            self.browser = await p.chromium.launch(headless=False)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            
            # 访问登录页
            print(f"🌐 访问登录页: {LOGIN_URL}")
            await self.page.goto(LOGIN_URL)
            await self.page.wait_for_load_state("networkidle")
            
            # 切换到密码登录
            print("🔄 切换到密码登录")
            await self.page.click("text=密码登录")
            await self.page.wait_for_timeout(1000)
            
            # 输入账号密码
            print(f"👤 输入账号: {ACCOUNT}")
            await self.page.fill('input[placeholder="请输入手机号码"]', ACCOUNT)
            await self.page.fill('input[type="password"]', PASSWORD)
            
            # 勾选同意协议
            print("☑️ 勾选同意协议")
            await self.page.evaluate('''() => {
                const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach(cb => cb.checked = true);
            }''')
            
            # 点击登录按钮
            print("🔐 点击登录")
            buttons = await self.page.query_selector_all("button")
            for btn in buttons:
                text = await btn.text_content()
                if text and "登录" in text.strip():
                    await btn.click()
                    break
            
            # 等待登录完成
            await self.page.wait_for_timeout(3000)
            await self.page.wait_for_load_state("networkidle")
            
            # 保存 Cookie
            cookies = await self.context.cookies()
            with open(COOKIE_FILE, 'w') as f:
                json.dump(cookies, f)
            print(f"✅ Cookie 已保存到: {COOKIE_FILE}")
            
            print(f"✅ 登录成功! 当前URL: {self.page.url}")
            return self.page
    
    async def login(self) -> Page:
        """
        自动登录：优先使用已登录的浏览器会话
        
        Returns:
            Page: 登录后的页面对象
        """
        async with async_playwright() as p:
            # 连接CDP浏览器（不复用现有会话）
            print("🔗 连接CDP浏览器...")
            try:
                self.browser = await p.chromium.connect_over_cdp(self.cdp_url)
            except Exception as e:
                print(f"❌ CDP连接失败: {e}")
                return None
            
            # 获取现有上下文，不创建新的
            contexts = self.browser.contexts
            if not contexts:
                print("❌ 没有现有浏览器上下文")
                return None
            
            self.context = contexts[0]
            
            # 获取现有页面或创建新页面
            pages = self.context.pages
            if pages:
                self.page = pages[0]
            else:
                self.page = await self.context.new_page()
            
            print("✅ 已连接到已登录的浏览器")
            
            # 访问管理后台
            await self.page.goto(ADMIN_URL)
            await self.page.wait_for_timeout(2000)
            
            print(f"当前页面: {self.page.url}")
            return self.page
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            print("🔌 浏览器已关闭")


# ============== 便捷函数 ==============
async def login():
    """
    便捷登录函数（自动 Cookie → 手动）
    
    Returns:
        tuple: (page, login实例)
    """
    login = RRZLogin()
    page = await login.login()
    return page, login


# ============== 测试 ==============
if __name__ == "__main__":
    async def test():
        print("=" * 50)
        print("🚀 人人租登录测试 v2.0")
        print("=" * 50)
        
        # 自动登录（先Cookie，失败则手动）
        rrz_login = RRZLogin()
        page = await rrz_login.login()
        
        # 访问后台
        print("\n📱 访问管理后台...")
        await page.goto(ADMIN_URL)
        await page.wait_for_load_state("networkidle")
        
        # 截图
        await page.screenshot(path="./rrz_admin_logged.png", full_page=True)
        print(f"📸 截图保存: rrz_admin_logged.png")
        
        print(f"\n✅ 测试完成! 当前页面: {page.url}")
    
    asyncio.run(test())
