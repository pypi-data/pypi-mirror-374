"""
卡密心跳请求模型
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CDKeyHeartbeatRequest:
    """
    卡密心跳请求参数模型
    """
    # 卡密+Token+项目加密密钥+项目UUID+设备信息+时间戳 拼接之后md5加密的32位数据
    sign: str
    
    # 时间戳13或者10位数都行
    timestamp: str
    
    # 后台生成的卡密
    cdkey: str
    
    # 与登录时的设备ID一样
    cdkey_device_info: str
    
    # 项目UUID,在后台项目可以看到
    project_uuid: str
    
    # 登录成功时,返回的token值
    token: str
    
    def to_dict(self) -> dict:
        """
        将对象转换为字典格式
        
        Returns:
            dict: 包含所有请求参数的字典
        """
        return {
            "Sign": self.sign,
            "Timestamp": self.timestamp,
            "CDKEY": self.cdkey,
            "CDKEYDeviceInfo": self.cdkey_device_info,
            "ProjectUUID": self.project_uuid,
            "Token": self.token
        }