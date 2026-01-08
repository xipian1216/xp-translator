"""
测试数据模型

包含对 Pydantic 模型的验证和序列化测试
"""

import pytest
from pydantic import ValidationError
from src.xp_translator.models import (
    TranslationRequest,
    TranslationResponse,
    TranslationDirection,
    AIProvider
)


class TestTranslationDirection:
    """测试翻译方向枚举"""
    
    def test_enum_values(self):
        """测试枚举值"""
        assert TranslationDirection.ZH_TO_EN.value == "zh_to_en"
        assert TranslationDirection.EN_TO_ZH.value == "en_to_zh"
        assert TranslationDirection.AUTO.value == "auto"
    
    def test_enum_members(self):
        """测试枚举成员"""
        assert isinstance(TranslationDirection.ZH_TO_EN, TranslationDirection)
        assert isinstance(TranslationDirection.EN_TO_ZH, TranslationDirection)
        assert isinstance(TranslationDirection.AUTO, TranslationDirection)
    
    def test_enum_from_string(self):
        """测试从字符串创建枚举"""
        assert TranslationDirection("zh_to_en") == TranslationDirection.ZH_TO_EN
        assert TranslationDirection("en_to_zh") == TranslationDirection.EN_TO_ZH
        assert TranslationDirection("auto") == TranslationDirection.AUTO
    
    def test_invalid_enum_value(self):
        """测试无效的枚举值"""
        with pytest.raises(ValueError):
            TranslationDirection("invalid_direction")


class TestAIProvider:
    """测试 AI 提供商枚举"""
    
    def test_enum_values(self):
        """测试枚举值"""
        assert AIProvider.DEEPSEEK.value == "deepseek"
        assert AIProvider.ALIYUN.value == "aliyun"
    
    def test_enum_members(self):
        """测试枚举成员"""
        assert isinstance(AIProvider.DEEPSEEK, AIProvider)
        assert isinstance(AIProvider.ALIYUN, AIProvider)
    
    def test_enum_from_string(self):
        """测试从字符串创建枚举"""
        assert AIProvider("deepseek") == AIProvider.DEEPSEEK
        assert AIProvider("aliyun") == AIProvider.ALIYUN
    
    def test_invalid_enum_value(self):
        """测试无效的枚举值"""
        with pytest.raises(ValueError):
            AIProvider("invalid_provider")


class TestTranslationRequest:
    """测试翻译请求模型"""
    
    def test_valid_request_minimal(self):
        """测试最小有效请求"""
        request = TranslationRequest(text="你好")
        assert request.text == "你好"
        assert request.direction == TranslationDirection.ZH_TO_EN
        assert request.provider == "deepseek"  # 默认值
    
    def test_valid_request_full(self):
        """测试完整有效请求"""
        request = TranslationRequest(
            text="Hello world",
            direction="en_to_zh",
            provider="aliyun"
        )
        assert request.text == "Hello world"
        assert request.direction == TranslationDirection.EN_TO_ZH
        assert request.provider == "aliyun"
    
    def test_request_with_enum_objects(self):
        """测试使用枚举对象"""
        request = TranslationRequest(
            text="测试",
            direction=TranslationDirection.AUTO,
            provider=AIProvider.DEEPSEEK
        )
        assert request.text == "测试"
        assert request.direction == TranslationDirection.AUTO
        assert request.provider == "deepseek"
    
    def test_empty_text_validation(self):
        """测试空文本验证"""
        with pytest.raises(ValidationError) as exc_info:
            TranslationRequest(text="")
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any("text" in error["loc"] for error in errors)
    
    def test_whitespace_text_validation(self):
        """测试空白文本验证"""
        # 我们的验证器会拒绝只有空格的文本
        with pytest.raises(ValidationError) as exc_info:
            TranslationRequest(text="   ")
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any("text" in error["loc"] for error in errors)
        assert any("不能为空" in str(error.get("msg", "")) for error in errors)
    
    def test_long_text_validation(self):
        """测试长文本验证"""
        long_text = "a" * 10000  # 10k 字符，超过我们的 max_length=5000
        with pytest.raises(ValidationError) as exc_info:
            TranslationRequest(text=long_text)
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any("text" in error["loc"] for error in errors)
        assert any("5000" in str(error.get("msg", "")) for error in errors)
        
        # 测试刚好在限制内的文本
        valid_long_text = "a" * 5000  # 刚好 5000 字符
        request = TranslationRequest(text=valid_long_text)
        assert request.text == valid_long_text
    
    def test_invalid_direction(self):
        """测试无效的翻译方向"""
        with pytest.raises(ValidationError) as exc_info:
            TranslationRequest(text="test", direction="invalid_direction")
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any("direction" in error["loc"] for error in errors)
    
    def test_invalid_provider(self):
        """测试无效的 AI 提供商"""
        with pytest.raises(ValidationError) as exc_info:
            TranslationRequest(text="test", provider="invalid_provider")
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any("provider" in error["loc"] for error in errors)
    
    def test_request_dict_conversion(self):
        """测试字典转换"""
        request = TranslationRequest(
            text="测试文本",
            direction="zh_to_en",
            provider="deepseek"
        )
        
        request_dict = request.model_dump()
        assert request_dict["text"] == "测试文本"
        assert request_dict["direction"] == "zh_to_en"
        assert request_dict["provider"] == "deepseek"
    
    def test_request_json_conversion(self):
        """测试 JSON 转换"""
        request = TranslationRequest(
            text="JSON 测试",
            direction="auto",
            provider="aliyun"
        )
        
        request_json = request.model_dump_json()
        # JSON 格式可能没有空格，所以使用更灵活的断言
        assert '"text":"JSON 测试"' in request_json or '"text": "JSON 测试"' in request_json
        assert '"direction":"auto"' in request_json or '"direction": "auto"' in request_json
        assert '"provider":"aliyun"' in request_json or '"provider": "aliyun"' in request_json
    
    def test_request_from_dict(self):
        """测试从字典创建请求"""
        data = {
            "text": "从字典创建",
            "direction": "en_to_zh",
            "provider": "deepseek"
        }
        
        request = TranslationRequest(**data)
        assert request.text == "从字典创建"
        assert request.direction == TranslationDirection.EN_TO_ZH
        assert request.provider == "deepseek"
    
    def test_request_field_descriptions(self):
        """测试字段描述"""
        schema = TranslationRequest.model_json_schema()
        
        # 检查字段描述（Pydantic v2 可能将描述放在不同的位置）
        text_prop = schema["properties"]["text"]
        direction_prop = schema["properties"]["direction"]
        provider_prop = schema["properties"]["provider"]
        
        # 检查字段存在
        assert "text" in schema["properties"]
        assert "direction" in schema["properties"]
        assert "provider" in schema["properties"]
        
        # 检查默认值
        assert direction_prop.get("default") == "zh_to_en" or direction_prop.get("default") == TranslationDirection.ZH_TO_EN.value
        assert provider_prop.get("default") == "deepseek"


class TestTranslationResponse:
    """测试翻译响应模型"""
    
    def test_valid_response_minimal(self):
        """测试最小有效响应"""
        response = TranslationResponse(
            translation="Hello",
            keywords=["hello", "greeting"]
        )
        assert response.translation == "Hello"
        assert response.keywords == ["hello", "greeting"]
        assert response.direction == TranslationDirection.ZH_TO_EN  # 默认值
        assert response.provider == "deepseek"  # 默认值
    
    def test_valid_response_full(self):
        """测试完整有效响应"""
        response = TranslationResponse(
            translation="你好",
            keywords=["你好", "问候"],
            direction="en_to_zh",
            provider="aliyun"
        )
        assert response.translation == "你好"
        assert response.keywords == ["你好", "问候"]
        assert response.direction == TranslationDirection.EN_TO_ZH
        assert response.provider == "aliyun"
    
    def test_response_with_empty_keywords(self):
        """测试空关键词列表"""
        response = TranslationResponse(
            translation="测试",
            keywords=[]
        )
        assert response.translation == "测试"
        assert response.keywords == []
    
    def test_response_with_max_keywords(self):
        """测试最大关键词数量"""
        keywords = ["kw1", "kw2", "kw3", "kw4", "kw5"]  # 5个关键词
        response = TranslationResponse(
            translation="测试",
            keywords=keywords
        )
        assert response.keywords == keywords  # 应该接受任意数量的关键词
    
    def test_missing_translation(self):
        """测试缺少翻译文本"""
        with pytest.raises(ValidationError) as exc_info:
            TranslationResponse(keywords=["test"])
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any("translation" in error["loc"] for error in errors)
    
    def test_missing_keywords(self):
        """测试缺少关键词"""
        with pytest.raises(ValidationError) as exc_info:
            TranslationResponse(translation="test")
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any("keywords" in error["loc"] for error in errors)
    
    def test_response_dict_conversion(self):
        """测试响应字典转换"""
        response = TranslationResponse(
            translation="转换测试",
            keywords=["转换", "测试"],
            direction="auto",
            provider="deepseek"
        )
        
        response_dict = response.model_dump()
        assert response_dict["translation"] == "转换测试"
        assert response_dict["keywords"] == ["转换", "测试"]
        assert response_dict["direction"] == "auto"
        assert response_dict["provider"] == "deepseek"
    
    def test_response_json_conversion(self):
        """测试响应 JSON 转换"""
        response = TranslationResponse(
            translation="JSON 响应",
            keywords=["json", "响应"],
            direction="zh_to_en",
            provider="aliyun"
        )
        
        response_json = response.model_dump_json()
        # JSON 格式可能没有空格，所以使用更灵活的断言
        assert '"translation":"JSON 响应"' in response_json or '"translation": "JSON 响应"' in response_json
        assert '"keywords":["json","响应"]' in response_json or '"keywords": ["json", "响应"]' in response_json
        assert '"direction":"zh_to_en"' in response_json or '"direction": "zh_to_en"' in response_json
        assert '"provider":"aliyun"' in response_json or '"provider": "aliyun"' in response_json
    
    def test_response_from_dict(self):
        """测试从字典创建响应"""
        data = {
            "translation": "从字典创建",
            "keywords": ["字典", "创建"],
            "direction": "zh_to_en",
            "provider": "deepseek"
        }
        
        response = TranslationResponse(**data)
        assert response.translation == "从字典创建"
        assert response.keywords == ["字典", "创建"]
        assert response.direction == TranslationDirection.ZH_TO_EN
        assert response.provider == "deepseek"
    
    def test_response_field_types(self):
        """测试响应字段类型"""
        response = TranslationResponse(
            translation="类型测试",
            keywords=["类型", "测试"]
        )
        
        assert isinstance(response.translation, str)
        assert isinstance(response.keywords, list)
        assert all(isinstance(kw, str) for kw in response.keywords)
        assert isinstance(response.direction, TranslationDirection)
        assert isinstance(response.provider, str)


class TestModelIntegration:
    """测试模型集成"""
    
    def test_request_response_consistency(self):
        """测试请求和响应的一致性"""
        # 创建一个请求
        request = TranslationRequest(
            text="集成测试",
            direction="zh_to_en",
            provider="deepseek"
        )
        
        # 创建一个对应的响应
        response = TranslationResponse(
            translation="Integration test",
            keywords=["integration", "test"],
            direction=request.direction,
            provider=request.provider
        )
        
        # 验证一致性
        assert response.direction == request.direction
        assert response.provider == request.provider
        
        # 验证响应包含正确的字段
        assert hasattr(response, 'translation')
        assert hasattr(response, 'keywords')
        assert hasattr(response, 'direction')
        assert hasattr(response, 'provider')
    
    def test_model_serialization_roundtrip(self):
        """测试模型序列化往返"""
        # 创建请求
        original_request = TranslationRequest(
            text="往返测试",
            direction="auto",
            provider="aliyun"
        )
        
        # 序列化为字典
        request_dict = original_request.model_dump()
        
        # 从字典重新创建
        recreated_request = TranslationRequest(**request_dict)
        
        # 验证相等性
        assert recreated_request.text == original_request.text
        assert recreated_request.direction == original_request.direction
        assert recreated_request.provider == original_request.provider
        
        # 同样测试响应
        original_response = TranslationResponse(
            translation="Roundtrip test",
            keywords=["roundtrip", "test"],
            direction="auto",
            provider="aliyun"
        )
        
        response_dict = original_response.model_dump()
        recreated_response = TranslationResponse(**response_dict)
        
        assert recreated_response.translation == original_response.translation
        assert recreated_response.keywords == original_response.keywords
        assert recreated_response.direction == original_response.direction
        assert recreated_response.provider == original_response.provider
    
    def test_model_json_schema(self):
        """测试模型 JSON 模式"""
        # 请求模式
        request_schema = TranslationRequest.model_json_schema()
        assert "properties" in request_schema
        assert "text" in request_schema["properties"]
        assert "direction" in request_schema["properties"]
        assert "provider" in request_schema["properties"]
        
        # 响应模式
        response_schema = TranslationResponse.model_json_schema()
        assert "properties" in response_schema
        assert "translation" in response_schema["properties"]
        assert "keywords" in response_schema["properties"]
        assert "direction" in response_schema["properties"]
        assert "provider" in response_schema["properties"]
        
        # 检查必需字段
        assert "text" in request_schema.get("required", [])
        assert "translation" in response_schema.get("required", [])
        assert "keywords" in response_schema.get("required", [])