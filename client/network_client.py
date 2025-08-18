import json
import requests
import logging
import time
import threading
from typing import List, Dict, Optional
from datetime import datetime

class MessageClient:
    def __init__(self, config: Dict):
        self.config = config
        self.server_url = f"http://{config['client']['server_host']}:{config['client']['server_port']}"
        self.reconnect_interval = config['client']['reconnect_interval']
        self.is_connected = False
        self.monitor_thread = None
        self.should_stop = False
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=getattr(logging, self.config['logging']['level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('MessageClient')
    
    def check_connection(self) -> bool:
        """检查服务器连接状态"""
        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=5)
            if response.status_code == 200:
                self.is_connected = True
                self.logger.info("Connected to server")
                return True
            else:
                self.is_connected = False
                self.logger.warning(f"Server returned status code: {response.status_code}")
                return False
        except Exception as e:
            self.is_connected = False
            self.logger.error(f"Connection error: {str(e)}")
            return False
    
    def get_messages(self) -> List[Dict]:
        """获取所有消息"""
        try:
            response = requests.get(f"{self.server_url}/api/messages", timeout=10)
            if response.status_code == 200:
                data = response.json()
                messages = data.get('messages', [])
                total = data.get('total', 0)
                
                # 如果总消息数大于当前返回的消息数，说明有分页
                if total > len(messages):
                    self.logger.info(f"Found {total} total messages, but only {len(messages)} returned. Fetching all messages...")
                    all_messages = messages.copy()
                    
                    # 获取每个消息的详情
                    for i in range(len(messages), total):
                        message_detail = self.get_message(i)
                        if message_detail:
                            all_messages.append(message_detail)
                        else:
                            self.logger.warning(f"Failed to get message {i}")
                    
                    return all_messages
                else:
                    return messages
            else:
                self.logger.error(f"Failed to get messages: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Error getting messages: {str(e)}")
            return []
    
    def get_message(self, message_id: int) -> Optional[Dict]:
        """获取单个消息详情"""
        try:
            response = requests.get(f"{self.server_url}/api/messages/{message_id}", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Failed to get message {message_id}: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting message {message_id}: {str(e)}")
            return None
    
    def send_message(self, message_type: str, content: str = "", image_data: str = "", title: str = "") -> bool:
        """发送消息到服务器
        
        Args:
            message_type: 消息类型 ('text', 'image', 'mixed')
            content: 文本内容
            image_data: base64编码的图片数据
            title: 消息标题
        
        Returns:
            bool: 发送是否成功
        """
        try:
            message_data = {
                'type': message_type,
                'content': content,
                'image_data': image_data,
                'title': title or f"{message_type.upper()}消息"
            }
            
            response = requests.post(
                f"{self.server_url}/api/messages",
                json=message_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Message sent successfully: {result.get('message_id')}")
                return True
            else:
                self.logger.error(f"Failed to send message: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            return False
    
    def delete_message(self, message_id: int) -> bool:
        """删除消息"""
        try:
            response = requests.delete(f"{self.server_url}/api/messages/{message_id}", timeout=10)
            if response.status_code == 200:
                self.logger.info(f"Message deleted successfully: {message_id}")
                return True
            else:
                self.logger.error(f"Failed to delete message {message_id}: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Error deleting message {message_id}: {str(e)}")
            return False
    
    def delete_all_messages(self) -> bool:
        """删除所有消息"""
        try:
            response = requests.delete(f"{self.server_url}/api/messages", timeout=30)
            if response.status_code == 200:
                result = response.json()
                deleted_count = result.get('deleted_count', 0)
                self.logger.info(f"All messages deleted successfully: {deleted_count} messages removed")
                return True
            else:
                self.logger.error(f"Failed to delete all messages: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Error deleting all messages: {str(e)}")
            return False
    
    def start_connection_monitor(self):
        """启动连接监控线程"""
        def monitor():
            while not self.should_stop:
                self.check_connection()
                time.sleep(self.reconnect_interval)
        
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Connection monitor started")
    
    def close(self):
        """关闭网络客户端和停止线程"""
        self.logger.info("Closing MessageClient...")
        
        # 停止监控线程
        self.should_stop = True
        if self.monitor_thread and self.monitor_thread.is_alive():
            # 等待线程结束，最多等待2秒
            self.monitor_thread.join(timeout=2.0)
            if self.monitor_thread.is_alive():
                self.logger.warning("Monitor thread did not stop gracefully")
        
        self.logger.info("MessageClient closed")
    
    def format_message_preview(self, message: Dict) -> str:
        """格式化消息预览文本 - 显示标题、时间和部分内容"""
        title = message.get('title', '无标题')
        timestamp = message.get('timestamp', '')
        content = message.get('content', '')
        
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime('%H:%M:%S')
        except:
            time_str = timestamp
        
        # 获取内容预览（显示2行）
        content_preview = ''
        if content and content.strip():
            # 移除多余的换行符和空格，但保留段落结构
            clean_content = content.strip()
            # 将连续的换行符替换为单个空格
            import re
            clean_content = re.sub(r'\n+', ' ', clean_content)
            clean_content = re.sub(r'\r+', '', clean_content)
            
            # 限制内容预览长度为3行，每行约30个字符（适应261像素宽度）
            max_chars_per_line = 30
            max_total_chars = max_chars_per_line * 3
            
            if len(clean_content) > max_total_chars:
                # 如果内容超过3行，截断并添加省略号
                first_line = clean_content[:max_chars_per_line]
                second_line = clean_content[max_chars_per_line:max_chars_per_line*2]
                third_line = clean_content[max_chars_per_line*2:max_total_chars]
                content_preview = f"{first_line}\n{second_line}\n{third_line}..."
            elif len(clean_content) > max_chars_per_line * 2:
                # 如果内容超过2行但不超过3行，分成三行
                first_line = clean_content[:max_chars_per_line]
                second_line = clean_content[max_chars_per_line:max_chars_per_line*2]
                third_line = clean_content[max_chars_per_line*2:]
                content_preview = f"{first_line}\n{second_line}\n{third_line}"
            elif len(clean_content) > max_chars_per_line:
                # 如果内容超过1行但不超过2行，分成两行
                first_line = clean_content[:max_chars_per_line]
                second_line = clean_content[max_chars_per_line:]
                content_preview = f"{first_line}\n{second_line}"
            else:
                # 如果内容不超过1行，直接显示
                content_preview = clean_content
            
        # 显示标题、时间和内容预览 - 时间右对齐
        # 使用字符串格式化，标题左对齐，时间右对齐
        max_title_length = 28  # 标题最大长度（减少2个中文字符宽度，让时间右对齐）
        if len(title) > max_title_length:
            title_display = title[:max_title_length-3] + "..."
        else:
            title_display = title.ljust(max_title_length)
        
        if content_preview:
            return f"{title_display}{time_str}\n{content_preview}"
        else:
            return f"{title_display}{time_str}"
    
    def format_message_detail(self, message: Dict) -> str:
        """格式化消息详情文本"""
        title = message.get('title', '无标题')
        timestamp = message.get('timestamp', '')
        msg_type = message.get('type', '未知')
        content = message.get('content', '')
        
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            time_str = timestamp
        
        detail = f"标题: {title}  |  时间: {time_str}  |  类型: {msg_type}  |  ID: {message.get('id', 'N/A')}\n"
        detail += "-" * 82 + "\n"
        
        if content:
            detail += f"内容:\n{content}\n\n"
        
        if message.get('image_data'):
            detail += "[包含图片数据]\n"
        
        return detail