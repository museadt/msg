#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图文消息发送函数
功能：提供便捷的函数接口来发送图文消息到消息服务器
"""

# 导入必要的模块
import requests    # 用于发送HTTP请求
import base64      # 用于图片的base64编码
import os          # 用于文件路径操作


def send_mixed_message(image_path, text_content, title="图文消息", server_url="http://127.0.0.1:5001"):
    """
    发送图文混合消息到服务器
    
    参数:
        image_path (str): 图片文件的完整路径
        text_content (str): 消息的文字内容
        title (str): 消息标题，默认为"图文消息"
        server_url (str): 服务器地址，默认为"http://127.0.0.1:5001"
    
    返回:
        bool: 发送成功返回True，失败返回False
    """
    try:
        # 检查图片文件是否存在
        if not os.path.exists(image_path):
            print(f"❌ 图片文件不存在: {image_path}")
            return False
        
        # 读取图片文件并进行base64编码
        # 'rb'表示以二进制模式读取文件，确保图片数据不会被错误解析
        with open(image_path, 'rb') as f:
            image_content = f.read()  # 读取图片的二进制数据
        
        # 将图片的二进制数据编码为base64字符串
        # base64编码可以将二进制数据转换为文本格式，便于在HTTP请求中传输
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # 构建要发送的消息数据结构
        # 这个字典包含了服务器处理图文消息所需的所有信息
        message_data = {
            "type": "mixed",                              # 消息类型：mixed表示图文混合消息
            "content": text_content,                       # 消息的文字内容
            "title": title,                                # 消息标题，显示在客户端消息列表中
            "image_data": image_base64,                   # 图片的base64编码数据
            "image_name": os.path.basename(image_path)    # 图片文件名，从完整路径中提取
        }
        
        # 向服务器发送POST请求，提交消息数据
        # 使用json参数自动将Python字典转换为JSON格式
        response = requests.post(f"{server_url}/api/messages", json=message_data)
        
        # 打印服务器响应的HTTP状态码
        # 200表示成功，其他状态码表示各种错误
        print(f"发送结果: {response.status_code}")
        
        # 打印服务器返回的响应内容
        # 通常包含消息发送结果和相关信息
        print(f"响应内容: {response.text}")
        
        # 返回发送结果
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ 发送消息时发生错误: {str(e)}")
        return False



# 在这里填入你的参数来发送消息
if __name__ == "__main__":

    your_title = "消息通知2"    # 填写消息标题（可选，默认为"图文消息"）
    your_text_content = "游戏角色死亡先是花，然后是卡，最后审核。我现在到审核其实也不难，兰州拉面老板们以前就是手搓这个出名，应该还需要一当你女朋友拿出这个四联 你应该就觉得事情不简单了到两人。不确定后面还有没有[捂脸]。"    # 填写你要发送的文字内容
    your_image_path = "d:\\python_Scripts_32\\my_msg\\server\\-2025-08-06-14_04_43.png"    # 填写你要发送的图片路径
    


    
    # 调用函数发送消息
    success = send_mixed_message(
        image_path=your_image_path,
        text_content=your_text_content,
        title=your_title
    )
    
    if success:
        print("✅ 消息发送成功！")
    else:
        print("❌ 消息发送失败！")
