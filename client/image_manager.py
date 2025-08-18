import os
import base64
import hashlib
import subprocess
from datetime import datetime
from typing import Optional, Tuple
from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QHBoxLayout, QDesktopWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide2.QtGui import QPixmap, QImage, QCursor, QPainter
from PySide2.QtCore import Qt, QSize, QPoint

class ImageManager:
    """图片管理器 - 负责图片的保存、加载和显示"""
    
    def __init__(self, save_directory: str = None):
        if save_directory is None:
            # 默认保存到client目录下的saved_images文件夹
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.save_directory = os.path.join(current_dir, "saved_images")
        else:
            self.save_directory = save_directory
        self.ensure_save_directory()
    
    def ensure_save_directory(self):
        """确保保存目录存在"""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def generate_image_filename(self, message_id: int, image_data: str) -> str:
        """生成唯一的图片文件名"""
        # 使用消息ID和图片数据哈希生成唯一文件名
        hash_obj = hashlib.md5(f"{message_id}_{image_data}".encode())
        unique_hash = hash_obj.hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"msg_{message_id}_{timestamp}_{unique_hash}.png"
    
    def save_image_from_base64(self, message_id: int, image_data: str) -> Optional[str]:
        """从base64数据保存图片到本地
        
        Args:
            message_id: 消息ID
            image_data: base64编码的图片数据
            
        Returns:
            保存的文件路径，失败返回None
        """
        try:
            # 解码base64数据
            binary_data = base64.b64decode(image_data)
            
            # 生成文件名
            filename = self.generate_image_filename(message_id, image_data)
            filepath = os.path.join(self.save_directory, filename)
            
            # 保存图片
            with open(filepath, 'wb') as f:
                f.write(binary_data)
            
            return filepath
            
        except Exception as e:
            print(f"保存图片失败: {e}")
            return None
    
    def load_image_from_file(self, filepath: str) -> Optional[QImage]:
        """从文件加载图片
        
        Args:
            filepath: 图片文件路径
            
        Returns:
            QImage对象，失败返回None
        """
        try:
            image = QImage(filepath)
            if image.isNull():
                return None
            return image
        except Exception as e:
            print(f"加载图片失败: {e}")
            return None
    
    def load_image_from_base64(self, image_data: str) -> Optional[QImage]:
        """从base64数据加载图片
        
        Args:
            image_data: base64编码的图片数据
            
        Returns:
            QImage对象，失败返回None
        """
        try:
            binary_data = base64.b64decode(image_data)
            image = QImage()
            image.loadFromData(binary_data)
            return image if not image.isNull() else None
        except Exception as e:
            print(f"从base64加载图片失败: {e}")
            return None

class ImageViewerDialog(QDialog):
    """图片查看器对话框 - 支持滚轮缩放和1:1显示"""
    
    def __init__(self, image: QImage, image_path: str = None, parent=None):
        # 不设置父窗口，使其成为独立窗口
        super().__init__(None)
        self.image = image
        self.image_path = image_path
        self.parent_window = parent  # 保存父窗口引用
        self.current_scale = 1.0  # 当前缩放比例
        self.setup_ui()
        self.setup_window()
        
        # 如果有父窗口，监听其销毁事件
        if self.parent_window:
            self.parent_window.destroyed.connect(self.on_parent_destroyed)
    
    def on_parent_destroyed(self):
        """父窗口销毁时的处理"""
        # 延迟关闭自己，确保父窗口完全关闭
        from PySide2.QtCore import QTimer
        QTimer.singleShot(100, self.close)
    
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("图片查看器")
        self.setModal(False)
        
        # 主布局
        layout = QVBoxLayout()
        
        # 创建图形视图
        self.graphics_view = QGraphicsView()
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.graphics_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.graphics_view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # 创建场景
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        
        # 创建图片项
        self.pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(self.image))
        self.scene.addItem(self.pixmap_item)
        
        # 设置场景大小
        self.scene.setSceneRect(self.pixmap_item.boundingRect())
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 1:1显示按钮
        self.actual_size_button = QPushButton("1:1显示")
        self.actual_size_button.clicked.connect(self.reset_to_actual_size)
        self.actual_size_button.setStyleSheet(
            "QPushButton {"
            "    background-color: #4CAF50;"
            "    color: white;"
            "    border: 2px solid #333;"
            "    border-radius: 5px;"
            "    padding: 5px 15px;"
            "    font-weight: bold;"
            "    min-width: 80px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #45a049;"
            "    border-color: #45a049;"
            "}"
        )
        
        # 图片路径显示标签
        self.path_label = QLabel()
        if self.image_path:
            # 显示文件名而不是完整路径，节省空间
            filename = os.path.basename(self.image_path)
            self.path_label.setText(f"文件: {filename}")
            self.path_label.setStyleSheet(
                "QLabel {"
                "    background-color: #1e1e1e;"
                "    color: #f8f8f2;"
                "    padding: 5px 10px;"
                "    border: 1px solid #444;"
                "    border-radius: 3px;"
                "    font-size: 12px;"
                "}"
            )
            self.path_label.setToolTip(f"完整路径: {self.image_path}")
        else:
            self.path_label.setText("文件: 未保存")
            self.path_label.setStyleSheet(
                "QLabel {"
                "    background-color: #1e1e1e;"
                "    color: #888888;"
                "    padding: 5px 10px;"
                "    border: 1px solid #444;"
                "    border-radius: 3px;"
                "    font-size: 12px;"
                "}"
            )
        
        # 打开目录按钮
        self.open_folder_button = QPushButton("打开位置")
        self.open_folder_button.clicked.connect(self.open_image_folder)
        self.open_folder_button.setEnabled(self.image_path is not None)
        self.open_folder_button.setStyleSheet(
            "QPushButton {"
            "    background-color: #FF9800;"
            "    color: white;"
            "    border: 2px solid #333;"
            "    border-radius: 5px;"
            "    padding: 5px 15px;"
            "    font-weight: bold;"
            "    min-width: 80px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #F57C00;"
            "    border-color: #F57C00;"
            "}"
            "QPushButton:disabled {"
            "    background-color: #555555;"
            "    color: #888888;"
            "    border-color: #333333;"
            "}"
        )
        
        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet(
            "QPushButton {"
            "    background-color: #9898ee;"
            "    color: black;"
            "    border: 2px solid #333;"
            "    border-radius: 5px;"
            "    padding: 5px 15px;"
            "    font-weight: bold;"
            "    min-width: 80px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #1e90ff;"
            "    border-color: #1e90ff;"
            "}"
        )
        
        # 添加按钮到布局
        button_layout.addWidget(self.actual_size_button)
        button_layout.addWidget(self.path_label)
        button_layout.addStretch()
        button_layout.addWidget(self.open_folder_button)
        button_layout.addWidget(close_button)
        button_layout.setContentsMargins(10, 10, 10, 10)
        
        # 添加到主布局
        layout.addWidget(self.graphics_view)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # 启用滚轮事件
        self.graphics_view.wheelEvent = self.wheelEvent
    
    def update_image_display(self):
        """更新图片显示"""
        # 创建缩放后的pixmap
        scaled_pixmap = QPixmap.fromImage(self.image)
        if self.current_scale != 1.0:
            new_size = QSize(
                int(self.image.width() * self.current_scale),
                int(self.image.height() * self.current_scale)
            )
            scaled_pixmap = scaled_pixmap.scaled(
                new_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        
        # 更新图形项
        self.pixmap_item.setPixmap(scaled_pixmap)
        
        # 更新场景大小
        self.scene.setSceneRect(self.pixmap_item.boundingRect())
        
        # 更新窗口标题
        self.show_image_info()
    
    def reset_to_actual_size(self):
        """重置到1:1显示"""
        self.current_scale = 1.0
        self.update_image_display()
        
        # 调整窗口大小以适应1:1图片
        self.adjust_window_to_image()
    
    def adjust_window_to_image(self):
        """调整窗口大小以适应图片"""
        # 获取屏幕尺寸
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        # 计算合适的窗口大小（留出边距）
        margin = 100  # 窗口边距
        available_width = screen_width - margin
        available_height = screen_height - margin
        
        # 计算窗口大小（缩放后的图片尺寸 + 边框和按钮空间）
        image_display_width = int(self.image.width() * self.current_scale)
        image_display_height = int(self.image.height() * self.current_scale)
        
        window_width = min(image_display_width + 50, available_width)
        window_height = min(image_display_height + 150, available_height)  # 增加按钮空间
        
        # 设置窗口大小
        self.resize(window_width, window_height)
        
        # 始终相对于屏幕中心定位
        screen_center_x = screen_geometry.x() + screen_width // 2
        screen_center_y = screen_geometry.y() + screen_height // 2
        x = screen_center_x - self.width() // 2
        y = screen_center_y - self.height() // 2
        self.move(x, y)
    
    def wheelEvent(self, event):
        """处理滚轮事件 - 缩放图片"""
        # 获取滚轮增量
        delta = event.angleDelta().y()
        
        # 计算缩放因子
        if delta > 0:
            # 向上滚动，放大
            scale_factor = 1.2
        else:
            # 向下滚动，缩小
            scale_factor = 0.8
        
        # 限制缩放范围
        new_scale = self.current_scale * scale_factor
        if new_scale < 0.1:
            new_scale = 0.1
        elif new_scale > 10.0:
            new_scale = 10.0
        
        # 更新缩放比例
        self.current_scale = new_scale
        
        # 更新显示
        self.update_image_display()
        
        # 阻止事件继续传播
        event.accept()
    

    

    
    def setup_window(self):
        """设置窗口属性"""
        # 获取屏幕尺寸
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        # 计算合适的窗口大小（留出边距）
        margin = 100  # 窗口边距
        available_width = screen_width - margin
        available_height = screen_height - margin
        
        # 计算窗口大小（图片尺寸 + 边框和按钮空间）
        window_width = min(self.image.width() + 50, available_width)
        window_height = min(self.image.height() + 150, available_height)  # 增加按钮空间
        
        # 设置窗口大小
        self.resize(window_width, window_height)
        self.setMinimumSize(400, 300)
        
        # 设置深色主题
        self.setStyleSheet(
            "QDialog {"
            "    background-color: #2b2b2b;"
            "    color: #f8f8f2;"
            "}"
            "QScrollArea {"
            "    background-color: #1e1e1e;"
            "    border: 1px solid #444;"
            "}"
            "QLabel {"
            "    background-color: #1e1e1e;"
            "    color: #f8f8f2;"
            "}"
        )
        
        # 始终相对于屏幕中心定位
        screen_center_x = screen_geometry.x() + screen_width // 2
        screen_center_y = screen_geometry.y() + screen_height // 2
        x = screen_center_x - self.width() // 2
        y = screen_center_y - self.height() // 2
        self.move(x, y)
    
    def show_image_info(self):
        """显示图片信息"""
        scale_percent = int(self.current_scale * 100)
        info = f"图片尺寸: {self.image.width()} x {self.image.height()} 像素 - 缩放: {scale_percent}%"
        self.setWindowTitle(f"图片查看器 - {info}")
    
    def open_image_folder(self):
        """打开图片所在文件夹"""
        if self.image_path and os.path.exists(self.image_path):
            # 获取图片所在目录
            folder_path = os.path.dirname(self.image_path)
            # 使用系统默认程序打开文件夹
            if os.name == 'nt':  # Windows系统
                os.startfile(folder_path)
            else:  # 其他系统
                try:
                    subprocess.run(['open', folder_path], check=True)  # macOS
                except:
                    try:
                        subprocess.run(['xdg-open', folder_path], check=True)  # Linux
                    except:
                        print(f"无法打开文件夹: {folder_path}")

# 便捷函数
def create_image_viewer(image_data, parent=None, image_path: str = None) -> ImageViewerDialog:
    """创建图片查看器对话框
    
    Args:
        image_data: base64编码的图片数据 或 QImage对象
        parent: 父窗口（用于监听销毁事件，但不作为父窗口）
        image_path: 图片文件路径
        
    Returns:
        ImageViewerDialog对象
    """
    # 检查传入的是QImage对象还是base64字符串
    if isinstance(image_data, QImage):
        image = image_data
    else:
        # 如果是base64字符串，则进行解码
        image_manager = ImageManager()
        image = image_manager.load_image_from_base64(image_data)
    
    if image:
        # 创建图片查看器，传递parent用于监听销毁事件
        viewer = ImageViewerDialog(image, image_path, parent)
        viewer.show_image_info()
        return viewer
    else:
        return None

def get_saved_image_path(message_id: int, image_data: str, save_directory: str = None) -> Optional[str]:
    """获取已保存图片的路径
    
    Args:
        message_id: 消息ID
        image_data: base64编码的图片数据
        save_directory: 保存目录，默认为None时使用client目录下的saved_images
        
    Returns:
        已保存的文件路径，如果不存在则返回None
    """
    try:
        if save_directory is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            save_directory = os.path.join(current_dir, "saved_images")
            
        if not os.path.exists(save_directory):
            return None
            
        # 生成预期的文件名
        hash_obj = hashlib.md5(f"{message_id}_{image_data}".encode())
        unique_hash = hash_obj.hexdigest()[:8]
        
        # 查找匹配的文件
        for filename in os.listdir(save_directory):
            if filename.startswith(f"msg_{message_id}_") and filename.endswith(".png"):
                if unique_hash in filename:
                    return os.path.join(save_directory, filename)
        
        return None
    except Exception as e:
        print(f"获取保存图片路径失败: {e}")
        return None

def save_image_automatically(message_id: int, image_data: str, save_directory: str = None) -> Optional[str]:
    """自动保存图片
    
    Args:
        message_id: 消息ID
        image_data: base64编码的图片数据
        save_directory: 保存目录，默认为None时使用client目录下的saved_images
        
    Returns:
        保存的文件路径，失败返回None
    """
    image_manager = ImageManager(save_directory)
    return image_manager.save_image_from_base64(message_id, image_data)

def delete_saved_image(message_id: int, save_directory: str = None) -> bool:
    """删除指定消息ID的所有保存图片
    
    Args:
        message_id: 消息ID
        save_directory: 保存目录，默认为None时使用client目录下的saved_images
        
    Returns:
        删除是否成功
    """
    try:
        if save_directory is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            save_directory = os.path.join(current_dir, "saved_images")
            
        if not os.path.exists(save_directory):
            return True  # 目录不存在，视为删除成功
            
        deleted_count = 0
        
        # 查找并删除所有匹配该消息ID的图片文件
        for filename in os.listdir(save_directory):
            if filename.startswith(f"msg_{message_id}_") and filename.endswith(".png"):
                filepath = os.path.join(save_directory, filename)
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"已删除图片文件: {filepath}")
                except Exception as e:
                    print(f"删除图片文件失败 {filepath}: {e}")
        
        print(f"消息 {message_id} 的图片文件已删除，共删除 {deleted_count} 个文件")
        return deleted_count > 0
        
    except Exception as e:
        print(f"删除消息 {message_id} 的图片文件时发生错误: {e}")
        return False
