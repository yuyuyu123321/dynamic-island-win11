#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控工具 - 监听系统音量、媒体播放、通知等事件
"""
import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class SystemMonitor(QObject):
    """系统监控器"""
    
    # 信号
    volume_changed = pyqtSignal(int)  # 音量百分比
    media_playing = pyqtSignal(dict)  # 媒体信息
    media_paused = pyqtSignal()  # 媒体暂停
    notification_received = pyqtSignal(str, str, object)  # 标题, 消息, 图标
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_monitoring = False
        self.monitor_thread = None
        self.last_volume = None
        self.last_media_state = None
        
        # 使用 QTimer 进行主线程的定时检查
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_system_state)
        self.timer.setInterval(500)  # 500ms 检查一次
        
    def start_monitoring(self):
        """开始监控"""
        self.is_monitoring = True
        self.timer.start()
        
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        self.timer.stop()
        
    def check_system_state(self):
        """检查系统状态"""
        if not self.is_monitoring:
            return
            
        try:
            self.check_volume()
            self.check_media()
        except Exception:
            pass  # 忽略错误，避免崩溃
            
    def check_volume(self):
        """检查音量变化"""
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            current_vol = int(volume.GetMasterVolumeLevelScalar() * 100)
            
            if self.last_volume != current_vol:
                self.last_volume = current_vol
                self.volume_changed.emit(current_vol)
        except Exception:
            pass
            
    def check_media(self):
        """检查媒体播放状态"""
        # 这里使用 Windows Media Control API 或简单的检查
        # 简化版本：使用 winsdk 或 pycaw 的会话
        try:
            from pycaw.pycaw import AudioUtilities
            sessions = AudioUtilities.GetAllSessions()
            
            for session in sessions:
                if session.Process:
                    process_name = session.Process.name()
                    # 检测常见媒体播放器
                    media_apps = ['spotify.exe', 'musicbee.exe', 'foobar2000.exe', 
                                  'chrome.exe', 'msedge.exe', 'firefox.exe']
                    if process_name.lower() in media_apps:
                        # 尝试获取媒体信息
                        info = {
                            'title': '正在播放',
                            'artist': process_name,
                            'is_playing': True
                        }
                        
                        state_changed = self.last_media_state != process_name
                        self.last_media_state = process_name
                        
                        if state_changed:
                            self.media_playing.emit(info)
                        return
                        
            # 没有媒体播放
            if self.last_media_state is not None:
                self.last_media_state = None
                self.media_paused.emit()
                
        except Exception:
            pass
            
    def set_volume(self, value):
        """设置音量"""
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            volume.SetMasterVolumeLevelScalar(value / 100.0, None)
        except Exception:
            pass
            
    def media_play_pause(self):
        """播放/暂停"""
        try:
            import pywinauto
            # 发送媒体键
            # 简化实现
        except Exception:
            pass
            
    def media_next(self):
        """下一首"""
        try:
            import pywinauto
        except Exception:
            pass
            
    def media_previous(self):
        """上一首"""
        try:
            import pywinauto
        except Exception:
            pass
            
    def simulate_media_key(self, key_code):
        """模拟媒体按键"""
        try:
            import win32api
            import win32con
            win32api.keybd_event(key_code, 0, 0, 0)
            win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        except Exception:
            pass
