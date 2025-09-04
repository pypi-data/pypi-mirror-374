"""
文本生成API模块
"""
from typing import List, Dict, Optional, Union
from .client import VolcEngineClient


class TextGenerationClient(VolcEngineClient):
    """
    文本生成API客户端
    """
    def __init__(self, api_key: str):
        super().__init__(api_key)
    
    def chat(self, 
             model: str, 
             messages: List[Dict],
             thinking: Optional[Dict] = None,
             stream: Optional[bool] = None,
             stream_options: Optional[Dict] = None,
             max_tokens: Optional[int] = None,
             max_completion_tokens: Optional[int] = None,
             service_tier: Optional[str] = None,
             stop: Optional[Union[str, List[str]]] = None,
             response_format: Optional[Dict] = None,
             frequency_penalty: Optional[float] = None,
             presence_penalty: Optional[float] = None,
             temperature: Optional[float] = None,
             top_p: Optional[float] = None,
             logprobs: Optional[bool] = None,
             top_logprobs: Optional[int] = None,
             logit_bias: Optional[Dict] = None,
             tools: Optional[List[Dict]] = None,
             parallel_tool_calls: Optional[bool] = None,
             tool_choice: Optional[Union[str, Dict]] = None) -> Dict:
        """
        调用文本生成接口
        
        :param model: 模型ID
        :param messages: 消息列表
        :param thinking: 深度思考模式控制
        :param stream: 是否流式返回
        :param stream_options: 流式响应选项
        :param max_tokens: 最大token数
        :param max_completion_tokens: 最大完成token数
        :param service_tier: 服务层级
        :param stop: 停止词
        :param response_format: 响应格式
        :param frequency_penalty: 频率惩罚
        :param presence_penalty: 存在惩罚
        :param temperature: 温度参数
        :param top_p: 核采样
        :param logprobs: 是否返回对数概率
        :param top_logprobs: 返回top logprobs数量
        :param logit_bias: logit偏差
        :param tools: 工具列表
        :param parallel_tool_calls: 是否并行工具调用
        :param tool_choice: 工具选择
        :return: API响应
        """
        # 构造请求数据
        data = {
            "model": model,
            "messages": messages
        }
        
        # 添加可选参数
        if thinking is not None:
            data["thinking"] = thinking
        if stream is not None:
            data["stream"] = stream
        if stream_options is not None:
            data["stream_options"] = stream_options
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        if max_completion_tokens is not None:
            data["max_completion_tokens"] = max_completion_tokens
        if service_tier is not None:
            data["service_tier"] = service_tier
        if stop is not None:
            data["stop"] = stop
        if response_format is not None:
            data["response_format"] = response_format
        if frequency_penalty is not None:
            data["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            data["presence_penalty"] = presence_penalty
        if temperature is not None:
            data["temperature"] = temperature
        if top_p is not None:
            data["top_p"] = top_p
        if logprobs is not None:
            data["logprobs"] = logprobs
        if top_logprobs is not None:
            data["top_logprobs"] = top_logprobs
        if logit_bias is not None:
            data["logit_bias"] = logit_bias
        if tools is not None:
            data["tools"] = tools
        if parallel_tool_calls is not None:
            data["parallel_tool_calls"] = parallel_tool_calls
        if tool_choice is not None:
            data["tool_choice"] = tool_choice
        
        # 发送请求
        return self._make_request("POST", "/chat/completions", data)