#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时钟组件 - 显示当前时间
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QFont


class ClockWidget(QWidget):
    """时钟控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.start_timer()
        
    def init_ui(self):
        """初始化 UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 时间显示
        self.time_label = QLabel(self)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet('''
            QLabel {
                color: white;
                font-size: 15px;
                font-weight: bold;
                background-color: transparent;
                letter-spacing: 1px;
            }
        ''')
        time_font = QFont('Segoe UI', 12, QFont.Weight.Bold)
        self.time_label.setFont(time_font)
        layout.addWidget(self.time_label)
        
        # 日期显示
        self.date_label = QLabel(self)
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet('''
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 11px;
                background-color: transparent;
            }
        ''')
        self.date_label.setFont(QFont('Segoe UI', 9))
        layout.addWidget(self.date_label)
        
        # 状态指示器
        self.status_label = QLabel(self)
        self.status_label.setFixedSize(8, 8)
        self.status_label.setStyleSheet('''
            QLabel {
                background-color: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
            }
        ''')
        layout.addWidget(self.status_label)
        
        self.update_time()
        
    def start_timer(self):
        """启动定时器"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 每秒更新
        
    def update_time(self):
        """更新时间显示"""
        current = QTime.currentTime()
        time_str = current.toString('HH:mm')
        self.time_label.setText(time_str)
        
        from PyQt6.QtCore import QDate
        date = QDate.currentDate()
        date_str = date.toString('MM月dd日')
        weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date.dayOfWeek() - 1]
        self.date_label.setText(f'{date_str} {weekday}')
        
    def set_status(self, active=True):
        """设置状态指示"""
        if active:
            self.status_label.setStyleSheet('''
                QLabel {
                    background-color: #4CAF50;
                    border-radius: 4px;
                }
            ''')
        else:
            self.status_label.setStyleSheet('''
                QLabel {
                    background-color: rgba(255, 255, 255, 0.3);
                    border-radius: 4px;
                }
            ''')
