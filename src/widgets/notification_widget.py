#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知组件 - 显示系统通知消息
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont


class NotificationWidget(QWidget):
    """通知控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化 UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)
        
        # 应用图标
        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(36, 36)
        self.icon_label.setStyleSheet('''
            QLabel {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                color: white;
                font-size: 16px;
            }
        ''')
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setText('📢')
        layout.addWidget(self.icon_label)
        
        # 文本内容
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        self.title_label = QLabel('通知', self)
        self.title_label.setStyleSheet('''
            QLabel {
                color: white;
                font-size: 13px;
                font-weight: bold;
                background-color: transparent;
            }
        ''')
        self.title_label.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        text_layout.addWidget(self.title_label)
        
        self.message_label = QLabel('', self)
        self.message_label.setStyleSheet('''
            QLabel {
                color: rgba(255, 255, 255, 0.85);
                font-size: 12px;
                background-color: transparent;
            }
        ''')
        self.message_label.setFont(QFont('Segoe UI', 9))
        self.message_label.setWordWrap(True)
        text_layout.addWidget(self.message_label)
        
        layout.addLayout(text_layout, 1)
        
        # 清除按钮
        self.clear_label = QLabel('✕', self)
        self.clear_label.setFixedSize(20, 20)
        self.clear_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clear_label.setStyleSheet('''
            QLabel {
                color: rgba(255, 255, 255, 0.5);
                font-size: 12px;
                background-color: transparent;
                border-radius: 10px;
            }
            QLabel:hover {
                color: white;
                background-color: rgba(255, 255, 255, 0.15);
            }
        ''')
        self.clear_label.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.clear_label)
        
    def show_notification(self, title, message, icon=None):
        """显示通知"""
        self.title_label.setText(title)
        self.message_label.setText(message)
        
        if icon:
            self.icon_label.setText(icon)
        else:
            self.icon_label.setText('📢')
            
    def set_app_icon(self, icon_path):
        """设置应用图标"""
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)
        else:
            self.icon_label.setText('📢')
