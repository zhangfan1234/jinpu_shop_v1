# build.py
import PyInstaller.__main__
import os

# 创建打包命令
args = [
    'main_ui.py',
    '--name=商品上传工具',
    '--windowed',  # 不显示控制台窗口
    '--onefile',   # 打包成单个文件
    '--icon=icon.png',  # 如果有图标的话
    '--add-data=config;config',
    '--add-data=utils;utils',
    '--add-data=scripts;scripts',
    '--add-data=闲鱼管家类目.txt;.',  # 添加根目录的文本文件到打包根目录
    '--add-data=./utils/闲鱼管家类目.txt;./utils',  # 添加根目录的文本文件到打包根目录
    '--hidden-import=PySide6.QtWidgets',
    '--hidden-import=PySide6.QtCore',
    '--hidden-import=PySide6.QtGui',
    '--hidden-import=pandas',
    '--hidden-import=openpyxl',
    '--hidden-import=DrissionPage',
]
PyInstaller.__main__.run(args)