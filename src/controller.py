import threading
from queue import Queue

class Controller:
    """控制器：管理GUI和显示窗口之间的通信"""
    def __init__(self):
        # 消息队列（线程安全）
        self.command_queue = Queue()
        
        # 窗口引用
        self.gui_window = None
        self.display_window = None
        
        # 当前状态
        self.is_playing = False
        
    def set_gui_window(self, gui_window):
        """设置GUI窗口引用"""
        self.gui_window = gui_window
        
    def set_display_window(self, display_window):
        """设置显示窗口引用"""
        self.display_window = display_window
        
    def display_selection(self):
        """显示选曲界面"""
        if self.gui_window:
            data = {
                'team1': self.gui_window.entry_1p_team.get() or "1P队伍", # 如果team1对应的字符串为空，就改为“1P队伍”
                'player1': self.gui_window.entry_1p_player.get() or "1P玩家",
                'music1': self.gui_window.entry_1p_song.get() or "music1",
                'team2': self.gui_window.entry_2p_team.get() or "2P队伍",
                'player2': self.gui_window.entry_2p_player.get() or "2P玩家",
                'music2': self.gui_window.entry_2p_song.get() or "music2",
                'process': self.gui_window.entry_process1.get() or "先锋战"
            }
            self._send_command("DISPLAY_SELECTION", data)
        
    def clear_screen(self):
        """清空屏幕，显示背景"""
        self._send_command("DISPLAY_SELECTION", {})

    def random_music(self):
        data = {
            'library': self.gui_window.entry_library.get() or '全曲库',
            'min_const': self.gui_window.entry_random_const_min.get() or '0.0',
            'max_const': self.gui_window.entry_random_const_max.get() or '16.0',
        }
        self._send_command("RANDOM_MUSIC", data)

    def show_round_result(self):
        """显示回合结果"""
        data = {
            'music_number': self.gui_window.entry_music_number.get() or '2',
            'team1': self.gui_window.result_entry_1p_team.get() or "1P队伍",
            'player1': self.gui_window.result_entry_1p_player.get() or "1P玩家",
            'team2': self.gui_window.result_entry_2p_team.get() or "2P队伍",
            'player2': self.gui_window.result_entry_2p_player.get() or "2P玩家",
            'track1_music': self.gui_window.track1_music.get() or "music1",
            'track1_1p_score': self.gui_window.track1_1p_score.get() or "0",
            'track1_2p_score': self.gui_window.track1_2p_score.get() or "0",
            'track2_music': self.gui_window.track2_music.get() or "music2",
            'track2_1p_score': self.gui_window.track2_1p_score.get() or "0",
            'track2_2p_score': self.gui_window.track2_2p_score.get() or "0",
            'track3_music': self.gui_window.track3_music.get() or "music3",
            'track3_1p_score': self.gui_window.track3_1p_score.get() or "0",
            'track3_2p_score': self.gui_window.track3_2p_score.get() or "0",
            'process': self.gui_window.entry_process2.get() or "先锋战"
        }
        self._send_command("SHOW_ROUND_RESULT", data)

    def show_team_score(self):
        """显示团队积分"""
        self._send_command("SHOW_TEAM_SCORE")

    def update_display(self, image_path):
        """更新显示窗口"""
        if self.display_window:
            # 在线程中更新显示，避免阻塞GUI
            thread = threading.Thread(
                target=self.display_window.display_image,
                args=(image_path,)
            )
            thread.daemon = True
            thread.start()
            
    def _send_command(self, command, data=None):
        """发送命令到显示窗口"""
        if self.display_window:
            self.display_window.receive_command(command, data)
            
    def close_all(self):
        """关闭所有窗口"""
        if self.display_window:
            self.display_window.close()
        if self.gui_window:
            self.gui_window.close()