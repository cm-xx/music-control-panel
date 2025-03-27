from PIL import Image, ImageDraw

# 创建一个 256x256 的图像
size = 256
image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# 绘制一个圆形背景
circle_color = (52, 152, 219)  # 蓝色
draw.ellipse([0, 0, size-1, size-1], fill=circle_color)

# 绘制播放按钮
button_color = (255, 255, 255)  # 白色
triangle_size = size // 3
x = size // 2
y = size // 2
points = [
    (x - triangle_size//2, y - triangle_size),
    (x - triangle_size//2, y + triangle_size),
    (x + triangle_size//2, y)
]
draw.polygon(points, fill=button_color)

# 保存为 ICO 文件
image.save('icon.ico', format='ICO') 