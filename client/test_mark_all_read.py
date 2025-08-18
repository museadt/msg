import sys
import os
import json
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtCore import QTimer

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui_client import MessageUI
from network_client import MessageClient

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return None

def test_mark_all_as_read():
    """测试全部已读功能"""
    app = QApplication(sys.argv)
    
    try:
        # 加载配置
        config = load_config()
        if not config:
            print("无法加载配置文件")
            sys.exit(1)
        
        # 创建客户端
        client = MessageClient(config)
        
        # 创建UI
        ui = MessageUI(client)
        ui.show()
        
        # 等待UI加载完成
        def test_functionality():
            print("开始测试全部已读功能...")
            
            # 检查是否有未读消息
            has_unread = False
            unread_count = 0
            for message in ui.current_messages:
                message_id = message.get('id')
                if message_id and not ui.read_status.get(message_id, False):
                    has_unread = True
                    unread_count += 1
            
            print(f"当前未读消息数量: {unread_count}")
            
            if has_unread:
                print("调用 mark_all_as_read 方法...")
                # 模拟用户点击全部已读按钮
                ui.mark_all_as_read()
                print("mark_all_as_read 方法调用完成")
            else:
                print("没有未读消息，无法测试全部已读功能")
                
            # 5秒后关闭应用
            QTimer.singleShot(5000, app.quit)
        
        # 3秒后开始测试
        QTimer.singleShot(3000, test_functionality)
        
        # 运行应用
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"测试失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_mark_all_as_read()