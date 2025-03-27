import ctypes
from ctypes import wintypes
import win32con
import win32api
import win32gui
import comtypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Windows 媒体按键的虚拟键码
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1

# 定义 INPUT 结构体
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]

class _INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("ki", KEYBDINPUT),
        ("mi", MOUSEINPUT),
        ("hi", HARDWAREINPUT),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("_input", _INPUT_UNION),
    ]

class PlayerController:
    def __init__(self):
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        
    def _send_media_key(self, vk_code):
        """发送媒体按键事件"""
        # 创建输入数组
        inputs = (INPUT * 2)()
        
        # 按键按下事件
        inputs[0].type = win32con.INPUT_KEYBOARD
        inputs[0]._input.ki.wVk = vk_code
        inputs[0]._input.ki.wScan = 0
        inputs[0]._input.ki.dwFlags = 0
        inputs[0]._input.ki.time = 0
        inputs[0]._input.ki.dwExtraInfo = None
        
        # 按键释放事件
        inputs[1].type = win32con.INPUT_KEYBOARD
        inputs[1]._input.ki.wVk = vk_code
        inputs[1]._input.ki.wScan = 0
        inputs[1]._input.ki.dwFlags = win32con.KEYEVENTF_KEYUP
        inputs[1]._input.ki.time = 0
        inputs[1]._input.ki.dwExtraInfo = None
        
        # 发送按键事件
        nInputs = len(inputs)
        cbSize = ctypes.sizeof(INPUT)
        result = self.user32.SendInput(nInputs, ctypes.pointer(inputs[0]), cbSize)
        if result != nInputs:
            error = ctypes.get_last_error()
            raise RuntimeError(f"SendInput failed with error code {error}")
        
    def get_playing_state(self):
        """获取当前是否正在播放音乐"""
        try:
            # 获取所有音频会话
            sessions = AudioUtilities.GetAllSessions()
            
            # 遍历所有会话
            for session in sessions:
                # 检查会话是否有效
                if session.Process and session.Process.name():
                    # 获取会话状态
                    state = session.State
                    process_name = session.Process.name().lower()
                    print(f"Session: {process_name}, State: {state}")  # 调试输出
                    
                    # 检查是否是常见的音乐播放器
                    if any(name in process_name for name in ['music', 'player', 'netease', 'qqmusic', 'spotify']):
                        # 如果会话正在播放，返回True
                        if state == 1:  # 1 表示正在播放
                            return True
                        elif state == 2:  # 2 表示暂停
                            return False
                    
            return False
            
        except Exception as e:
            print(f"获取播放状态失败: {e}")
            return False
        
    def play_pause(self):
        """播放/暂停"""
        try:
            self._send_media_key(VK_MEDIA_PLAY_PAUSE)
        except Exception as e:
            print(f"播放/暂停失败: {e}")
        
    def next_track(self):
        """下一曲"""
        try:
            self._send_media_key(VK_MEDIA_NEXT_TRACK)
        except Exception as e:
            print(f"下一曲失败: {e}")
        
    def previous_track(self):
        """上一曲"""
        try:
            self._send_media_key(VK_MEDIA_PREV_TRACK)
        except Exception as e:
            print(f"上一曲失败: {e}") 