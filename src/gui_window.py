import tkinter as tk
from tkinter import ttk, messagebox
from utils import Utils
import os

class GUIWindow:
    """GUI控制窗口"""
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("控制面板")
        self.root.geometry("650x800")
        
        # 防止重复打开
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="选歌界面显示控制器",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # 控制按钮区域
        control_frame = ttk.LabelFrame(main_frame, text="播放控制", padding="15")
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 按钮1
        self.btn1 = ttk.Button(
            control_frame,
            text="清空屏幕",
            command=self.clear_screen,
            width=20
        )
        self.btn1.pack(pady=10)
        
        # 按钮2
        self.btn2 = ttk.Button(
            control_frame,
            text="显示选曲",
            command=self.display_selection,
            width=20
        )
        self.btn2.pack(pady=10)

        # 按钮3
        self.btn3 = ttk.Button(
            control_frame,
            text="随机歌曲",
            command=self.random_music,
            width=20
        )
        self.btn3.pack(pady=10)
        
        # 文本输入区域
        input_frame = ttk.LabelFrame(main_frame, text="文本输入", padding="15")
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 1P队伍和队员名
        frame_1p = ttk.Frame(input_frame)
        frame_1p.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(frame_1p, text="1P队伍名: ").pack(side=tk.LEFT)
        self.entry_1p_team = ttk.Entry(frame_1p, width=30)
        self.entry_1p_team.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(frame_1p, text="1P队员名: ").pack(side=tk.LEFT)
        self.entry_1p_player = ttk.Entry(frame_1p, width=30)
        self.entry_1p_player.pack(side=tk.LEFT)
        
        """
        # 1P选曲
        song_frame_1p = ttk.Frame(input_frame)
        song_frame_1p.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(song_frame_1p, text="1P选曲: ").pack(side=tk.LEFT)
        self.entry_1p_song = ttk.Entry(song_frame_1p, width=10)
        self.entry_1p_song.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_1p_song.bind("<KeyRelease>", self.update_1p_song)
        self.label_1p_song = ttk.Label(song_frame_1p, text="请输入曲目ID", font=("Arial", 10))
        self.label_1p_song.pack(side=tk.LEFT)
        """

        # 2P选曲
        song_frame_1p = ttk.Frame(input_frame)
        song_frame_1p.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(song_frame_1p, text="1P选曲: ").pack(side=tk.LEFT)
        self.entry_1p_song = ttk.Combobox(song_frame_1p, 
                                         values=Utils().searchable_music_list,
                                         state="normal",  # 可输入
                                         width=50)
        self.entry_1p_song.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_1p_song.bind("<KeyRelease>", self.search_music)
        
        # 2P队伍和队员名
        frame_2p = ttk.Frame(input_frame)
        frame_2p.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(frame_2p, text="2P队伍名: ").pack(side=tk.LEFT)
        self.entry_2p_team = ttk.Entry(frame_2p, width=30)
        self.entry_2p_team.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(frame_2p, text="2P队员名: ").pack(side=tk.LEFT)
        self.entry_2p_player = ttk.Entry(frame_2p, width=30)
        self.entry_2p_player.pack(side=tk.LEFT)
        
        """
        # 2P选曲
        song_frame_2p = ttk.Frame(input_frame)
        song_frame_2p.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(song_frame_2p, text="2P选曲: ").pack(side=tk.LEFT)
        self.entry_2p_song = ttk.Entry(song_frame_2p, width=10)
        self.entry_2p_song.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_2p_song.bind("<KeyRelease>", self.update_2p_song)
        self.label_2p_song = ttk.Label(song_frame_2p, text="请输入曲目ID", font=("Arial", 10))
        self.label_2p_song.pack(side=tk.LEFT)
        """

        # 2P选曲
        song_frame_2p = ttk.Frame(input_frame)
        song_frame_2p.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(song_frame_2p, text="2P选曲: ").pack(side=tk.LEFT)
        self.entry_2p_song = ttk.Combobox(song_frame_2p, 
                                         values=Utils().searchable_music_list,
                                         state="normal",  # 可输入
                                         width=50)
        self.entry_2p_song.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_2p_song.bind("<KeyRelease>", self.search_music)

        # 随机曲
        random_const_frame = ttk.Frame(input_frame)
        random_const_frame.pack(fill=tk.X, pady=(10, 10))
        # 随机曲曲库
        tk.Label(random_const_frame, text="随机曲曲库: ").pack(side=tk.LEFT)
        self.entry_library = ttk.Combobox(random_const_frame,
                                        values=["全曲库"],
                                        state="readonly",  # 只读，不能输入
                                        width=20)
        self.entry_library.pack(side=tk.LEFT, padx=(0, 50))
        self.entry_library.set("全曲库")
        # 随机曲定数范围
        ttk.Label(random_const_frame, text="随机曲定数范围: ").pack(side=tk.LEFT)
        self.entry_random_const_min = ttk.Entry(random_const_frame, width=10)
        self.entry_random_const_min.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(random_const_frame, text="~").pack(side=tk.LEFT)
        self.entry_random_const_max = ttk.Entry(random_const_frame, width=10)
        self.entry_random_const_max.pack(side=tk.LEFT, padx=(10, 10))

        # 状态显示区域
        status_frame = ttk.LabelFrame(main_frame, text="状态信息", padding="15")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_label = ttk.Label(
            status_frame,
            text="就绪\n等待指令...",
            justify=tk.LEFT
        )
        self.status_label.pack(anchor=tk.W)
        
        # 当前状态
        self.current_label = ttk.Label(
            status_frame,
            text="当前图片: 无",
            font=("Arial", 10)
        )
        self.current_label.pack(anchor=tk.W, pady=(10, 0))

    def search_music(self, event):
        """搜索功能"""
        combo = event.widget
        value = combo.get()
        #print(f"搜索内容: {value}")
        
        data = [None]
        if value == '':
            combo['values'] = Utils().searchable_music_list
        else:
            data = []
            for item in Utils().searchable_music_list:
                if value.lower() in item.lower():
                    data.append(item)
            
            combo['values'] = data

        current_index = combo.current()
        if current_index == -1 and data:
            if event.keysym == 'Return':
                combo.event_generate('<Down>')
        
    def clear_screen(self):
        """清空屏幕"""
        self.controller.clear_screen()
        self.update_status("屏幕已清空...")
        self.current_label.config(text="当前图片: 背景")
        
    def display_selection(self):
        """显示选曲界面"""
        self.controller.display_selection()
        self.update_status("正在显示选曲界面...")
        self.current_label.config(text="当前图片: 选曲界面")

    def random_music(self):
        """随机选曲"""
        self.controller.random_music()
        self.update_status("正在随机歌曲...")
        self.current_label.config(text="当前图片: 随机选曲界面")
        
    def update_1p_song(self, event=None):
        """实时更新1P选曲显示文本"""
        text = self.entry_1p_song.get()
        music = Utils().music_list.get(text, None)
        if text == "":
            self.label_1p_song.config(text="请输入曲目ID")
        elif music:
            self.label_1p_song.config(text=f"曲目: {music['Name']} (难度: {music['Const']})")
        else:
            self.label_1p_song.config(text="找不到对应曲目！")
    
    def update_2p_song(self, event=None):
        """实时更新2P选曲显示文本"""
        text = self.entry_2p_song.get()
        music = Utils().music_list.get(text, None)
        if text == "":
            self.label_2p_song.config(text="请输入曲目ID")
        elif music:
            self.label_2p_song.config(text=f"曲目: {music['Name']} (难度: {music['Const']})")
        else:
            self.label_2p_song.config(text="找不到对应曲目！")
        
    def update_status(self, message):
        """更新状态信息"""
        self.status_label.config(text=message)
        
    def on_closing(self):
        """关闭窗口时的处理"""
        #if messagebox.askokcancel("退出", "确定要退出程序吗？"):
        if True:
            self.controller.close_all()
            self.root.quit()
            
    def close(self):
        """关闭窗口"""
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        """运行GUI"""
        self.root.mainloop()