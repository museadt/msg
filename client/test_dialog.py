import sys
import os
sys.path.append(os.path.dirname(__file__))

from PySide2.QtWidgets import QApplication, QMessageBox
from ui_client import CustomMessageBox

def test_custom_question():
    app = QApplication(sys.argv)
    
    # 测试Yes/No对话框
    result = CustomMessageBox.custom_question(
        None, 
        "测试对话框", 
        "这是一个测试消息，请点击Yes或No按钮。",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    
    print(f"用户选择: {result}")
    
    if result == QMessageBox.Yes:
        print("用户点击了Yes按钮")
    elif result == QMessageBox.No:
        print("用户点击了No按钮")
    else:
        print("用户取消或未选择")

if __name__ == "__main__":
    test_custom_question()