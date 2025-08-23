import sys
import os
from PySide2.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QListWidget, QListWidgetItem, QTextEdit, QLabel, 
                               QPushButton, QMessageBox, QFileDialog, QTextBrowser, QMenu, QDialog, 
                               QDialogButtonBox, QSpacerItem, QSizePolicy)
from PySide2.QtCore import Qt, QTimer, QThread, Signal, QFile, QByteArray, QBuffer, QUrl
from PySide2.QtGui import QIcon, QFont, QPixmap, QImage, QPainter, QColor, QDesktopServices, QPen
from PySide2.QtUiTools import QUiLoader
import json
import base64
import threading
from datetime import datetime
from typing import List, Dict

class CustomMessageBox(QDialog):
    """自定义无边框消息框"""
    
    def __init__(self, parent=None, title="", text="", icon_type=QMessageBox.Information):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setModal(True)
        self.setMinimumWidth(300)
        
        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        

        
        # 消息文本
        self.text_label = QLabel(text)
        self.text_label.setStyleSheet("font-size: 12px; color: #f8f8f2;")
        self.text_label.setWordWrap(True)
        self.text_label.setTextFormat(Qt.PlainText)
        layout.addWidget(self.text_label)
        
        # 按钮布局
        self.button_box = QDialogButtonBox()
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStyleSheet("""
            QDialogButtonBox {
                background-color: transparent;
            }
            QDialogButtonBox QPushButton {
                background-color: #9898ee;
                color: black;
                border: 2px solid #333;
                border-radius: 5px;
                padding: 5px 15px;
                font-size: 12px;
                min-width: 80px;
                margin: 0 5px;
            }
            QDialogButtonBox QPushButton:hover {
                background-color: #1e90ff;
                border-color: #1e90ff;
                color: black;
            }
        """)
        
        # 创建按钮布局容器以确保对齐
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.button_box)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 设置背景样式
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
                border: 2px solid #444;
                border-radius: 8px;
            }
        """)
        
        # 使窗口可拖动
        self.drag_position = None
        self.is_dragging = False
    
    
    def set_standard_buttons(self, buttons):
        """设置标准按钮"""
        # 将QMessageBox按钮枚举转换为QDialogButtonBox按钮枚举
        dialog_buttons = QDialogButtonBox.StandardButtons()
        
        if buttons & QMessageBox.Yes:
            dialog_buttons |= QDialogButtonBox.Yes
        if buttons & QMessageBox.No:
            dialog_buttons |= QDialogButtonBox.No
        if buttons & QMessageBox.Ok:
            dialog_buttons |= QDialogButtonBox.Ok
        if buttons & QMessageBox.Cancel:
            dialog_buttons |= QDialogButtonBox.Cancel
        if buttons & QMessageBox.Abort:
            dialog_buttons |= QDialogButtonBox.Abort
        if buttons & QMessageBox.Retry:
            dialog_buttons |= QDialogButtonBox.Retry
        if buttons & QMessageBox.Ignore:
            dialog_buttons |= QDialogButtonBox.Ignore
        if buttons & QMessageBox.Open:
            dialog_buttons |= QDialogButtonBox.Open
        if buttons & QMessageBox.Save:
            dialog_buttons |= QDialogButtonBox.Save
        if buttons & QMessageBox.SaveAll:
            dialog_buttons |= QDialogButtonBox.SaveAll
        if buttons & QMessageBox.Discard:
            dialog_buttons |= QDialogButtonBox.Discard
        if buttons & QMessageBox.Help:
            dialog_buttons |= QDialogButtonBox.Help
        if buttons & QMessageBox.Apply:
            dialog_buttons |= QDialogButtonBox.Apply
        if buttons & QMessageBox.Reset:
            dialog_buttons |= QDialogButtonBox.Reset
            
        self.button_box.setStandardButtons(dialog_buttons)
        
        # 设置按钮文本为中文
        if buttons & QMessageBox.Yes:
            yes_button = self.button_box.button(QDialogButtonBox.Yes)
            if yes_button:
                yes_button.setText("是的")
        if buttons & QMessageBox.No:
            no_button = self.button_box.button(QDialogButtonBox.No)
            if no_button:
                no_button.setText("否")
        if buttons & QMessageBox.Ok:
            ok_button = self.button_box.button(QDialogButtonBox.Ok)
            if ok_button:
                ok_button.setText("确定")
        if buttons & QMessageBox.Cancel:
            cancel_button = self.button_box.button(QDialogButtonBox.Cancel)
            if cancel_button:
                cancel_button.setText("取消")
    
    def set_default_button(self, button):
        """设置默认按钮"""
        # 将QMessageBox按钮枚举转换为QDialogButtonBox按钮枚举
        if button == QMessageBox.Yes:
            dialog_button = QDialogButtonBox.Yes
        elif button == QMessageBox.No:
            dialog_button = QDialogButtonBox.No
        elif button == QMessageBox.Ok:
            dialog_button = QDialogButtonBox.Ok
        elif button == QMessageBox.Cancel:
            dialog_button = QDialogButtonBox.Cancel
        elif button == QMessageBox.Abort:
            dialog_button = QDialogButtonBox.Abort
        elif button == QMessageBox.Retry:
            dialog_button = QDialogButtonBox.Retry
        elif button == QMessageBox.Ignore:
            dialog_button = QDialogButtonBox.Ignore
        elif button == QMessageBox.Open:
            dialog_button = QDialogButtonBox.Open
        elif button == QMessageBox.Save:
            dialog_button = QDialogButtonBox.Save
        elif button == QMessageBox.SaveAll:
            dialog_button = QDialogButtonBox.SaveAll
        elif button == QMessageBox.Discard:
            dialog_button = QDialogButtonBox.Discard
        elif button == QMessageBox.Help:
            dialog_button = QDialogButtonBox.Help
        elif button == QMessageBox.Apply:
            dialog_button = QDialogButtonBox.Apply
        elif button == QMessageBox.Reset:
            dialog_button = QDialogButtonBox.Reset
        else:
            dialog_button = None
            
        if dialog_button is not None:
            self.button_box.button(dialog_button).setDefault(True)
    
    def exec_(self):
        """执行对话框"""
        # 居中显示
        if self.parent():
            parent_rect = self.parent().geometry()
            self.move(
                parent_rect.x() + (parent_rect.width() - self.width()) // 2,
                parent_rect.y() + (parent_rect.height() - self.height()) // 2
            )
        return super().exec_()
    
    def mousePressEvent(self, event):
        """鼠标按下事件，用于拖动窗口"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.is_dragging = True
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件，用于拖动窗口"""
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            if self.drag_position is not None:
                self.move(event.globalPos() - self.drag_position)
                event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.is_dragging = False
        self.drag_position = None
        event.accept()

    @staticmethod
    def custom_question(parent, title, text, buttons=QMessageBox.Yes | QMessageBox.No, default_button=QMessageBox.No):
        """自定义问题对话框"""
        dialog = CustomMessageBox(parent, title, text, QMessageBox.Question)
        dialog.set_standard_buttons(buttons)
        dialog.set_default_button(default_button)
        
        # 使用变量来存储用户的选择
        dialog.result = default_button
        
        # 连接按钮点击信号
        yes_button = dialog.button_box.button(QDialogButtonBox.Yes)
        no_button = dialog.button_box.button(QDialogButtonBox.No)
        
        if yes_button:
            yes_button.clicked.connect(lambda: dialog.done(QMessageBox.Yes))
        if no_button:
            no_button.clicked.connect(lambda: dialog.done(QMessageBox.No))
        
        # 执行对话框并返回结果
        result = dialog.exec_()
        return result if result != QDialog.Rejected else default_button

    @staticmethod
    def custom_warning(parent, title, text):
        """自定义警告对话框"""
        dialog = CustomMessageBox(parent, title, text, QMessageBox.Warning)
        dialog.set_standard_buttons(QMessageBox.Ok)
        dialog.exec_()

    @staticmethod
    def custom_critical(parent, title, text):
        """自定义错误对话框"""
        dialog = CustomMessageBox(parent, title, text, QMessageBox.Critical)
        dialog.set_standard_buttons(QMessageBox.Ok)
        dialog.exec_()

    @staticmethod
    def custom_information(parent, title, text):
        """自定义信息对话框"""
        dialog = CustomMessageBox(parent, title, text, QMessageBox.Information)
        dialog.set_standard_buttons(QMessageBox.Ok)
        dialog.exec_()

# 导入网络客户端
from network_client import MessageClient
# 导入图片管理器
from image_manager import ImageManager, create_image_viewer, save_image_automatically

class MessageThread(QThread):
    """消息处理线程"""
    messages_updated = Signal(list)  # 消息列表更新信号
    connection_status = Signal(bool, str)  # 连接状态信号
    
    def __init__(self, client: MessageClient):
        super().__init__()
        self.client = client
        self.running = True
        self.update_interval = 2  # 更新间隔（秒）
    
    def run(self):
        """线程主循环"""
        last_messages = None
        while self.running:
            try:
                # 检查连接状态
                is_connected = self.client.check_connection()
                status_msg = "服务器已连接" if is_connected else "服务器未连接"
                self.connection_status.emit(is_connected, status_msg)
                
                # 获取消息列表
                if is_connected:
                    messages = self.client.get_messages()
                    # 只有在消息列表发生变化时才发送更新信号
                    if messages != last_messages:
                        self.messages_updated.emit(messages)
                        last_messages = messages
                
            except Exception as e:
                self.connection_status.emit(False, f"错误: {str(e)}")
            
            # 等待下一次更新
            self.msleep(self.update_interval * 1000)
    
    def stop(self):
        """停止线程"""
        self.running = False
        self.wait()

class MessageUI(QWidget):
    """消息客户端UI类"""
    
    def __init__(self, client: MessageClient):
        super().__init__()
        self.client = client
        self.current_messages = []
        self.read_status = {}  # 跟踪消息已读状态，key为消息ID，value为布尔值
        self.read_status_file = os.path.join(os.path.dirname(__file__), 'read_messages.json')
        self.processed_messages = set()  # 跟踪已处理的消息ID，避免重复保存图片
        self.messages_cleared = False  # 标记消息列表是否已被清空
        self.image_viewers = []  # 跟踪所有打开的图片查看器
        self.position_file = os.path.join(os.path.dirname(__file__), 'position.json')  # 位置信息文件
        self.load_read_status()  # 加载已读状态
        self.load_window_position()  # 加载窗口位置
        
        # 拖曳相关变量
        self.drag_position = None
        self.is_dragging = False
        
        # 初始化图片管理器
        self.image_manager = ImageManager()
        
        self.setup_ui()
        self.setup_connections()
        
        # 启动消息处理线程
        self.message_thread = MessageThread(client)
        self.message_thread.messages_updated.connect(self.update_message_list)
        self.message_thread.connection_status.connect(self.update_connection_status)
        self.message_thread.start()
    
    def setup_ui(self):
        """设置UI界面"""
        # 加载UI文件
        ui_file_path = os.path.join(os.path.dirname(__file__), 'win_client.ui')
        
        if not os.path.exists(ui_file_path):
            raise FileNotFoundError(f"UI文件不存在: {ui_file_path}")
        
        # 使用QUiLoader加载UI文件
        loader = QUiLoader()
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)
        
        # 加载UI
        self.ui = loader.load(ui_file)
        ui_file.close()
        
        if not self.ui:
            raise RuntimeError(f"无法加载UI文件: {loader.errorString()}")

        # 隐藏标题栏
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 获取UI中的控件
        self.message_list = self.ui.findChild(QListWidget, "message_list")
        self.message_display = self.ui.findChild(QTextEdit, "message_display")
        self.info_label = self.ui.findChild(QLabel, "info_label")
        
        # 将QTextEdit替换为QTextBrowser以支持富文本和链接点击
        if self.message_display:
            # 获取原有QTextEdit的属性
            geometry = self.message_display.geometry()
            size_policy = self.message_display.sizePolicy()
            original_html = self.message_display.toHtml()  # 获取原有HTML内容
            
            # 创建新的QTextBrowser用于显示文字内容
            self.message_display = QTextBrowser(self.ui)
            self.message_display.setGeometry(geometry)
            self.message_display.setSizePolicy(size_policy)
            self.message_display.setHtml(original_html)  # 保留原有HTML内容
            self.message_display.setOpenLinks(False)  # 禁用自动打开链接
            self.message_display.anchorClicked.connect(self.on_anchor_clicked)  # 处理链接点击
        
        # 从UI文件中获取图片显示区域（独立于message_display的条件）
        self.image_display = self.ui.findChild(QTextBrowser, "image_display")
        if self.image_display:
            # 设置QTextBrowser属性
            self.image_display.setOpenLinks(False)  # 禁用自动打开链接
            self.image_display.anchorClicked.connect(self.on_anchor_clicked)  # 处理链接点击
            # image_display控件现在始终显示，不再初始隐藏
            print(f"调试: image_display控件初始化成功")
        else:
            print(f"警告: 未找到image_display控件")
        
        # 从UI文件中获取按钮
        self.del_list_pushButton = self.ui.findChild(QPushButton, "del_list_pushButton")
        self.all_read_pushButton = self.ui.findChild(QPushButton, "all_read_pushButton")
        
        # 获取最小化和关闭按钮
        self.mini_pushButton = self.ui.findChild(QPushButton, "mini_pushButton")
        self.close_pushButton = self.ui.findChild(QPushButton, "close_pushButton")
        
        # 设置最小化和关闭按钮的字体和文本
        from PySide2.QtGui import QFont
        
        # 从本地字体文件加载Segoe MDL2 Assets字体
        from PySide2.QtGui import QFontDatabase
        font_id = QFontDatabase.addApplicationFont("fonts/segmdl2.ttf")
        if font_id < 0:
            print("调试: 无法加载本地字体文件，将使用系统字体")
            mdl2_font = QFont("Segoe MDL2 Assets")
        else:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                mdl2_font = QFont(font_families[0])
                print("调试: 成功加载本地字体文件")
            else:
                print("调试: 无法从字体文件获取字体族，将使用系统字体")
                mdl2_font = QFont("Segoe MDL2 Assets")
        mdl2_font.setPointSize(8)  # 设置字体大小为8
        
        # 设置最小化按钮
        if self.mini_pushButton:
            self.mini_pushButton.setFont(mdl2_font)
            self.mini_pushButton.setText("\uE949")  # 最小化符号
            print("调试: mini_pushButton 字体和文本已设置")
        
        # 设置关闭按钮
        if self.close_pushButton:
            self.close_pushButton.setFont(mdl2_font)
            self.close_pushButton.setText("\uE106")  # 关闭符号
            print("调试: close_pushButton 字体和文本已设置")
        
        # 验证所有控件都已找到
        if not all([self.message_list, self.message_display, self.info_label]):
            raise RuntimeError("UI文件中缺少必要的控件")
        
        # 设置主布局
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)
        
        # 为主窗口安装事件过滤器来监听窗口激活事件
        self.installEventFilter(self)
        
        # 设置消息列表每项显示4行高度，以容纳标题、时间和3行内容预览
        if self.message_list:
            # 获取字体高度
            font_metrics = self.message_list.fontMetrics()
            line_height = font_metrics.height()
            # 设置每项的高度为4行的高度，减少边距
            item_height = line_height * 4 + 5  # 4行高度 + 5像素边距
            self.message_list.setUniformItemSizes(True)
            # 修改为AdjustToContentsOnFirstShow，避免出现水平滚动条
            self.message_list.setSizeAdjustPolicy(QListWidget.AdjustToContentsOnFirstShow)
            # 设置水平滚动条策略为永不显示，确保内容宽度限制在控件范围内
            self.message_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            # 设置文本换行模式，确保长文本能够自动换行
            self.message_list.setWordWrap(True)
            # 通过设置item委托来控制高度，而不是样式表
            self.message_list.setItemDelegate(QListWidget.itemDelegate(self.message_list))
        
        # 设置窗口属性
        self.setWindowTitle("消息客户端")
        # 从UI文件中获取窗口大小并固定，禁止用户拖拽调整
        ui_geometry = self.ui.geometry()
        self.setFixedSize(ui_geometry.width(), ui_geometry.height())
        self.setStyleSheet("""
            QWidget {
                background-color: black;
                color: #f8f8f2;
            }
        """)
    
    def setup_connections(self):
        """设置信号连接"""
        self.message_list.itemClicked.connect(self.on_message_selected)
        self.message_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.message_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # 连接清空列表按钮
        if self.del_list_pushButton:
            self.del_list_pushButton.clicked.connect(self.clear_all_messages)
            print("调试: del_list_pushButton 已连接")
        else:
            print("调试: 未找到 del_list_pushButton")
        
        # 连接全部已读按钮
        if self.all_read_pushButton:
            self.all_read_pushButton.clicked.connect(self.mark_all_as_read_improved)
            print("调试: all_read_pushButton 已连接到 mark_all_as_read_improved 方法")
        else:
            print("调试: 未找到 all_read_pushButton 按钮")
        
        # 连接最小化按钮
        if self.mini_pushButton:
            self.mini_pushButton.clicked.connect(self.hide)
            print("调试: mini_pushButton 已连接")
        else:
            print("调试: 未找到 mini_pushButton 按钮")
        
        # 连接关闭按钮
        if self.close_pushButton:
            self.close_pushButton.clicked.connect(self.hide)
            print("调试: close_pushButton 已连接到 hide 方法")
        else:
            print("调试: 未找到 close_pushButton 按钮")
        
        # 连接应用程序焦点变化信号
        QApplication.instance().focusChanged.connect(self.on_focus_changed)
    
    def update_message_list(self, messages: List[Dict]):
        """更新消息列表"""
        # 如果消息列表已被清空，则跳过更新
        if self.messages_cleared:
            return
            
        # 保存当前选中的消息ID
        selected_message_id = None
        current_item = self.message_list.currentItem()
        if current_item:
            current_index = self.message_list.row(current_item)
            if 0 <= current_index < len(self.current_messages):
                selected_message_id = self.current_messages[current_index].get('id')
        
        # 保存当前滚动位置
        scroll_position = self.message_list.verticalScrollBar().value()
        
        # 检查消息列表是否真的发生了变化
        messages_changed = len(messages) != len(self.current_messages)
        if not messages_changed:
            for i, msg in enumerate(messages):
                if i >= len(self.current_messages) or msg != self.current_messages[i]:
                    messages_changed = True
                    break
        
        # 如果消息列表没有变化，只更新统计信息
        if not messages_changed:
            # 更新状态栏显示消息统计信息
            if hasattr(self, 'message_thread') and self.message_thread:
                is_connected = self.client.check_connection()
                status_msg = "服务器已连接" if is_connected else "服务器未连接"
                self.update_connection_status(is_connected, status_msg)
            return
        
        # 消息列表有变化，进行完整更新
        self.current_messages = messages
        self.message_list.clear()
        
        selected_index = -1
        has_new_messages = False
        for i, message in enumerate(messages):
            preview = self.client.format_message_preview(message)
            item = QListWidgetItem(preview)
            
            # 检查是否是新消息
            message_id = message.get('id')
            is_new_message = False
            
            if message_id:
                # 检查是否是真正的新消息
                # 新消息判断逻辑：如果消息ID不在read_status中或在read_status中为false，则认为是新消息
                is_new_message = message_id not in self.read_status or not self.read_status.get(message_id, False)
                
                # 确保新消息在read_status中有记录
                if message_id not in self.read_status:
                    self.read_status[message_id] = False
                    has_new_messages = True
                elif not self.read_status[message_id]:
                    has_new_messages = True
                
                # 根据已读状态设置图标
                if self.read_status.get(message_id, False):
                    # 已读消息显示透明图标
                    item.setIcon(self.create_transparent_icon())
                else:
                    # 未读消息显示红点
                    item.setIcon(self.create_colored_dot_icon('#ff0000'))
                
                # 检查是否是之前选中的消息
                if message_id == selected_message_id:
                    selected_index = i
            
            # 对所有包含图片的消息自动保存图片
            if message.get('image_data'):
                message_id = message.get('id', 0)
                image_data = message['image_data']
                print(f"调试: 消息 {message_id} 包含图片数据，长度: {len(image_data)}")
                # 检查是否已经处理过这个消息的图片
                if message_id not in self.processed_messages:
                    print(f"调试: 消息 {message_id} 未处理过，开始保存图片")
                    saved_path = save_image_automatically(message_id, image_data)
                    if saved_path:
                        print(f"消息图片已自动保存到: {saved_path}")
                    else:
                        print(f"调试: 消息 {message_id} 图片保存失败")
                    # 将消息ID添加到已处理集合中
                    self.processed_messages.add(message_id)
                else:
                    print(f"调试: 消息 {message_id} 已经处理过，跳过保存")
            
            self.message_list.addItem(item)
        
        # 恢复选中状态
        if selected_index >= 0:
            self.message_list.setCurrentRow(selected_index)
        
        # 只有在有新消息时才滚动到顶部，否则保持原来的滚动位置
        if has_new_messages:
            self.message_list.verticalScrollBar().setValue(0)
        else:
            self.message_list.verticalScrollBar().setValue(scroll_position)
        
        # 更新状态栏显示消息统计信息
        if hasattr(self, 'message_thread') and self.message_thread:
            # 模拟连接状态更新来触发统计信息显示
            is_connected = self.client.check_connection()
            status_msg = "服务器已连接" if is_connected else "服务器未连接"
            self.update_connection_status(is_connected, status_msg)
    
    def update_connection_status(self, is_connected: bool, status_msg: str):
        """更新连接状态"""
        # 构建更丰富的状态信息
        if is_connected and hasattr(self, 'current_messages') and self.current_messages:      # 确保有消息列表
            total_messages = len(self.current_messages)
            unread_count = sum(1 for msg in self.current_messages if msg.get('id') and not self.read_status.get(msg.get('id'), False))
            read_count = total_messages - unread_count
            image_count = sum(1 for msg in self.current_messages if msg.get('image_data'))
            text_count = total_messages - image_count
            
            # 构建详细的状态信息
            status_info = f"{status_msg} | 总计: {total_messages} | 未读: {unread_count} | 已读: {read_count}"
            self.info_label.setText(status_info)
        else:
            self.info_label.setText(status_msg)
        

    def on_message_selected(self, item):
        """处理消息选择事件"""
        index = self.message_list.row(item)
        if 0 <= index < len(self.current_messages):
            message = self.current_messages[index]
            
            # 标记消息为已读
            message_id = message.get('id')
            if message_id and not self.read_status.get(message_id, False):
                self.read_status[message_id] = True
                # 同步更新processed_messages状态
                self.processed_messages.add(message_id)
                # 设置透明图标
                item.setIcon(self.create_transparent_icon())
                # 立即保存已读状态
                self.save_read_status()
                
                # 停止消息闪烁
                self.stop_tray_flashing()
            
            self.display_message_detail(message)
    
    def display_message_detail(self, message: Dict):
        """显示消息详情"""
        # 清空所有显示区域
        self.clear_display()
        
        # 获取消息详情文本
        detail = self.client.format_message_detail(message)
        
        # 移除默认的"[包含图片数据]"文本，因为我们会在下面显示实际图片
        if message.get('image_data'):
            detail = detail.replace("[包含图片数据]\n", "")
        
        # 将文字内容显示到主文本区域
        self.message_display.setText(detail)
        
        # 如果有图片数据，在单独的图片区域显示
        if message.get('image_data'):
            # 确保image_display控件存在且可见
            if hasattr(self, 'image_display') and self.image_display:
                self.display_image_in_separate_area(message)
            else:
                print("警告: image_display控件不存在，无法显示图片")
    
    def display_image_in_separate_area(self, message: Dict):
        """在单独的图片区域显示图片"""
        try:
            # 检查image_display控件是否存在
            if not hasattr(self, 'image_display') or not self.image_display:
                print("警告: image_display控件不存在")
                return
                
            message_id = message.get('id', 0)
            image_data = message['image_data']
            
            # 尝试获取已保存的图片路径
            saved_path = None
            try:
                from image_manager import get_saved_image_path
                saved_path = get_saved_image_path(message_id, image_data)
            except:
                pass
            
            # 解码base64图片数据
            binary_data = base64.b64decode(image_data)
            
            # 创建QImage从数据
            image = QImage()
            image.loadFromData(binary_data)
            
            if not image.isNull():
                # 获取控件的实际宽度
                control_width = self.image_display.width() - 20  # 留出边距
                
                # 判断图片是否需要缩放
                if image.width() > control_width:
                    # 图片宽度大于控件，水平充满整个控件
                    scaled_image = image.scaled(control_width, image.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    image_style = f'width: {control_width}px; height: auto; cursor: pointer; border: 2px solid #444; user-select: none; -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none;'
                else:
                    # 图片宽度小于控件，按原大小显示
                    scaled_image = image
                    image_style = f'width: {image.width()}px; height: {image.height()}px; cursor: pointer; border: 2px solid #444; user-select: none; -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none;'
                
                # 将图片转换为HTML格式插入到QTextBrowser中
                byte_array = QByteArray()
                buffer = QBuffer(byte_array)
                buffer.open(QBuffer.WriteOnly)
                scaled_image.save(buffer, "PNG")
                base64_image = base64.b64encode(byte_array.data()).decode('utf-8')
                
                # 创建可点击的图片链接
                image_id = f"img_{message_id}_{hash(image_data) % 10000}"
                html_image = f'<a href="image:{image_id}" style="text-decoration: none; color: inherit;"><img src="data:image/png;base64,{base64_image}" style="{image_style}" title="点击查看原图"></a>'
                
                # 添加图片信息（居中显示）
                image_info = f'<div style="color: #888; font-size: 12px; margin: 5px 0; text-align: center;">图片尺寸: {image.width()} × {image.height()} 像素</div>'
                if saved_path:
                    image_info += f'<div style="color: #4CAF50; font-size: 12px; margin: 5px 0; text-align: center;">✓ 已保存到: {saved_path}</div>'
                
                # 在图片显示区域设置内容（图片居中）
                html_content = f'<div style="text-align: center; user-select: none; -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none;">{html_image}</div>' + image_info
                self.image_display.setHtml(html_content)
                # 禁用文本选择功能，但保留链接点击功能
                self.image_display.setTextInteractionFlags(
                    Qt.LinksAccessibleByMouse | Qt.LinksAccessibleByKeyboard
                )
                self.image_display.show()  # 显示图片区域
                
                # 存储图片数据以便点击时使用
                if not hasattr(self, 'image_data_cache'):
                    self.image_data_cache = {}
                self.image_data_cache[image_id] = image_data
                
            else:
                self.image_display.setHtml('<div style="color: #ff4444;">[图片数据无效或格式不支持]</div>')
                self.image_display.show()
                
        except Exception as e:
            self.image_display.setHtml(f'<div style="color: #ff4444;">[图片显示错误: {str(e)}]</div>')
            self.image_display.show()
    
    def refresh_messages(self):
        """手动刷新消息列表"""
        # 重置清空标志，允许重新加载消息
        self.messages_cleared = False
        try:
            messages = self.client.get_messages()
            self.update_message_list(messages)
            # update_message_list方法中已经会更新统计信息，这里不需要重复设置
            self.info_label.setText("消息列表已刷新")
            # 延迟更新统计信息
            QTimer.singleShot(100, lambda: self.update_connection_status(True, "已连接"))
        except Exception as e:
            self.info_label.setText(f"刷新失败: {str(e)}")
    
    def on_anchor_clicked(self, url: QUrl):
        """处理链接点击事件"""
        url_string = url.toString()
        
        if url_string.startswith("image:"):
            # 处理图片点击
            image_id = url_string[6:]  # 去掉"image:"前缀
            if hasattr(self, 'image_data_cache') and image_id in self.image_data_cache:
                image_data = self.image_data_cache[image_id]
                
                # 解码base64图片数据
                try:
                    binary_data = base64.b64decode(image_data)
                    # 创建QImage从数据
                    image = QImage()
                    image.loadFromData(binary_data)
                    
                    if not image.isNull():
                        # 尝试获取图片路径
                        saved_path = None
                        try:
                            # 从image_id中提取message_id
                            # image_id格式: img_{message_id}_{hash}
                            parts = image_id.split('_')
                            if len(parts) >= 2:
                                message_id = int(parts[1])
                                from image_manager import get_saved_image_path
                                saved_path = get_saved_image_path(message_id, image_data)
                        except:
                            pass
                        
                        # 创建图片查看器对话框，传递QImage对象和图片路径
                        viewer = create_image_viewer(image, self, saved_path)
                        if viewer:
                            # 将查看器添加到跟踪列表
                            self.image_viewers.append(viewer)
                            # 监听查看器的销毁事件，以便从列表中移除
                            viewer.destroyed.connect(lambda: self.remove_image_viewer(viewer))
                            viewer.show()
                    else:
                        custom_warning(self, "错误", "图片数据无效或格式不支持")
                except Exception as e:
                    custom_warning(self, "错误", f"图片处理失败: {str(e)}")
        else:
            # 处理其他链接
            QDesktopServices.openUrl(url)
    
    def clear_display(self):
        """清空显示"""
        self.message_display.clear()
        # 清空图片显示区域
        if hasattr(self, 'image_display'):
            self.image_display.clear()
            # 不隐藏image_display控件，保持界面布局完整
            # self.image_display.hide()
        # 清空图片缓存
        if hasattr(self, 'image_data_cache'):
            self.image_data_cache.clear()
    
    def clear_all_messages(self):
        """清空所有消息列表"""
        # 确认对话框
        reply = CustomMessageBox.custom_question(
            self, 
            "确认清空", 
            "确定要清空所有消息吗？\n\n此操作将：\n1. 清空本地消息列表\n2. 删除所有本地保存的图片文件\n3. 清空已读状态\n4. 删除服务端所有消息数据\n\n警告：此操作不可恢复！\n",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 先尝试删除服务端所有消息
            server_deleted = False
            try:
                server_deleted = self.client.delete_all_messages()
                if not server_deleted:
                    # 服务端删除失败，显示错误提示并返回
                    custom_warning(
                        self, 
                        "清空失败", 
                        "无法从服务端删除消息，请检查网络连接。\n\n本地数据保持不变。"
                    )
                    return
            except Exception as e:
                # 删除过程中出现错误，显示错误提示并返回
                custom_critical(
                    self, 
                    "清空错误", 
                    f"清空消息时发生错误：\n{str(e)}\n\n本地数据保持不变。"
                )
                print(f"清空消息时发生错误: {e}")
                return
            
            # 只有服务端删除成功后，才继续删除本地数据
            # 删除所有本地保存的图片文件
            deleted_images_count = 0
            try:
                from image_manager import delete_saved_image
                # 遍历所有当前消息，删除对应的图片文件
                for message in self.current_messages:
                    message_id = message.get('id')
                    if message_id:
                        if delete_saved_image(message_id):
                            deleted_images_count += 1
            except Exception as e:
                print(f"删除本地图片文件时发生错误: {e}")
            
            # 清空消息列表
            self.message_list.clear()
            self.current_messages = []
            # 清空消息详情显示
            self.clear_display()
            # 清空已读状态
            self.read_status = {}
            self.processed_messages = set()
            # 保存状态
            self.save_read_status()
            # 不设置清空标志，允许消息线程自动重新加载消息
            # self.messages_cleared = True
            # 显示成功消息
            success_text = f"消息列表已完全清空，已删除 {deleted_images_count} 个本地图片文件和服务端所有数据"
            self.info_label.setText(success_text)
            
            # 清空后立即刷新消息列表，重新从服务器获取消息
    
    def create_colored_dot_icon(self, color: str):
        """创建指定颜色的圆点图标"""
        # 创建一个16x16的像素图
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)  # 透明背景
        
        # 创建画家并绘制圆点
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        
        # 设置颜色并绘制圆点
        painter.setBrush(QColor(color))
        painter.setPen(Qt.NoPen)  # 无边框
        painter.drawEllipse(2, 2, 12, 12)  # 在中心绘制一个12x12的圆
        
        painter.end()
        return QIcon(pixmap)
    
    def create_transparent_icon(self):
        """创建完全透明的图标"""
        # 创建一个16x16的完全透明像素图
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)  # 完全透明背景
        return QIcon(pixmap)
    
    def send_test_message(self):
        """发送测试消息"""
        try:
            success = self.client.send_message(
                message_type="text",
                content=f"这是一条测试消息，发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                title="测试消息"
            )
            
            if success:
                self.info_label.setText("测试消息发送成功")
                # 自动刷新消息列表
                self.refresh_messages()
            else:
                self.info_label.setText("测试消息发送失败")
                
        except Exception as e:
            self.info_label.setText(f"发送测试消息失败: {str(e)}")
    
    def load_read_status(self):
        """从文件加载已读状态和已处理消息"""
        try:
            if os.path.exists(self.read_status_file):
                with open(self.read_status_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 检查数据格式，支持两种格式：
                    # 1. {"read_messages": [1, 2, 3]} - 旧格式
                    # 2. {"1": true, "2": false} - 新格式
                    if "read_messages" in data:
                        # 旧格式：将已读消息列表转换为字典
                        read_list = data["read_messages"]
                        self.read_status = {msg_id: True for msg_id in read_list}
                        # 旧格式没有processed_messages，初始化为空集合
                        self.processed_messages = set()
                    else:
                        # 新格式：将字符串类型的键转换为整数类型，但跳过processed_messages字段
                        self.read_status = {int(k): v for k, v in data.items() if k != "processed_messages"}
                        # 加载已处理消息集合
                        if "processed_messages" in data:
                            self.processed_messages = set(data["processed_messages"])
                        else:
                            self.processed_messages = set()
                        # 同步状态：将read_status中为true的消息ID也添加到processed_messages中
                        for msg_id, is_read in self.read_status.items():
                            if is_read and msg_id not in self.processed_messages:
                                self.processed_messages.add(msg_id)
        except Exception as e:
            print(f"加载已读状态失败: {e}")
            self.read_status = {}
            self.processed_messages = set()
    
    def save_read_status(self):
        """保存已读状态和已处理消息到文件"""
        try:
            with open(self.read_status_file, 'w', encoding='utf-8') as f:
                # 将整数类型的键转换为字符串类型以便JSON序列化
                data = {str(k): v for k, v in self.read_status.items()}
                # 添加已处理消息集合
                data["processed_messages"] = list(self.processed_messages)
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存已读状态失败: {e}")
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.message_list.itemAt(position)
        if not item:
            return
        
        index = self.message_list.row(item)
        if 0 <= index < len(self.current_messages):
            message = self.current_messages[index]
            message_id = message.get('id')
            
            if message_id:
                # 创建右键菜单
                menu = QMenu(self)
                # 设置菜单样式
                menu.setStyleSheet("""
                    QMenu {
                        background-color: #1a1a1a;
                        border: 1px solid #444;
                        border-radius: 2px;
                        padding: 1px;
                        /* 确保所有角都有圆角 */
                        alternate-background-color: transparent;
                    }
                    QMenu::item {
                        background-color: transparent;
                        color: #f8f8f2;
                        border: none;
                        border-radius: 2px;
                        padding: 6px 30px;
                        margin: 0px;
                    }
                    QMenu::item:selected {
                        background-color: #07c160;
                        color: white;
                        border: none;
                    }
                    QMenu::item:hover {
                        background-color: #333333;
                        color: #ffffff;
                        border: 2px;
                    }
                """)
                
                # 添加删除动作
                delete_action = menu.addAction("删除消息")
                # 使用functools.partial传递message_id和index，而不是item对象
                import functools
                delete_action.triggered.connect(functools.partial(self.delete_message_by_id, message_id, index))
                
                # 显示菜单
                menu.exec_(self.message_list.mapToGlobal(position))
    
    def delete_message(self, message_id: int, item: QListWidgetItem):
        """删除消息"""
        # 获取item的索引
        index = self.message_list.row(item)
        
        # 确认对话框
        reply = CustomMessageBox.custom_question(
            self, 
            "单条消息----确认删除", 
            f"确定要删除这条消息吗？\n\n此操作将同时删除本地记录和服务端数据库中的数据。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 1. 从服务端删除
                success = self.client.delete_message(message_id)
                
                if success:
                    # 2. 从本地状态中删除
                    if message_id in self.read_status:
                        del self.read_status[message_id]
                    
                    if message_id in self.processed_messages:
                        self.processed_messages.remove(message_id)
                    
                    # 3. 删除本地保存的图片文件（如果存在）
                    try:
                        from image_manager import delete_saved_image
                        delete_saved_image(message_id)
                    except Exception as e:
                        print(f"删除本地图片文件失败: {e}")
                    
                    # 4. 在删除item之前获取所有需要的信息
                    current_index_before_delete = self.message_list.currentRow()
                    is_current_item_being_deleted = (current_index_before_delete == index)
                    
                    # 5. 从当前消息列表中删除
                    if 0 <= index < len(self.current_messages):
                        del self.current_messages[index]
                    
                    # 6. 从UI列表中删除（使用之前获取的index）
                    self.message_list.takeItem(index)
                    
                    # 7. 清空详情显示（如果删除的是当前选中的消息）
                    if is_current_item_being_deleted:
                        self.clear_display()
                    
                    # 7. 保存状态
                    self.save_read_status()
                    
                    # 8. 显示成功消息
                    self.info_label.setText(f"消息 {message_id} 已删除")

                    # 9. 延迟更新统计信息
                    QTimer.singleShot(100, lambda: self.update_connection_status(True, "已连接"))
                    
                    print(f"消息 {message_id} 删除成功")
                    
                else:
                    # 服务端删除失败
                    CustomMessageBox.custom_warning(
                        self, 
                        "删除失败", 
                        f"无法从服务端删除消息 {message_id}，请检查网络连接。"
                    )
                    
            except Exception as e:
                # 删除过程中出现错误
                CustomMessageBox.custom_critical(
                    self, 
                    "删除错误", 
                    f"删除消息时发生错误：\n{str(e)}"
                )
                print(f"删除消息 {message_id} 时发生错误: {e}")
    
    def delete_message_by_id(self, message_id: int, index: int):
        """通过消息ID和索引删除消息（避免直接传递item对象）"""
        # 首先检查索引是否有效
        if index < 0 or index >= self.message_list.count():
            CustomMessageBox.custom_warning(self, "删除错误", "消息索引无效，可能已被删除。")
            return
        
        # 通过索引获取item对象
        item = self.message_list.item(index)
        if not item:
            CustomMessageBox.custom_warning(self, "删除错误", "消息项不存在，可能已被删除。")
            return
        
        # 调用原来的delete_message方法
        self.delete_message(message_id, item)
    
    def mark_all_as_read(self):
        """将所有未读消息标记为已读"""
        print("调试: mark_all_as_read 方法被调用")
        # 统计标记为已读的消息数量
        marked_count = 0
        print(f"调试: 当前消息数量: {len(self.current_messages)}")
        
        # 遍历所有当前消息
        for message in self.current_messages:
            message_id = message.get('id')
            if message_id and not self.read_status.get(message_id, False):
                # 标记为已读
                self.read_status[message_id] = True
                # 添加到已处理消息集合
                self.processed_messages.add(message_id)
                marked_count += 1
        
        if marked_count > 0:
            # 保存已读状态
            self.save_read_status()
            
            # 更新消息列表显示（刷新图标）
            self.update_message_list(self.current_messages)
            
            # 停止消息闪烁
            self.stop_tray_flashing()
            
            # 显示成功消息
            self.info_label.setText(f"已将 {marked_count} 条消息标记为已读")

            
            # 延迟更新统计信息
            QTimer.singleShot(100, lambda: self.update_connection_status(True, "已连接"))
        else:
            # 如果没有未读消息，显示提示
            self.info_label.setText("没有未读消息需要标记")

    
    def mark_all_as_read_improved(self):
        """将所有未读消息标记为已读（改进版 - 直接隐藏红点）"""
        print("调试: mark_all_as_read_improved 方法被调用")
        # 统计标记为已读的消息数量
        marked_count = 0
        print(f"调试: 当前消息数量: {len(self.current_messages)}")
        
        # 遍历所有当前消息，直接操作每个消息项的图标
        for i, message in enumerate(self.current_messages):
            message_id = message.get('id')
            if message_id and not self.read_status.get(message_id, False):
                # 标记为已读
                self.read_status[message_id] = True
                # 添加到已处理消息集合
                self.processed_messages.add(message_id)
                marked_count += 1
                
                # 直接获取对应的列表项并设置透明图标（隐藏红点）
                item = self.message_list.item(i)
                if item:
                    print(f"调试: 为消息 {message_id} 设置透明图标")
                    item.setIcon(self.create_transparent_icon())
        
        if marked_count > 0:
            # 保存已读状态
            self.save_read_status()
            
            # 停止消息闪烁
            self.stop_tray_flashing()
            
            # 显示成功消息
            self.info_label.setText(f"已将 {marked_count} 条消息标记为已读")

            
            # 延迟更新统计信息
            QTimer.singleShot(100, lambda: self.update_connection_status(True, "已连接"))
        else:
            # 如果没有未读消息，显示提示
            self.info_label.setText("没有未读消息需要标记")

    
    def stop_tray_flashing(self):
        """停止系统托盘图标闪烁"""
        # 尝试调用main_client.py中的stop_message_flashing函数
        try:
            # 导入stop_message_flashing函数
            from main_client import stop_message_flashing
            # 获取主窗口实例
            main_window = None
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, QMainWindow) and widget.objectName() == "MainWindow":
                    main_window = widget
                    break
            
            if main_window:
                stop_message_flashing(main_window)
                print("调试: 通过stop_tray_flashing停止了消息闪烁")
            else:
                # 如果找不到主窗口，尝试直接使用当前窗口
                if hasattr(self, 'is_flashing') and self.is_flashing:
                    self.is_flashing = False
                    if hasattr(self, 'flash_timer') and self.flash_timer:
                        self.flash_timer.stop()
                    if hasattr(self, 'tray_icon') and self.tray_icon and hasattr(self, 'normal_icon'):
                        self.tray_icon.setIcon(self.normal_icon)
                    print("调试: 通过本地方式停止了消息闪烁")
        except Exception as e:
            print(f"停止托盘闪烁时出错: {e}")
            # 备用方案：检查本地托盘图标
            if hasattr(self, 'tray_icon') and self.tray_icon:
                if hasattr(self, 'flash_timer') and self.flash_timer:
                    self.flash_timer.stop()
                if hasattr(self, 'normal_icon'):
                    self.tray_icon.setIcon(self.normal_icon)
    
    def showEvent(self, event):
        """窗口显示事件"""
        print("调试: 主窗口显示，停止闪烁")
        self.stop_tray_flashing()
        # 将窗口置于前台
        self.raise_()
        self.activateWindow()
        # 调用父类的showEvent
        super().showEvent(event)
    
    def focusInEvent(self, event):
        """窗口获得焦点事件"""
        print("调试: 主窗口获得焦点，停止闪烁")
        self.stop_tray_flashing()
        # 将窗口置于前台
        self.raise_()
        self.activateWindow()
        # 调用父类的focusInEvent
        super().focusInEvent(event)
    
    def changeEvent(self, event):
        """窗口状态变化事件"""
        # 当窗口被激活时停止闪烁
        if event.type() == event.ActivationChange and self.isActiveWindow():
            print("调试: 主窗口变为活动状态，停止闪烁")
            self.stop_tray_flashing()
            # 将窗口置于前台
            self.raise_()
            self.activateWindow()
        # 调用父类的changeEvent
        super().changeEvent(event)
    
    def on_focus_changed(self, old, new):
        """应用程序焦点变化事件处理"""
        # 当新的焦点控件是我们的窗口或其子控件时，停止闪烁
        if new and (new == self or self.isAncestorOf(new)):
            print("调试: 应用程序焦点变化到主窗口，停止闪烁")
            self.stop_tray_flashing()
            # 将窗口置于前台
            self.raise_()
            self.activateWindow()
    
    def remove_image_viewer(self, viewer):
        """从跟踪列表中移除已关闭的图片查看器"""
        if viewer in self.image_viewers:
            self.image_viewers.remove(viewer)
            print(f"图片查看器已从跟踪列表中移除，当前剩余 {len(self.image_viewers)} 个查看器")
    
    def closeEvent(self, event):
        """窗口关闭事件 - 最小化到托盘"""
        # 忽略关闭事件，改为隐藏窗口（最小化到托盘）
        event.ignore()
        self.hide()
        print("窗口已最小化到托盘")
    
    def save_window_position(self):
        """保存窗口位置信息"""
        try:
            position_data = {
                'x': self.x(),
                'y': self.y(),
                'width': self.width(),
                'height': self.height()
            }
            with open(self.position_file, 'w', encoding='utf-8') as f:
                json.dump(position_data, f, indent=2)
            print(f"窗口位置已保存到: {self.position_file}")
        except Exception as e:
            print(f"保存窗口位置失败: {e}")
    
    def load_window_position(self):
        """加载窗口位置信息"""
        try:
            if os.path.exists(self.position_file):
                with open(self.position_file, 'r', encoding='utf-8') as f:
                    position_data = json.load(f)
                
                # 设置窗口位置和大小
                self.move(position_data['x'], position_data['y'])
                self.resize(position_data['width'], position_data['height'])
                print(f"窗口位置已从 {self.position_file} 加载")
            else:
                print("位置信息文件不存在，使用默认位置")
        except Exception as e:
            print(f"加载窗口位置失败: {e}")
    
    def force_close(self):
        """强制关闭程序（真正退出）"""
        # 保存窗口位置
        self.save_window_position()
        
        # 优先关闭所有打开的图片查看器
        self.close_all_image_viewers()
        
        # 保存已读状态
        self.save_read_status()
        
        # 在后台异步停止消息处理线程
        if hasattr(self, 'message_thread'):
            # 使用QTimer.singleShot在事件循环中异步执行线程停止
            QTimer.singleShot(0, self._stop_message_thread_async)
        
        # 强制关闭应用程序
        QApplication.quit()
    
    def close_all_image_viewers(self):
        """关闭所有打开的图片查看器"""
        if self.image_viewers:
            print(f"正在关闭 {len(self.image_viewers)} 个图片查看器...")
            # 复制列表以避免在迭代时修改列表
            viewers_to_close = self.image_viewers.copy()
            for viewer in viewers_to_close:
                try:
                    if viewer.isVisible():
                        viewer.close()
                        print("图片查看器已关闭")
                except Exception as e:
                    print(f"关闭图片查看器时发生错误: {e}")
            # 清空列表
            self.image_viewers.clear()
            print("所有图片查看器已关闭")
    
    def _stop_message_thread_async(self):
        """异步停止消息处理线程"""
        try:
            if hasattr(self, 'message_thread'):
                self.message_thread.stop()
                print("消息处理线程已停止")
        except Exception as e:
            print(f"停止消息处理线程时发生错误: {e}")
    
    def mousePressEvent(self, event):
        """鼠标按下事件处理"""
        if event.button() == Qt.LeftButton:
            # 检查是否点击在空白区域（没有控件的地方）
            clicked_widget = self.childAt(event.pos())
            
            # 更准确的空白区域检测：检查点击的控件是否是主要的UI控件
            main_ui_widgets = [self.message_list, self.message_display, self.info_label, 
                            self.del_list_pushButton, self.all_read_pushButton]
            
            # 如果点击的是主窗口本身或者是非主要控件区域，则允许拖曳
            if clicked_widget is None or clicked_widget == self or clicked_widget not in main_ui_widgets:
                # 进一步检查：如果点击的是某个控件的子控件，且该子控件不是可交互的，也允许拖曳
                allow_drag = True
                if clicked_widget and clicked_widget != self:
                    # 检查是否是主要控件的子控件
                    for widget in main_ui_widgets:
                        if widget and widget.isAncestorOf(clicked_widget):
                            # 如果是主要控件的子控件，检查是否是可交互的控件类型
                            if isinstance(clicked_widget, (QPushButton, QListWidget, QTextEdit, QTextBrowser, QLabel)):
                                allow_drag = False
                                break
                
                if allow_drag:
                    # 开始拖曳
                    self.is_dragging = True
                    self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                    event.accept()
                    return
        # 如果不是拖曳情况，调用父类方法
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件处理"""
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            # 移动窗口
            new_position = event.globalPos() - self.drag_position
            self.move(new_position)
            event.accept()
            return
        # 如果不是拖曳情况，调用父类方法
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件处理"""
        if event.button() == Qt.LeftButton and self.is_dragging:
            # 结束拖曳
            self.is_dragging = False
            self.drag_position = None
            # 保存新的窗口位置
            self.save_window_position()
            event.accept()
            return
        # 如果不是拖曳情况，调用父类方法
        super().mouseReleaseEvent(event)