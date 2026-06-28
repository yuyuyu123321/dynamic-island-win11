#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
媒体监听器 - 使用 Windows Runtime API 监听媒体播放状态
"""
import threading
from PyQt6.QtCore import QObject, pyqtSignal


class MediaListener(QObject):
    """媒体监听器"""
    
    media_changed = pyqtSignal(dict)
    playback_state_changed = pyqtSignal(bool)  # True=playing, False=paused
    
    def __init__(self):
        super().__init__()
        self.is_listening = False
        self.current_info = {}
        self.listener_thread = None
        
    def start_listening(self):
        """开始监听媒体事件"""
        self.is_listening = True
        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener_thread.start()
        
    def stop_listening(self):
        """停止监听"""
        self.is_listening = False
        
    def _listen_loop(self):
        """监听循环"""
        try:
            # 尝试使用 winsdk / Windows Runtime API
            from winsdk.windows.media.control import (
                GlobalSystemMediaTransportControlsSessionManager as MediaManager
            )
            
            async def get_media_info():
                manager = await MediaManager.request_async()
                sessions = manager.get_sessions()
                
                for session in sessions:
                    info = await session.try_get_media_properties_async()
                    playback = session.get_playback_info()
                    
                    title = info.title if info else '未知'
                    artist = info.artist if info else '未知'
                    album = info.album_title if info else ''
                    
                    is_playing = playback.playback_status == 4  # 4 = Playing
                    
                    media_info = {
                        'title': title,
                        'artist': artist,
                        'album': album,
                        'is_playing': is_playing,
                        'album_art': None
                    }
                    
                    self.media_changed.emit(media_info)
                    self.playback_state_changed.emit(is_playing)
                    
            import asyncio
            while self.is_listening:
                try:
                    asyncio.run(get_media_info())
                except Exception:
                    pass
                import time
                time.sleep(2)
                
        except ImportError:
            # 回退方案：使用简单的进程检测
            self._fallback_listen()
            
    def _fallback_listen(self):
        """回退监听方案"""
        import psutil
        media_processes = ['spotify.exe', 'musicbee.exe', 'foobar2000.exe']
        
        while self.is_listening:
            found = False
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and proc.info['name'].lower() in media_processes:
                    found = True
                    info = {
                        'title': '正在播放',
                        'artist': proc.info['name'],
                        'album': '',
                        'is_playing': True,
                        'album_art': None
                    }
                    self.media_changed.emit(info)
                    self.playback_state_changed.emit(True)
                    break
                    
            if not found:
                self.playback_state_changed.emit(False)
                
            import time
            time.sleep(3)
