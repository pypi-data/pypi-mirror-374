# -- coding: utf-8 --
# Project: frappeclient
# Created Date: 2025 05 Sa
# Author: liming
# Email: lmlala@aliyun.com
# Copyright (c) 2025 FiuAI



import logging
from typing import List
from .token import TokenConfig, Tokens
from .type import ClientConfig

logger = logging.getLogger(__name__)

TOKENS = None
CLIENTCONFIG = None

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
    
    global TOKENS, CLIENTCONFIG
    

    TOKENS = Tokens(tokens)
    TOKENS.validate_tokens()
    TOKENS.load_tokens(tokens)

    CLIENTCONFIG = ClientConfig(
        url=url, 
        max_api_retry=max_api_retry, 
        timeout=timeout,
        verify=verify,
        tokens=tokens)