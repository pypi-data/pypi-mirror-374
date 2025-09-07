"""
卡密登录请求模型
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CDKeyLoginRequest:
    """
    卡密登录请求参数模型
    """
    # 卡密+卡密项目密钥+卡密项目UUID+设备信息+时间戳,然后进行md5加密获得的32位的字符串
    sign: str
    
    # 时间戳13或者10位数都行,时间戳是从1970年1月1日（UTC/GMT的午夜）开始所经过的秒数，不考虑闰秒。
    timestamp: str
    
    # 后台生成的卡密
    cdkey: str
    
    # 设备ID,可以读取本机IMEI或其他不变参数作为设备ID,也可以用UUID,推荐使用UUID
    cdkey_device_info: str
    
    # 项目UUID,在后台项目可以看到
    project_uuid: str
    
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
            "ProjectUUID": self.project_uuid
        }