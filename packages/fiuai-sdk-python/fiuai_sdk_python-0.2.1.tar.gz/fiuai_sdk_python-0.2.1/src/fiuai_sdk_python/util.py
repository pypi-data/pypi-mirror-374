# -- coding: utf-8 --
# Project: frappeclient
# Created Date: 2025 05 Sa
# Author: liming
# Email: lmlala@aliyun.com
# Copyright (c) 2025 FiuAI



import logging
from typing import List, Optional
from .token import TokenConfig, Tokens
from .type import ClientConfig

logger = logging.getLogger(__name__)


class FiuaiConfig:
    """FiuaiSDK 配置单例类"""
    _instance: Optional['FiuaiConfig'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.tokens: Optional[Tokens] = None
            self.client_config: Optional[ClientConfig] = None
            self._initialized = True
    
    def init(self, url: str, tokens: List[TokenConfig], max_api_retry: int = 3, 
             timeout: int = 5, verify: bool = False):
        """
        初始化 FiuaiSDK 全局配置
        
        Args:
            url: API 服务器地址
            tokens: Token 配置列表
            max_api_retry: 最大重试次数
            timeout: 请求超时时间
            verify: 是否验证 SSL 证书
        """
        # 初始化 TOKENS（构造函数内部已经调用了 load_tokens）
        self.tokens = Tokens(tokens)
        
        # 初始化客户端配置
        self.client_config = ClientConfig(
            url=url, 
            max_api_retry=max_api_retry, 
            timeout=timeout,
            verify=verify,
            tokens=tokens)
    
    def get_tokens(self) -> Optional[Tokens]:
        """获取 TOKENS 实例"""
        return self.tokens
    
    def get_client_config(self) -> Optional[ClientConfig]:
        """获取 CLIENTCONFIG 实例"""
        return self.client_config
    
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self.tokens is not None and self.client_config is not None


# 创建全局单例实例
_config = FiuaiConfig()

# 为了保持向后兼容，提供全局变量访问
def get_tokens():
    return _config.get_tokens()

def get_client_config():
    return _config.get_client_config()

def is_initialized():
    return _config.is_initialized()

def create_headers(key, secret, user, tenant="", company=""):

    headers = {
        "Fiuai-Internal-Auth": "true",
        "Fiuai-Internal-Key": key,
        "Fiuai-Internal-Secret": secret,
        "Fiuai-Internal-User": user,
        "Fiuai-Internal-Tenant": tenant,
        "Fiuai-Internal-Company": company,
        "Accept": "application/json",
    }

    return headers




def init_fiuai(
    url: str,
    tokens: List[TokenConfig],
    max_api_retry: int=3,
    timeout: int=5,
    verify: bool=False
):
    """
    初始化 FiuaiSDK 全局配置
    
    Args:
        url: API 服务器地址
        tokens: Token 配置列表
        max_api_retry: 最大重试次数
        timeout: 请求超时时间
        verify: 是否验证 SSL 证书
    """
    _config.init(url, tokens, max_api_retry, timeout, verify)