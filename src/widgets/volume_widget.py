#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音量控制组件 - 显示和控制系统音量
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSlider
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class VolumeWidget(QWidget):
    """音量控制控件"""
    
    volume_changed = pyqtSignal(int)  # 0-100
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_volume = 50
        self.is_muted = False
        self.init_ui()
        
    def init_ui(self):
        """初始化 UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # 音量图标
        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet('''
            QLabel {
                color: white;
                font-size: 14px;
                background-color: transparent;
            }
        ''')
        self.update_icon()
        layout.addWidget(self.icon_label)
        
        # 滑块
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(0, 100)
        self.slider.setValue(self.current_volume)
        self.slider.setStyleSheet('''
            QSlider::groove:horizontal {
                height: 4px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                width: 14px;
                height: 14px;
                margin: -5px 0;
                background: white;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #e0e0e0;
            }
            QSlider::sub-page:horizontal {
                background: white;
                border-radius: 2px;
            }
        ''')
        self.slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.slider, 1)
        
        # 音量百分比
        self.percent_label = QLabel(f'{self.current_volume}%', self)
        self.percent_label.setFixedWidth(40)
        self.percent_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.percent_label.setStyleSheet('''
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
                background-color: transparent;
            }
        ''')
        self.percent_label.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        layout.addWidget(self.percent_label)
        
    def update_icon(self):
        """更新音量图标"""
        if self.is_muted:
            self.icon_label.setText('🔇')
        elif self.current_volume == 0:
            self.icon_label.setText('🔈')
        elif self.current_volume < 50:
            self.icon_label.setText('🔉')
        else:
            self.icon_label.setText('🔊')
            
    def update_volume(self, volume):
        """更新音量显示"""
        self.current_volume = max(0, min(100, volume))
        self.slider.blockSignals(True)
        self.slider.setValue(self.current_volume)
        self.slider.blockSignals(False)
        self.percent_label.setText(f'{self.current_volume}%')
        self.update_icon()
        
    def set_muted(self, muted):
        """设置静音状态"""
        self.is_muted = muted
        self.update_icon()
        
    def on_slider_changed(self, value):
        """滑块值变化"""
        self.current_volume = value
        self.percent_label.setText(f'{value}%')
        self.update_icon()
        self.volume_changed.emit(value)
