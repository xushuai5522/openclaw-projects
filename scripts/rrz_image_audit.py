#!/usr/bin/env python3
"""
人人租平台商品AI审核 - 图片审核规则
"""

# 图片审核规则（用于AI视觉模型）
IMAGE_AUDIT_RULES = """
平台图片审核规则：
1. 图片底色：必须为纯白底色（商品主体以外不允许有白色以外的其他背景色，如灰色、黑色等）
2. 图片尺寸：至少600x600px，清晰美观
3. 主图内容：仅允许商品展示，禁止添加任何文字内容（文字、水印、标签等）
4. 商品完整性：商品主体完整，无明显缺陷或水印
5. 正品判断：是否为正品苹果/小米等产品
6. 成色判断：根据外观判断商品成色（90新、95新等）
"""

# 完整审核规则
FULL_AUDIT_RULES = """
请作为闲鱼/电商平台商品审核员，审核这张图片中的商品。

平台审核规则：
【图片规则】
1. 图片底色：必须为纯白底色
2. 图片尺寸：至少600x600px，清晰美观
3. 主图内容：仅允许商品展示，禁止添加任何文字内容（文字、水印、标签等）
4. 商品完整性：商品主体完整，无明显缺陷或水印
5. 正品判断：是否为正品苹果/小米等产品
6. 成色判断：根据外观判断商品成色（90新、95新等）

【标题规则】
1. 标题格式: 90新 + 品牌 + 型号 + 商品特点
2. 禁止词: 免押、免息、分期，最佳、最便宜等

【套餐规则】
1. 套餐内需要详细写明具体租用方式
2. 删除套餐中的"租赁"字眼

请从以下角度审核：
1. 商品是否为正品？
2. 图片是否为纯白底色？是否符合平台要求？
3. 图片是否清晰（至少600x600px）？
4. 主图是否包含文字内容？（禁止）
5. 是否存在违规内容（禁止词、虚假宣传等）？
6. 商品成色是几成新？
7. 最终审核结论：是否通过？不通过说明原因。
"""

# 测试函数
def test_audit():
    import requests
    
    api_key = "675362ca-6313-43e5-a705-3046f668e2b1"
    image_url = "https://gw.alicdn.com/imgextra/i4/1917047079/O1CN01EN7EeY22AEmw7hjJB_!!1917047079.jpg"
    
    prompt = f"""
{FULL_AUDIT_RULES}
"""
    
    response = requests.post(
        "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "doubao-seed-1-6-vision-250815",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            "max_tokens": 1000
        },
        timeout=90
    )
    
    print(response.json())

if __name__ == "__main__":
    test_audit()
