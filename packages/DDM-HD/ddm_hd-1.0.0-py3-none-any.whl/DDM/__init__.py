"""
DDM Package

DDM (Digital Distribution Management) 是一个用于卡密验证和管理的Python包。
该包提供了与卡密系统API交互的功能，包括登录验证和心跳保持连接。

主要类和函数：
- CDKeyClient: 主要的API客户端类，用于执行登录和心跳操作
- CDKeyLoginRequest/CDKeyLoginResponse: 登录请求和响应模型
- CDKeyHeartbeatRequest/CDKeyHeartbeatResponse: 心跳请求和响应模型
- CDKeyConfig: 配置模型，用于存储共享参数
- CDKeySession: 会话管理模型，用于自动管理登录状态和token
- generate_sign/generate_heartbeat_sign: 签名生成工具函数
- get_timestamp: 时间戳获取工具函数
- get_machine_code/get_device_info: 设备信息获取工具函数

使用示例：
    from DDM import CDKeyClient, CDKeyConfig, get_device_info

    # 自动获取设备信息
    device_info = get_device_info()
    
    # 创建配置对象
    config = CDKeyConfig(cdkey="卡密", project_secret="项目密钥", 
                        project_uuid="项目UUID", device_info=device_info)
    
    # 创建客户端实例
    client = CDKeyClient(config)
    
    # 登录
    response = client.login()
    
    if response.success:
        # 心跳（自动使用登录返回的token）
        heartbeat_response = client.heartbeat()
        if heartbeat_response.success:
            print("心跳成功")
"""
__version__ = '1.0.0'
__author__ = 'Your Name'

from .api.cdkey_client import CDKeyClient
from .models.cdkey_login_request import CDKeyLoginRequest
from .models.cdkey_login_response import CDKeyLoginResponse
from .models.cdkey_heartbeat_request import CDKeyHeartbeatRequest
from .models.cdkey_heartbeat_response import CDKeyHeartbeatResponse
from .models.config import CDKeyConfig
from .models.session import CDKeySession
from .utils.helpers import generate_sign, generate_heartbeat_sign, get_timestamp
from .utils.device_info import get_machine_code, get_device_info

__all__ = [
    'CDKeyClient',
    'CDKeyLoginRequest',
    'CDKeyLoginResponse',
    'CDKeyHeartbeatRequest',
    'CDKeyHeartbeatResponse',
    'CDKeyConfig',
    'CDKeySession',
    'generate_sign',
    'generate_heartbeat_sign',
    'get_timestamp',
    'get_machine_code',
    'get_device_info'
]