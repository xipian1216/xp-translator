"""
Pytest 配置文件

提供测试所需的共享 fixture 和配置
"""

import os
import sys
from unittest.mock import Mock, patch, AsyncMock
import pytest
from fastapi.testclient import TestClient

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.xp_translator.api import app
from src.xp_translator.clients import BaseAIClient, DeepSeekClient, AliyunQwenClient, MockAIClient


@pytest.fixture
def test_client():
    """提供 FastAPI 测试客户端"""
    return TestClient(app)


@pytest.fixture
def mock_ai_client():
    """提供模拟的 AI 客户端"""
    client = MockAIClient()
    return client


@pytest.fixture
def mock_deepseek_client():
    """提供模拟的 DeepSeek 客户端"""
    with patch('openai.OpenAI') as mock_openai:
        mock_instance = Mock()
        mock_instance.chat.completions.create = AsyncMock(return_value=Mock(
            choices=[Mock(message=Mock(content='Mocked translation. Keywords: test, mock, example'))]
        ))
        mock_openai.return_value = mock_instance
        
        client = DeepSeekClient()
        client.client = mock_instance
        return client


@pytest.fixture
def mock_aliyun_client():
    """提供模拟的通义千问客户端"""
    with patch('openai.OpenAI') as mock_openai:
        mock_instance = Mock()
        mock_instance.chat.completions.create = AsyncMock(return_value=Mock(
            choices=[Mock(message=Mock(content='Mocked translation. Keywords: test, mock, example'))]
        ))
        mock_openai.return_value = mock_instance
        
        client = AliyunQwenClient()
        client.client = mock_instance
        return client


@pytest.fixture
def sample_translation_request():
    """提供示例翻译请求数据"""
    return {
        "text": "你好世界",
        "direction": "zh_to_en",
        "provider": "deepseek"
    }


@pytest.fixture
def sample_translation_response():
    """提供示例翻译响应数据"""
    return {
        "translation": "Hello world",
        "keywords": ["hello", "world", "greeting"],
        "direction": "zh_to_en",
        "provider": "deepseek"
    }


@pytest.fixture
def env_vars():
    """设置测试环境变量"""
    original_env = {}
    
    # 保存原始环境变量
    env_keys = [
        "DEEPSEEK_API_KEY",
        "DEEPSEEK_BASE_URL",
        "DEEPSEEK_MODEL",
        "ALIYUN_API_KEY",
        "ALIYUN_BASE_URL",
        "ALIYUN_MODEL",
        "AI_PROVIDER"
    ]
    
    for key in env_keys:
        original_env[key] = os.environ.get(key)
    
    # 设置测试环境变量
    os.environ["DEEPSEEK_API_KEY"] = "test-deepseek-key"
    os.environ["DEEPSEEK_BASE_URL"] = "https://api.deepseek.com"
    os.environ["DEEPSEEK_MODEL"] = "deepseek-chat"
    os.environ["ALIYUN_API_KEY"] = "test-aliyun-key"
    os.environ["ALIYUN_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    os.environ["ALIYUN_MODEL"] = "qwen-plus"
    os.environ["AI_PROVIDER"] = "deepseek"
    
    yield
    
    # 恢复原始环境变量
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture(autouse=True)
def cleanup_mocks():
    """自动清理所有模拟对象"""
    yield
    # 清理所有 patch
    patch.stopall()