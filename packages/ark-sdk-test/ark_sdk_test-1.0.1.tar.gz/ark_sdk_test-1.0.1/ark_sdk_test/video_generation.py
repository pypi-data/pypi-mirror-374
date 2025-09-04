"""
视频生成API模块
"""
from typing import List, Dict, Optional
from .client import VolcEngineClient


class VideoGenerationClient(VolcEngineClient):
    """
    视频生成API客户端
    """
    def __init__(self, api_key: str):
        super().__init__(api_key)
    
    def create_video_task(self,
                          model: str,
                          content: List[Dict],
                          callback_url: Optional[str] = None,
                          return_last_frame: Optional[bool] = False) -> Dict:
        """
        创建视频生成任务
        
        :param model: 模型ID
        :param content: 内容列表（文本和图片）
        :param callback_url: 回调URL
        :param return_last_frame: 是否返回最后一帧
        :return: API响应，包含任务ID
        """
        # 构造请求数据
        data = {
            "model": model,
            "content": content
        }
        
        # 添加可选参数
        if callback_url is not None:
            data["callback_url"] = callback_url
        if return_last_frame is not None:
            data["return_last_frame"] = return_last_frame
        
        # 发送请求
        return self._make_request("POST", "/contents/generations/tasks", data)
    
    def get_video_task(self, task_id: str) -> Dict:
        """
        查询视频生成任务状态
        
        :param task_id: 任务ID
        :return: 任务状态信息
        """
        # 发送请求
        return self._make_request("GET", f"/contents/generations/tasks/{task_id}")