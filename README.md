# 通知系统

一个简洁的通知系统，包含服务端和PC客户端，支持文本、图片和图文混排消息的发送和接收。

## 系统架构

```
通知系统/
├── server/                # 服务端目录
│   ├── server.py         # 服务端程序
│   └── config.json       # 服务端配置文件
├── client/                # 客户端目录
│   ├── main.py           # 客户端主程序
│   ├── network_client.py # 网络客户端模块
│   ├── ui_module.py      # UI界面模块
│   ├── win_client.ui     # UI界面定义文件
│   └── config.json       # 客户端配置文件
├── config.json           # 根目录配置文件（模板）
├── requirements.txt       # Python依赖包
├── start.bat             # 启动脚本
└── README.md             # 说明文档
```

## 功能特性

### 服务端功能
- 接收文本、图片、图文混排消息
- 消息存储和转发
- RESTful API接口
- 健康检查接口
- 配置文件管理

### 客户端功能
- 模块化设计
- 实时消息列表显示
- 消息详情查看
- 连接状态监控
- 自动重连机制
- 测试消息发送

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务端

```bash
cd server
python server.py
```

或者使用启动脚本：
```bash
start.bat
```

服务端将在 `0.0.0.0:5001` 上启动，支持接收HTTP请求。

### 3. 启动客户端

```bash
cd client
python main.py
```

或者使用启动脚本：
```bash
start.bat
```

客户端将启动图形界面，自动连接到服务端。

## 配置文件说明

`config.json` 文件包含系统配置：

```json
{
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
```

## API接口文档

### 1. 发送消息

**POST** `/api/messages`

请求体格式：
```json
{
  "type": "text|image|mixed",
  "content": "消息内容",
  "image_data": "base64编码的图片数据",
  "title": "消息标题"
}
```

响应：
```json
{
  "success": true,
  "message_id": 1,
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### 2. 获取消息列表

**GET** `/api/messages`

响应：
```json
{
  "messages": [
    {
      "id": 1,
      "type": "text",
      "timestamp": "2024-01-01T12:00:00.000000",
      "content": "消息内容",
      "image_data": "",
      "title": "消息标题"
    }
  ],
  "total": 1
}
```

### 3. 获取单个消息

**GET** `/api/messages/{message_id}`

响应：
```json
{
  "id": 1,
  "type": "text",
  "timestamp": "2024-01-01T12:00:00.000000",
  "content": "消息内容",
  "image_data": "",
  "title": "消息标题"
}
```

### 4. 删除消息

**DELETE** `/api/messages/{message_id}`

响应：
```json
{
  "success": true
}
```

### 5. 健康检查

**GET** `/api/health`

响应：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000",
  "messages_count": 1
}
```

## 使用示例

### 发送文本消息

```python
import requests
import json

url = "http://localhost:5001/api/messages"
data = {
    "type": "text",
    "content": "这是一条文本消息",
    "title": "文本通知"
}

response = requests.post(url, json=data)
print(response.json())
```

### 发送图片消息

```python
import base64
import requests

# 读取图片并转换为base64
with open("image.jpg", "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode()

url = "http://localhost:5001/api/messages"
data = {
    "type": "image",
    "content": "这是一张图片",
    "image_data": image_data,
    "title": "图片通知"
}

response = requests.post(url, json=data)
print(response.json())
```

### 发送图文混排消息

```python
import base64
import requests

# 读取图片并转换为base64
with open("image.jpg", "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode()

url = "http://localhost:5001/api/messages"
data = {
    "type": "mixed",
    "content": "这是一条图文混排的消息，包含文本和图片",
    "image_data": image_data,
    "title": "图文通知"
}

response = requests.post(url, json=data)
print(response.json())
```

## 客户端界面说明

### 主界面布局
- **左侧**：消息列表，显示所有接收到的消息预览
- **右侧**：消息详情，显示选中消息的完整内容
- **底部**：状态栏，显示连接状态和操作按钮

### 功能按钮
- **刷新**：手动刷新消息列表
- **清空**：清空右侧消息详情显示
- **发送测试消息**：发送一条测试消息到服务端

### 连接状态
- **绿色**：已连接到服务端
- **红色**：未连接或连接错误

## 注意事项

1. 确保服务端先启动，客户端才能正常连接
2. 配置文件中的端口设置需要保持一致
3. 图片数据使用base64编码传输，注意大小限制
4. 客户端会自动尝试重连，间隔时间可在配置文件中设置
5. 日志文件会记录系统运行状态和错误信息

## 故障排除

### 常见问题

1. **客户端无法连接服务端**
   - 检查服务端是否已启动
   - 检查网络连接和防火墙设置
   - 确认配置文件中的服务器地址和端口正确

2. **消息发送失败**
   - 检查服务端是否正常运行
   - 确认消息格式正确
   - 查看日志文件获取详细错误信息

3. **UI界面显示异常**
   - 确认PySide2已正确安装
   - 检查UI文件是否存在
   - 重启应用程序

### 日志查看

日志文件位置：`app.log`

包含以下信息：
- 系统启动和关闭记录
- 连接状态变化
- 消息发送和接收记录
- 错误和异常信息

## 扩展功能

系统采用模块化设计，可以轻松扩展以下功能：

1. **消息推送**：集成WebSocket实现实时推送
2. **用户认证**：添加用户登录和权限管理
3. **消息持久化**：使用数据库存储消息
4. **多媒体支持**：支持音频、视频等更多媒体类型
5. **消息过滤**：添加消息分类和过滤功能
6. **通知提醒**：添加桌面通知或声音提醒

## 许可证

本项目采用MIT许可证，详情请参阅LICENSE文件。