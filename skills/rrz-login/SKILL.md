# SKILL.md - 人人租登录技能

## 描述
人人租商家后台自动登录技能，完全自动化，不需要人工干预。

## 前置条件
1. Chrome浏览器已启动（CDP端口18800）
2. 已安装playwright: `pip install playwright && playwright install chromium`

## 功能
- **完全自动登录**，不依赖人工
- 复用现有浏览器会话
- 支持重试机制

## 自动登录方法

### 关键发现
- 用 JS 点击登录按钮比 Playwright click 更稳定
- 必须勾选协议复选框
- 登录地址: https://www.rrzu.com/auth/server-login

### 使用方式

#### 方式1: 直接执行脚本
```bash
python3 /Users/xs/.openclaw/workspace/rrz_auto_v3.py
```

#### 方式2: Python调用
```python
import asyncio
from rrz_auto_v3 import auto_login

async def main():
    success, message = await auto_login()
    print(message)

asyncio.run(main())
```

## 登录流程步骤
1. 连接CDP浏览器（port 18800）
2. 获取现有上下文（不创建新的）
3. 访问登录页
4. 点击"密码登录"切换
5. 输入账号密码
6. **勾选协议**（关键）
7. **用JS点击登录按钮**（关键）
8. 等待登录结果

## 配置文件
- 自动登录脚本: `/Users/xs/.openclaw/workspace/rrz_auto_v3.py`
- 登录模块: `/Users/xs/.openclaw/workspace/rrz_login.py`

## 注意事项
- 依赖已运行的Chrome浏览器（带CDP）
- **必须使用JS点击登录按钮**，Playwright click可能失败
- 必须勾选同意协议

## 相关链接
- 登录页: https://www.rrzu.com/auth/server-login
- 管理后台: https://admin.rrzu.com
- 账号: 15162152584
- 密码: 152584
