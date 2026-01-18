import tkinter as tk
from tkinter import ttk


class SizeSelectorDialog:
    """窗口大小选择对话框"""
    
    # 预定义的窗口大小
    SIZE_PRESETS = {
        "1920x1080": (1920, 1080),
        "1280x720": (1280, 720),
        "960x540": (960, 540),
        "1600x900": (1600, 900),
        "2560x1440": (2560, 1440),
    }
    
    def __init__(self, parent=None):
        self.parent = parent
        self.selected_size = None
        self.dialog = tk.Toplevel(parent) if parent else tk.Tk()
        self.dialog.title("选择显示窗口大小")
        self.dialog.geometry("400x480")
        self.dialog.resizable(False, False)
        
        # 如果有父窗口，设为模态
        if parent:
            self.dialog.transient(parent)
            self.dialog.grab_set()
        
        self.setup_ui()
        
        # 窗口居中显示
        self.center_window()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="请选择显示窗口大小",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # 预设大小选择框
        preset_frame = ttk.LabelFrame(main_frame, text="预设大小", padding="15")
        preset_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.size_var = tk.StringVar(value=list(self.SIZE_PRESETS.keys())[0])
        
        for size_name in self.SIZE_PRESETS.keys():
            radio = ttk.Radiobutton(
                preset_frame,
                text=size_name,
                variable=self.size_var,
                value=size_name
            )
            radio.pack(anchor=tk.W, pady=8)
        
        # 自定义大小输入框
        custom_frame = ttk.LabelFrame(main_frame, text="自定义大小", padding="15")
        custom_frame.pack(fill=tk.X, pady=(0, 15))
        
        input_frame = ttk.Frame(custom_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="宽度:").pack(side=tk.LEFT, padx=(0, 5))
        self.width_entry = ttk.Entry(input_frame, width=10)
        self.width_entry.pack(side=tk.LEFT, padx=(0, 15))
        self.width_entry.insert(0, "1920")
        
        ttk.Label(input_frame, text="高度:").pack(side=tk.LEFT, padx=(0, 5))
        self.height_entry = ttk.Entry(input_frame, width=10)
        self.height_entry.pack(side=tk.LEFT)
        self.height_entry.insert(0, "1080")
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 0))
        
        # 确定按钮
        ok_button = ttk.Button(
            button_frame,
            text="确定",
            command=self.on_ok,
            width=15
        )
        ok_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 取消按钮
        cancel_button = ttk.Button(
            button_frame,
            text="取消",
            command=self.on_cancel,
            width=15
        )
        cancel_button.pack(side=tk.LEFT)
        
    def center_window(self):
        """将窗口居中显示"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_ok(self):
        """确定按钮回调"""
        try:
            # 检查是否选择了预设或使用自定义
            if self.size_var.get():
                # 使用预设大小
                self.selected_size = self.SIZE_PRESETS[self.size_var.get()]
            else:
                # 使用自定义大小
                width = int(self.width_entry.get())
                height = int(self.height_entry.get())
                
                if width <= 0 or height <= 0:
                    raise ValueError("宽度和高度必须为正数")
                
                if width / height != 16 / 9:
                    raise ValueError("宽高比必须为16:9")
                
                self.selected_size = (width, height)
            
            self.dialog.destroy()
        except ValueError as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("输入错误", f"请输入有效的数值:\n{e}")
    
    def on_cancel(self):
        """取消按钮回调"""
        self.selected_size = None
        self.dialog.destroy()
    
    def show(self):
        """显示对话框并返回选择的大小"""
        self.dialog.wait_window()
        return self.selected_size


def select_window_size(parent=None):
    """便利函数：显示大小选择对话框"""
    dialog = SizeSelectorDialog(parent)
    return dialog.show()
