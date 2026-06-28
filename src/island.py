#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dynamic Island 主窗口 - 核心 UI 逻辑
"""
import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSlider, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QPoint
from PyQt6.QtGui import QColor, QIcon, QAction, QPainter, QBrush

from animations import IslandAnimator
from widgets.media_widget import MediaWidget
from widgets.volume_widget import VolumeWidget
from widgets.notification_widget import NotificationWidget
from widgets.clock_widget import ClockWidget
from widgets.settings_widget import SettingsDialog
from utils.system_monitor import SystemMonitor


class DynamicIsland(QWidget):
    """动态岛主窗口"""
    
    # 信号定义
    state_changed = pyqtSignal(str)  # collapsed, expanded, media, volume, notification
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.island_config = self.config.get('island', {})
        self.features = self.config.get('features', {})
        
        # 当前状态
        self.current_state = 'collapsed'
        self.previous_state = 'collapsed'
        self.is_dragging = False
        self.drag_position = QPoint()
        self.is_media_playing = False  # 媒体是否正在播放
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.timeout.connect(self._on_auto_hide_timeout)
        self.auto_hide_timer.setSingleShot(True)
        
        # 尺寸配置
        self.collapsed_size = QSize(
            self.island_config.get('width_collapsed', 170),
            self.island_config.get('height_collapsed', 36)
        )
        self.expanded_size = QSize(
            self.island_config.get('width_expanded', 400),
            self.island_config.get('height_expanded', 75)
        )
        self.media_size = QSize(
            self.island_config.get('width_media', 420),
            self.island_config.get('height_media', 115)
        )
        self.volume_size = QSize(
            self.island_config.get('width_volume', 320),
            self.island_config.get('height_volume', 75)
        )
        self.notification_size = QSize(
            self.island_config.get('width_notification', 400),
            self.island_config.get('height_notification', 100)
        )
        
        self.animation_duration = self.island_config.get('animation_duration', 200)
        self.auto_hide_delay = self.island_config.get('auto_hide_delay', 3500)
        self.bg_opacity = self.island_config.get('background_opacity', 210)
        self.border_radius = self.island_config.get('border_radius', 18)
        self.glow_effect = self.island_config.get('glow_effect', True)
        
        self.init_ui()
        self.init_widgets()
        self.init_system_tray()
        self.init_animator()
        self.init_position()
        self.init_system_monitor()
        
    def init_ui(self):
        """初始化 UI"""
        # 窗口属性设置
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 设置固定大小（初始为收缩状态）
        self.setFixedSize(self.collapsed_size)
        
        # 主布局 - 直接放在窗口上，内边距就是背景圆角的内边距
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(12, 6, 12, 6)
        self.main_layout.setSpacing(0)
        
        # 鼠标跟踪
        self.setMouseTracking(True)
        
    def init_widgets(self):
        """初始化各个功能组件"""
        self.stacked_widgets = {}
        
        # 内容容器 - 透明背景，不设置样式表背景
        self.content_widget = QWidget(self)
        self.content_widget.setStyleSheet('background: transparent;')
        
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        self.main_layout.addWidget(self.content_widget)
        
        # 时钟组件（默认显示）
        if self.features.get('clock', True):
            self.clock_widget = ClockWidget(self.content_widget)
            self.stacked_widgets['clock'] = self.clock_widget
            self.content_layout.addWidget(self.clock_widget)
        
        # 媒体组件
        if self.features.get('media', True):
            self.media_widget = MediaWidget(self.content_widget)
            self.media_widget.play_pause_clicked.connect(self.on_media_play_pause)
            self.media_widget.next_clicked.connect(self.on_media_next)
            self.media_widget.prev_clicked.connect(self.on_media_prev)
            self.stacked_widgets['media'] = self.media_widget
            self.content_layout.addWidget(self.media_widget)
            self.media_widget.hide()
        
        # 音量组件
        if self.features.get('volume', True):
            self.volume_widget = VolumeWidget(self.content_widget)
            self.volume_widget.volume_changed.connect(self.on_volume_changed)
            self.stacked_widgets['volume'] = self.volume_widget
            self.content_layout.addWidget(self.volume_widget)
            self.volume_widget.hide()
        
        # 通知组件
        if self.features.get('notifications', True):
            self.notification_widget = NotificationWidget(self.content_widget)
            self.stacked_widgets['notification'] = self.notification_widget
            self.content_layout.addWidget(self.notification_widget)
            self.notification_widget.hide()
        
        # 默认显示时钟
        self.active_widget = 'clock'
        
    def init_system_tray(self):
        """初始化系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip('Windows 11 Dynamic Island')
        
        # 创建简单图标（使用系统图标）
        self.tray_icon.setIcon(QIcon.fromTheme('applications-system'))
        
        # 托盘菜单
        tray_menu = QMenu()
        
        show_action = QAction('显示', self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction('隐藏', self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        settings_action = QAction('⚙ 设置', self)
        settings_action.triggered.connect(self.open_settings)
        tray_menu.addAction(settings_action)
        
        quit_action = QAction('退出', self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
        
    def init_animator(self):
        """初始化动画器"""
        self.animator = IslandAnimator(self, self.animation_duration)
        
    def init_position(self):
        """初始化窗口位置"""
        screen = QApplication.primaryScreen().geometry()
        position = self.island_config.get('position', 'top-center')
        
        if position == 'top-center':
            x = (screen.width() - self.width()) // 2
            y = 8
        elif position == 'top-left':
            x = 20
            y = 8
        elif position == 'top-right':
            x = screen.width() - self.width() - 20
            y = 8
        else:
            x = (screen.width() - self.width()) // 2
            y = 8
            
        self.move(x, y)
        self.original_position = QPoint(x, y)
        
    def init_system_monitor(self):
        """初始化系统监控"""
        self.system_monitor = SystemMonitor(self)
        self.system_monitor.volume_changed.connect(self.on_system_volume_changed)
        self.system_monitor.media_playing.connect(self.on_system_media_playing)
        self.system_monitor.media_paused.connect(self.on_system_media_paused)
        self.system_monitor.notification_received.connect(self.on_system_notification)
        self.system_monitor.start_monitoring()
        
    def paintEvent(self, event):
        """绘制事件 - 绘制圆角背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        
        bg_color = QColor(0, 0, 0)
        bg_color.setAlpha(self.bg_opacity)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(self.rect(), self.border_radius, self.border_radius)
        
        painter.end()
        
    # === 状态切换 ===
    
    def expand_to(self, state, widget_name=None):
        """展开到指定状态"""
        if self.current_state == state and (widget_name is None or self.active_widget == widget_name):
            return
            
        self.previous_state = self.current_state
        self.current_state = state
        
        # 获取目标尺寸
        if state == 'collapsed':
            target_size = self.collapsed_size
        elif state == 'expanded':
            target_size = self.expanded_size
        elif state == 'media':
            target_size = self.media_size
        elif state == 'volume':
            target_size = self.volume_size
        elif state == 'notification':
            target_size = self.notification_size
        else:
            target_size = self.expanded_size
        
        # 切换显示的组件
        if widget_name and widget_name in self.stacked_widgets:
            self.switch_widget(widget_name)
        
        # 执行动画
        self.animator.animate_size(target_size)
        self.state_changed.emit(state)
        
        # 设置自动隐藏定时器
        if state != 'collapsed' and state != 'media':
            self.auto_hide_timer.start(self.auto_hide_delay)
        elif state == 'media':
            # 媒体播放时重置 auto_hide，但使用更长的延迟
            self.auto_hide_timer.start(self.auto_hide_delay * 2)
            
    def _on_auto_hide_timeout(self):
        """自动隐藏定时器到期"""
        # 如果媒体正在播放，不要收缩，而是保持 media 状态
        if self.is_media_playing:
            # 媒体仍在播放，重新展开到 media（重置定时器）
            self.expand_to('media', 'media')
        else:
            self.collapse()

    def collapse(self):
        """收缩回默认状态"""
        self.expand_to('collapsed', 'clock')
        
    def switch_widget(self, widget_name):
        """切换显示的组件"""
        if self.active_widget == widget_name:
            return
            
        # 隐藏当前组件
        if self.active_widget in self.stacked_widgets:
            self.stacked_widgets[self.active_widget].hide()
        
        # 显示新组件
        if widget_name in self.stacked_widgets:
            self.stacked_widgets[widget_name].show()
            self.active_widget = widget_name
            
    # === 事件处理 ===
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_dragging and (event.buttons() & Qt.MouseButton.LeftButton):
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.snap_to_edge()
            event.accept()
            
    def enterEvent(self, event):
        """鼠标进入事件"""
        # 悬停时稍微展开
        if self.current_state == 'collapsed':
            self.expand_to('expanded', 'clock')
        event.accept()
        
    def leaveEvent(self, event):
        """鼠标离开事件"""
        # 如果处于展开状态且不在拖拽中，启动自动隐藏
        if self.current_state != 'collapsed' and not self.is_dragging:
            self.auto_hide_timer.start(self.auto_hide_delay)
        event.accept()
        
    def snap_to_edge(self):
        """吸附到屏幕边缘"""
        screen = QApplication.primaryScreen().geometry()
        pos = self.pos()
        x = pos.x()
        y = pos.y()
        
        # 垂直方向吸附到顶部
        if y < screen.height() // 4:
            y = 8
        elif y > screen.height() * 3 // 4:
            y = screen.height() - self.height() - 8
        else:
            y = max(8, min(y, screen.height() - self.height() - 8))
        
        # 水平方向吸附
        if x < screen.width() // 4:
            x = 8
        elif x > screen.width() * 3 // 4:
            x = screen.width() - self.width() - 8
        else:
            # 吸附到中心
            x = (screen.width() - self.width()) // 2
            
        self.animator.animate_position(QPoint(x, y))
        self.original_position = QPoint(x, y)
        
    def on_tray_activated(self, reason):
        """托盘图标激活"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            
    def quit_app(self):
        """退出应用"""
        self.system_monitor.stop_monitoring()
        self.tray_icon.hide()
        QApplication.quit()
        
    def open_settings(self):
        """打开设置窗口"""
        if hasattr(self, 'settings_dialog') and self.settings_dialog.isVisible():
            self.settings_dialog.raise_()
            self.settings_dialog.activateWindow()
            return
            
        self.settings_dialog = SettingsDialog(self.config, self)
        self.settings_dialog.settings_changed.connect(self.apply_settings)
        self.settings_dialog.show()
        
    def apply_settings(self, settings):
        """应用设置变更"""
        # 更新本地配置
        self.island_config.update(settings)
        
        # 重新计算尺寸
        self.collapsed_size = QSize(
            settings.get('width_collapsed', self.collapsed_size.width()),
            settings.get('height_collapsed', self.collapsed_size.height())
        )
        self.expanded_size = QSize(
            settings.get('width_expanded', self.expanded_size.width()),
            settings.get('height_expanded', self.expanded_size.height())
        )
        self.media_size = QSize(
            settings.get('width_media', self.media_size.width()),
            settings.get('height_media', self.media_size.height())
        )
        self.volume_size = QSize(
            settings.get('width_volume', self.volume_size.width()),
            settings.get('height_volume', self.volume_size.height())
        )
        self.notification_size = QSize(
            settings.get('width_notification', self.notification_size.width()),
            settings.get('height_notification', self.notification_size.height())
        )
        
        # 更新动画和外观
        self.animation_duration = settings.get('animation_duration', self.animation_duration)
        self.auto_hide_delay = settings.get('auto_hide_delay', self.auto_hide_delay)
        self.bg_opacity = settings.get('background_opacity', self.bg_opacity)
        self.border_radius = settings.get('border_radius', self.border_radius)
        
        # 更新动画器
        self.animator.duration = self.animation_duration
        self.animator.size_animation.setDuration(self.animation_duration)
        self.animator.pos_animation.setDuration(self.animation_duration)
        
        # 更新定时器
        self.auto_hide_timer.setInterval(self.auto_hide_delay)
        
        # 重绘
        self.update()
        
        # 如果当前处于收缩状态，直接调整大小
        if self.current_state == 'collapsed':
            self.setFixedSize(self.collapsed_size)
        elif self.current_state == 'expanded':
            self.setFixedSize(self.expanded_size)
        elif self.current_state == 'media':
            self.setFixedSize(self.media_size)
        elif self.current_state == 'volume':
            self.setFixedSize(self.volume_size)
        elif self.current_state == 'notification':
            self.setFixedSize(self.notification_size)
            
    # === 系统事件回调 ===
                
    def on_media_play_pause(self):
        """播放/暂停"""
        self.system_monitor.media_play_pause()
        
    def on_media_next(self):
        """下一首"""
        self.system_monitor.media_next()
        
    def on_media_prev(self):
        """上一首"""
        self.system_monitor.media_previous()
        
    def on_volume_changed(self, value):
        """音量变化"""
        self.system_monitor.set_volume(value)
        
    def on_system_volume_changed(self, value):
        """系统音量变化"""
        if self.volume_widget:
            self.volume_widget.update_volume(value)
            self.expand_to('volume', 'volume')
            
    def on_system_media_playing(self, info):
        """系统媒体播放"""
        self.is_media_playing = True
        if self.media_widget:
            self.media_widget.update_media_info(info)
            self.expand_to('media', 'media')
            
    def on_system_media_paused(self):
        """系统媒体暂停"""
        self.is_media_playing = False
        self.collapse()
        
    def on_system_notification(self, title, message, icon=None):
        """系统通知"""
        if self.notification_widget:
            self.notification_widget.show_notification(title, message, icon)
            self.expand_to('notification', 'notification')
            
    def show_notification(self, title, message, icon=None, duration=3000):
        """显示通知"""
        self.on_system_notification(title, message, icon)
        self.auto_hide_timer.start(duration)
