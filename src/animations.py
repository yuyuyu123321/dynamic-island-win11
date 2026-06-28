#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动画系统 - 负责灵动岛的各种平滑动画
"""
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QSize, QPoint, Qt


class IslandAnimator:
    """灵动岛动画器"""
    
    def __init__(self, widget, duration=300):
        self.widget = widget
        self.duration = duration
        
        # 尺寸动画
        self.size_animation = QPropertyAnimation(widget, b'size')
        self.size_animation.setDuration(duration)
        self.size_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # 位置动画
        self.pos_animation = QPropertyAnimation(widget, b'pos')
        self.pos_animation.setDuration(duration)
        self.pos_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
    def animate_size(self, target_size, callback=None):
        """动画改变尺寸"""
        self.size_animation.stop()
        self.size_animation.setStartValue(self.widget.size())
        self.size_animation.setEndValue(target_size)
        
        if callback:
            self.size_animation.finished.connect(callback)
            
        self.size_animation.start()
        
    def animate_position(self, target_pos, callback=None):
        """动画改变位置"""
        self.pos_animation.stop()
        self.pos_animation.setStartValue(self.widget.pos())
        self.pos_animation.setEndValue(target_pos)
        
        if callback:
            self.pos_animation.finished.connect(callback)
            
        self.pos_animation.start()
        
    def animate_size_and_position(self, target_size, target_pos, callback=None):
        """同时动画改变尺寸和位置"""
        self.animate_size(target_size)
        self.animate_position(target_pos, callback)
        
    def bounce_animation(self):
        """弹跳动画 - 用于通知提醒"""
        original_pos = self.widget.pos()
        
        def bounce_up():
            self.pos_animation.setStartValue(original_pos)
            self.pos_animation.setEndValue(QPoint(original_pos.x(), original_pos.y() - 10))
            self.pos_animation.finished.connect(bounce_down)
            self.pos_animation.start()
            
        def bounce_down():
            self.pos_animation.finished.disconnect(bounce_down)
            self.pos_animation.setStartValue(QPoint(original_pos.x(), original_pos.y() - 10))
            self.pos_animation.setEndValue(original_pos)
            self.pos_animation.start()
            
        bounce_up()
        
    def pulse_animation(self):
        """脉冲动画 - 用于强调"""
        original_size = self.widget.size()
        target_size = QSize(
            int(original_size.width() * 1.05),
            int(original_size.height() * 1.05)
        )
        
        def pulse_in():
            self.size_animation.setStartValue(original_size)
            self.size_animation.setEndValue(target_size)
            self.size_animation.finished.connect(pulse_out)
            self.size_animation.start()
            
        def pulse_out():
            self.size_animation.finished.disconnect(pulse_out)
            self.size_animation.setStartValue(target_size)
            self.size_animation.setEndValue(original_size)
            self.size_animation.start()
            
        pulse_in()
