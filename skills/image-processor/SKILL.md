# 技能：电商图片处理

从闲鱼数据获取商品图片，处理成白底图用于闲鱼/人人租上架。

## 功能
1. 从闲鱼监控数据获取商品图片URL
2. 去除水印（简单裁剪）
3. 转换为白底正方形图（800x800px，满足平台要求）

## 使用方法

```bash
python3 image_processor.py "商品关键词"
```

## 示例
```bash
# 处理笔记本内存图片
python3 image_processor.py "DDR4 16G 笔记本内存"

# 处理示波器图片  
python3 image_processor.py "示波器"
```

## 输出
- 目录：`~/workspace/product_images/`
- 格式：JPEG, 800x800px, 白底

## 依赖
- Pillow
- requests
