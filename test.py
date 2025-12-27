import tkinter as tk
from PIL import Image, ImageTk
import time

class FadeOutEffect:
    def __init__(self, root, image_path, duration=2.0):
        self.root = root
        self.duration = duration  # 淡出总时长（秒）
        
        # 加载原始图片
        self.original_img = Image.open(image_path).convert("RGBA")
        self.current_alpha = 1.0  # 初始透明度（1.0=不透明）
        
        # 创建显示标签
        self.label = tk.Label(root)
        self.label.pack()
        
        # 开始淡出
        self.fade_out()
    
    def fade_out(self, start_time=None):
        if start_time is None:
            start_time = time.time()
        
        elapsed = time.time() - start_time
        progress = min(elapsed / self.duration, 1.0)
        
        # 计算当前透明度（从1.0到0.0）
        self.current_alpha = 1.0 - progress
        
        # 应用透明度
        self.update_image()
        
        if progress < 1.0:
            # 继续动画
            self.root.after(16, self.fade_out, start_time)  # 约60fps
        else:
            print("淡出完成")
    
    def update_image(self):
        """更新图片透明度"""
        img = self.original_img.copy()
        alpha_data = img.getdata()
        new_data = []
        
        for item in alpha_data:
            new_alpha = int(item[3] * self.current_alpha)
            new_data.append((item[0], item[1], item[2], new_alpha))
        
        img.putdata(new_data)
        self.photo = ImageTk.PhotoImage(img)
        self.label.config(image=self.photo)

# 使用示例
root = tk.Tk()
root.geometry("400x300")
fade = FadeOutEffect(root, "tester.png", duration=2.0)
root.mainloop()