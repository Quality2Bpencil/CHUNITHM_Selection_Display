from PIL import Image, ImageDraw, ImageFont

def get_text_size_bbox(text, font, draw=None):
    """
    使用textbbox获取文字大小（推荐）
    
    Args:
        text: 文字内容
        font: 字体对象
        draw: ImageDraw对象（可选）
    
    Returns:
        (width, height): 文字宽高
    """
    # 如果提供了draw对象，直接使用
    if draw is not None:
        bbox = draw.textbbox((0, 0), text, font=font)
    else:
        # 创建临时画布
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), text, font=font)
    
    # bbox格式: (left, top, right, bottom)
    width = bbox[2] - bbox[0]  # right - left
    height = bbox[3] - bbox[1] # bottom - top
    
    return width, height, bbox

# 使用示例
font = ImageFont.truetype("arial.ttf", 36)
text = "Hello World!"

width, height, bbox = get_text_size_bbox(text, font)
print(f"文字尺寸: {width} x {height}")
print(f"边界框: {bbox}")