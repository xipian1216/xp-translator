"""
数据模型定义
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum
import re


class TranslationDirection(str, Enum):
    """翻译方向枚举"""
    ZH_TO_EN = "zh_to_en"  # 中文到英文（默认）
    EN_TO_ZH = "en_to_zh"  # 英文到中文
    AUTO = "auto"          # 自动检测


class AIProvider(str, Enum):
    """AI 提供商枚举"""
    DEEPSEEK = "deepseek"  # DeepSeek（默认）
    ALIYUN = "aliyun"      # 通义千问


class TranslationRequest(BaseModel):
    """翻译请求模型"""
    text: str = Field(
        min_length=1,
        max_length=5000,
        description="要翻译的文本，不能为空，最大长度5000字符"
    )
    direction: TranslationDirection = Field(
        default=TranslationDirection.ZH_TO_EN,
        description="翻译方向：zh_to_en（中文到英文，默认）, en_to_zh（英文到中文）, auto（自动检测）"
    )
    provider: str = Field(
        default="deepseek",
        description="AI 提供商：deepseek（DeepSeek，默认）, aliyun（通义千问）"
    )
    
    @field_validator('text')
    @classmethod
    def validate_text_not_empty(cls, v: str) -> str:
        """验证文本不为空"""
        if not v or not v.strip():
            raise ValueError('文本不能为空')
        return v.strip()
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """验证 AI 提供商"""
        valid_providers = ['deepseek', 'aliyun', 'mock']
        if v not in valid_providers:
            raise ValueError(f'无效的 AI 提供商，必须是: {", ".join(valid_providers)}')
        return v


class TranslationResponse(BaseModel):
    """翻译响应模型"""
    translation: str
    keywords: List[str]
    direction: TranslationDirection = Field(
        default=TranslationDirection.ZH_TO_EN,
        description="实际使用的翻译方向"
    )
    provider: str = Field(
        default="deepseek",
        description="使用的 AI 提供商"
    )