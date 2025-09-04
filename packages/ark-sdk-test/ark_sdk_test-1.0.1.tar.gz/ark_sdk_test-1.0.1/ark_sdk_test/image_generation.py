"""
文生图API模块
"""
from typing import List, Dict, Optional
from .client import VolcEngineClient


class ImageGenerationClient(VolcEngineClient):
    """
    文生图API客户端
    """
    def __init__(self, api_key: str):
        super().__init__(api_key)
    
    def generate_image(self,
                       prompt: str,
                       model: str,
                       response_format: Optional[str] = "url",
                       size: Optional[str] = "1024x1024",
                       seed: Optional[int] = -1,
                       guidance_scale: Optional[float] = 2.5,
                       watermark: Optional[bool] = True) -> Dict:
        """
        调用文生图接口生成图片
        
        :param prompt: 用于生成图像的提示词
        :param model: 模型ID
        :param response_format: 返回格式 ("url" 或 "b64_json")
        :param size: 图像尺寸
        :param seed: 随机种子
        :param guidance_scale: 指导比例
        :param watermark: 是否添加水印
        :return: API响应
        """
        # 构造请求数据
        data = {
            "prompt": prompt,
            "model": model,
            "response_format": response_format,
            "size": size,
            "seed": seed,
            "guidance_scale": guidance_scale,
            "watermark": watermark
        }
        
        # 发送请求
        return self._make_request("POST", "/images/generations", data)