#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
媒体播放组件 - 显示当前播放的音乐信息
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QColor


class MediaWidget(QWidget):
    """媒体播放控件"""
    
    # 信号
    play_pause_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    prev_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化 UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(12)
        
        # 专辑封面
        self.album_art = QLabel(self)
        self.album_art.setFixedSize(48, 48)
        self.album_art.setStyleSheet('''
            QLabel {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 8px;
            }
        ''')
        self.album_art.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.album_art.setText('🎵')
        font = self.album_art.font()
        font.setPointSize(16)
        self.album_art.setFont(font)
        layout.addWidget(self.album_art)
        
        # 歌曲信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        self.title_label = QLabel('未在播放', self)
        self.title_label.setStyleSheet('''
            QLabel {
                color: white;
                font-size: 13px;
                font-weight: bold;
                background-color: transparent;
            }
        ''')
        self.title_label.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        info_layout.addWidget(self.title_label)
        
        self.artist_label = QLabel('-', self)
        self.artist_label.setStyleSheet('''
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 11px;
                background-color: transparent;
            }
        ''')
        self.artist_label.setFont(QFont('Segoe UI', 9))
        info_layout.addWidget(self.artist_label)
        
        layout.addLayout(info_layout, 1)
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.prev_btn = self.create_control_btn('⏮')
        self.prev_btn.clicked.connect(self.prev_clicked.emit)
        btn_layout.addWidget(self.prev_btn)
        
        self.play_btn = self.create_control_btn('▶')
        self.play_btn.clicked.connect(self.play_pause_clicked.emit)
        btn_layout.addWidget(self.play_btn)
        
        self.next_btn = self.create_control_btn('⏭')
        self.next_btn.clicked.connect(self.next_clicked.emit)
        btn_layout.addWidget(self.next_btn)
        
        layout.addLayout(btn_layout)
        
        # 进度条（简化版）
        self.progress_label = QLabel('', self)
        self.progress_label.setStyleSheet('''
            QLabel {
                color: rgba(255, 255, 255, 0.5);
                font-size: 10px;
                background-color: transparent;
            }
        ''')
        self.progress_label.setFont(QFont('Segoe UI', 8))
        layout.addWidget(self.progress_label)
        
    def create_control_btn(self, text):
        """创建控制按钮"""
        btn = QPushButton(text, self)
        btn.setFixedSize(28, 28)
        btn.setStyleSheet('''
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.1);
            }
        ''')
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn
        
    def update_media_info(self, info):
        """更新媒体信息"""
        title = info.get('title', '未知歌曲')
        artist = info.get('artist', '未知艺人')
        is_playing = info.get('is_playing', False)
        album_art = info.get('album_art', None)
        
        self.title_label.setText(self.truncate_text(title, 25))
        self.artist_label.setText(self.truncate_text(artist, 30))
        
        # 更新播放按钮图标
        self.play_btn.setText('⏸' if is_playing else '▶')
        
        # 更新专辑封面
        if album_art and os.path.exists(album_art):
            pixmap = QPixmap(album_art)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                self.album_art.setPixmap(pixmap)
        else:
            self.album_art.setText('🎵')
            
        # 更新进度
        position = info.get('position', 0)
        duration = info.get('duration', 0)
        if duration > 0:
            self.progress_label.setText(f'{self.format_time(position)}/{self.format_time(duration)}')
        else:
            self.progress_label.setText('')
            
    def truncate_text(self, text, max_length):
        """截断文本"""
        if len(text) > max_length:
            return text[:max_length - 2] + '...'
        return text
        
    def format_time(self, seconds):
        """格式化时间"""
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f'{minutes}:{secs:02d}'
        
    def reset(self):
        """重置状态"""
        self.title_label.setText('未在播放')
        self.artist_label.setText('-')
        self.play_btn.setText('▶')
        self.album_art.setText('🎵')
        self.progress_label.setText('')

import os