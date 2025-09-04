"""
火山方舟SDK主模块
"""
from .text_generation import TextGenerationClient
from .image_generation import ImageGenerationClient
from .video_generation import VideoGenerationClient


class VolcEngineSDK:
    """
    火山方舟SDK主类
    """
    def __init__(self, api_key: str):
        """
        初始化SDK
        :param api_key: API密钥
        """
        self.text_gen = TextGenerationClient(api_key)
        self.image_gen = ImageGenerationClient(api_key)
        self.video_gen = VideoGenerationClient(api_key)
        
    @property
    def chat(self):
        """
        获取文本生成客户端
        :return: TextGenerationClient实例
        """
        return self.text_gen
        
    @property
    def image(self):
        """
        获取文生图客户端
        :return: ImageGenerationClient实例
        """
        return self.image_gen
        
    @property
    def video(self):
        """
        获取视频生成客户端
        :return: VideoGenerationClient实例
        """
        return self.video_gen