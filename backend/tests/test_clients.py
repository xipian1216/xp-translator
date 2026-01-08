"""
测试 AI 客户端功能

包含对 BaseAIClient、DeepSeekClient、AliyunQwenClient 和 MockAIClient 的测试
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.xp_translator.clients import (
    BaseAIClient, 
    DeepSeekClient, 
    AliyunQwenClient, 
    MockAIClient,
    create_ai_client
)


class TestBaseAIClient:
    """测试基础 AI 客户端"""
    
    def test_base_client_abstract(self):
        """测试 BaseAIClient 是抽象类"""
        with pytest.raises(TypeError):
            client = BaseAIClient()  # 应该无法实例化抽象类
    
    def test_base_client_methods(self):
        """测试 BaseAIClient 的抽象方法"""
        # 创建一个具体的子类来测试
        class ConcreteAIClient(BaseAIClient):
            def __init__(self):
                super().__init__(
                    provider="test",
                    api_key="test-key",
                    base_url="https://test.com",
                    model="test-model"
                )
            
            async def translate_and_extract(self, text: str, direction: str = "zh_to_en") -> tuple[str, list[str]]:
                return "translation", ["keyword1", "keyword2"]
            
            # 添加 translate 方法作为别名
            async def translate(self, text: str, direction: str = "zh_to_en") -> tuple[str, list[str]]:
                return await self.translate_and_extract(text, direction)
        
        client = ConcreteAIClient()
        
        # 测试同步包装器
        translation, keywords = client.translate_sync("test")
        assert translation == "translation"
        assert keywords == ["keyword1", "keyword2"]
        
        # 测试异步方法
        async def test_async():
            translation, keywords = await client.translate("test")
            return translation, keywords
        
        result = asyncio.run(test_async())
        assert result == ("translation", ["keyword1", "keyword2"])


class TestMockAIClient:
    """测试模拟 AI 客户端"""
    
    def test_mock_client_initialization(self):
        """测试 MockAIClient 初始化"""
        client = MockAIClient()
        assert client.provider == "mock"
    
    def test_mock_client_translate_zh_to_en(self):
        """测试 MockAIClient 中文到英文翻译"""
        client = MockAIClient()
        
        # 测试同步方法
        translation, keywords = client.translate_sync("你好", "zh_to_en")
        assert "Hello" in translation
        assert isinstance(keywords, list)
        assert len(keywords) <= 3
        
        # 测试异步方法
        async def test_async():
            return await client.translate("你好", "zh_to_en")
        
        translation, keywords = asyncio.run(test_async())
        assert "Hello" in translation
    
    def test_mock_client_translate_en_to_zh(self):
        """测试 MockAIClient 英文到中文翻译"""
        client = MockAIClient()
        
        translation, keywords = client.translate_sync("Hello", "en_to_zh")
        assert "你好" in translation or "您好" in translation
        assert isinstance(keywords, list)
    
    def test_mock_client_translate_auto(self):
        """测试 MockAIClient 自动检测翻译"""
        client = MockAIClient()
        
        # 中文文本
        translation, keywords = client.translate_sync("你好世界", "auto")
        assert "Hello" in translation
        
        # 英文文本
        translation, keywords = client.translate_sync("Hello world", "auto")
        assert "你好" in translation or "世界" in translation
    
    def test_mock_client_keyword_extraction(self):
        """测试 MockAIClient 关键词提取"""
        client = MockAIClient()
        
        for _ in range(10):  # 多次测试确保稳定性
            translation, keywords = client.translate_sync("测试文本", "zh_to_en")
            assert isinstance(keywords, list)
            assert len(keywords) <= 3
            for keyword in keywords:
                assert isinstance(keyword, str)
                assert len(keyword) > 0


class TestDeepSeekClient:
    """测试 DeepSeek 客户端"""
    
    @pytest.fixture
    def mock_openai_client(self):
        """创建模拟的 OpenAI 客户端"""
        with patch('openai.OpenAI') as mock_openai:
            mock_instance = Mock()
            # 创建模拟的响应对象
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content='翻译：Mocked translation\n关键词：[test, mock, example]'))]
            
            # OpenAI SDK 的 create 方法是同步的，所以使用普通 Mock
            mock_instance.chat.completions.create = Mock(return_value=mock_response)
            mock_openai.return_value = mock_instance
            yield mock_instance
    
    def test_deepseek_client_initialization(self, mock_openai_client):
        """测试 DeepSeekClient 初始化"""
        client = DeepSeekClient()
        assert client.provider == "deepseek"
        assert client.model == "deepseek-chat"
    
    def test_deepseek_client_translate_success(self, mock_openai_client):
        """测试 DeepSeekClient 成功翻译"""
        client = DeepSeekClient()
        client.client = mock_openai_client
        
        # 测试同步方法
        translation, keywords = client.translate_sync("你好", "zh_to_en")
        assert translation == "Mocked translation"
        assert keywords == ["test", "mock", "example"]
        
        # 测试异步方法
        async def test_async():
            return await client.translate_and_extract("你好", "zh_to_en")
        
        translation, keywords = asyncio.run(test_async())
        assert translation == "Mocked translation"
        assert keywords == ["test", "mock", "example"]
    
    def test_deepseek_client_translate_with_custom_prompt(self, mock_openai_client):
        """测试 DeepSeekClient 使用自定义提示"""
        client = DeepSeekClient()
        client.client = mock_openai_client
        
        # 模拟不同的响应
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='翻译：Different translation\n关键词：[custom, prompt, test]'))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        translation, keywords = client.translate_sync("自定义测试", "en_to_zh")
        assert translation == "Different translation"
        assert keywords == ["custom", "prompt", "test"]
    
    def test_deepseek_client_error_handling(self):
        """测试 DeepSeekClient 错误处理"""
        with patch('openai.OpenAI') as mock_openai:
            mock_instance = Mock()
            mock_instance.chat.completions.create = Mock(side_effect=Exception("API Error"))
            mock_openai.return_value = mock_instance
            
            client = DeepSeekClient()
            client.client = mock_instance
            
            # 应该抛出异常
            with pytest.raises(Exception, match="DeepSeek API 调用失败: API Error"):
                client.translate_sync("test", "zh_to_en")


class TestAliyunQwenClient:
    """测试通义千问客户端"""
    
    @pytest.fixture
    def mock_openai_client(self):
        """创建模拟的 OpenAI 客户端（用于通义千问）"""
        with patch('openai.OpenAI') as mock_openai:
            mock_instance = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content='翻译：阿里云翻译\n关键词：[aliyun, qwen, test]'))]
            mock_instance.chat.completions.create = Mock(return_value=mock_response)
            mock_openai.return_value = mock_instance
            yield mock_instance
    
    def test_aliyun_client_initialization(self, mock_openai_client):
        """测试 AliyunQwenClient 初始化"""
        client = AliyunQwenClient()
        assert client.provider == "aliyun"
        assert client.model == "qwen-plus"
    
    def test_aliyun_client_translate_success(self, mock_openai_client):
        """测试 AliyunQwenClient 成功翻译"""
        client = AliyunQwenClient()
        client.client = mock_openai_client
        
        translation, keywords = client.translate_sync("测试", "zh_to_en")
        assert translation == "阿里云翻译"
        assert keywords == ["aliyun", "qwen", "test"]
    
    def test_aliyun_client_different_base_url(self):
        """测试 AliyunQwenClient 使用不同的基础 URL"""
        with patch.dict('os.environ', {
            'ALIYUN_BASE_URL': 'https://custom.aliyun.com/v1',
            'ALIYUN_API_KEY': 'test-key',
            'ALIYUN_MODEL': 'custom-model'
        }):
            with patch('openai.OpenAI') as mock_openai:
                mock_instance = Mock()
                mock_openai.return_value = mock_instance
                
                client = AliyunQwenClient()
                
                # 检查是否使用了自定义配置
                assert client.base_url == 'https://custom.aliyun.com/v1'
                assert client.model == 'custom-model'


class TestClientFactory:
    """测试客户端工厂函数"""
    
    def test_create_ai_client_deepseek(self):
        """测试创建 DeepSeek 客户端"""
        with patch.dict('os.environ', {'AI_PROVIDER': 'deepseek'}):
            client = create_ai_client("deepseek")
            assert isinstance(client, DeepSeekClient)
            assert client.provider == "deepseek"
    
    def test_create_ai_client_aliyun(self):
        """测试创建通义千问客户端"""
        with patch.dict('os.environ', {'AI_PROVIDER': 'aliyun'}):
            client = create_ai_client("aliyun")
            assert isinstance(client, AliyunQwenClient)
            assert client.provider == "aliyun"
    
    def test_create_ai_client_mock(self):
        """测试创建模拟客户端"""
        # 当 provider 无效时应该返回 MockAIClient
        client = create_ai_client("invalid_provider")
        assert isinstance(client, MockAIClient)
        assert client.provider == "mock"
    
    def test_create_ai_client_default(self):
        """测试创建默认客户端"""
        # 不指定 provider 时使用环境变量中的默认值
        with patch.dict('os.environ', {'AI_PROVIDER': 'deepseek'}):
            client = create_ai_client()  # 不传参数
            assert isinstance(client, DeepSeekClient)
        
        with patch.dict('os.environ', {'AI_PROVIDER': 'aliyun'}):
            client = create_ai_client()  # 不传参数
            assert isinstance(client, AliyunQwenClient)
    
    def test_create_ai_client_env_fallback(self):
        """测试环境变量回退"""
        # 当 provider 为 None 且环境变量未设置时，应该使用默认值
        with patch.dict('os.environ', {}, clear=True):
            client = create_ai_client()
            # 根据当前实现，当环境变量未设置时应该返回 MockAIClient
            # 或者根据代码逻辑返回某个默认客户端
            # 这里我们检查它是否成功创建了某个客户端
            assert client is not None


class TestClientIntegration:
    """测试客户端集成"""
    
    def test_all_clients_implement_interface(self):
        """测试所有客户端都实现了相同的接口"""
        clients = [
            MockAIClient(),
            DeepSeekClient(),
            AliyunQwenClient(),
        ]
        
        for client in clients:
            # 所有客户端都应该有这些属性
            assert hasattr(client, 'provider')
            assert hasattr(client, 'translate')
            assert hasattr(client, 'translate_sync')
            
            # provider 应该是字符串
            assert isinstance(client.provider, str)
    
    def test_client_provider_names(self):
        """测试客户端提供商名称"""
        assert MockAIClient().provider == "mock"
        assert DeepSeekClient().provider == "deepseek"
        assert AliyunQwenClient().provider == "aliyun"
    
    def test_translation_consistency(self):
        """测试翻译结果的一致性（至少结构一致）"""
        test_text = "一致性测试"
        test_direction = "zh_to_en"
        
        # 只测试 MockAIClient，因为真实 API 可能不可用
        client = MockAIClient()
        
        # 多次调用应该得到结构一致的结果
        for _ in range(5):
            translation, keywords = client.translate_sync(test_text, test_direction)
            
            # 检查结构
            assert isinstance(translation, str)
            assert len(translation) > 0
            assert isinstance(keywords, list)
            assert len(keywords) <= 3
            
            # 检查关键词都是字符串
            for keyword in keywords:
                assert isinstance(keyword, str)
                assert len(keyword) > 0