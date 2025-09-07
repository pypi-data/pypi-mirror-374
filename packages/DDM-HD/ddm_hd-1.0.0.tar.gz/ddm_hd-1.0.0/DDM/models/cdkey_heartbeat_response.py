"""
卡密心跳响应模型
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CDKeyHeartbeatResponse:
    """
    卡密心跳响应参数模型
    """
    # 剩余秒数
    remaining_time: int
    
    # 卡密+登录成功的Token+项目加密密钥+项目UUID+设备信息+返回的Timestamp
    sign: str
    
    # 时间戳13或者10位数都行,时间戳就是1970年
    timestamp: str
    
    # 1 登录成功,其他值看msg
    code: int
    
    # 消息
    msg: str
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CDKeyHeartbeatResponse':
        """
        从字典数据创建CDKeyHeartbeatResponse对象
        
        Args:
            data (dict): 响应数据字典
            
        Returns:
            CDKeyHeartbeatResponse: 响应对象实例
        """
        return cls(
            remaining_time=int(data.get("RemainingTime", 0)),
            sign=data.get("Sign", ""),
            timestamp=data.get("Timestamp", ""),
            code=int(data.get("code", 0)),
            msg=data.get("msg", "")
        )
        
    def is_success(self) -> bool:
        """
        判断心跳是否成功
        
        Returns:
            bool: 心跳成功返回True，否则返回False
        """
        return self.code == 1
        
    @property
    def success(self) -> bool:
        """
        心跳是否成功的属性
        
        Returns:
            bool: 心跳成功返回True，否则返回False
        """
        return self.is_success()