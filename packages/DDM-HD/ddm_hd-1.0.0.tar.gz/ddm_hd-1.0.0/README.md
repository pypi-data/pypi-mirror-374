# DDM-HD (Digital Distribution Management - HD)

DDM-HD 是一个用于卡密验证和管理的Python库。该库提供了与卡密系统API交互的功能，包括登录验证和心跳保持连接。

## 功能特点

- **自动设备信息获取**：基于硬件信息自动生成唯一的设备标识符
- **配置管理**：通过配置对象一次性设置共享参数
- **会话管理**：自动管理登录状态和token
- **网络重试机制**：内置网络连接重试和超时处理
- **异常处理**：完善的错误处理和清晰的错误信息
- **向后兼容**：支持传统方式调用

## 安装

```bash
pip install DDM-HD
```

## 使用方法

### 基本使用

```python
from DDM import CDKeyClient, CDKeyConfig

config = CDKeyConfig(
    cdkey="你的卡密",
    project_secret="你的项目密钥",
    project_uuid="你的项目UUID"
)

client = CDKeyClient(config)


response = client.login()

if response.success:
    print("登录成功!")
    print(f"Token: {response.token}")
    
    heartbeat_response = client.heartbeat()
    
    if heartbeat_response.success:
        print("心跳成功!")
```



## API参考

### 主要类和函数

- `CDKeyClient`: 主要的API客户端类，用于执行登录和心跳操作
- `CDKeyConfig`: 配置模型，用于存储共享参数
- `get_device_info()`: 获取设备信息函数

### 响应对象

所有API调用返回的响应对象都包含以下属性：

- `success`: 布尔值，表示调用是否成功
- `code`: 状态码
- `msg`: 消息描述

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request。