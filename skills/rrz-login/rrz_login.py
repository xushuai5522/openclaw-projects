#!/usr/bin/env python3
"""
人人租登录模块 v1.0
提供登录功能，返回浏览器页面对象供后续操作

使用示例:
    from rrz_login import login
    
    # 登录并获取页面
    page, browser = await login()
    
    # 执行后续操作
    await page.goto('https://admin.rrzu.com')
"""

import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# ============== 配置 ==============
CDP_URL = "http://127.0.0.1:18800"  # Chrome调试端口
LOGIN_URL = "https://www.rrzu.com/auth/server-login"
ACCOUNT = "15162152584"
PASSWORD = "152584"

# ============== 登录类 ==============
class RRZLogin:
    """人人租登录控制器"""
    
    def __init__(self, cdp_url: str = CDP_URL):
        self.cdp_url = cdp_url
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
    
    async def login(self, account: str = ACCOUNT, password: str = PASSWORD) -> Page:
        """
        执行登录流程
        
        Args:
            account: 登录账号 (默认: 15162152584)
            password: 登录密码 (默认: 152584)
        
        Returns:
            Page: 登录后的页面对象
        """
        async with async_playwright() as p:
            # 1. 连接浏览器
            print(f"📡 连接浏览器: {self.cdp_url}")
            self.browser = await p.chromium.connect_over_cdp(self.cdp_url)
            
            # 2. 创建新上下文（无痕模式）
            print("🔒 创建新上下文（无痕模式）")
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            
            # 3. 访问登录页
            print(f"🌐 访问登录页: {LOGIN_URL}")
            await self.page.goto(LOGIN_URL)
            await self.page.wait_for_load_state("networkidle")
            
            # 4. 切换到密码登录
            print("🔄 切换到密码登录")
            await self.page.click("text=密码登录")
            await self.page.wait_for_timeout(1000)
            
            # 5. 输入账号密码
            print(f"👤 输入账号: {account}")
            await self.page.fill('input[placeholder="请输入手机号码"]', account)
            await self.page.fill('input[type="password"]', password)
            
            # 6. 勾选同意协议（关键步骤！）
            print("☑️ 勾选同意协议")
            await self.page.evaluate('''() => {
                const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach(cb => cb.checked = true);
            }''')
            
            # 7. 点击登录按钮
            print("🔐 点击登录")
            buttons = await self.page.query_selector_all("button")
            for btn in buttons:
                text = await btn.text_content()
                if text and "登录" in text.strip():
                    await btn.click()
                    break
            
            # 8. 等待登录完成
            await self.page.wait_for_timeout(3000)
            await self.page.wait_for_load_state("networkidle")
            
            print(f"✅ 登录成功! 当前URL: {self.page.url}")
            
            return self.page
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            print("🔌 浏览器已关闭")


# ============== 便捷函数 ==============
async def login(account: str = ACCOUNT, password: str = PASSWORD):
    """
    便捷登录函数
    
    Returns:
        tuple: (page, login实例)
    """
    login = RRZLogin()
    page = await login.login(account, password)
    return page, login


# ============== 测试 ==============
if __name__ == "__main__":
    async def test():
        print("=" * 50)
        print("🚀 人人租登录测试")
        print("=" * 50)
        
        # 登录
        rrz_login = RRZLogin()
        page = await rrz_login.login()
        
        # 访问后台
        print("\n📱 访问管理后台...")
        await page.goto("https://admin.rrzu.com")
        await page.wait_for_load_state("networkidle")
        
        # 截图
        await page.screenshot(path="./rrz_admin_logged.png", full_page=True)
        print(f"📸 截图保存: rr_admin_logged.png")
        
        print(f"\n✅ 测试完成! 当前页面: {page.url}")
        
        # 保持浏览器打开，不关闭
        # await rrz_login.close()
    
    asyncio.run(test())
