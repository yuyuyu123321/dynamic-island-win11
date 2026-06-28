#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控工具 - 监听系统音量、媒体播放、通知等事件
"""
import time
import asyncio
from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class SystemMonitor(QObject):
    """系统监控器"""
    
    # 信号
    volume_changed = pyqtSignal(int)  # 音量百分比
    media_playing = pyqtSignal(dict)  # 媒体信息 {title, artist, album, is_playing}
    media_paused = pyqtSignal()  # 媒体暂停
    notification_received = pyqtSignal(str, str, object)  # 标题, 消息, 图标
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_monitoring = False
        self.last_volume = None
        self.last_media_info = None
        self.last_media_playing = False
        
        # winsdk 是否可用
        self.winsdk_available = False
        try:
            from winsdk.windows.media.control import (
                GlobalSystemMediaTransportControlsSessionManager as MediaManager
            )
            self.winsdk_available = True
        except ImportError:
            pass
        
        # 使用 QTimer 进行定时检查
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_system_state)
        self.timer.setInterval(1000)  # 1秒检查一次
        
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
        except Exception:
            pass
            
        try:
            if self.winsdk_available:
                self.check_media_winsdk()
            else:
                self.check_media_fallback()
        except Exception:
            pass
            
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
            
    def check_media_winsdk(self):
        """使用 Windows Media Control API 检测媒体播放（支持QQ音乐、网易云等）"""
        try:
            from winsdk.windows.media.control import (
                GlobalSystemMediaTransportControlsSessionManager as MediaManager
            )
            
            async def _get_media():
                manager = await MediaManager.request_async()
                sessions = manager.get_sessions()
                
                if not sessions:
                    # 没有媒体会话，如果之前有播放则暂停
                    if self.last_media_playing:
                        self.last_media_playing = False
                        self.last_media_info = None
                        self.media_paused.emit()
                    return
                
                # 获取第一个活跃会话
                session = sessions[0]
                
                # 获取媒体属性
                try:
                    media_props = await session.try_get_media_properties_async()
                    playback_info = session.get_playback_info()
                    
                    title = media_props.title if media_props and media_props.title else '未知歌曲'
                    artist = media_props.artist if media_props and media_props.artist else '未知艺人'
                    album = media_props.album_title if media_props and media_props.album_title else ''
                    
                    # 播放状态: 4 = Playing, 5 = Paused
                    playback_status = playback_info.playback_status
                    is_playing = playback_status == 4
                    
                    # 构建媒体信息
                    info = {
                        'title': title,
                        'artist': artist,
                        'album': album,
                        'is_playing': is_playing
                    }
                    
                    # 检测状态变化
                    if is_playing and (self.last_media_info != info or not self.last_media_playing):
                        self.last_media_info = info
                        self.last_media_playing = True
                        self.media_playing.emit(info)
                    elif not is_playing and self.last_media_playing:
                        self.last_media_playing = False
                        self.media_paused.emit()
                        
                except Exception:
                    pass
            
            # 运行异步获取
            asyncio.run(_get_media())
            
        except Exception:
            self.check_media_fallback()
            
    def check_media_fallback(self):
        """后备方案：通过 pycaw 检测音频会话"""
        try:
            from pycaw.pycaw import AudioUtilities
            sessions = AudioUtilities.GetAllSessions()
            
            found_media = False
            for session in sessions:
                if not session.Process:
                    continue
                    
                process_name = session.Process.name()
                # 检测常见媒体播放器（包括QQ音乐、网易云等）
                media_apps = [
                    'qqmusic.exe', 'cloudmusic.exe',  # QQ音乐、网易云音乐
                    'spotify.exe', 'musicbee.exe', 'foobar2000.exe',
                    'chrome.exe', 'msedge.exe', 'firefox.exe',
                    'qq.exe', 'wechat.exe',  # QQ、微信也可能播放语音
                ]
                
                if process_name.lower() in media_apps:
                    found_media = True
                    info = {
                        'title': '正在播放',
                        'artist': process_name.replace('.exe', ''),
                        'album': '',
                        'is_playing': True
                    }
                    
                    # 避免重复发送
                    if self.last_media_info != info or not self.last_media_playing:
                        self.last_media_info = info
                        self.last_media_playing = True
                        self.media_playing.emit(info)
                    break
                    
            # 没有媒体播放
            if not found_media and self.last_media_playing:
                self.last_media_playing = False
                self.last_media_info = None
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
            import win32api
            import win32con
            # VK_MEDIA_PLAY_PAUSE = 0xB3
            win32api.keybd_event(0xB3, 0, 0, 0)
            win32api.keybd_event(0xB3, 0, win32con.KEYEVENTF_KEYUP, 0)
        except Exception:
            pass
            
    def media_next(self):
        """下一首"""
        try:
            import win32api
            import win32con
            # VK_MEDIA_NEXT_TRACK = 0xB0
            win32api.keybd_event(0xB0, 0, 0, 0)
            win32api.keybd_event(0xB0, 0, win32con.KEYEVENTF_KEYUP, 0)
        except Exception:
            pass
            
    def media_previous(self):
        """上一首"""
        try:
            import win32api
            import win32con
            # VK_MEDIA_PREV_TRACK = 0xB1
            win32api.keybd_event(0xB1, 0, 0, 0)
            win32api.keybd_event(0xB1, 0, win32con.KEYEVENTF_KEYUP, 0)
        except Exception:
            pass
