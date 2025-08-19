import sys
import os
import json
import threading
import time
from PySide2.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon, QMenu
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QIcon

# Windows API相关
if sys.platform == 'win32':
    try:
        import win32api
        import win32con
        import win32event
        import win32gui
        import win32process
        WINDOWS_API_AVAILABLE = True
    except ImportError:
        WINDOWS_API_AVAILABLE = False
else:
    WINDOWS_API_AVAILABLE = False

# 导入自定义模块
from network_client import MessageClient
from ui_client import MessageUI

def load_config():
    """加载配置文件"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 如果配置文件不存在，创建默认配置
        default_config = {
            "server": {
                "host": "0.0.0.0",
                "port": 5001
            },
            "client": {
                "server_host": "localhost",
                "server_port": 5001,
                "reconnect_interval": 5
            },
            "logging": {
                "level": "INFO",
                "file": "app.log"
            }
        }
        
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        return default_config
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        sys.exit(1)

def create_single_instance_mutex():
    """创建单实例互斥体"""
    if not WINDOWS_API_AVAILABLE:
        print("警告: Windows API不可用，无法启用单实例功能")
        return None
    
    try:
        # 创建唯一的互斥体名称
        mutex_name = "Global\\MyMessageClient_SingleInstance_Mutex"
        
        # 尝试创建互斥体
        mutex = win32event.CreateMutex(None, False, mutex_name)
        
        # 检查是否已经存在
        # ERROR_ALREADY_EXISTS = 183
        if win32api.GetLastError() == 183:
            print("检测到已有实例正在运行")
            return None
        
        print("单实例互斥体创建成功")
        return mutex
    except Exception as e:
        print(f"创建单实例互斥体失败: {e}")
        return None

def find_and_activate_existing_instance():
    """查找已运行的实例窗口（简化版，仅用于检测）"""
    if not WINDOWS_API_AVAILABLE:
        print("警告: Windows API不可用，无法检测已有实例")
        return False
    
    try:
        # 窗口标题
        window_title = "消息客户端"
        
        def callback(hwnd, extra):
            """枚举窗口回调函数"""
            window_text = win32gui.GetWindowText(hwnd)
            if window_title in window_text:
                print(f"找到已有实例窗口: {window_text}")
                return False  # 停止枚举
            return True  # 继续枚举
        
        # 枚举所有窗口
        win32gui.EnumWindows(callback, None)
        return True
        
    except Exception as e:
        print(f"检测已有实例失败: {e}")
        return False

def is_instance_running():
    """检查是否已有实例运行"""
    if not WINDOWS_API_AVAILABLE:
        # 如果Windows API不可用，使用文件锁作为备选方案
        lock_file = os.path.join(os.path.dirname(__file__), ".instance_lock")
        try:
            # 尝试创建并锁定文件
            import fcntl
            lock_fd = open(lock_file, 'w')
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # 如果成功，说明没有其他实例运行
            lock_fd.write(str(os.getpid()))
            lock_fd.flush()
            return lock_fd
        except (ImportError, IOError):
            # 在Windows上或者文件锁定失败
            return None
    
    # 使用Windows互斥体检测
    mutex = create_single_instance_mutex()
    if mutex is None:
        # 已有实例运行
        return None
    
    return mutex

def create_tray_icon(main_window):
    """创建系统托盘图标"""
    # 加载图标文件
    icons_dir = os.path.join(os.path.dirname(__file__), 'icons')
    normal_icon_path = os.path.join(icons_dir, 'normal.bmp')
    flash_icon_path = os.path.join(icons_dir, 'flash.bmp')
    
    # 创建托盘图标
    tray_icon = QSystemTrayIcon()
    
    # 检查图标文件是否存在
    if os.path.exists(normal_icon_path):
        normal_icon = QIcon(normal_icon_path)
        tray_icon.setIcon(normal_icon)
        print("托盘图标加载成功")
    else:
        print(f"警告: 未找到正常状态图标文件: {normal_icon_path}")
        # 使用默认图标
        tray_icon.showMessage("消息客户端", "托盘图标文件未找到", QSystemTrayIcon.Warning)
    
    # 创建托盘菜单
    tray_menu = QMenu()
    
    # 显示/隐藏主窗口动作
    show_action = tray_menu.addAction("显示主窗口")
    show_action.triggered.connect(main_window.show)
    
    hide_action = tray_menu.addAction("隐藏主窗口")
    hide_action.triggered.connect(main_window.hide)
    
    tray_menu.addSeparator()
    
    # 退出动作
    quit_action = tray_menu.addAction("退出")
    quit_action.triggered.connect(main_window.force_close)
    
    # 设置托盘菜单
    tray_icon.setContextMenu(tray_menu)
    
    # 显示托盘图标
    tray_icon.show()
    
    # 双击托盘图标显示/隐藏主窗口，并停止闪烁
    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.DoubleClick:
            print("双击托盘图标：开始处理")
            # 停止消息闪烁
            stop_message_flashing(main_window)
            # 延迟显示主窗口，确保UI刷新完成
            QTimer.singleShot(100, lambda: show_main_window_after_refresh(main_window))
    
    def show_main_window_after_refresh(main_window):
        """在UI刷新完成后显示主窗口"""
        # 显示主窗口并置于前台
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        # 在Windows上确保窗口能够真正置于前台
        if sys.platform == 'win32':
            # 设置窗口为前台窗口
            try:
                import win32gui
                import win32con
                # 获取窗口句柄
                hwnd = int(main_window.winId())
                # 如果窗口最小化，先恢复
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                # 将窗口置于前台
                win32gui.SetForegroundWindow(hwnd)
                print("Windows前台窗口设置完成")
            except ImportError:
                print("pywin32未安装，使用默认方法置顶窗口")
                # 使用Qt内置的方法再次尝试置顶
                main_window.setWindowState(main_window.windowState() & ~Qt.WindowMinimized)
                main_window.show()
                main_window.raise_()
                main_window.activateWindow()
            except Exception as e:
                print(f"设置Windows前台窗口失败: {e}")
        
        # 强制刷新UI
        main_window.update()
        QApplication.processEvents()
        print("双击托盘图标：主窗口显示完成")
    
    tray_icon.activated.connect(on_tray_activated)
    
    return tray_icon, normal_icon_path, flash_icon_path

def setup_message_flashing(tray_icon, normal_icon_path, flash_icon_path, main_window):
    """设置消息闪烁功能"""
    # 检查图标文件是否存在
    if not os.path.exists(normal_icon_path) or not os.path.exists(flash_icon_path):
        print("警告: 图标文件不完整，无法启用闪烁功能")
        return
    
    # 加载图标
    normal_icon = QIcon(normal_icon_path)
    flash_icon = QIcon(flash_icon_path)
    
    # 创建闪烁定时器
    flash_timer = QTimer()
    flash_timer.timeout.connect(lambda: toggle_tray_icon(tray_icon, normal_icon, flash_icon))
    
    # 设置闪烁状态
    main_window.is_flashing = False
    main_window.flash_timer = flash_timer
    main_window.normal_icon = normal_icon
    main_window.flash_icon = flash_icon
    main_window.tray_icon = tray_icon
    
    # 连接消息更新信号来触发闪烁
    if hasattr(main_window, 'message_thread'):
        main_window.message_thread.messages_updated.connect(
            lambda messages: check_new_messages_and_flash(main_window, messages)
        )
    
    print("消息闪烁功能设置完成")

def toggle_tray_icon(tray_icon, normal_icon, flash_icon):
    """切换托盘图标状态"""
    if tray_icon.icon().cacheKey() == normal_icon.cacheKey():
        tray_icon.setIcon(flash_icon)
    else:
        tray_icon.setIcon(normal_icon)

def check_new_messages_and_flash(main_window, messages):
    """检查新消息并触发闪烁"""
    if not messages:
        return
    
    # 检查是否有新消息（未读消息）
    has_new_messages = False
    for message in messages:
        message_id = message.get('id')
        # 检查消息是否未读（不在read_status中或值为False）
        if message_id and (message_id not in main_window.read_status or not main_window.read_status.get(message_id, False)):
            has_new_messages = True
            break
    
    # 如果有新消息且当前没有在闪烁，则开始闪烁
    if has_new_messages and not main_window.is_flashing:
        start_message_flashing(main_window)

def start_message_flashing(main_window):
    """开始消息闪烁"""
    if main_window.is_flashing:
        return
    
    main_window.is_flashing = True
    main_window.flash_timer.start(500)  # 每500毫秒切换一次图标
    
    # 显示通知
    main_window.tray_icon.showMessage(
        "新消息", 
        "您有新的消息", 
        QSystemTrayIcon.Information,
        3000  # 显示3秒
    )
    
    print("开始消息闪烁")

def test_flashing(main_window):
    """测试闪烁功能"""
    print("测试闪烁功能...")
    start_message_flashing(main_window)

def stop_message_flashing(main_window):
    """停止消息闪烁（不自动标记消息为已读）"""
    if not main_window.is_flashing:
        return
    
    main_window.is_flashing = False
    main_window.flash_timer.stop()
    main_window.tray_icon.setIcon(main_window.normal_icon)
    
    print("停止消息闪烁")
    
    # 注意：不再自动将所有消息标记为已读
    # 让用户通过点击消息或全部已读按钮来控制已读状态
    # 这样可以避免双击托盘图标时红点不消失的问题

def main():
    """主程序入口"""
    # 单实例检测
    instance_lock = is_instance_running()
    if instance_lock is None:
        # 创建QApplication实例用于显示弹窗
        app = QApplication(sys.argv)
        QMessageBox.information(None, "提示", "程序已在运行，请不要重复启动！")
        print("已有实例正在运行，显示提示后退出")
        sys.exit(0)
    
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 设置应用程序窗口图标
    icons_dir = os.path.join(os.path.dirname(__file__), 'icons')
    normal_icon_path = os.path.join(icons_dir, 'normal.bmp')
    if os.path.exists(normal_icon_path):
        try:
            app_icon = QIcon(normal_icon_path)
            app.setWindowIcon(app_icon)
            print("应用程序图标设置成功")
        except Exception as e:
            print(f"设置应用程序图标失败: {e}")
    else:
        print("提示: 未找到normal.bmp图标文件，跳过设置应用程序图标")
    
    # 加载配置
    config = load_config()
    print(f"配置加载成功: {config}")
    
    # 创建网络客户端
    try:
        client = MessageClient(config)
        print("网络客户端创建成功")
        
        # 启动连接监控
        client.start_connection_monitor()
        print("连接监控已启动")
        
    except Exception as e:
        QMessageBox.critical(None, "错误", f"创建网络客户端失败: {str(e)}")
        # 清理互斥体
        cleanup_instance_lock(instance_lock)
        sys.exit(1)
    
    # 创建主窗口
    try:
        main_window = MessageUI(client)
        main_window.show()
        print("主窗口创建成功")
        
    except Exception as e:
        QMessageBox.critical(None, "错误", f"创建主窗口失败: {str(e)}")
        # 清理互斥体
        cleanup_instance_lock(instance_lock)
        sys.exit(1)
    
    # 创建托盘图标
    try:
        tray_icon, normal_icon_path, flash_icon_path = create_tray_icon(main_window)
        print("托盘图标创建成功")
        
        # 等待消息线程创建完成后设置消息闪烁功能
        def setup_flashing_when_ready():
            if hasattr(main_window, 'message_thread') and main_window.message_thread:
                # 设置消息闪烁功能
                setup_message_flashing(tray_icon, normal_icon_path, flash_icon_path, main_window)
                # 连接消息更新信号来触发闪烁
                main_window.message_thread.messages_updated.connect(
                    lambda messages: check_new_messages_and_flash(main_window, messages)
                )
                print("消息闪烁功能设置完成")
            else:
                # 如果消息线程还没创建，稍后再试
                QTimer.singleShot(100, setup_flashing_when_ready)
        
        # 延迟设置闪烁功能，只设置一次
        QTimer.singleShot(500, setup_flashing_when_ready)
        
    except Exception as e:
        print(f"创建托盘图标时发生错误: {str(e)}")
        # 托盘图标创建失败不影响程序运行
    
    # 设置程序退出时的清理函数
    def cleanup():
        print("程序退出，清理资源")
        
        # 保存窗口位置
        if hasattr(main_window, 'save_window_position'):
            try:
                main_window.save_window_position()
                print("窗口位置已保存")
            except Exception as e:
                print(f"保存窗口位置失败: {e}")
        
        # 先停止消息处理线程
        if hasattr(main_window, 'message_thread'):
            try:
                main_window.message_thread.stop()
                print("消息处理线程已停止")
            except Exception as e:
                print(f"停止消息处理线程失败: {e}")
        
        # 关闭网络客户端
        if hasattr(main_window, 'client'):
            try:
                main_window.client.close()
                print("网络客户端已关闭")
            except Exception as e:
                print(f"关闭网络客户端失败: {e}")
        
        # 清理互斥体
        cleanup_instance_lock(instance_lock)
    
    # 连接应用程序退出信号
    app.aboutToQuit.connect(cleanup)
    
    # 运行应用程序
    print("应用程序启动成功")
    sys.exit(app.exec_())

def cleanup_instance_lock(instance_lock):
    """清理实例锁资源"""
    try:
        if WINDOWS_API_AVAILABLE and hasattr(instance_lock, 'Close'):
            # 清理Windows互斥体
            win32api.CloseHandle(instance_lock)
            print("Windows互斥体已清理")
        elif hasattr(instance_lock, 'close'):
            # 清理文件锁
            instance_lock.close()
            # 删除锁文件
            lock_file = os.path.join(os.path.dirname(__file__), ".instance_lock")
            if os.path.exists(lock_file):
                os.remove(lock_file)
            print("文件锁已清理")
    except Exception as e:
        print(f"清理实例锁失败: {e}")

if __name__ == "__main__":
    main()