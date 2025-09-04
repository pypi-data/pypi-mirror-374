# ark_sdk_test - 火山方舟API SDK

ark_sdk_test是火山方舟平台的Python SDK，提供了对文本生成、文生图和视频生成API的封装。

## 安装

### 从PyPI安装（推荐）

```bash
pip install ark_sdk_test
```

### 从源码安装

```bash
pip install -r requirements.txt
```

## 安装

### 从PyPI安装（推荐）

```bash
pip install ark_sdk_test
```

### 从源码安装

```bash
pip install .
```

## 使用说明

1. 克隆项目到本地
2. 安装依赖：`pip install -r requirements.txt`
3. 在代码中导入SDK并使用

### 运行测试

```bash
# 运行测试
pytest

# 或者运行测试并生成覆盖率报告
pytest --cov=ark_sdk_test --cov-report=html
```

### 初始化SDK

```python
from ark_sdk_test import VolcEngineSDK

# 使用您的API密钥初始化SDK
sdk = VolcEngineSDK("YOUR_API_KEY")
```

### 文本生成 (Chat)

```python
# 调用文本生成接口
response = sdk.chat.chat(
    model="doubao-1-5-pro-32k-250115",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)

print(response)
```

### 文生图 (Image Generation)

```python
# 调用文生图接口
response = sdk.image.generate_image(
    prompt="一只可爱的猫咪",
    model="doubao-seedream-3-0-t2i-250415",
    size="1024x1024"
)

print(response)
```

### 视频生成 (Video Generation)

```python
# 创建视频生成任务
response = sdk.video.create_video_task(
    model="doubao-seedance-1-0-pro-250528",
    content=[
        {
            "type": "text",
            "text": "多个镜头。一名侦探进入一间光线昏暗的房间。他检查桌上的线索，手里拿起桌上的某个物品。镜头转向他正在思索。 --ratio 16:9"
        }
    ]
)

task_id = response["id"]
print(f"任务ID: {task_id}")

# 查询任务状态
status = sdk.video.get_video_task(task_id)
print(status)
```

## 模块说明

- `VolcEngineSDK`: SDK主类，提供对所有API的访问
- `TextGenerationClient`: 文本生成API客户端
- `ImageGenerationClient`: 文生图API客户端
- `VideoGenerationClient`: 视频生成API客户端