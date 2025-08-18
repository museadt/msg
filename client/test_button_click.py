import sys
import os
import json
from PySide2.QtWidgets import QApplication
from network_client import MessageClient
from ui_client import MessageUI

def test_button_click():
    """测试按钮点击功能"""
    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("配置加载成功:", config)
    
    # 创建网络客户端
    client = MessageClient(config)
    print("网络客户端创建成功")
    
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MessageUI(client)
    window.show()
    
    # 等待窗口初始化完成
    app.processEvents()
    
    print("=== 开始测试按钮点击功能 ===")
    
    # 检查按钮是否存在
    if hasattr(window, 'all_read_pushButton') and window.all_read_pushButton:
        print("找到 all_read_pushButton 按钮")
        
        # 模拟按钮点击
        print("模拟点击 all_read_pushButton 按钮...")
        window.all_read_pushButton.click()
        
        # 处理事件
        app.processEvents()
        
        print("按钮点击测试完成")
    else:
        print("错误: 未找到 all_read_pushbutton 按钮")
        
        # 打印所有可用的按钮属性
        print("可用按钮属性:")
        for attr in dir(window):
            if 'button' in attr.lower():
                print(f"  {attr}: {getattr(window, attr, 'None')}")
    
    # 关闭窗口
    window.close()
    app.quit()

if __name__ == "__main__":
    test_button_click()