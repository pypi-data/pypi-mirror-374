"""
火山方舟API SDK 客户端
"""
import requests
import json


class VolcEngineClient:
    """
    火山方舟API客户端基类
    """
    def __init__(self, api_key: str):
        """
        初始化客户端
        :param api_key: API密钥
        """
        self.api_key = api_key
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, data=None):
        """
        发送HTTP请求
        :param method: HTTP方法
        :param endpoint: API端点
        :param data: 请求数据
        :return: 响应数据
        """
        url = f"{self.base_url}{endpoint}"
        
        if method.upper() == "GET":
            response = requests.get(url, headers=self.headers, params=data)
        elif method.upper() == "POST":
            response = requests.post(url, headers=self.headers, json=data)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
        
        response.raise_for_status()
        return response.json()