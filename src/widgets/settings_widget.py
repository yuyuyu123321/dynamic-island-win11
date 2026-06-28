#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置窗口 - 自定义灵动岛尺寸和样式
"""
import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QSpinBox,
    QPushButton, QGroupBox, QDialog, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class SettingsDialog(QDialog):
    """设置对话框"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config or {}
        self.island_config = self.config.get('island', {})
        self.setWindowTitle('灵动岛设置')
        self.setFixedSize(420, 540)
        self.setStyleSheet('''
            QDialog {
                background-color: #1e1e1e;
            }
            QGroupBox {
                color: #e0e0e0;
                font-weight: bold;
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #cccccc;
                font-size: 12px;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #333;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                margin: -5px 0;
                background: #4CAF50;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #66BB6A;
            }
            QSlider::sub-page:horizontal {
                background: #4CAF50;
                border-radius: 3px;
            }
            QSpinBox {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px;
                min-width: 60px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        ''')
        self.init_ui()
        self.load_values()
        
    def init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # 标题
        title = QLabel('⚙ 灵动岛自定义设置', self)
        title.setStyleSheet('color: white; font-size: 16px; font-weight: bold;')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 宽度设置组
        width_group = QGroupBox('宽度设置 (像素)', self)
        width_layout = QVBoxLayout(width_group)
        width_layout.setSpacing(10)
        
        self.width_sliders = {}
        width_items = [
            ('width_collapsed', '收缩状态宽度', 80, 300),
            ('width_expanded', '展开状态宽度', 200, 600),
            ('width_media', '媒体状态宽度', 250, 700),
            ('width_volume', '音量状态宽度', 180, 500),
            ('width_notification', '通知状态宽度', 200, 600),
        ]
        for key, label, min_val, max_val in width_items:
            self.width_sliders[key] = self.create_slider_row(width_layout, label, min_val, max_val)
        
        layout.addWidget(width_group)
        
        # 高度设置组
        height_group = QGroupBox('高度设置 (像素)', self)
        height_layout = QVBoxLayout(height_group)
        height_layout.setSpacing(10)
        
        self.height_sliders = {}
        height_items = [
            ('height_collapsed', '收缩状态高度', 24, 60),
            ('height_expanded', '展开状态高度', 50, 120),
            ('height_media', '媒体状态高度', 80, 180),
            ('height_volume', '音量状态高度', 50, 120),
            ('height_notification', '通知状态高度', 60, 150),
        ]
        for key, label, min_val, max_val in height_items:
            self.height_sliders[key] = self.create_slider_row(height_layout, label, min_val, max_val)
        
        layout.addWidget(height_group)
        
        # 动画与外观组
        anim_group = QGroupBox('动画与外观', self)
        anim_layout = QVBoxLayout(anim_group)
        anim_layout.setSpacing(10)
        
        self.anim_sliders = {}
        anim_items = [
            ('animation_duration', '动画时长 (ms)', 50, 800),
            ('auto_hide_delay', '自动隐藏延迟 (ms)', 1000, 8000),
            ('background_opacity', '背景透明度 (0-255)', 100, 255),
            ('border_radius', '圆角大小 (px)', 8, 40),
        ]
        for key, label, min_val, max_val in anim_items:
            self.anim_sliders[key] = self.create_slider_row(anim_layout, label, min_val, max_val)
        
        layout.addWidget(anim_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.preview_btn = QPushButton('👁 实时预览', self)
        self.preview_btn.clicked.connect(self.on_preview)
        btn_layout.addWidget(self.preview_btn)
        
        self.save_btn = QPushButton('💾 保存并应用', self)
        self.save_btn.clicked.connect(self.on_save)
        btn_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton('↺ 恢复默认', self)
        self.reset_btn.setStyleSheet('''
            QPushButton {
                background-color: #555;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        ''')
        self.reset_btn.clicked.connect(self.on_reset)
        btn_layout.addWidget(self.reset_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
    def create_slider_row(self, parent_layout, label_text, min_val, max_val):
        """创建滑块行"""
        row = QHBoxLayout()
        row.setSpacing(10)
        
        label = QLabel(label_text, self)
        label.setFixedWidth(130)
        row.addWidget(label)
        
        slider = QSlider(Qt.Orientation.Horizontal, self)
        slider.setRange(min_val, max_val)
        slider.setCursor(Qt.CursorShape.PointingHandCursor)
        row.addWidget(slider, 1)
        
        spinbox = QSpinBox(self)
        spinbox.setRange(min_val, max_val)
        spinbox.setFixedWidth(60)
        row.addWidget(spinbox)
        
        # 同步滑块和数值框
        slider.valueChanged.connect(spinbox.setValue)
        spinbox.valueChanged.connect(slider.setValue)
        
        parent_layout.addLayout(row)
        return {'slider': slider, 'spinbox': spinbox}
        
    def load_values(self):
        """加载当前配置值"""
        # 宽度
        for key, widgets in self.width_sliders.items():
            value = self.island_config.get(key, widgets['slider'].minimum())
            widgets['slider'].setValue(value)
            
        # 高度
        for key, widgets in self.height_sliders.items():
            value = self.island_config.get(key, widgets['slider'].minimum())
            widgets['slider'].setValue(value)
            
        # 动画与外观
        for key, widgets in self.anim_sliders.items():
            value = self.island_config.get(key, widgets['slider'].minimum())
            widgets['slider'].setValue(value)
            
    def get_settings(self):
        """获取当前设置值"""
        settings = {}
        
        for key, widgets in self.width_sliders.items():
            settings[key] = widgets['slider'].value()
            
        for key, widgets in self.height_sliders.items():
            settings[key] = widgets['slider'].value()
            
        for key, widgets in self.anim_sliders.items():
            settings[key] = widgets['slider'].value()
            
        return settings
        
    def on_preview(self):
        """实时预览"""
        settings = self.get_settings()
        self.settings_changed.emit(settings)
        
    def on_save(self):
        """保存并应用"""
        settings = self.get_settings()
        
        # 更新配置
        self.config['island'] = settings
        
        # 保存到文件 - 项目根目录的 config.json
        # settings_widget.py 在 src/widgets/，需要回到根目录
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_path = os.path.join(root_dir, 'config.json')
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f'保存配置失败: {e}')
            
        self.settings_changed.emit(settings)
        self.accept()
        
    def on_reset(self):
        """恢复默认"""
        defaults = {
            'width_collapsed': 170,
            'height_collapsed': 36,
            'width_expanded': 400,
            'height_expanded': 75,
            'width_media': 420,
            'height_media': 115,
            'width_volume': 320,
            'height_volume': 75,
            'width_notification': 400,
            'height_notification': 100,
            'animation_duration': 200,
            'auto_hide_delay': 3500,
            'background_opacity': 210,
            'border_radius': 18,
        }
        
        for key, value in defaults.items():
            if key in self.width_sliders:
                self.width_sliders[key]['slider'].setValue(value)
            elif key in self.height_sliders:
                self.height_sliders[key]['slider'].setValue(value)
            elif key in self.anim_sliders:
                self.anim_sliders[key]['slider'].setValue(value)
