import tkinter as tk
from tkinter import ttk, font
from PIL import Image, ImageTk, ImageDraw, ImageFont
from utils import Utils, CurrentProcess
import os
import random

class DisplayWindow:
    """独立的图片显示窗口，负责显示图片和选曲界面"""
    
    def __init__(self, controller, window_size=None):
        self.controller = controller
        self.root = tk.Toplevel()
        self.root.title("输出窗口")
        
        # 防止重复打开
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 图片缓存，防止垃圾回收
        self.image_references = []
        
        # 初始化缩放系数（相对于1920x1080）
        self.scale_x = 1.0
        self.scale_y = 1.0
        
        self.setup_ui(window_size)

        self.preloaded = self.preload_images()
        self.preloaded_fonts, self.preloaded_BPM_font = self.preload_fonts()

        self._display_background('background')
        self.current_process = CurrentProcess.NONE
        
    def _scale(self, value, axis='x'):
        """应用缩放系数
        
        Args:
            value: 原始值
            axis: 轴向 ('x' 或 'y')
        
        Returns:
            缩放后的值
        """
        if axis == 'x':
            return int(value * self.scale_x)
        else:  # axis == 'y'
            return int(value * self.scale_y)
    
    def _scale_font_size(self, font_size):
        """缩放字体大小，使用平均缩放系数"""
        avg_scale = (self.scale_x + self.scale_y) / 2
        return max(1, int(font_size * avg_scale))
    
    def _scale_coord(self, x, y):
        """缩放坐标"""
        return self._scale(x, 'x'), self._scale(y, 'y')
    
    def _scale_size(self, width, height):
        """缩放大小"""
        return self._scale(width, 'x'), self._scale(height, 'y')
    
    def preload_images(self):
        """预加载必要的图片资源"""
        # 这里可以预加载一些常用的图片资源，提升显示速度
        preloaded = {}
        background_path = Utils().resource_path("assets/picture/bg.png")
        width = 1920 * self.scale_x
        height = 1080 * self.scale_y
        if os.path.exists(background_path):
            preloaded['background'] = self._load_image(background_path, width, height)
        background_path = Utils().resource_path("assets/picture/lv_bg.png")
        if os.path.exists(background_path):
            preloaded['lv_background'] = self._load_image(background_path, width, height)
        preloaded[Utils().resource_path("assets/picture/frame.png")] = Image.open(Utils().resource_path("assets/picture/frame.png")).convert('RGBA')
        preloaded[Utils().resource_path("assets/picture/levels.dds")] = Image.open(Utils().resource_path("assets/picture/levels.dds")).convert('RGBA')
        return preloaded
    
    def preload_fonts(self):
        """预加载必要的字体资源"""
        preloaded_fonts = {}
        font_path = Utils().resource_path("assets/fonts/SEGA_MARUGOTHICDB.ttf")
        if os.path.exists(font_path):
            for size in range(3, 61):
                preloaded_fonts[size] = ImageFont.truetype(font_path, size)
        BPM_font_path = Utils().resource_path("assets/fonts/Helvetica Bold.ttf")
        preloaded_BPM_font = ImageFont.truetype(BPM_font_path, 24)
        return preloaded_fonts, preloaded_BPM_font

    def setup_ui(self, window_size=None):
        """设置用户界面"""
        # 使用传入的窗口大小，或默认为1920x1080
        if window_size is None:
            window_size = (1920, 1080)
        
        width, height = window_size
        self.root.geometry(f"{width}x{height}")
        
        # 计算缩放系数（相对于1920x1080的默认大小）
        self.scale_x = width / 1920.0
        self.scale_y = height / 1080.0
        
        # 禁止调整窗口大小（宽度和高度都不可调整）
        self.root.resizable(False, False)

        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 图片显示区域（带边框）
        display_frame = ttk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=2)
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas用于显示图片，根据窗口大小调整
        self.canvas = tk.Canvas(
            display_frame,
            width=width - 20,
            height=height - 20,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack()
        
    def display_selection(self, data):
        """显示选曲界面"""
        try:
            self.root.after(0, self._update_selection, data)
        except Exception as e:
            print(f"显示选曲错误: {e}")

    def random_music(self, data):
        min_const, max_const = 0.0, 16.0
        try:
            min_const = float(data['min_const'])
        except (ValueError, TypeError):
            pass
        try:
            max_const = float(data['max_const'])
        except (ValueError, TypeError):
            pass
        if min_const > max_const:
            min_const, max_const = max_const, min_const

        if data['library'] == '全曲库':
            unfiltered_music = Utils().music_list
        else:
            unfiltered_music = Utils().users_music_list.get(data['library'], '全曲库')
        filtered_music = filtered_music = [music for music in unfiltered_music.values() if music.get('Const', 0.0) >= min_const and music.get('Const', 16.0) <= max_const]
        if filtered_music == []:
            filtered_music = list(Utils().music_list.values())

        random_music_number = 35 + random.randint(-5, 5)
        random_music_list = []
        for index in range(random_music_number):
            music = random.choice(filtered_music)
            random_music_list.append(music)
        #print(random_music_list)
        self.scroller(random_music_number, random_music_list)

    def scroller(self, random_music_number, random_music_list):

        self.canvas.delete("all")
        self.image_references.clear()
        
        canvas_width = int(self.canvas.winfo_width())
        canvas_height = int(self.canvas.winfo_height())
        
        # 显示背景
        self._display_background('lv_background')

        #标题
        self.canvas.create_text(
                canvas_width // 2,
                self._scale(130, 'y'),
                text='随机选曲',
                font=("Microsoft YaHei", self._scale_font_size(50), "bold"),
                fill="black",
                anchor=tk.CENTER
            )

        image_time = 1.4

        #边框图片大小
        frame_width = self._scale(424, 'x')
        frame_height = self._scale(510, 'y')
        frame_time = image_time
        frame_path = Utils().resource_path("assets/picture/frame.png")

        #曲绘图片大小
        jacket_width = self._scale(300, 'x')
        jacket_height = self._scale(300, 'y')
        jacket_time = image_time
        jacket_dy_position = self._scale(100, 'y')

        text_max_width = self._scale(560, 'x')
        nd_max_width = self._scale(278, 'x')

        title_y_position = self._scale(834, 'y')

        #两侧的等级框
        level_image_path = Utils().resource_path("assets/picture/levels.dds")
        level_left = 4
        level_top = 378
        level_right = 79
        level_bottom = 462
        level_width = self._scale(level_right - level_left, 'x')
        level_height = self._scale(level_bottom - level_top, 'y')
        level_time = image_time
        level_dx_position = self._scale(223, 'x')
        level_dy_position = self._scale(160, 'y')

        level_number_path = level_image_path
        level_number_top = 519
        level_number_bottom = 554
        level_number_left = [
            12, 54, 92, 132, 171, 212, 252, 293, 331, 371
        ]
        level_number_right = [
            36, 69, 117, 157, 197, 237, 276, 316, 356, 540
        ]
        level_plus_top = 517
        level_plus_bottom = 530
        level_plus_left = 411
        level_plus_right = 424
        level_plus_width = self._scale(level_plus_right - level_plus_left, 'x')
        level_plus_height = self._scale(level_plus_bottom - level_plus_top, 'y')
        level_number_height = self._scale(level_number_bottom - level_number_top, 'y')
        level_number_time = level_time

        level_number_dy_position = self._scale(178, 'y')

        title_dy_position = self._scale(240, 'y')
        composer_dy_position = self._scale(288, 'y')

        BPM_dx_position = self._scale(256, 'x')
        BPM_dy_position = self._scale(328, 'y')
        BPM_font_size = self._scale_font_size(24)

        nd_top = 491
        nd_left = 193
        nd_right = 311
        nd_bottom = 501

        nd_width = self._scale(nd_right - nd_left, 'x')
        nd_height = self._scale(nd_bottom - nd_top, 'y')

        nd_dx_position = self._scale(-191, 'x')
        nd_dy_position = self._scale(328, 'y')
        nd_name_dx_position = self._scale(-102, 'x')
        _nd_font_size = 16

        font_path = Utils().resource_path("assets/fonts/SEGA_MARUGOTHICDB.ttf")
        BPM_font_path = Utils().resource_path("assets/fonts/Helvetica Bold.ttf")

        index = 0
        music_list_information = []
        for music in random_music_list:
            music_list_information.append({})
            music_list_information[index]['x_position'] = canvas_width // 2 + self._scale(800 * index, 'x')

            if music_list_information[index]['x_position'] - frame_width * frame_time // 2 <= canvas_width:
                music_name, title_font_size = self.get_adaptive_font_size(music['Name'], font_path, text_max_width, 56, initial_size=40, min_size=30)
                composer_name, composer_font_size = self.get_adaptive_font_size(music['Composer'], font_path, text_max_width, 44, initial_size=20, min_size=15)
                nd_name, nd_font_size = self.get_adaptive_font_size(music['ND'], font_path, nd_max_width, 24, initial_size=_nd_font_size, min_size=_nd_font_size)

                crop_region = (level_left, level_top, level_right, level_bottom)
                img_overlay_list=[
                    {
                        'path': music['Jacket'],
                        'position': (
                            int(frame_width*frame_time) // 2,
                            int(frame_height*frame_time) // 2 - jacket_dy_position
                        ),
                        'size': (int(jacket_width*jacket_time), int(jacket_height*jacket_time)),
                        'alpha': 1.0,
                        'crop': None
                    },
                    {
                        'path': level_image_path,
                        'position': (
                            int(frame_width*frame_time) // 2 - level_dx_position,
                            int(frame_height*frame_time) // 2 + level_dy_position
                        ),
                        'size': (int(level_width*level_time), int(level_height*level_time)),
                        'alpha': 1.0,
                        'crop': crop_region
                    },
                    {
                        'path': level_image_path,
                        'position': (
                            int(frame_width*frame_time) // 2 + nd_dx_position,
                            int(frame_height*frame_time) // 2 + nd_dy_position
                        ),
                        'size': (int(nd_width*level_time), int(nd_height*level_time)),
                        'alpha': 1.0,
                        'crop': (nd_left, nd_top, nd_right, nd_bottom)
                    }
                ]

                # 等级
                level = music['Const']
                if level < 10:
                    pass # 应该不会打小于10级的歌吧，我是懒狗不做了
                elif level < 100:
                    number1 = int(level) // 10
                    number2 = int(level) % 10
                    decimal = level - int(level)
                    crop_region = (level_number_left[number1], level_number_top, level_number_right[number1], level_number_bottom)
                    level_number_width = self._scale(level_number_right[number1] - level_number_left[number1], 'x')
                    img_overlay_list.append(
                        {
                            'path': level_number_path,
                            'position': (
                                int(frame_width * frame_time) // 2 - level_dx_position + self._scale(- 2 - 20, 'x'),
                                int(frame_height * frame_time) // 2 + level_number_dy_position
                            ),
                            'size': (int(level_number_width*level_time), int(level_number_height*level_number_time)),
                            'alpha': 1.0,
                            'crop': crop_region
                        }
                    )
                    crop_region = (level_number_left[number2], level_number_top, level_number_right[number2], level_number_bottom)
                    level_number_width = self._scale(level_number_right[number2] - level_number_left[number2], 'x')
                    img_overlay_list.append(
                        {
                            'path': level_number_path,
                            'position': (
                                int(frame_width * frame_time) // 2 - level_dx_position + self._scale(- 2 + 20, 'x'),
                                int(frame_height * frame_time) // 2 + level_number_dy_position
                            ),
                            'size': (int(level_number_width*level_time), int(level_number_height*level_number_time)),
                            'alpha': 1.0,
                            'crop': crop_region
                        }
                    )
                    if decimal >= 0.5:
                        crop_region = (level_plus_left, level_plus_top, level_plus_right, level_plus_bottom)
                        img_overlay_list.append(
                            {
                                'path': level_number_path,
                                'position': (
                                    int(frame_width * frame_time) // 2 - level_dx_position + self._scale(40, 'x'),
                                    int(frame_height * frame_time) // 2 + level_number_dy_position - self._scale(30, 'y')
                                ),
                                'size': (int(level_plus_width*level_time), int(level_plus_height*level_number_time)),
                                'alpha': 1.0,
                                'crop': crop_region
                            }
                        )
                else:
                    pass
                tk_box = self.overlay_image(
                    base_image_path=frame_path,
                    img_overlay_list=img_overlay_list,
                    text_overlay_list=[
                        {
                            'text': music_name,
                            'position': (
                                int(frame_width*frame_time) // 2,
                                int(frame_height*frame_time) // 2 + title_dy_position
                            ),
                            'font_size': title_font_size,
                        },
                        {
                            'text': composer_name,
                            'position': (
                                int(frame_width*frame_time) // 2,
                                int(frame_height*frame_time) // 2 + composer_dy_position
                            ),
                            'font_size': composer_font_size,
                        },
                        {
                            'text': str(round(float(music['BPM']))),
                            'position': (
                                int(frame_width*frame_time) // 2 + BPM_dx_position,
                                int(frame_height*frame_time) // 2 + BPM_dy_position
                            ),
                            'font_size': BPM_font_size,
                            'font_path': BPM_font_path
                        },
                        {
                            'text': nd_name,
                            'position': (
                                int(frame_width*frame_time) // 2 + nd_name_dx_position,
                                int(frame_height*frame_time) // 2 + nd_dy_position
                            ),
                            'font_size': nd_font_size,
                            'font_path': font_path,
                            'anchor': 'lm'
                        }
                    ],
                    target_size=(int(frame_width*frame_time), int(frame_height*frame_time))
                )
                music_list_information[index]['box'] = self.canvas.create_image(
                    music_list_information[index]['x_position'],
                    canvas_height // 2 + self._scale(50, 'y'),
                    image=tk_box,
                    anchor=tk.CENTER
                )
                self.image_references.append(tk_box)
                
            else:
                music_list_information[index]['box'] = None

            index += 1

            """
            #边框
            if music_list_information[index]['x_position'] - frame_width * frame_time // 2 <= canvas_width:
                tk_frame = self._load_image(frame_path, frame_width*frame_time, frame_height*frame_time)
                music_list_information[index]['frame'] = self.canvas.create_image(
                    music_list_information[index]['x_position'],
                    canvas_height // 2 + 50,
                    image=tk_frame,
                    anchor=tk.CENTER
                )
                self.image_references.append(tk_frame)
            else:
                music_list_information[index]['box'] = None

            #曲名
            if music_list_information[index]['x_position'] - frame_width * frame_time // 2 <= canvas_width:
                text = music['Name']
                text, font_size = self._get_adaptive_font_size(text, "SEGA_MaruGothic-DB", 582, 56, initial_size=30, min_size=20)
                music_list_information[index]['title'] = self.canvas.create_text(
                    music_list_information[index]['x_position'],
                    title_y_position,
                    text=text,
                    font=("SEGA_MaruGothic-DB", font_size),
                    fill="black",
                    anchor=tk.CENTER
                )
            else:
                music_list_information[index]['title'] = None

            #曲师
            if music_list_information[index]['x_position'] - frame_width * frame_time // 2 <= canvas_width:
                text = music['Composer']
                text, font_size = self._get_adaptive_font_size(text, "SEGA_MaruGothic-DB", 582, 56, initial_size=16, min_size=12)
                music_list_information[index]['composer'] = self.canvas.create_text(
                    music_list_information[index]['x_position'],
                    title_y_position + 44,
                    text=text,
                    font=("SEGA_MaruGothic-DB", font_size),
                    fill="black",
                    anchor=tk.CENTER
                )
            else:
                music_list_information[index]['composer'] = None

            #曲绘
            if music_list_information[index]['x_position'] - frame_width * frame_time // 2 <= canvas_width:
                tk_jacket = self._load_image(music['Jacket'], jacket_width*jacket_time, jacket_height*jacket_time)
                music_list_information[index]['jacket'] = self.canvas.create_image(
                    music_list_information[index]['x_position'],
                    jacket_y_position,
                    image=tk_jacket,
                    anchor=tk.CENTER
                )
                self.image_references.append(tk_jacket)
            else:
                music_list_information[index]['jacket'] = None

            #等级框
            if music_list_information[index]['x_position'] - frame_width * frame_time // 2 <= canvas_width:
                tk_level = self._load_image(level_image_path, level_width*level_time, level_height*level_time, crop=crop_region)
                music_list_information[index]['level'] = self.canvas.create_image(
                    music_list_information[index]['x_position'] - level_dx_position,
                    level_y_position,
                    image=tk_level,
                    anchor=tk.CENTER
                )
                self.image_references.append(tk_level)
            else:
                music_list_information[index]['level'] = None
            """

        def fade_out():
            index_range = [random_music_number-1, random_music_number-3]
            alpha = 1.0
            def step():
                if self.current_process != CurrentProcess.RANDOM_MUSIC:
                    return

                nonlocal alpha
                alpha -= 0.05
                for index in index_range:
                    if alpha <= 0:
                        if music_list_information[index]['box']:
                            self.canvas.delete(music_list_information[index]['box'])
                        return
                    
                    if music_list_information[index]['box']:
                        # 获取原始PIL图像
                        original_img = music_list_information[index]['img']
                        
                        # 创建带透明度的新图像（这就是操作final_img）
                        faded_img = self._create_faded_image(original_img, alpha)
                        
                        # 转换为PhotoImage
                        new_tk = ImageTk.PhotoImage(faded_img)
                        
                        # 更新canvas上的图像
                        self.canvas.itemconfig(music_list_information[index]['box'], image=new_tk)
                        self.image_references.append(new_tk)
                self.root.after(30, step)
            step()
            return
            index_range = [random_music_number-1, random_music_number-3]
            alpha = 1.0
            beta = 1.0
            def step():
                nonlocal alpha, beta
                alpha -= 0.1
                beta -= 0.25
                for index in index_range:
                    if alpha <= 0:
                        # 删除最后一个音乐的items
                        if music_list_information[index]['frame']:
                            self.canvas.delete(music_list_information[index]['frame'])
                        if music_list_information[index]['jacket']:
                            self.canvas.delete(music_list_information[index]['jacket'])
                        return
                    if beta <= 0:
                        if music_list_information[index]['title']:
                            self.canvas.delete(music_list_information[index]['title'])
                        if music_list_information[index]['composer']:
                            self.canvas.delete(music_list_information[index]['composer'])
                    # 更新frame透明度
                    if music_list_information[index]['frame']:
                        tk_frame = self._load_image(frame_path, frame_width*frame_time, frame_height*frame_time, alpha=alpha)
                        if tk_frame:
                            self.canvas.itemconfig(music_list_information[index]['frame'], image=tk_frame)
                            self.image_references.append(tk_frame)
                    # 更新jacket透明度
                    if music_list_information[index]['jacket']:
                        tk_jacket = self._load_image(random_music_list[index]['Jacket'], jacket_width*jacket_time, jacket_height*jacket_time, alpha=alpha)
                        if tk_jacket:
                            self.canvas.itemconfig(music_list_information[index]['jacket'], image=tk_jacket)
                            self.image_references.append(tk_jacket)
                    # 更新level透明度
                    if music_list_information[index]['level']:
                        tk_level = self._load_image(level_image_path, level_width*level_time, level_height*level_time, crop=crop_region, alpha=alpha)
                        if tk_level:
                            self.canvas.itemconfig(music_list_information[index]['level'], image=tk_level)
                            self.image_references.append(tk_level)
                    # 更新title颜色，从black渐变到white
                    if music_list_information[index]['title']:
                        gray_value = int(255 * (1 - beta))
                        color = f'#{gray_value:02x}{gray_value:02x}{gray_value:02x}'
                        self.canvas.itemconfig(music_list_information[index]['title'], fill=color)
                    # 更新composer颜色，从black渐变到white
                    if music_list_information[index]['composer']:
                        gray_value = int(255 * (1 - beta))
                        color = f'#{gray_value:02x}{gray_value:02x}{gray_value:02x}'
                        self.canvas.itemconfig(music_list_information[index]['composer'], fill=color)
                self.root.after(30, step)
            step()

        max_speed = 70.0
        speed = 0.0
        acceleration = 0.5
        deceleration = 0.7
        total_distance = self._scale((random_music_number - 2) * 800, 'x')

        def move():
            if self.current_process != CurrentProcess.RANDOM_MUSIC:
                return

            nonlocal speed, total_distance
            if total_distance <= 0:
                self.root.after(700, fade_out)
                return
            elif total_distance < speed * speed / deceleration / 2 + 20 and speed > 1+ deceleration:
                speed -= deceleration
            elif speed < max_speed:
                speed += acceleration
            total_distance -= int(speed)
            index = 0
            for music in random_music_list:
                music_list_information[index]['x_position'] -= int(speed)

                if music_list_information[index]['box']:
                    self.canvas.coords(music_list_information[index]['box'], music_list_information[index]['x_position'], canvas_height // 2 + self._scale(50, 'y'))
                    if music_list_information[index]['x_position'] + frame_width * frame_time // 2 < 0:
                        self.canvas.delete(music_list_information[index]['box'])
                        music_list_information[index]['box'] = None
                elif (music_list_information[index]['x_position'] - frame_width * frame_time // 2 <= canvas_width and
                      music_list_information[index]['x_position'] + frame_width * frame_time // 2 >=0):
                    # 实时生成box
                    music_name, title_font_size = self.get_adaptive_font_size(music['Name'], font_path, text_max_width, 56, initial_size=40, min_size=30)
                    composer_name, composer_font_size = self.get_adaptive_font_size(music['Composer'], font_path, text_max_width, 44, initial_size=20, min_size=15)
                    nd_name, nd_font_size = self.get_adaptive_font_size(music['ND'], font_path, nd_max_width, 24, initial_size=_nd_font_size, min_size=_nd_font_size)

                    crop_region = (level_left, level_top, level_right, level_bottom)
                    img_overlay_list=[
                        {
                            'path': music['Jacket'],
                            'position': (
                                int(frame_width*frame_time) // 2,
                                int(frame_height*frame_time) // 2 - jacket_dy_position
                            ),
                            'size': (int(jacket_width*jacket_time), int(jacket_height*jacket_time)),
                            'alpha': 1.0,
                            'crop': None
                        },
                        {
                            'path': level_image_path,
                            'position': (
                                int(frame_width*frame_time) // 2 - level_dx_position,
                                int(frame_height*frame_time) // 2 + level_dy_position
                            ),
                            'size': (int(level_width*level_time), int(level_height*level_time)),
                            'alpha': 1.0,
                            'crop': crop_region
                        },
                        {
                            'path': level_image_path,
                            'position': (
                                int(frame_width*frame_time) // 2 + nd_dx_position,
                                int(frame_height*frame_time) // 2 + nd_dy_position
                            ),
                            'size': (int(nd_width*level_time), int(nd_height*level_time)),
                            'alpha': 1.0,
                            'crop': (nd_left, nd_top, nd_right, nd_bottom)
                        }
                    ]

                    # 等级
                    level = music['Const']
                    if level < 10:
                        pass # 应该不会打小于10级的歌吧，我是懒狗不做了
                    elif level < 100:
                        number1 = int(level) // 10
                        number2 = int(level) % 10
                        decimal = level - int(level)
                        crop_region = (level_number_left[number1], level_number_top, level_number_right[number1], level_number_bottom)
                        level_number_width = self._scale(level_number_right[number1] - level_number_left[number1], 'x')
                        img_overlay_list.append(
                            {
                                'path': level_number_path,
                                'position': (
                                    int(frame_width * frame_time) // 2 - level_dx_position + self._scale(- 2 - 20, 'x'),
                                    int(frame_height * frame_time) // 2 + level_number_dy_position
                                ),
                                'size': (int(level_number_width*level_time), int(level_number_height*level_number_time)),
                                'alpha': 1.0,
                                'crop': crop_region
                            }
                        )
                        crop_region = (level_number_left[number2], level_number_top, level_number_right[number2], level_number_bottom)
                        level_number_width = self._scale(level_number_right[number2] - level_number_left[number2], 'x')
                        img_overlay_list.append(
                            {
                                'path': level_number_path,
                                'position': (
                                    int(frame_width * frame_time) // 2 - level_dx_position + self._scale(- 2 + 20, 'x'),
                                    int(frame_height * frame_time) // 2 + level_number_dy_position
                                ),
                                'size': (int(level_number_width*level_time), int(level_number_height*level_number_time)),
                                'alpha': 1.0,
                                'crop': crop_region
                            }
                        )
                        if decimal >= 0.5:
                            crop_region = (level_plus_left, level_plus_top, level_plus_right, level_plus_bottom)
                            img_overlay_list.append(
                                {
                                    'path': level_number_path,
                                    'position': (
                                        int(frame_width * frame_time) // 2 - level_dx_position + self._scale(40, 'x'),
                                        int(frame_height * frame_time) // 2 + level_number_dy_position - self._scale(30, 'y')
                                    ),
                                    'size': (int(level_plus_width*level_time), int(level_plus_height*level_number_time)),
                                    'alpha': 1.0,
                                    'crop': crop_region
                                }
                            )
                    else:
                        pass

                    if index == random_music_number - 1 or index == random_music_number - 3:
                        tk_box, music_list_information[index]['img'] = self.overlay_image(
                            base_image_path=frame_path,
                            img_overlay_list=img_overlay_list,
                            text_overlay_list=[
                                {
                                    'text': music_name,
                                    'position': (
                                        int(frame_width*frame_time) // 2,
                                        int(frame_height*frame_time) // 2 + title_dy_position
                                    ),
                                    'font_size': title_font_size,
                                },
                                {
                                    'text': composer_name,
                                    'position': (
                                        int(frame_width*frame_time) // 2,
                                        int(frame_height*frame_time) // 2 + composer_dy_position
                                    ),
                                    'font_size': composer_font_size,
                                },
                                {
                                    'text': str(round(float(music['BPM']))),
                                    'position': (
                                        int(frame_width*frame_time) // 2 + BPM_dx_position,
                                        int(frame_height*frame_time) // 2 + BPM_dy_position
                                    ),
                                    'font_size': BPM_font_size,
                                    'font_path': BPM_font_path
                                },
                                {
                                    'text': nd_name,
                                    'position': (
                                        int(frame_width*frame_time) // 2 + nd_name_dx_position,
                                        int(frame_height*frame_time) // 2 + nd_dy_position
                                    ),
                                    'font_size': nd_font_size,
                                    'font_path': font_path,
                                    'anchor': 'lm'
                                }
                            ],
                            target_size=(int(frame_width*frame_time), int(frame_height*frame_time)),
                            output_img=True
                        )
                    else:
                        tk_box = self.overlay_image(
                            base_image_path=frame_path,
                            img_overlay_list=img_overlay_list,
                            text_overlay_list=[
                                {
                                    'text': music_name,
                                    'position': (
                                        int(frame_width*frame_time) // 2,
                                        int(frame_height*frame_time) // 2 + title_dy_position
                                    ),
                                    'font_size': title_font_size,
                                },
                                {
                                    'text': composer_name,
                                    'position': (
                                        int(frame_width*frame_time) // 2,
                                        int(frame_height*frame_time) // 2 + composer_dy_position
                                    ),
                                    'font_size': composer_font_size,
                                },
                                {
                                    'text': str(round(float(music['BPM']))),
                                    'position': (
                                        int(frame_width*frame_time) // 2 + BPM_dx_position,
                                        int(frame_height*frame_time) // 2 + BPM_dy_position
                                    ),
                                    'font_size': BPM_font_size,
                                    'font_path': BPM_font_path
                                },
                                {
                                    'text': nd_name,
                                    'position': (
                                        int(frame_width*frame_time) // 2 + nd_name_dx_position,
                                        int(frame_height*frame_time) // 2 + nd_dy_position
                                    ),
                                    'font_size': nd_font_size,
                                    'font_path': font_path,
                                    'anchor': 'lm'
                                }
                            ],
                            target_size=(int(frame_width*frame_time), int(frame_height*frame_time))
                        )
                    music_list_information[index]['box'] = self.canvas.create_image(
                        music_list_information[index]['x_position'],
                        canvas_height // 2 + self._scale(50, 'y'),
                        image=tk_box,
                        anchor=tk.CENTER
                    )
                    self.image_references.append(tk_box)

                index += 1

                continue
                #边框
                if music_list_information[index]['frame']:
                    self.canvas.coords(music_list_information[index]['frame'], music_list_information[index]['x_position'], canvas_height // 2 + 50)
                    if music_list_information[index]['x_position'] + frame_width * frame_time // 2 < 0:
                        self.canvas.delete(music_list_information[index]['frame'])
                        music_list_information[index]['frame'] = None
                elif (music_list_information[index]['x_position'] - frame_width * frame_time // 2 <= canvas_width and
                      music_list_information[index]['x_position'] + frame_width * frame_time // 2 >=0):
                    tk_frame = self._load_image(frame_path, frame_width*frame_time, frame_height*frame_time)
                    music_list_information[index]['frame'] = self.canvas.create_image(
                        music_list_information[index]['x_position'],
                        canvas_height // 2 + 50,
                        image=tk_frame,
                        anchor=tk.CENTER
                    )
                    self.image_references.append(tk_frame)

                #曲名
                if music_list_information[index]['title']:
                    self.canvas.coords(music_list_information[index]['title'], music_list_information[index]['x_position'], title_y_position)
                    if music_list_information[index]['x_position'] + frame_width * frame_time // 2 < 0:
                        self.canvas.delete(music_list_information[index]['title'])
                        music_list_information[index]['title'] = None
                elif (music_list_information[index]['x_position'] - frame_width * frame_time // 2 <= canvas_width and
                      music_list_information[index]['x_position'] + frame_width * frame_time // 2 >=0):
                    text = music['Name']
                    text, font_size = self._get_adaptive_font_size(text, "SEGA_MaruGothic-DB", 582, 56, initial_size=30, min_size=20)
                    music_list_information[index]['title'] = self.canvas.create_text(
                        music_list_information[index]['x_position'],
                        title_y_position,
                        text=text,
                        font=("SEGA_MaruGothic-DB", font_size),
                        fill="black",
                        anchor=tk.CENTER
                    )

                #曲师
                if music_list_information[index]['composer']:
                    self.canvas.coords(music_list_information[index]['composer'], music_list_information[index]['x_position'], title_y_position + 44)
                    if music_list_information[index]['x_position'] + frame_width * frame_time // 2 < 0:
                        self.canvas.delete(music_list_information[index]['composer'])
                        music_list_information[index]['composer'] = None
                elif (music_list_information[index]['x_position'] - frame_width * frame_time // 2 <= canvas_width and
                        music_list_information[index]['x_position'] + frame_width * frame_time // 2 >=0):
                    text = music['Composer']
                    text, font_size = self._get_adaptive_font_size(text, "SEGA_MaruGothic-DB", 582, 56, initial_size=16, min_size=12)
                    music_list_information[index]['composer'] = self.canvas.create_text(
                        music_list_information[index]['x_position'],
                        title_y_position + 44,
                        text=text,
                        font=("SEGA_MaruGothic-DB", font_size),
                        fill="black",
                        anchor=tk.CENTER
                    )

                #曲绘
                if music_list_information[index]['jacket']:
                    self.canvas.coords(music_list_information[index]['jacket'], music_list_information[index]['x_position'], jacket_y_position)
                    if music_list_information[index]['x_position'] + frame_width * frame_time // 2 < 0:
                        self.canvas.delete(music_list_information[index]['jacket'])
                        music_list_information[index]['jacket'] = None
                elif (music_list_information[index]['x_position'] - frame_width * frame_time // 2 <= canvas_width and
                      music_list_information[index]['x_position'] + frame_width * frame_time // 2 >=0):
                    tk_jacket = self._load_image(music['Jacket'], jacket_width*jacket_time, jacket_height*jacket_time)
                    music_list_information[index]['jacket'] = self.canvas.create_image(
                        music_list_information[index]['x_position'],
                        jacket_y_position,
                        image=tk_jacket,
                        anchor=tk.CENTER
                    )
                    self.image_references.append(tk_jacket)

                #等级框
                if music_list_information[index]['level']:
                    self.canvas.coords(music_list_information[index]['level'], music_list_information[index]['x_position'] - level_dx_position, level_y_position)
                    if music_list_information[index]['x_position'] + frame_width * frame_time // 2 < 0:
                        self.canvas.delete(music_list_information[index]['level'])
                        music_list_information[index]['level'] = None
                elif (music_list_information[index]['x_position'] - frame_width * frame_time // 2 <= canvas_width and
                      music_list_information[index]['x_position'] + frame_width * frame_time // 2 >=0):
                    tk_level = self._load_image(level_image_path, level_width*level_time, level_height*level_time, crop=crop_region)
                    music_list_information[index]['level'] = self.canvas.create_image(
                        music_list_information[index]['x_position'] - level_dx_position,
                        level_y_position,
                        image=tk_level,
                        anchor=tk.CENTER
                    )
                    self.image_references.append(tk_level)

                index += 1

            # 每隔30毫秒调用一次移动函数
            self.root.after(30, move)

        self.root.after(1000, move)
            
    def _update_selection(self, data):
        """更新选曲显示"""
        self.canvas.delete("all")
        self.image_references.clear()
        
        canvas_width = int(self.canvas.winfo_width())
        canvas_height = int(self.canvas.winfo_height())
        
        # 显示背景
        self._display_background('background')

        if data:
            image_time = 1.4

            image_time = 1.4

            #边框图片大小
            frame_width = self._scale(424, 'x')
            frame_height = self._scale(510, 'y')
            frame_time = image_time
            frame_path = Utils().resource_path("assets/picture/frame.png")

            #曲绘图片大小
            jacket_width = self._scale(300, 'x')
            jacket_height = self._scale(300, 'y')
            jacket_time = image_time
            jacket_dy_position = self._scale(100, 'y')

            #文字最大长度
            text_max_width = self._scale(560, 'x')
            nd_max_width = self._scale(278, 'x')

            level_image_path = Utils().resource_path("assets/picture/levels.dds")
            level_left = 4
            level_top = 378
            level_right = 79
            level_bottom = 462
            level_width = self._scale(level_right - level_left, 'x')
            level_height = self._scale(level_bottom - level_top, 'y')
            level_time = image_time
            level_dx_position = self._scale(223, 'x')
            level_dy_position = self._scale(160, 'y')

            level_number_path = level_image_path
            level_number_top = 519
            level_number_bottom = 554
            level_number_left = [
                12, 54, 92, 132, 171, 212, 252, 293, 331, 371
            ]
            level_number_right = [
                36, 69, 117, 157, 197, 237, 276, 316, 356, 540
            ]
            level_plus_top = 517
            level_plus_bottom = 530
            level_plus_left = 411
            level_plus_right = 424
            level_plus_width = self._scale(level_plus_right - level_plus_left, 'x')
            level_plus_height = self._scale(level_plus_bottom - level_plus_top, 'y')
            level_number_height = self._scale(level_number_bottom - level_number_top, 'y')
            level_number_time = level_time

            level_number_dy_position = self._scale(178, 'y')

            title_dy_position = self._scale(240, 'y')
            composer_dy_position = self._scale(288, 'y')

            BPM_dx_position = self._scale(256, 'x')
            BPM_dy_position = self._scale(328, 'y')
            BPM_font_size = self._scale_font_size(24)

            nd_top = 491
            nd_left = 193
            nd_right = 311
            nd_bottom = 501

            nd_width = self._scale(nd_right - nd_left, 'x')
            nd_height = self._scale(nd_bottom - nd_top, 'y')

            nd_dx_position = self._scale(-191, 'x')
            nd_dy_position = self._scale(328, 'y')
            nd_name_dx_position = self._scale(-102, 'x')
            _nd_font_size = 16

            font_path = Utils().resource_path("assets/fonts/SEGA_MARUGOTHICDB.ttf")
            BPM_font_path = Utils().resource_path("assets/fonts/Helvetica Bold.ttf")

            # 队名与选手名
            text = data['team1']
            self.canvas.create_text(
                canvas_width // 2 - self._scale(400, 'x'),
                self._scale(105, 'y'),
                text=text,
                font=("Microsoft YaHei", self._scale_font_size(40), "bold"),
                fill="black",
                anchor=tk.CENTER
            )

            text = f'{data['player1']} 的自选曲'
            self.canvas.create_text(
                canvas_width // 2 - self._scale(400, 'x'),
                self._scale(175, 'y'),
                text=text,
                font=("Microsoft YaHei", self._scale_font_size(40), "bold"),
                fill="black",
                anchor=tk.CENTER
            )

            text = data['team2']
            self.canvas.create_text(
                canvas_width // 2 + self._scale(400, 'x'),
                self._scale(105, 'y'),
                text=text,
                font=("Microsoft YaHei", self._scale_font_size(40), "bold"),
                fill="black",
                anchor=tk.CENTER
            )

            text = f'{data['player2']} 的自选曲'
            self.canvas.create_text(
                canvas_width // 2 + self._scale(400, 'x'),
                self._scale(175, 'y'),
                text=text,
                font=("Microsoft YaHei", self._scale_font_size(40), "bold"),
                fill="black",
                anchor=tk.CENTER
            )
            
            # 左侧曲目
            random_music1 = random.choice(list(Utils().music_list.values()))
            music1_id = data['music1'].split()[0]
            music1 = Utils().music_list.get(music1_id, random_music1) # 如果找不到对应曲目，就用随机曲
            music1_name, title_font_size = self.get_adaptive_font_size(music1['Name'], font_path, text_max_width, 56, initial_size=40, min_size=30)
            composer1_name, composer_font_size = self.get_adaptive_font_size(music1['Composer'], font_path, text_max_width, 44, initial_size=20, min_size=15)
            nd1_name, nd_font_size = self.get_adaptive_font_size(music1['ND'], font_path, nd_max_width, 24, initial_size=_nd_font_size, min_size=_nd_font_size)
            jacket1_path = music1['Jacket']

            crop_region = (level_left, level_top, level_right, level_bottom)
            img_overlay_list1=[
                {
                    'path': jacket1_path,
                    'position': (
                        int(frame_width*frame_time) // 2,
                        int(frame_height*frame_time) // 2 - jacket_dy_position
                    ),
                    'size': (int(jacket_width*jacket_time), int(jacket_height*jacket_time)),
                    'alpha': 1.0,
                    'crop': None
                },
                {
                    'path': level_image_path,
                    'position': (
                        int(frame_width*frame_time) // 2 - level_dx_position,
                        int(frame_height*frame_time) // 2 + level_dy_position
                    ),
                    'size': (int(level_width*level_time), int(level_height*level_time)),
                    'alpha': 1.0,
                    'crop': crop_region
                },
                {
                    'path': level_image_path,
                    'position': (
                        int(frame_width*frame_time) // 2 + nd_dx_position,
                        int(frame_height*frame_time) // 2 + nd_dy_position
                    ),
                    'size': (int(nd_width*level_time), int(nd_height*level_time)),
                    'alpha': 1.0,
                    'crop': (nd_left, nd_top, nd_right, nd_bottom)
                }
            ]

            # 左侧曲目等级
            level1 = music1['Const']
            if level1 < 10:
                pass # 应该不会打小于10级的歌吧，我是懒狗不做了
            elif level1 <100:
                number1 = int(level1) // 10
                number2 = int(level1) % 10
                decimal = level1 - int(level1)
                crop_region = (level_number_left[number1], level_number_top, level_number_right[number1], level_number_bottom)
                level_number_width = self._scale(level_number_right[number1] - level_number_left[number1], 'x')
                img_overlay_list1.append(
                    {
                        'path': level_number_path,
                        'position': (
                            int(frame_width * frame_time) // 2 - level_dx_position + self._scale(- 2 - 20, 'x'),
                            int(frame_height * frame_time) // 2 + level_number_dy_position
                        ),
                        'size': (int(level_number_width*level_time), int(level_number_height*level_number_time)),
                        'alpha': 1.0,
                        'crop': crop_region
                    }
                )
                crop_region = (level_number_left[number2], level_number_top, level_number_right[number2], level_number_bottom)
                level_number_width = self._scale(level_number_right[number2] - level_number_left[number2], 'x')
                img_overlay_list1.append(
                    {
                        'path': level_number_path,
                        'position': (
                            int(frame_width * frame_time) // 2 - level_dx_position + self._scale(- 2 + 20, 'x'),
                            int(frame_height * frame_time) // 2 + level_number_dy_position
                        ),
                        'size': (int(level_number_width*level_time), int(level_number_height*level_number_time)),
                        'alpha': 1.0,
                        'crop': crop_region
                    }
                )
                if decimal >= 0.5:
                    crop_region = (level_plus_left, level_plus_top, level_plus_right, level_plus_bottom)
                    img_overlay_list1.append(
                        {
                            'path': level_number_path,
                            'position': (
                                int(frame_width * frame_time) // 2 - level_dx_position + self._scale(40, 'x'),
                                int(frame_height * frame_time) // 2 + level_number_dy_position + self._scale(-30, 'y')
                            ),
                            'size': (int(level_plus_width*level_time), int(level_plus_height*level_number_time)),
                            'alpha': 1.0,
                            'crop': crop_region
                        }
                    )
            else:
                pass
            
            tk_left_picture = self.overlay_image(
                base_image_path=frame_path,
                img_overlay_list=img_overlay_list1,
                text_overlay_list=[
                    {
                        'text': music1_name,
                        'position': (
                            int(frame_width*frame_time) // 2,
                            int(frame_height*frame_time) // 2 + title_dy_position
                        ),
                        'font_size': title_font_size,
                    },
                    {
                        'text': composer1_name,
                        'position': (
                            int(frame_width*frame_time) // 2,
                            int(frame_height*frame_time) // 2 + composer_dy_position
                        ),
                        'font_size': composer_font_size,
                    },
                    {
                        'text': str(round(float(music1['BPM']))),
                        'position': (
                            int(frame_width*frame_time) // 2 + BPM_dx_position,
                            int(frame_height*frame_time) // 2 + BPM_dy_position
                        ),
                        'font_size': BPM_font_size,
                        'font_path': BPM_font_path
                    },
                    {
                        'text': nd1_name,
                        'position': (
                            int(frame_width*frame_time) // 2 + nd_name_dx_position,
                            int(frame_height*frame_time) // 2 + nd_dy_position
                        ),
                        'font_size': nd_font_size,
                        'font_path': font_path,
                        'anchor': 'lm'
                    }
                ],
                target_size=(int(frame_width*frame_time), int(frame_height*frame_time))
            )
            if tk_left_picture:
                self.canvas.create_image(
                    canvas_width // 2 - self._scale(400, 'x'),
                    canvas_height // 2 + self._scale(50, 'y'),
                    image=tk_left_picture,
                    anchor=tk.CENTER
                )
                self.image_references.append(tk_left_picture)

            # 右侧曲目
            random_music1 = random.choice(list(Utils().music_list.values()))
            music2_id = data['music2'].split()[0]
            music2 = Utils().music_list.get(music2_id, random_music1) # 如果找不到对应曲目，就用随机曲
            music2_name, title_font_size = self.get_adaptive_font_size(music2['Name'], font_path, text_max_width, 56, initial_size=40, min_size=30)
            composer2_name, composer_font_size = self.get_adaptive_font_size(music2['Composer'], font_path, text_max_width, 44, initial_size=20, min_size=15)
            nd2_name, nd_font_size = self.get_adaptive_font_size(music2['ND'], font_path, nd_max_width, 24, initial_size=_nd_font_size, min_size=_nd_font_size)
            jacket2_path = music2['Jacket']

            crop_region = (level_left, level_top, level_right, level_bottom)
            img_overlay_list1=[
                {
                    'path': jacket2_path,
                    'position': (
                        int(frame_width*frame_time) // 2,
                        int(frame_height*frame_time) // 2 - jacket_dy_position
                    ),
                    'size': (int(jacket_width*jacket_time), int(jacket_height*jacket_time)),
                    'alpha': 1.0,
                    'crop': None
                },
                {
                    'path': level_image_path,
                    'position': (
                        int(frame_width*frame_time) // 2 - level_dx_position,
                        int(frame_height*frame_time) // 2 + level_dy_position
                    ),
                    'size': (int(level_width*level_time), int(level_height*level_time)),
                    'alpha': 1.0,
                    'crop': crop_region
                },
                {
                    'path': level_image_path,
                    'position': (
                        int(frame_width*frame_time) // 2 + nd_dx_position,
                        int(frame_height*frame_time) // 2 + nd_dy_position
                    ),
                    'size': (int(nd_width*level_time), int(nd_height*level_time)),
                    'alpha': 1.0,
                    'crop': (nd_left, nd_top, nd_right, nd_bottom)
                }
            ]

            # 右侧曲目等级
            level2 = music2['Const']
            if level2 < 10:
                pass # 应该不会打小于10级的歌吧，我是懒狗不做了
            elif level2 <100:
                number1 = int(level2) // 10
                number2 = int(level2) % 10
                decimal = level2 - int(level2)
                crop_region = (level_number_left[number1], level_number_top, level_number_right[number1], level_number_bottom)
                level_number_width = self._scale(level_number_right[number1] - level_number_left[number1], 'x')
                img_overlay_list1.append(
                    {
                        'path': level_number_path,
                        'position': (
                            int(frame_width * frame_time) // 2 - level_dx_position + self._scale(- 2 - 20, 'x'),
                            int(frame_height * frame_time) // 2 + level_number_dy_position
                        ),
                        'size': (int(level_number_width*level_time), int(level_number_height*level_number_time)),
                        'alpha': 1.0,
                        'crop': crop_region
                    }
                )
                crop_region = (level_number_left[number2], level_number_top, level_number_right[number2], level_number_bottom)
                level_number_width = self._scale(level_number_right[number2] - level_number_left[number2], 'x')
                img_overlay_list1.append(
                    {
                        'path': level_number_path,
                        'position': (
                            int(frame_width * frame_time) // 2 - level_dx_position + self._scale(- 2 + 20, 'x'),
                            int(frame_height * frame_time) // 2 + level_number_dy_position
                        ),
                        'size': (int(level_number_width*level_time), int(level_number_height*level_number_time)),
                        'alpha': 1.0,
                        'crop': crop_region
                    }
                )
                if decimal >= 0.5:
                    crop_region = (level_plus_left, level_plus_top, level_plus_right, level_plus_bottom)
                    img_overlay_list1.append(
                        {
                            'path': level_number_path,
                            'position': (
                                int(frame_width * frame_time) // 2 - level_dx_position + self._scale(40, 'x'),
                                int(frame_height * frame_time) // 2 + level_number_dy_position + self._scale(-30, 'y')
                            ),
                            'size': (int(level_plus_width*level_time), int(level_plus_height*level_number_time)),
                            'alpha': 1.0,
                            'crop': crop_region
                        }
                    )
            else:
                pass
            
            tk_right_picture = self.overlay_image(
                base_image_path=frame_path,
                img_overlay_list=img_overlay_list1,
                text_overlay_list=[
                    {
                        'text': music2_name,
                        'position': (
                            int(frame_width*frame_time) // 2,
                            int(frame_height*frame_time) // 2 + title_dy_position
                        ),
                        'font_size': title_font_size,
                    },
                    {
                        'text': composer2_name,
                        'position': (
                            int(frame_width*frame_time) // 2,
                            int(frame_height*frame_time) // 2 + composer_dy_position
                        ),
                        'font_size': composer_font_size,
                    },
                    {
                        'text': str(round(float(music2['BPM']))),
                        'position': (
                            int(frame_width*frame_time) // 2 + BPM_dx_position,
                            int(frame_height*frame_time) // 2 + BPM_dy_position
                        ),
                        'font_size': BPM_font_size,
                        'font_path': BPM_font_path
                    },
                    {
                        'text': nd2_name,
                        'position': (
                            int(frame_width*frame_time) // 2 + nd_name_dx_position,
                            int(frame_height*frame_time) // 2 + nd_dy_position
                        ),
                        'font_size': nd_font_size,
                        'font_path': font_path,
                        'anchor': 'lm'
                    }
                ],
                target_size=(int(frame_width*frame_time), int(frame_height*frame_time))
            )
            if tk_right_picture:
                self.canvas.create_image(
                    canvas_width // 2 + self._scale(400, 'x'),
                    canvas_height // 2 + self._scale(50, 'y'),
                    image=tk_right_picture,
                    anchor=tk.CENTER
                )
                self.image_references.append(tk_right_picture)

        # 如果有数据，显示图片
        if data and False: # 这些都被重构了，我操你妈
            image_time = 1.4

            #边框图片大小
            frame_width = 424
            frame_height = 510
            frame_time = image_time

            #曲绘图片大小
            jacket_width = 300
            jacket_height = 300
            jacket_time = image_time

            # 两侧的边框
            frame_path = "assets/picture/frame.png"
            tk_frame = self._load_image(frame_path, frame_width*frame_time, frame_height*frame_time)
            if tk_frame:
                # 左侧边框
                self.canvas.create_image(
                    canvas_width // 2 - 400,
                    canvas_height // 2 + 50,
                    image=tk_frame,
                    anchor=tk.CENTER
                )
                self.image_references.append(tk_frame)
                # 右侧边框
                self.canvas.create_image(
                    canvas_width // 2 + 400,
                    canvas_height // 2 + 50,
                    image=tk_frame,
                    anchor=tk.CENTER
                )
                self.image_references.append(tk_frame)
            
            text = data['team1']
            self.canvas.create_text(
                canvas_width // 2 - 400,
                105,
                text=text,
                font=("Microsoft YaHei", 40, "bold"),
                fill="black",
                anchor=tk.CENTER
            )

            text = f'{data['player1']} 的自选曲'
            self.canvas.create_text(
                canvas_width // 2 - 400,
                175,
                text=text,
                font=("Microsoft YaHei", 40, "bold"),
                fill="black",
                anchor=tk.CENTER
            )

            text = data['team2']
            self.canvas.create_text(
                canvas_width // 2 + 400,
                105,
                text=text,
                font=("Microsoft YaHei", 40, "bold"),
                fill="black",
                anchor=tk.CENTER
            )

            text = f'{data['player2']} 的自选曲'
            self.canvas.create_text(
                canvas_width // 2 + 400,
                175,
                text=text,
                font=("Microsoft YaHei", 40, "bold"),
                fill="black",
                anchor=tk.CENTER
            )

            random_music1 = random.choice(list(Utils().music_list.values()))
            music1_id = data['music1']
            music1 = Utils().music_list.get(music1_id, random_music1) # 如果找不到对应曲目，就用随机曲
            
            text = music1['Name']
            text, font_size = self._get_adaptive_font_size(text, "SEGA_MaruGothic-DB", 582, 56, initial_size=30, min_size=20)
            self.canvas.create_text(
                canvas_width // 2 - 400,
                834,
                text=text,
                font=("SEGA_MaruGothic-DB", font_size),
                fill="black",
                anchor=tk.CENTER
            )

            text = music1['Composer']
            text, font_size = self._get_adaptive_font_size(text, "SEGA_MaruGothic-DB", 582, 56, initial_size=16, min_size=12)
            self.canvas.create_text(
                canvas_width // 2 - 400,
                878,
                text=text,
                font=("SEGA_MaruGothic-DB", font_size),
                fill="black",
                anchor=tk.CENTER
            )

            jacket1_path = music1['Jacket']
            tk_jacket1 = self._load_image(jacket1_path, jacket_width*jacket_time, jacket_height*jacket_time)
            if tk_jacket1:
                # 左侧曲绘
                self.canvas.create_image(
                    canvas_width // 2 - 400,
                    canvas_height // 2 - 44,
                    image=tk_jacket1,
                    anchor=tk.CENTER
                )
                self.image_references.append(tk_jacket1)

            random_music2 = random.choice(list(Utils().music_list.values()))
            music2_id = data['music2']
            music2 = Utils().music_list.get(music2_id, random_music2) # 如果找不到对应曲目，就用随机曲
            
            text = music2['Name']
            text, font_size = self._get_adaptive_font_size(text, "SEGA_MaruGothic-DB", 582, 56, initial_size=30, min_size=20)
            self.canvas.create_text(
                canvas_width // 2 + 400,
                834,
                text=text,
                font=("SEGA_MaruGothic-DB", font_size),
                fill="black",
                anchor=tk.CENTER
            )

            text = music2['Composer']
            text, font_size = self._get_adaptive_font_size(text, "SEGA_MaruGothic-DB", 582, 56, initial_size=16, min_size=12)
            self.canvas.create_text(
                canvas_width // 2 + 400,
                878,
                text=text,
                font=("SEGA_MaruGothic-DB", font_size),
                fill="black",
                anchor=tk.CENTER
            )

            jacket2_path = music2['Jacket']
            tk_jacket2 = self._load_image(jacket2_path, jacket_width*jacket_time, jacket_height*jacket_time)
            if tk_jacket2:
                # 右侧曲绘
                self.canvas.create_image(
                    canvas_width // 2 + 400,
                    canvas_height // 2 - 44,
                    image=tk_jacket2,
                    anchor=tk.CENTER
                )
                self.image_references.append(tk_jacket2)

            #两侧的等级框
            level_image_path = "assets/picture/levels.dds"
            level_left = 4
            level_top = 378
            level_right = 79
            level_bottom = 462
            crop_region = (level_left, level_top, level_right, level_bottom)
            level_width = level_right - level_left
            level_height = level_bottom - level_top
            level_time = image_time
            tk_level = self._load_image(level_image_path, level_width*level_time, level_height*level_time, crop=crop_region)
            if tk_level:
                # 左侧等级框
                self.canvas.create_image(
                    canvas_width // 2 - 623,
                    canvas_height // 2 + 210,
                    image=tk_level,
                    anchor=tk.CENTER
                )
                self.image_references.append(tk_level)
                # 右侧等级框
                self.canvas.create_image(
                    canvas_width // 2 + 177,
                    canvas_height // 2 + 210,
                    image=tk_level,
                    anchor=tk.CENTER
                )
                self.image_references.append(tk_level)

            #两侧的等级字样
            level_number_path = level_image_path
            level_number_top = 519
            level_number_bottom = 554
            level_number_left = [
                12, 54, 92, 132, 171, 212, 252, 293, 331, 371
            ]
            level_number_right = [
                36, 69, 117, 157, 197, 237, 276, 316, 356, 540
            ]
            level_plus_top = 517
            level_plus_bottom = 530
            level_plus_left = 411
            level_plus_right = 424
            level_plus_width = self._scale(level_plus_right - level_plus_left, 'x')
            level_plus_height = self._scale(level_plus_bottom - level_plus_top, 'y')
            level_number_height = self._scale(level_number_bottom - level_number_top, 'y')
            level_number_time = level_time

            #左侧等级
            level1 = music1['Const']
            if level1 < 10:
                pass # 应该不会打小于10级的歌吧，我是懒狗不做了
            elif level1 <100:
                number1 = int(level1) // 10
                number2 = int(level1) % 10
                decimal = level1 - int(level1)
                crop_region = (level_number_left[number1], level_number_top, level_number_right[number1], level_number_bottom)
                level_number_width = level_number_right[number1] - level_number_left[number1]
                tk_level1_number1 = self._load_image(level_number_path, level_number_width*level_time, level_number_height*level_number_time, crop=crop_region)
                if tk_level1_number1:
                    # 十位数字
                    self.canvas.create_image(
                        canvas_width // 2 - 623 - 2 - 20,
                        canvas_height // 2 + 228,
                        image=tk_level1_number1,
                        anchor=tk.CENTER
                    )
                    self.image_references.append(tk_level1_number1)
                crop_region = (level_number_left[number2], level_number_top, level_number_right[number2], level_number_bottom)
                level_number_width = level_number_right[number2] - level_number_left[number2]
                tk_level1_number2 = self._load_image(level_number_path, level_number_width*level_time, level_number_height*level_number_time, crop=crop_region)
                if tk_level1_number2:
                    # 个位数字
                    self.canvas.create_image(
                        canvas_width // 2 - 623 - 2 + 20,
                        canvas_height // 2 + 228,
                        image=tk_level1_number2,
                        anchor=tk.CENTER
                    )
                    self.image_references.append(tk_level1_number2)
                if decimal >= 0.5:
                    crop_region = (level_plus_left, level_plus_top, level_plus_right, level_plus_bottom)
                    tk_level1_plus = self._load_image(level_number_path, level_plus_width*level_time, level_plus_height*level_number_time, crop=crop_region)
                    if tk_level1_plus:
                        # 加号
                        self.canvas.create_image(
                            canvas_width // 2 - 623 + 40,
                            canvas_height // 2 + 198,
                            image=tk_level1_plus,
                            anchor=tk.CENTER
                        )
                        self.image_references.append(tk_level1_plus)
            else:
                pass

            #右侧等级
            level2 = music2['Const']
            if level2 < 10:
                pass # 应该不会打小于10级的歌吧，我是懒狗不做了
            elif level2 <100:
                number1 = int(level2) // 10
                number2 = int(level2) % 10
                decimal = level2 - int(level2)
                crop_region = (level_number_left[number1], level_number_top, level_number_right[number1], level_number_bottom)
                level_number_width = level_number_right[number1] - level_number_left[number1]
                tk_level2_number1 = self._load_image(level_number_path, level_number_width*level_time, level_number_height*level_number_time, crop=crop_region)
                if tk_level2_number1:
                    # 十位数字
                    self.canvas.create_image(
                        canvas_width // 2 + 177 - 2 - 20,
                        canvas_height // 2 + 228,
                        image=tk_level2_number1,
                        anchor=tk.CENTER
                    )
                    self.image_references.append(tk_level2_number1)
                crop_region = (level_number_left[number2], level_number_top, level_number_right[number2], level_number_bottom)
                level_number_width = level_number_right[number2] - level_number_left[number2]
                tk_level2_number2 = self._load_image(level_number_path, level_number_width*level_time, level_number_height*level_number_time, crop=crop_region)
                if tk_level2_number2:
                    # 个位数字
                    self.canvas.create_image(
                        canvas_width // 2 + 177 - 2 + 20,
                        canvas_height // 2 + 228,
                        image=tk_level2_number2,
                        anchor=tk.CENTER
                    )
                    self.image_references.append(tk_level2_number2)
                if decimal >= 0.5:
                    crop_region = (level_plus_left, level_plus_top, level_plus_right, level_plus_bottom)
                    tk_level2_plus = self._load_image(level_number_path, level_plus_width*level_time, level_plus_height*level_number_time, crop=crop_region)
                    if tk_level2_plus:
                        # 加号
                        self.canvas.create_image(
                            canvas_width // 2 + 177 + 40,
                            canvas_height // 2 + 198,
                            image=tk_level2_plus,
                            anchor=tk.CENTER
                        )
                        self.image_references.append(tk_level2_plus)
            else:
                pass

    def _get_adaptive_font_size(self, text, family, max_width, max_height, initial_size, min_size): # 旧版本，大概率停用
        """计算自适应字体大小，确保文本不超过指定宽度和高度"""
        new_text = text
        size = initial_size
        f = font.Font(family=family, size=size)
        while (f.measure(text) > max_width or f.metrics("linespace") > max_height) and size > min_size:
            size -= 1
            f.config(size=size)
        if (f.measure(text) > max_width or f.metrics("linespace") > max_height):
            tmp_text = new_text
            while (f.measure(tmp_text) > max_width or f.metrics("linespace") > max_height):
                new_text = new_text[:-1]
                tmp_text = new_text + '...'
            new_text = new_text + '...'
        return new_text, size
    
    def get_adaptive_font_size(self, text, font_path, max_width, max_height, initial_size, min_size): # 新版，用这个
        """计算自适应字体大小，确保文本不超过指定宽度和高度"""
        size = int(initial_size * self.scale_x)
        min_size = int(min_size * self.scale_x)
        if font_path == Utils().resource_path("assets/fonts/SEGA_MARUGOTHICDB.ttf"):
            font = self.preloaded_fonts.get(size, None)
        if not font:
            font = ImageFont.truetype(font_path, size)
        while (font.getlength(text) > max_width or font.getmetrics()[0] + font.getmetrics()[1] > max_height) and size > min_size:
            size -= 1
            font = self.preloaded_fonts.get(size, None)
            if not font:
                font = ImageFont.truetype(font_path, size)
        if (font.getlength(text) > max_width or font.getmetrics()[0] + font.getmetrics()[1] > max_height):
            tmp_text = text
            while (font.getlength(tmp_text) > max_width or font.getmetrics()[0] + font.getmetrics()[1] > max_height):
                text = text[:-1]
                tmp_text = text + '...'
            text = text + '...'
        return text, size

    def _load_image(self, path, width, height, crop=None, alpha=1.0): # 好像没啥用，感觉可以删了
        """加载并调整图片大小，返回Tkinter图片对象，支持裁剪和透明度"""
        try:
            pil_image = Image.open(path)
            if crop:
                pil_image = pil_image.crop(crop)
            
            if width > 1 and height > 1:
                # 计算缩放比例
                img_width, img_height = pil_image.size
                ratio = min(width / img_width, height / img_height)
                new_size = (int(img_width * ratio), int(img_height * ratio))
                
                if new_size[0] > 0 and new_size[1] > 0:
                    pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
            
            if alpha < 1.0:
                pil_image = pil_image.convert('RGBA')
                alpha_img = Image.new('L', pil_image.size, int(alpha * 255))
                pil_image.putalpha(alpha_img)
            
            return ImageTk.PhotoImage(pil_image)
        except Exception:
            return None
        
    def _create_faded_image(self, pil_img, alpha):
        """创建带透明度的PIL图像"""
        if pil_img.mode != 'RGBA':
            pil_img = pil_img.convert('RGBA')
        
        # 复制图像
        img_copy = pil_img.copy()
        
        # 分离并修改alpha通道
        r, g, b, a = img_copy.split()
        a = a.point(lambda p: int(p * alpha))
        
        # 返回新的PIL图像
        return Image.merge('RGBA', (r, g, b, a))
        
    def overlay_image(self, base_image_path, img_overlay_list, text_overlay_list, target_size=None, output_img=False):
        """
        使用PIL直接叠加图片
        
        Args:
            base_image_path: 底图路径
            img_overlay_list: 覆盖图信息列表，每个元素为字典:
                {
                    'path': '图片路径',
                    'position': (x, y),      # 可选，默认(0,0)
                    'size': (w, h),          # 可选，覆盖图大小
                    'crop': (l,t,r,b),       # 可选，裁剪
                    'alpha': 0.5,            # 可选，透明度
                    'anchor': 'center'       # 可选，锚点位置
                }
            text_overlay_list: 文字覆盖列表
            [
                {
                    'text': '文字内容',
                    'position': (x, y),
                    'font_size': 24,
                    'color': (0, 0, 0),  # RGB颜色: 黑色
                    'alpha': 1.0
                },
                ...
            ]
            output_path: 输出路径（可选）
            target_size: 目标尺寸 (width, height)
        
        Returns:
            ImageTk.PhotoImage 对象
        """
        try:
            # 加载底图
            base_img = None
            if self.preloaded.get(base_image_path):
                base_img = self.preloaded[base_image_path].copy()
            else:
                base_img = Image.open(base_image_path).convert('RGBA')
            
            # 调整底图大小
            if target_size:
                base_img = base_img.resize(target_size, Image.Resampling.LANCZOS)
            
            final_img = base_img.copy()
            
            composite_layer = Image.new('RGBA', final_img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(composite_layer)

            for overlay_info in img_overlay_list:
                path = overlay_info.get('path')
                if not path:
                    continue
                    
                # 加载覆盖图（考虑缓存）
                overlay_img = None
                if self.preloaded.get(path):
                    overlay_img = self.preloaded[path].copy()
                else:
                    overlay_img = Image.open(path).convert('RGBA')
                
                # 裁剪
                if crop := overlay_info.get('crop'):
                    overlay_img = overlay_img.crop(crop)
                
                # 调整大小
                if size := overlay_info.get('size'):
                    overlay_img = overlay_img.resize(size, Image.Resampling.LANCZOS)
                
                # 透明度处理 - 优化这个部分
                alpha = overlay_info.get('alpha', 1.0)
                if alpha < 1.0:
                    # 方法1: 使用split和point（比putdata快10倍以上）
                    r, g, b, a = overlay_img.split()
                    a = a.point(lambda p: int(p * alpha))
                    overlay_img = Image.merge('RGBA', (r, g, b, a))
                    mask = a
                else:
                    mask = overlay_img
                
                # 计算位置
                x, y = position = overlay_info.get('position', (0, 0))
                overlay_width, overlay_height = overlay_img.size
                
                # 锚点调整
                anchor = overlay_info.get('anchor', 'center')
                if anchor == 'center':
                    x -= overlay_width // 2
                    y -= overlay_height // 2
                elif anchor == 'lm':
                    y -= overlay_height // 2
                elif anchor == 'rb':
                    x -= overlay_width
                    y -= overlay_height
                elif anchor == 'rt':
                    x -= overlay_width
                elif anchor == 'lb':
                    y -= overlay_height
                
                # 边界检查（优化边界计算）
                x = max(0, min(x, composite_layer.width - overlay_width))
                y = max(0, min(y, composite_layer.height - overlay_height))
                
                # 直接粘贴到合成层
                composite_layer.paste(overlay_img, (x, y), mask)

            # 所有图层处理完后，一次性合成
            final_img = Image.alpha_composite(final_img, composite_layer)

            # 处理文字覆盖
            for text_info in text_overlay_list:
                text = text_info.get('text', '')
                position = text_info.get('position', (0, 0))
                font_size = text_info.get('font_size', 24)
                color = text_info.get('color', (0, 0, 0))
                alpha = text_info.get('alpha', 1.0)
                # 加载字体
                if text_info.get('font_path'):
                    font_path = text_info.get('font_path')
                    if font_path == Utils().resource_path("assets/fonts/Helvetica Bold.ttf") and font_size == 24:
                        font = self.preloaded_BPM_font
                    else:
                        font = ImageFont.truetype(font_path, font_size)
                else:
                    font = self.preloaded_fonts.get(font_size, ImageFont.load_default())
                
                if not text:
                    continue
               
                # 计算带透明度的颜色
                if alpha < 1.0:
                    # 转换为RGBA颜色
                    color = color + (int(255 * alpha),)
                else:
                    color = color + (255,)

                anchor = text_info.get('anchor', 'mm')
                
                # 绘制文字
                draw = ImageDraw.Draw(final_img)
                draw.text(position, text, font=font, fill=color, anchor=anchor)
            
            # 转换为Tkinter图片
            if output_img:
                return ImageTk.PhotoImage(final_img),final_img
            else:
                return ImageTk.PhotoImage(final_img)
            
        except Exception as e:
            print(f"图片叠加失败: {e}")
            return None
            
    def _display_background(self, bg_img):
        """显示背景图片"""
        tk_bg = self.preloaded.get(bg_img)
        if tk_bg:
            self.canvas.create_image(0, 0, image=tk_bg, anchor=tk.NW)
            self.image_references.append(tk_bg)
                
    def _show_error(self, message):
        """显示错误信息"""
        self.canvas.delete("all")
        self.canvas.create_text(
            self.canvas.winfo_width() // 2,
            self.canvas.winfo_height() // 2,
            text=message,
            fill="white",
            font=("Arial", 20),
            anchor=tk.CENTER
        )
    
    def receive_command(self, command, data):
        """接收控制器命令并分发处理"""
        handlers = {
            "DISPLAY_SELECTION": self.display_selection,
            "RANDOM_MUSIC": self.random_music
        }
        
        handler = handlers.get(command)
        if handler:
            try:
                if command == "RANDOM_MUSIC":
                    self.current_process = CurrentProcess.RANDOM_MUSIC
                elif command == "DISPLAY_SELECTION":
                    if data is None:
                        self.current_process = CurrentProcess.NONE
                    else:
                        self.current_process = CurrentProcess.DISPLAY_SELECTION
                handler(data)
            except Exception as e:
                self._show_error(f"命令处理错误 ({command}): {str(e)}")
        else:
            self._show_error(f"未知命令: {command}")
        
    def on_closing(self):
        """关闭窗口时的处理"""
        self.root.destroy()
        
    def close(self):
        """关闭窗口"""
        self.root.destroy()