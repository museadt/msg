import sys
import os
import time
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide2.QtCore import QTimer
from PySide2.QtGui import QIcon

# 导入主客户端模块
from main_client import create_tray_icon, setup_message_flashing, start_message_flashing, stop_message_flashing

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("系统托盘测试")
        self.setGeometry(100, 100, 400, 300)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 创建标签
        self.label = QLabel("系统托盘闪烁测试")
        self.label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.label)
        
        # 创建按钮
        self.start_button = QPushButton("开始闪烁")
        self.stop_button = QPushButton("停止闪烁")
        self.hide_button = QPushButton("隐藏窗口")
        
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.hide_button)
        
        # 连接按钮信号
        self.start_button.clicked.connect(self.start_flashing)
        self.stop_button.clicked.connect(self.stop_flashing)
        self.hide_button.clicked.connect(self.hide_window)
        
        # 初始化属性
        self.is_flashing = False
        self.flash_timer = None
        self.tray_icon = None
        self.normal_icon = None
        self.flash_icon = None
        
        # 创建托盘图标
        self.setup_tray()
        
        # 模拟消息数据
        self.current_messages = []
        self.read_status = {}
        
    def setup_tray(self):
        """设置系统托盘"""
        try:
            self.tray_icon, normal_icon_path, flash_icon_path = create_tray_icon(self)
            setup_message_flashing(self.tray_icon, normal_icon_path, flash_icon_path, self)
            print("系统托盘设置完成")
        except Exception as e:
            print(f"设置系统托盘时出错: {e}")
    
    def start_flashing(self):
        """开始闪烁测试"""
        try:
            # 模拟新消息
            test_message = {
                'id': int(time.time()),
                'title': '测试消息',
                'content': '这是一条测试消息，用于验证系统托盘闪烁功能',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.current_messages = [test_message]
            # 确保消息是未读状态
            self.read_status[test_message['id']] = False
            
            # 开始闪烁
            start_message_flashing(self)
            self.label.setText("闪烁中...双击托盘图标停止")
            print("开始闪烁测试")
            
        except Exception as e:
            print(f"开始闪烁时出错: {e}")
    
    def stop_flashing(self):
        """停止闪烁测试"""
        try:
            stop_message_flashing(self)
            self.label.setText("闪烁已停止")
            print("停止闪烁测试")
        except Exception as e:
            print(f"停止闪烁时出错: {e}")
    
    def hide_window(self):
        """隐藏窗口"""
        self.hide()
        self.label.setText("窗口已隐藏，双击托盘图标显示")
        print("窗口已隐藏")

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()