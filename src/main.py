#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dynamic Island for Windows 11 - 入口文件
"""
import sys
import os
import json
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase

# 添加 src 到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from island import DynamicIsland


def load_config(config_path):
    """加载配置文件"""
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def main():
    """主函数"""
    # 启用高 DPI 支持（PyQt6 中部分属性已废弃，使用 try/except）
    try:
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    except (AttributeError, TypeError):
        pass
    try:
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    except (AttributeError, TypeError):
        pass

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # 设置全局字体
    available_fonts = QFontDatabase.families()
    
    # 优先使用系统字体
    preferred_fonts = ['Segoe UI', 'Microsoft YaHei', 'PingFang SC', 'Noto Sans SC']
    for font_name in preferred_fonts:
        if font_name in available_fonts:
            from PyQt6.QtGui import QFont
            app.setFont(QFont(font_name, 10))
            break

    # 确定项目根目录和配置文件路径（使用绝对路径）
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(project_root, 'config.json')

    # 加载配置
    config = load_config(config_path)

    # 创建灵动岛主窗口，传递配置文件路径
    island = DynamicIsland(config, config_path)
    island.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
