from controller import Controller
from gui_window import GUIWindow
from display_window import DisplayWindow
from utils import Utils
from size_selector import select_window_size

def main():
    # 显示窗口大小选择对话框
    window_size = select_window_size()
    
    # 如果用户取消选择，使用默认大小
    if window_size is None:
        window_size = (1920, 1080)
    
    # 创建控制器实例，传入音乐列表
    controller = Controller()
    
    # 创建GUI控制窗口
    gui_window = GUIWindow(controller)
    
    # 创建显示窗口，传入选择的大小
    display_window = DisplayWindow(controller, window_size)
    
    # 设置控制器的窗口引用
    controller.set_gui_window(gui_window)
    controller.set_display_window(display_window)
    
    # 启动GUI主循环
    gui_window.root.mainloop()

if __name__ == "__main__":
    main()