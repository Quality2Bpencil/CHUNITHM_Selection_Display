import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from utils import Utils
import pandas as pd
import os

class GUIWindow:
    """GUI控制窗口"""
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("控制面板")
        self.root.geometry("680x800")
        
        # 防止重复打开
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建Canvas和Scrollbar用于滚动
        canvas = tk.Canvas(self.root, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 主框架放在Canvas中
        main_frame = ttk.Frame(canvas, padding="20")
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        # 更新Canvas滚动区域
        def on_frame_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_canvas_configure(event=None):
            # 设置Canvas窗口宽度与Canvas相同，避免水平滚动条
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())
        
        main_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            try:
                # 获取当前焦点的控件
                focus_widget = self.root.focus_get()
                
                # 如果焦点在 Combobox 上，不处理滚轮（让 Combobox 处理其下拉列表的滚动）
                if isinstance(focus_widget, ttk.Combobox):
                    return
            except KeyError:
                # Combobox 下拉列表的 'popdown' 窗口会导致 KeyError，此时不处理滚轮
                return
            
            # 检查内容是否超出 Canvas 范围，只有超出时才处理滚轮
            scroll_region = canvas.cget("scrollregion").split()
            if scroll_region:
                content_height = float(scroll_region[3]) - float(scroll_region[1])
                canvas_height = canvas.winfo_height()
                
                # 只有当内容高度大于 Canvas 高度时，才处理滚轮
                if content_height > canvas_height:
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # 绑定点击事件，点击空白处失焦
        def _on_click(event):
            # 获取点击位置的控件
            widget = event.widget
            # 如果点击的是 Canvas 或 main_frame，则失焦
            if widget == canvas or widget == main_frame:
                self.root.focus_set()
        
        # 只在main_frame范围内绑定，使用bind_all让所有子widget都能触发
        self.root.bind_all("<MouseWheel>", _on_mousewheel)
        self.root.bind_all("<Button-1>", _on_click)
        
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

        # 第一行：清空屏幕按钮（居中）
        row1_frame = ttk.Frame(control_frame)
        row1_frame.pack(pady=10)

        self.btn_clear = ttk.Button(
            row1_frame,
            text="清空屏幕",
            command=self.clear_screen,
            width=20
        )
        self.btn_clear.pack()

        # 第二行：显示选曲与随机歌曲
        row2_frame = ttk.Frame(control_frame)
        row2_frame.pack(pady=10)

        self.btn_show_selection = ttk.Button(
            row2_frame,
            text="显示选曲",
            command=self.display_selection,
            width=20
        )
        self.btn_show_selection.pack(side=tk.LEFT, padx=5)

        self.btn_random_music = ttk.Button(
            row2_frame,
            text="随机歌曲",
            command=self.random_music,
            width=20
        )
        self.btn_random_music.pack(side=tk.LEFT, padx=5)

        # 第三行：小局结果与团队积分
        row3_frame = ttk.Frame(control_frame)
        row3_frame.pack(pady=10)

        self.btn_round_result = ttk.Button(
            row3_frame,
            text="显示小局结果",
            command=self.show_round_result,  # 需要添加这个方法
            width=20
        )
        self.btn_round_result.pack(side=tk.LEFT, padx=5)

        self.btn_team_score = ttk.Button(
            row3_frame,
            text="显示团队积分",
            command=self.show_team_score,  # 需要添加这个方法
            width=20
        )
        self.btn_team_score.pack(side=tk.LEFT, padx=5)
        
        # 文本输入区域
        input_frame = ttk.LabelFrame(main_frame, text="指定选曲", padding="15")
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

        # 1P选曲
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

        # 随机选曲区域
        random_frame = ttk.LabelFrame(main_frame, text="随机选曲", padding="15")
        random_frame.pack(fill=tk.X, pady=(0, 20))

        # 随机曲
        random_const_frame = ttk.Frame(random_frame)
        random_const_frame.pack(fill=tk.X, pady=(0, 20))
        # 随机曲曲库
        tk.Label(random_const_frame, text="随机曲曲库: ").pack(side=tk.LEFT)
        entry_library = ttk.Combobox(random_const_frame,
                                    values=["全曲库"] + list(Utils().users_music_list.keys()),
                                    state="readonly",  # 只读，不能输入
                                    width=20)
        entry_library.pack(side=tk.LEFT, padx=(0, 50))
        entry_library.set("全曲库")
        # 随机曲定数范围
        ttk.Label(random_const_frame, text="随机曲定数范围: ").pack(side=tk.LEFT)
        self.entry_random_const_min = ttk.Entry(random_const_frame, width=10)
        self.entry_random_const_min.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(random_const_frame, text="~").pack(side=tk.LEFT)
        self.entry_random_const_max = ttk.Entry(random_const_frame, width=10)
        self.entry_random_const_max.pack(side=tk.LEFT, padx=(10, 10))

        # 导入Excel曲库按钮
        self.btn1 = ttk.Button(
            random_frame,
            text="导入Excel曲库",
            command=self.import_excel,
            width=20
        )
        self.btn1.pack(side=tk.LEFT, padx=(90,0))
        
        # 导入TXT曲库按钮
        self.btn2 = ttk.Button(
            random_frame,
            text="导入TXT曲库",
            command=self.import_txt,
            width=20
        )
        self.btn2.pack(side=tk.LEFT, padx=(100,0))

        #小局结果区域
        result_frame = ttk.LabelFrame(main_frame, text="小局结果显示", padding="15")
        result_frame.pack(fill=tk.X, pady=(0, 20))

        # 曲数
        music_number_frame = ttk.Frame(result_frame)
        music_number_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(music_number_frame, text="曲数: ").pack(side=tk.LEFT)
        self.music_number = ttk.Combobox(music_number_frame,
                                        values=["2", "3"],
                                        state="readonly",  # 只读，不能输入
                                        width=20)
        self.music_number.pack(side=tk.LEFT, padx=(5, 10))
        self.music_number.set("2")

        # 1P队伍和队员名
        result_frame_1p = ttk.Frame(result_frame)
        result_frame_1p.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(result_frame_1p, text="1P队伍名: ").pack(side=tk.LEFT)
        self.result_entry_1p_team = ttk.Entry(result_frame_1p, width=30)
        self.result_entry_1p_team.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(result_frame_1p, text="1P队员名: ").pack(side=tk.LEFT)
        self.result_entry_1p_player = ttk.Entry(result_frame_1p, width=30)
        self.result_entry_1p_player.pack(side=tk.LEFT)

        # 2P队伍和队员名
        result_frame_2p = ttk.Frame(result_frame)
        result_frame_2p.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(result_frame_2p, text="2P队伍名: ").pack(side=tk.LEFT)
        self.result_entry_2p_team = ttk.Entry(result_frame_2p, width=30)
        self.result_entry_2p_team.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(result_frame_2p, text="2P队员名: ").pack(side=tk.LEFT)
        self.result_entry_2p_player = ttk.Entry(result_frame_2p, width=30)
        self.result_entry_2p_player.pack(side=tk.LEFT)

        # Track1
        track1_frame = ttk.Frame(result_frame)
        track1_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(track1_frame, text="Track 1: ").pack(side=tk.LEFT)
        self.track1_music = ttk.Combobox(track1_frame, 
                                         values=Utils().searchable_music_list,
                                         state="normal",  # 可输入
                                         width=33)
        self.track1_music.pack(side=tk.LEFT, padx=(0, 10))
        self.track1_music.bind("<KeyRelease>", self.search_music)
        ttk.Label(track1_frame, text="1P分数: ").pack(side=tk.LEFT)
        self.track1_1p_score = ttk.Entry(track1_frame, width=10)
        self.track1_1p_score.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(track1_frame, text="2P分数: ").pack(side=tk.LEFT)
        self.track1_2p_score = ttk.Entry(track1_frame, width=10)
        self.track1_2p_score.pack(side=tk.LEFT, padx=(0, 10))

        # Track2
        track2_frame = ttk.Frame(result_frame)
        track2_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(track2_frame, text="Track 2: ").pack(side=tk.LEFT)
        self.track2_music = ttk.Combobox(track2_frame, 
                                         values=Utils().searchable_music_list,
                                         state="normal",  # 可输入
                                         width=33)
        self.track2_music.pack(side=tk.LEFT, padx=(0, 10))
        self.track2_music.bind("<KeyRelease>", self.search_music)
        ttk.Label(track2_frame, text="1P分数: ").pack(side=tk.LEFT)
        self.track2_1p_score = ttk.Entry(track2_frame, width=10)
        self.track2_1p_score.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(track2_frame, text="2P分数: ").pack(side=tk.LEFT)
        self.track2_2p_score = ttk.Entry(track2_frame, width=10)
        self.track2_2p_score.pack(side=tk.LEFT, padx=(0, 10))

        # Track3
        track3_frame = ttk.Frame(result_frame)
        track3_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(track3_frame, text="Track 3: ").pack(side=tk.LEFT)
        self.track3_music = ttk.Combobox(track3_frame, 
                                         values=Utils().searchable_music_list,
                                         state="normal",  # 可输入
                                         width=33)
        self.track3_music.pack(side=tk.LEFT, padx=(0, 10))
        self.track3_music.bind("<KeyRelease>", self.search_music)
        ttk.Label(track3_frame, text="1P分数: ").pack(side=tk.LEFT)
        self.track3_1p_score = ttk.Entry(track3_frame, width=10)
        self.track3_1p_score.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(track3_frame, text="2P分数: ").pack(side=tk.LEFT)
        self.track3_2p_score = ttk.Entry(track3_frame, width=10)
        self.track3_2p_score.pack(side=tk.LEFT, padx=(0, 10))

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
        
    def display_selection(self):
        """显示选曲界面"""
        self.controller.display_selection()

    def random_music(self):
        """随机选曲"""
        self.controller.random_music()
        
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

    def show_round_result(self):
        pass

    def show_team_score(self):
        pass

    def import_excel(self):
        """导入Excel文件"""
        file_path = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                filename = os.path.splitext(os.path.basename(file_path))[0]
                df = pd.read_excel(file_path, header=None)
                id_list = []
                util = Utils()
                for i in range(len(df)):
                    for j in range (len(df.columns)):
                        content = str(df.iloc[i, j]).strip()
                        for key, value in util.music_list.items():
                            if content == key or content == value['Name']:
                                id_list.append(key)
                id_list = list(dict.fromkeys(id_list))
                if id_list == []:
                    messagebox.showerror("导入失败", "你的Excel文档里找不到曲目")
                    return
                music_list = {music_id: util.music_list[music_id] for music_id in id_list}
                util.add_music_list(filename, music_list)
                self.entry_library['values']=["全曲库"] + list(Utils().users_music_list.keys())
                messagebox.showinfo("导入成功", f"你成功导入了名为“{filename}”的曲库")
                
            except Exception as e:
                messagebox.showerror("导入错误", f"导入Excel文件失败:\n{str(e)}")
    
    def import_txt(self):
        """导入TXT文件"""
        file_path = filedialog.askopenfilename(
            title="选择TXT文件",
            filetypes=[("Excel文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                id_list = []
                util = Utils()
                filename = os.path.splitext(os.path.basename(file_path))[0]
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    for line in lines:
                        content = line.strip()
                        for key, value in util.music_list.items():
                            if content == key or content == value['Name']:
                                id_list.append(key)
                id_list = list(dict.fromkeys(id_list))
                if id_list == []:
                    messagebox.showerror("导入失败", "你的TXT文档里找不到曲目")
                    return
                music_list = {music_id: util.music_list[music_id] for music_id in id_list}
                util.add_music_list(filename, music_list)
                self.entry_library['values']=["全曲库"] + list(Utils().users_music_list.keys())
                messagebox.showinfo("导入成功", f"你成功导入了名为“{filename}”的曲库")
                
            except Exception as e:
                messagebox.showerror("导入错误", f"导入TXT文件失败:\n{str(e)}")
        
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