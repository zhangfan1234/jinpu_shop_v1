# main_gui.py
import sys
import os
import threading
import time
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QCheckBox,
    QGroupBox, QMessageBox, QProgressBar, QComboBox, QRadioButton,
    QButtonGroup
)
from PySide6.QtCore import Qt, QThread, Signal, Slot, QMimeData, QTimer
from PySide6.QtGui import QFont, QTextCursor, QDragEnterEvent, QDropEvent

import config.jp_data as jp
import utils.excel_operations as excel
import scripts.tb_up as tb
import scripts.xy_up as xy
import scripts.wd_up as wd
from DrissionPage import ChromiumPage, ChromiumOptions


class DragDropLabel(QLabel):
    """支持拖拽的文件/目录标签"""
    file_dropped = Signal(str)

    def __init__(self, text="", accept_files=True, accept_dirs=True, parent=None):
        super().__init__(text, parent)
        self.accept_files = accept_files
        self.accept_dirs = accept_dirs
        self.setAcceptDrops(True)
        self.setMinimumHeight(30)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                min-height: 20px;
            }
            QLabel:hover {
                border-color: #4CAF50;
                background-color: #f9f9f9;
            }
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                url = urls[0].toLocalFile()
                is_file = os.path.isfile(url)
                is_dir = os.path.isdir(url)

                if (is_file and self.accept_files) or (is_dir and self.accept_dirs):
                    event.acceptProposedAction()
                    self.setStyleSheet("""
                        QLabel {
                            border: 2px solid #4CAF50;
                            border-radius: 5px;
                            padding: 8px;
                            background-color: #e8f5e9;
                            min-height: 20px;
                        }
                    """)
                    return

        event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                min-height: 20px;
            }
            QLabel:hover {
                border-color: #4CAF50;
                background-color: #f9f9f9;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if (os.path.isfile(file_path) and self.accept_files) or \
                    (os.path.isdir(file_path) and self.accept_dirs):
                self.setText(file_path)
                self.file_dropped.emit(file_path)

        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                min-height: 20px;
            }
            QLabel:hover {
                border-color: #4CAF50;
                background-color: #f9f9f9;
            }
        """)


class BrowserManager(QThread):
    """浏览器管理线程"""
    update_signal = Signal(str)
    browser_ready_signal = Signal(list)  # 浏览器准备好，发送平台列表
    finished_signal = Signal()
    error_signal = Signal(str)

    def __init__(self, platform_list):
        super().__init__()
        self.platform_list = platform_list
        self.page = None
        self._stop_flag = False

    def run(self):
        try:
            self.update_signal.emit("正在启动浏览器...")

            # 检查是否已经停止
            if self._stop_flag:
                return

            co = ChromiumOptions().set_paths(local_port=9999)
            self.page = ChromiumPage(addr_or_opts=co)

            # 为每个平台打开标签页
            for platform in self.platform_list:
                if self._stop_flag:
                    break

                if platform == "淘宝":
                    self.page.new_tab("https://loginmyseller.taobao.com/")
                    self.update_signal.emit("已打开淘宝页面")
                elif platform == "闲鱼":
                    self.page.new_tab("https://goofish.pro/sale/product/all")
                    self.update_signal.emit("已打开闲鱼页面")
                elif platform == "微店":
                    self.page.new_tab("https://d.weidian.com/weidian-pc/weidian-loader/#/pc-vue-item-list/item/list")
                    self.update_signal.emit("已打开微店页面")

                # 短暂延迟，避免请求过快
                time.sleep(1)

            if not self._stop_flag:
                self.update_signal.emit("浏览器启动完成，请登录平台...")
                self.browser_ready_signal.emit(self.platform_list)

        except Exception as e:
            self.error_signal.emit(f"浏览器启动失败: {str(e)}")
        finally:
            self.finished_signal.emit()

    def stop(self):
        """安全停止浏览器线程"""
        self._stop_flag = True
        if self.page:
            try:
                self.page.quit()
            except:
                pass
        self.quit()
        self.wait(2000)  # 等待2秒


class UploadWorkerThread(QThread):
    """上传工作线程 - 修改为更安全的中断方式"""
    update_signal = Signal(str)
    progress_signal = Signal(int)  # 进度信号
    finished_signal = Signal()
    error_signal = Signal(str)

    def __init__(self, platform_list, excel_path, image_path):
        super().__init__()
        self.platform_list = platform_list
        self.excel_path = excel_path
        self.image_path = image_path
        self._stop_flag = False
        self._current_operation = None

    def run(self):
        try:
            # 检查是否已经停止
            if self._stop_flag:
                return

            self.update_signal.emit("正在读取Excel数据...")

            # 读取Excel数据
            tb_dict_list, xy_dict_list, wd_dict_list = excel.read_csv_to_dict(self.excel_path)

            # 执行上传任务
            for platform in self.platform_list:
                if self._stop_flag:
                    self.update_signal.emit(f"{platform}上传已中断")
                    break

                self._current_operation = platform

                if platform == "淘宝":
                    self.update_signal.emit(f"开始上传淘宝商品，共{len(tb_dict_list)}个...")
                    start = datetime.now()
                    self.safe_tb_upload(tb_dict_list)
                    end = datetime.now()
                    self.update_signal.emit(f"淘宝发布完成，耗时: {end - start}")

                elif platform == "闲鱼":
                    self.update_signal.emit(f"开始上传闲鱼商品，共{len(xy_dict_list)}个...")
                    start = datetime.now()
                    self.safe_xy_upload(xy_dict_list)
                    end = datetime.now()
                    self.update_signal.emit(f"闲鱼发布完成，耗时: {end - start}")

                elif platform == "微店":
                    self.update_signal.emit(f"开始上传微店商品，共{len(wd_dict_list)}个...")
                    start = datetime.now()
                    self.safe_wd_upload(wd_dict_list)
                    end = datetime.now()
                    self.update_signal.emit(f"微店发布完成，耗时: {end - start}")

            if not self._stop_flag:
                self.update_signal.emit("所有任务完成！")
                self.finished_signal.emit()

        except Exception as e:
            self.error_signal.emit(str(e))

    def safe_tb_upload(self, tb_dict_list):
        """安全的淘宝上传，支持中断"""
        if self._stop_flag:
            return

        # 这里可以添加分块上传逻辑，每上传一个商品检查一次中断标志
        # 由于tb.tb_main可能是阻塞的，我们这里用一个简单的包装
        try:
            tb.tb_main(tb_dict_list, self.excel_path, self.image_path)
        except Exception as e:
            if self._stop_flag:
                raise InterruptedError("用户中断上传")
            else:
                raise e

    def safe_xy_upload(self, xy_dict_list):
        """安全的闲鱼上传，支持中断"""
        if self._stop_flag:
            return

        try:
            xy.xy_main(xy_dict_list, self.excel_path, self.image_path)
        except Exception as e:
            if self._stop_flag:
                raise InterruptedError("用户中断上传")
            else:
                raise e

    def safe_wd_upload(self, wd_dict_list):
        """安全的微店上传，支持中断"""
        if self._stop_flag:
            return

        try:
            wd.wd_main(wd_dict_list, self.excel_path, self.image_path)
        except Exception as e:
            if self._stop_flag:
                raise InterruptedError("用户中断上传")
            else:
                raise e

    def stop(self):
        """安全停止上传线程"""
        self._stop_flag = True
        self._current_operation = None
        # 不立即终止线程，而是设置标志位
        self.update_signal.emit(f"正在停止{self._current_operation}上传...")

        # 等待线程自然退出，但设置超时
        self.quit()
        if not self.wait(3000):  # 等待3秒
            self.terminate()  # 如果3秒后还没退出，强制终止
            self.wait()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.browser_manager = None
        self.upload_worker = None
        self.current_platform = None
        self.is_uploading = False
        self.stop_requested = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("商品上传工具")
        self.setGeometry(100, 100, 900, 700)

        # 设置主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 主布局
        layout = QVBoxLayout(main_widget)

        # 标题
        title_label = QLabel("商品上传系统")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 20px 0;")
        layout.addWidget(title_label)

        # 文件选择区域
        file_group = QGroupBox("文件设置")
        file_layout = QVBoxLayout()

        # Excel文件选择
        excel_layout = QHBoxLayout()
        self.excel_label = QLabel("津铺商品库:")
        self.excel_label.setMinimumWidth(80)
        self.excel_path_edit = DragDropLabel("未选择", accept_files=True, accept_dirs=False)
        self.excel_path_edit.file_dropped.connect(self.on_excel_dropped)
        self.excel_btn = QPushButton("选择文件")
        self.excel_btn.clicked.connect(self.select_excel_file)
        self.excel_btn.setFixedWidth(100)

        excel_layout.addWidget(self.excel_label)
        excel_layout.addWidget(self.excel_path_edit, 1)
        excel_layout.addWidget(self.excel_btn)
        file_layout.addLayout(excel_layout)

        # 图片目录选择
        image_layout = QHBoxLayout()
        self.image_label = QLabel("主图目录:")
        self.image_label.setMinimumWidth(80)
        self.image_path_edit = DragDropLabel("未选择", accept_files=False, accept_dirs=True)
        self.image_path_edit.file_dropped.connect(self.on_image_dropped)
        self.image_btn = QPushButton("选择目录")
        self.image_btn.clicked.connect(self.select_image_dir)
        self.image_btn.setFixedWidth(100)

        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.image_path_edit, 1)
        image_layout.addWidget(self.image_btn)
        file_layout.addLayout(image_layout)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # 平台选择区域
        platform_group = QGroupBox("选择平台")
        platform_layout = QHBoxLayout()

        # 使用单选按钮
        self.platform_group = QButtonGroup(self)

        self.tb_radio = QRadioButton("淘宝")
        self.xy_radio = QRadioButton("闲鱼")
        self.wd_radio = QRadioButton("微店")

        self.platform_group.addButton(self.tb_radio)
        self.platform_group.addButton(self.xy_radio)
        self.platform_group.addButton(self.wd_radio)

        # 默认选中淘宝
        self.tb_radio.setChecked(True)

        platform_layout.addWidget(self.tb_radio)
        platform_layout.addWidget(self.xy_radio)
        platform_layout.addWidget(self.wd_radio)
        platform_layout.addStretch()

        platform_group.setLayout(platform_layout)
        layout.addWidget(platform_group)

        # 状态显示区域
        status_group = QGroupBox("状态")
        status_layout = QVBoxLayout()

        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-weight: bold;
                padding: 8px;
                background-color: #ecf0f1;
                border-radius: 4px;
            }
        """)
        status_layout.addWidget(self.status_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # 控制按钮区域
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("开始上传")
        self.start_btn.clicked.connect(self.start_upload)
        self.start_btn.setMinimumHeight(45)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_upload)
        self.stop_btn.setMinimumHeight(45)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)

        # 输出区域
        output_group = QGroupBox("运行日志")
        output_layout = QVBoxLayout()

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(250)

        # 工具栏
        log_toolbar = QHBoxLayout()
        clear_btn = QPushButton("清空日志")
        clear_btn.clicked.connect(self.clear_output)
        clear_btn.setFixedWidth(100)

        log_toolbar.addWidget(clear_btn)
        log_toolbar.addStretch()

        output_layout.addWidget(self.output_text)
        output_layout.addLayout(log_toolbar)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        layout.addStretch()

    def on_excel_dropped(self, file_path):
        """处理Excel文件拖拽"""
        if os.path.isfile(file_path) and file_path.lower().endswith(('.xlsm', '.xlsx', '.xls')):
            self.excel_path_edit.setText(file_path)
            self.log_message(f"已拖拽Excel文件: {file_path}")
        else:
            QMessageBox.warning(self, "警告", "请拖拽有效的Excel文件(.xlsm/.xlsx/.xls)")

    def on_image_dropped(self, dir_path):
        """处理图片目录拖拽"""
        if os.path.isdir(dir_path):
            self.image_path_edit.setText(dir_path)
            self.log_message(f"已拖拽主图目录: {dir_path}")
        else:
            QMessageBox.warning(self, "警告", "请拖拽有效的目录")

    def select_excel_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "", "Excel Files (*.xlsm *.xlsx *.xls)"
        )
        if file_path:
            self.excel_path_edit.setText(file_path)
            self.log_message(f"已选择Excel文件: {file_path}")

    def select_image_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择主图目录")
        if dir_path:
            self.image_path_edit.setText(dir_path)
            self.log_message(f"已选择主图目录: {dir_path}")

    def get_selected_platform(self):
        """获取选中的平台（单选）"""
        if self.tb_radio.isChecked():
            return "淘宝"
        elif self.xy_radio.isChecked():
            return "闲鱼"
        elif self.wd_radio.isChecked():
            return "微店"
        return None

    def start_upload(self):
        if self.is_uploading:
            QMessageBox.warning(self, "警告", "已有任务正在运行，请先停止当前任务")
            return

        # 检查文件路径
        excel_path = self.excel_path_edit.text()
        if not excel_path or not os.path.exists(excel_path):
            QMessageBox.warning(self, "警告", "请选择有效的Excel文件！")
            return

        image_path = self.image_path_edit.text()
        if not image_path or not os.path.exists(image_path):
            QMessageBox.warning(self, "警告", "请选择有效的主图目录！")
            return

        # 检查平台选择
        platform = self.get_selected_platform()
        if not platform:
            QMessageBox.warning(self, "警告", "请选择一个平台！")
            return

        self.current_platform = platform
        self.is_uploading = True
        self.stop_requested = False
        self.status_label.setText("正在启动浏览器...")

        # 禁用控制按钮
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度

        # 启动浏览器管理线程
        self.browser_manager = BrowserManager([platform])
        self.browser_manager.update_signal.connect(self.log_message)
        self.browser_manager.browser_ready_signal.connect(self.on_browser_ready)
        self.browser_manager.finished_signal.connect(self.on_browser_finished)
        self.browser_manager.error_signal.connect(self.on_browser_error)
        self.browser_manager.start()

    def on_browser_ready(self, platforms):
        """浏览器准备就绪，显示登录确认"""
        if self.stop_requested:
            return

        self.status_label.setText("请登录平台...")

        # 使用QTimer延迟显示对话框，避免阻塞线程
        QTimer.singleShot(500, self.show_login_confirmation)

    def show_login_confirmation(self):
        """显示登录确认对话框"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("登录确认")
        msg_box.setText(f"已打开{self.current_platform}页面，请登录后点击确认")
        msg_box.setInformativeText("请确保完成登录操作后再点击确认")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Yes)

        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                font-size: 14px;
            }
        """)

        # 非阻塞显示，使用finished信号
        msg_box.finished.connect(self.on_login_confirmation_finished)
        msg_box.show()

    def on_login_confirmation_finished(self, result):
        """登录确认对话框结果"""
        if result == QMessageBox.Yes:
            self.status_label.setText("登录确认，开始上传...")
            self.log_message("用户确认登录，开始上传数据...")

            # 启动上传任务
            QTimer.singleShot(1000, self.start_upload_task)
        else:
            self.status_label.setText("已取消")
            self.log_message("用户取消上传")
            self.reset_buttons()
            self.cleanup_threads()

    def start_upload_task(self):
        """启动上传任务"""
        if self.stop_requested:
            return

        excel_path = self.excel_path_edit.text()
        image_path = self.image_path_edit.text()
        platform = self.current_platform

        # 启动上传工作线程
        self.upload_worker = UploadWorkerThread([platform], excel_path, image_path)
        self.upload_worker.update_signal.connect(self.log_message)
        self.upload_worker.finished_signal.connect(self.on_task_finished)
        self.upload_worker.error_signal.connect(self.on_task_error)
        self.upload_worker.start()

    def stop_upload(self):
        """停止上传"""
        self.stop_requested = True
        self.status_label.setText("正在停止...")
        self.stop_btn.setEnabled(False)  # 立即禁用停止按钮，防止重复点击

        # 记录停止请求
        self.log_message("正在停止任务，请等待...")

        # 先停止上传线程
        if self.upload_worker and self.upload_worker.isRunning():
            self.upload_worker.stop()

        # 再停止浏览器线程
        if self.browser_manager and self.browser_manager.isRunning():
            self.browser_manager.stop()

        # 使用QTimer延迟重置按钮状态，确保线程已完全停止
        QTimer.singleShot(1000, self.check_and_reset)

    def check_and_reset(self):
        """检查线程状态并重置按钮"""
        # 检查线程是否还在运行
        threads_running = False

        if self.upload_worker and self.upload_worker.isRunning():
            threads_running = True
            self.upload_worker.terminate()  # 强制终止
            self.upload_worker.wait()

        if self.browser_manager and self.browser_manager.isRunning():
            threads_running = True
            self.browser_manager.terminate()  # 强制终止
            self.browser_manager.wait()

        if threads_running:
            self.log_message("任务已被强制终止")

        self.reset_buttons()
        self.cleanup_threads()

    def on_browser_finished(self):
        """浏览器线程完成"""
        # 浏览器线程完成处理
        pass

    def on_browser_error(self, error_msg):
        """浏览器错误"""
        self.log_message(f"浏览器错误: {error_msg}")
        self.status_label.setText("浏览器错误")
        if not self.stop_requested:
            self.reset_buttons()
            self.cleanup_threads()

    def on_task_finished(self):
        """上传任务完成"""
        if not self.stop_requested:
            self.log_message("任务完成！")
            self.status_label.setText("任务完成")

            # 显示完成消息
            QMessageBox.information(self, "完成", "商品上传任务已完成！")

        self.reset_buttons()
        self.cleanup_threads()

    def on_task_error(self, error_msg):
        """上传任务出错"""
        if "用户中断上传" in str(error_msg):
            self.log_message("上传任务已被用户中断")
        else:
            self.log_message(f"发生错误: {error_msg}")

        self.status_label.setText("出错" if not self.stop_requested else "已停止")

        if not self.stop_requested:
            QMessageBox.critical(self, "错误", f"任务执行出错:\n{error_msg}")

        self.reset_buttons()
        self.cleanup_threads()

    def cleanup_threads(self):
        """清理线程资源"""
        if self.upload_worker:
            if self.upload_worker.isRunning():
                self.upload_worker.terminate()
                self.upload_worker.wait()
            self.upload_worker = None

        if self.browser_manager:
            if self.browser_manager.isRunning():
                self.browser_manager.terminate()
                self.browser_manager.wait()
            self.browser_manager = None

        self.is_uploading = False
        self.stop_requested = False

    def reset_buttons(self):
        """重置按钮状态"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)

    def log_message(self, message):
        """记录日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.append(f"[{timestamp}] {message}")
        self.output_text.moveCursor(QTextCursor.End)

        # 自动滚动到底部
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_output(self):
        """清空日志"""
        self.output_text.clear()

    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.is_uploading:
            reply = QMessageBox.question(
                self, "确认退出",
                "有任务正在运行，确定要退出吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.No:
                event.ignore()
                return

        # 停止所有线程
        self.stop_requested = True

        if self.upload_worker and self.upload_worker.isRunning():
            self.upload_worker.stop()

        if self.browser_manager and self.browser_manager.isRunning():
            self.browser_manager.stop()

        # 等待一段时间让线程停止
        QTimer.singleShot(1000, lambda: event.accept())
        event.accept()


def main():
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()