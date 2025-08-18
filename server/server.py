import json
import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import base64
import threading
import time
import sqlite3
import schedule

app = Flask(__name__)
CORS(app)

# 数据库配置
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'messages.db')

def init_database():
    """初始化SQLite数据库"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 创建消息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            content TEXT,
            image_data TEXT,
            title TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    logging.info("Database initialized")

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def clear_database():
    """清空数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='messages'")
    conn.commit()
    conn.close()
    logging.info("Database cleared")

def setup_scheduler():
    """设置定时任务 - 每周日23:00清空数据库"""
    schedule.every().sunday.at("23:00").do(clear_database)
    logging.info("Scheduler setup: database will be cleared every Sunday at 23:00")
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

# 配置日志
def setup_logging():
    config = load_config()
    logging.basicConfig(
        level=getattr(logging, config['logging']['level']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config['logging']['file']),
            logging.StreamHandler()
        ]
    )

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/api/messages', methods=['POST'])
def receive_message():
    try:
        data = request.get_json()
        
        # 验证必要字段
        if 'type' not in data:
            return jsonify({'error': 'Message type is required'}), 400
            
        if data['type'] not in ['text', 'image', 'mixed']:
            return jsonify({'error': 'Invalid message type'}), 400
            
        # 创建消息对象
        message = {
            'type': data['type'],
            'timestamp': datetime.now().isoformat(),
            'content': data.get('content', ''),
            'image_data': data.get('image_data', ''),  # base64编码的图片数据
            'title': data.get('title', '无标题')
        }
        
        # 插入数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (type, timestamp, content, image_data, title)
            VALUES (?, ?, ?, ?, ?)
        ''', (message['type'], message['timestamp'], message['content'], 
              message['image_data'], message['title']))
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logging.info(f"Received message: {message_id}, type: {message['type']}")
        
        # 转发消息给所有连接的客户端（这里简化处理，实际可能需要WebSocket）
        return jsonify({
            'success': True,
            'message_id': message_id,
            'timestamp': message['timestamp']
        }), 200
        
    except Exception as e:
        logging.error(f"Error receiving message: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages', methods=['GET'])
def get_messages():
    try:
        # 从数据库获取所有消息，按时间倒序
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM messages ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        conn.close()
        
        # 转换为字典列表
        messages = []
        for row in rows:
            messages.append({
                'id': row['id'],
                'type': row['type'],
                'timestamp': row['timestamp'],
                'content': row['content'],
                'image_data': row['image_data'],
                'title': row['title']
            })
        
        return jsonify({
            'messages': messages,
            'total': len(messages)
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting messages: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/<int:message_id>', methods=['GET'])
def get_message(message_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM messages WHERE id = ?', (message_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Message not found'}), 404
            
        message = {
            'id': row['id'],
            'type': row['type'],
            'timestamp': row['timestamp'],
            'content': row['content'],
            'image_data': row['image_data'],
            'title': row['title']
        }
        
        return jsonify(message), 200
        
    except Exception as e:
        logging.error(f"Error getting message {message_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM messages WHERE id = ?', (message_id,))
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        if affected_rows == 0:
            return jsonify({'error': 'Message not found'}), 404
            
        logging.info(f"Deleted message: {message_id}")
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logging.error(f"Error deleting message {message_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages', methods=['DELETE'])
def delete_all_messages():
    """删除所有消息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 先获取要删除的消息数量
        cursor.execute('SELECT COUNT(*) FROM messages')
        count = cursor.fetchone()[0]
        
        # 删除所有消息
        cursor.execute('DELETE FROM messages')
        cursor.execute('DELETE FROM sqlite_sequence WHERE name=\'messages\'')
        conn.commit()
        conn.close()
        
        logging.info(f"Deleted all messages: {count} messages removed")
        return jsonify({
            'success': True,
            'deleted_count': count
        }), 200
        
    except Exception as e:
        logging.error(f"Error deleting all messages: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM messages')
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'messages_count': count
        }), 200
        
    except Exception as e:
        logging.error(f"Error in health check: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    setup_logging()
    config = load_config()
    
    # 初始化数据库
    init_database()
    
    # 设置定时任务
    setup_scheduler()
    
    logging.info("Starting message server...")
    logging.info(f"Server will run on {config['server']['host']}:{config['server']['port']}")
    
    app.run(
        host=config['server']['host'],
        port=config['server']['port'],
        debug=True,
        threaded=True
    )