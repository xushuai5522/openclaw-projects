#!/usr/bin/env python3
"""
优化的人人租商品发布完整流程
处理弹窗 + 填写表单 + 提交审核
"""
import asyncio
from playwright.async_api import async_playwright

async def close_all_popups(page):
    """关闭所有弹窗"""
    for _ in range(5):
        # 方法1: 点击按钮
        await page.evaluate('''() => {
            const keywords = ['暂不', '跳过', '知道', '×', '我知道了'];
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {
                const text = btn.textContent;
                if (keywords.some(k => text.includes(k))) {
                    btn.click();
                }
            }
        }''')
        await asyncio.sleep(0.3)
        
        # 方法2: 按Escape
        await page.keyboard.press('Escape')
        await asyncio.sleep(0.2)
        
        # 方法3: 点击遮罩
        await page.evaluate('''() => {
            const backdrops = document.querySelectorAll('.ant-modal-backdrop');
            backdrops.forEach(el => el && el.click && el.click());
        }''')
        await asyncio.sleep(0.2)

async def main():
    print("开始自动化...")
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(
            'http://127.0.0.1:18800',
            timeout=60000
        )
        ctx = browser.contexts[0]
        
        if not ctx.pages:
            print("没有页面")
            await browser.close()
            return
        
        page = ctx.pages[-1]
        
        # 1. 关闭所有弹窗
        await close_all_popups(page)
        await asyncio.sleep(1)
        
        # 2. 获取iframe
        frame = page.frame(name='rrzuji')
        if not frame:
            print("未找到iframe")
            await browser.close()
            return
        
        # 3. 选择分类
        print("选择分类...")
        await frame.click('input[placeholder*="一级类目"]')
        await asyncio.sleep(0.5)
        await frame.click('text=电脑/平板')
        await asyncio.sleep(0.5)
        
        await frame.click('input[placeholder*="二级类目"]')
        await asyncio.sleep(0.5)
        await frame.click('text=平板')
        await asyncio.sleep(0.5)
        
        # 4. 填写品牌型号
        print("填写品牌型号...")
        await frame.fill('input[placeholder*="品牌"]', 'Tektronix')
        await frame.fill('input[placeholder*="型号"]', 'MDO3052')
        await asyncio.sleep(0.5)
        
        # 5. 点击下一步
        print("点击下一步...")
        await frame.evaluate('window.scrollTo(0, 500)')
        await asyncio.sleep(0.5)
        
        await frame.evaluate('''() => {
            const btns = document.querySelectorAll('button');
            for (let btn of btns) {
                if (btn.textContent.includes('确认') && btn.textContent.includes('下一步')) {
                    btn.click();
                }
            }
        }''')
        await asyncio.sleep(3)
        
        # 6. 关闭新弹窗
        await close_all_popups(page)
        await asyncio.sleep(1)
        
        # 7. 新增租赁方案
        print("新增租赁方案...")
        await frame.evaluate('''() => {
            const btns = document.querySelectorAll('button');
            for (let btn of btns) {
                if (btn.textContent.includes('新增租赁方案')) {
                    btn.click();
                }
            }
        }''')
        await asyncio.sleep(2)
        
        # 8. 填写租金方案
        print("填写租金...")
        await frame.evaluate('window.scrollTo(0, 400)')
        await asyncio.sleep(0.5)
        
        # 填写押金和7天租金
        await frame.evaluate('''() => {
            const inputs = document.querySelectorAll('.ant-input-number input');
            if (inputs[0]) { inputs[0].value = '2308'; inputs[0].dispatchEvent(new Event('input')); }
            if (inputs[1]) { inputs[1].value = '259'; inputs[1].dispatchEvent(new Event('input')); }
        }''')
        await asyncio.sleep(1)
        
        # 9. 展开更多选项
        try:
            await frame.click('text=展开更多支付选项', timeout=3000)
            await asyncio.sleep(1)
        except:
            pass
        
        # 10. 填写更多租金
        await frame.evaluate('''() => {
            const inputs = document.querySelectorAll('.ant-input-number input');
            const values = [432, 1231, 2332, 4406]; // 30天, 90天, 180天, 365天
            for (let i = 2; i < inputs.length && i-2 < values.length; i++) {
                inputs[i].value = values[i-2];
                inputs[i].dispatchEvent(new Event('input'));
            }
        }''')
        await asyncio.sleep(1)
        
        # 11. 截图保存
        await page.screenshot(path='/tmp/rrz_final.png', full_page=True)
        
        # 12. 提交审核
        print("提交审核...")
        await frame.evaluate('window.scrollTo(0, 1000)')
        await asyncio.sleep(0.5)
        
        await frame.evaluate('''() => {
            const btns = document.querySelectorAll('button');
            for (let btn of btns) {
                if (btn.textContent.includes('提交审核')) {
                    btn.click();
                }
            }
        }''')
        
        await asyncio.sleep(2)
        await page.screenshot(path='/tmp/rrz_submitted.png', full_page=True)
        
        print("完成！")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
