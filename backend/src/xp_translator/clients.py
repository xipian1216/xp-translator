"""
AI 客户端模块
支持多种大模型 API：DeepSeek、通义千问等
"""

import os
import asyncio
from typing import List, Optional
from openai import OpenAI


class BaseAIClient:
    """AI 客户端基类"""
    
    def __init__(self, provider: str, api_key: str, base_url: str, model: str):
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        
        if not self.api_key:
            raise ValueError(f"{provider.upper()}_API_KEY 未配置，请检查 .env 文件")
            
        # 使用 OpenAI SDK 初始化客户端（兼容模式）
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    async def translate_and_extract(self, text: str, direction: str = "zh_to_en") -> tuple[str, List[str]]:
        """翻译文本并提取关键词（子类必须实现）"""
        raise NotImplementedError("子类必须实现此方法")
    
    def translate_sync(self, text: str, direction: str = "zh_to_en") -> tuple[str, List[str]]:
        """同步版本的翻译方法"""
        return asyncio.run(self.translate_and_extract(text, direction))


class DeepSeekClient(BaseAIClient):
    """DeepSeek API 客户端"""
    
    def __init__(self):
        super().__init__(
            provider="deepseek",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        )
        
    async def translate_and_extract(self, text: str, direction: str = "zh_to_en") -> tuple[str, List[str]]:
        """使用 DeepSeek API 进行翻译和关键词提取
        
        Args:
            text: 要翻译的文本
            direction: 翻译方向，可选值：zh_to_en（中文到英文），en_to_zh（英文到中文），auto（自动检测）
        """
        prompt = self._build_translation_prompt(text, direction)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的翻译助手，擅长多语言翻译和关键词提取。"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            return self._parse_response(content, direction, text)
            
        except Exception as e:
            raise Exception(f"DeepSeek API 调用失败: {str(e)}")
    
    # 为了兼容性，添加 translate 方法作为 translate_and_extract 的别名
    async def translate(self, text: str, direction: str = "zh_to_en") -> tuple[str, List[str]]:
        """翻译方法（translate_and_extract 的别名）"""
        return await self.translate_and_extract(text, direction)
    
    def _build_translation_prompt(self, text: str, direction: str) -> str:
        """构建翻译提示词"""
        if direction == "zh_to_en":
            source_lang = "中文"
            target_lang = "英文"
            keyword_lang = "英文"
        elif direction == "en_to_zh":
            source_lang = "英文"
            target_lang = "中文"
            keyword_lang = "中文"
        else:  # auto 或默认
            # 简单检测：如果包含中文字符，则认为是中文到英文
            import re
            if re.search(r'[\u4e00-\u9fff]', text):
                source_lang = "中文"
                target_lang = "英文"
                keyword_lang = "英文"
            else:
                source_lang = "英文"
                target_lang = "中文"
                keyword_lang = "中文"
        
        return f'''请将以下{source_lang}文本翻译成{target_lang}，并提取3个最重要的关键词（{keyword_lang}）：

{source_lang}文本：{text}

请严格按照以下格式回复：
翻译：[{target_lang}翻译]
关键词：[关键词1, 关键词2, 关键词3]

注意：
1. 翻译要准确自然
2. 关键词要是{keyword_lang}名词或短语
3. 关键词用逗号分隔，不要有编号
4. 只返回上述格式，不要有其他内容'''
    
    def _parse_response(self, content: str, direction: str, original_text: str) -> tuple[str, List[str]]:
        """解析 API 响应
        
        Args:
            content: API 返回的内容
            direction: 翻译方向
            original_text: 原始文本
        """
        translation = ""
        keywords = []
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("翻译："):
                translation = line.replace("翻译：", "").strip()
            elif line.startswith("关键词："):
                keywords_str = line.replace("关键词：", "").strip()
                # 移除方括号并分割
                if keywords_str.startswith('[') and keywords_str.endswith(']'):
                    keywords_str = keywords_str[1:-1]
                keywords = [k.strip() for k in keywords_str.split(',')]
        
        # 如果解析失败，使用备用方案
        if not translation:
            if direction == "zh_to_en" or direction == "auto":
                translation = f"Translated: {original_text}"
            else:
                translation = f"翻译：{original_text}"
        
        if not keywords:
            if direction == "zh_to_en" or direction == "auto":
                keywords = ["translation", "text", "content"]
            else:
                keywords = ["翻译", "文本", "内容"]
        
        # 限制关键词数量
        keywords = keywords[:3]
        
        return translation, keywords


class AliyunQwenClient(BaseAIClient):
    """通义千问 API 客户端（阿里云 DashScope）"""
    
    def __init__(self):
        super().__init__(
            provider="aliyun",
            api_key=os.getenv("ALIYUN_API_KEY"),
            base_url=os.getenv("ALIYUN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            model=os.getenv("ALIYUN_MODEL", "qwen-plus")
        )
    
    async def translate_and_extract(self, text: str, direction: str = "zh_to_en") -> tuple[str, List[str]]:
        """使用通义千问 API 进行翻译和关键词提取
        
        Args:
            text: 要翻译的文本
            direction: 翻译方向，可选值：zh_to_en（中文到英文），en_to_zh（英文到中文），auto（自动检测）
        """
        prompt = self._build_translation_prompt(text, direction)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的翻译助手，擅长多语言翻译和关键词提取。"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            return self._parse_response(content, direction, text)
            
        except Exception as e:
            raise Exception(f"通义千问 API 调用失败: {str(e)}")
    
    # 为了兼容性，添加 translate 方法作为 translate_and_extract 的别名
    async def translate(self, text: str, direction: str = "zh_to_en") -> tuple[str, List[str]]:
        """翻译方法（translate_and_extract 的别名）"""
        return await self.translate_and_extract(text, direction)
    
    def _build_translation_prompt(self, text: str, direction: str) -> str:
        """构建翻译提示词（与 DeepSeek 相同）"""
        if direction == "zh_to_en":
            source_lang = "中文"
            target_lang = "英文"
            keyword_lang = "英文"
        elif direction == "en_to_zh":
            source_lang = "英文"
            target_lang = "中文"
            keyword_lang = "中文"
        else:  # auto 或默认
            # 简单检测：如果包含中文字符，则认为是中文到英文
            import re
            if re.search(r'[\u4e00-\u9fff]', text):
                source_lang = "中文"
                target_lang = "英文"
                keyword_lang = "英文"
            else:
                source_lang = "英文"
                target_lang = "中文"
                keyword_lang = "中文"
        
        return f'''请将以下{source_lang}文本翻译成{target_lang}，并提取3个最重要的关键词（{keyword_lang}）：

{source_lang}文本：{text}

请严格按照以下格式回复：
翻译：[{target_lang}翻译]
关键词：[关键词1, 关键词2, 关键词3]

注意：
1. 翻译要准确自然
2. 关键词要是{keyword_lang}名词或短语
3. 关键词用逗号分隔，不要有编号
4. 只返回上述格式，不要有其他内容'''
    
    def _parse_response(self, content: str, direction: str, original_text: str) -> tuple[str, List[str]]:
        """解析 API 响应（与 DeepSeek 相同）
        
        Args:
            content: API 返回的内容
            direction: 翻译方向
            original_text: 原始文本
        """
        translation = ""
        keywords = []
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("翻译："):
                translation = line.replace("翻译：", "").strip()
            elif line.startswith("关键词："):
                keywords_str = line.replace("关键词：", "").strip()
                # 移除方括号并分割
                if keywords_str.startswith('[') and keywords_str.endswith(']'):
                    keywords_str = keywords_str[1:-1]
                keywords = [k.strip() for k in keywords_str.split(',')]
        
        # 如果解析失败，使用备用方案
        if not translation:
            if direction == "zh_to_en" or direction == "auto":
                translation = f"Translated: {original_text}"
            else:
                translation = f"翻译：{original_text}"
        
        if not keywords:
            if direction == "zh_to_en" or direction == "auto":
                keywords = ["translation", "text", "content"]
            else:
                keywords = ["翻译", "文本", "内容"]
        
        # 限制关键词数量
        keywords = keywords[:3]
        
        return translation, keywords


class MockAIClient:
    """模拟大模型 API 调用（备用方案）"""
    
    def __init__(self):
        self.provider = "mock"
        pass
    
    async def translate_and_extract(self, text: str, direction: str = "zh_to_en") -> tuple[str, List[str]]:
        """模拟翻译和关键词提取（当真实 API 不可用时使用）
        
        Args:
            text: 要翻译的文本
            direction: 翻译方向，可选值：zh_to_en（中文到英文），en_to_zh（英文到中文），auto（自动检测）
        """
        # 中文到英文翻译映射
        zh_to_en_map = {
            "你好": "Hello",
            "世界": "World",
            "翻译": "Translation",
            "人工智能": "Artificial Intelligence",
            "学习": "Learning",
            "项目": "Project",
            "测试": "Test",
            "开发": "Development",
            "代码": "Code",
            "程序": "Program"
        }
        
        # 英文到中文翻译映射
        en_to_zh_map = {
            "hello": "你好",
            "world": "世界",
            "translation": "翻译",
            "artificial intelligence": "人工智能",
            "learning": "学习",
            "project": "项目",
            "test": "测试",
            "development": "开发",
            "code": "代码",
            "program": "程序"
        }
        
        # 关键词映射
        zh_keywords_map = {
            "你好": ["问候", "打招呼", "欢迎"],
            "世界": ["世界", "全球", "地球"],
            "翻译": ["翻译", "语言", "转换"],
            "人工智能": ["人工智能", "AI", "机器学习"],
            "学习": ["学习", "教育", "知识"],
            "项目": ["项目", "任务", "工作"],
            "测试": ["测试", "检验", "验证"],
            "开发": ["开发", "编程", "软件"],
            "代码": ["代码", "编程", "源码"],
            "程序": ["程序", "应用", "软件"]
        }
        
        en_keywords_map = {
            "hello": ["greeting", "hello", "welcome"],
            "world": ["world", "global", "earth"],
            "translation": ["translation", "language", "convert"],
            "artificial intelligence": ["AI", "artificial intelligence", "machine learning"],
            "learning": ["learning", "study", "education"],
            "project": ["project", "task", "assignment"],
            "test": ["test", "testing", "validation"],
            "development": ["development", "coding", "programming"],
            "code": ["code", "programming", "source"],
            "program": ["program", "application", "software"]
        }
        
        # 根据方向选择翻译映射
        if direction == "zh_to_en":
            translation_map = zh_to_en_map
            keywords_map = en_keywords_map
            default_translation = f"Translated: {text}"
            default_keywords = ["translation", "text", "content"]
        elif direction == "en_to_zh":
            translation_map = en_to_zh_map
            keywords_map = zh_keywords_map
            default_translation = f"翻译：{text}"
            default_keywords = ["翻译", "文本", "内容"]
        else:  # auto
            # 简单检测：如果包含中文字符，则认为是中文到英文
            import re
            if re.search(r'[\u4e00-\u9fff]', text):
                translation_map = zh_to_en_map
                keywords_map = en_keywords_map
                default_translation = f"Translated: {text}"
                default_keywords = ["translation", "text", "content"]
            else:
                translation_map = en_to_zh_map
                keywords_map = zh_keywords_map
                default_translation = f"翻译：{text}"
                default_keywords = ["翻译", "文本", "内容"]
        
        # 查找匹配的翻译
        translation = default_translation
        for key, value in translation_map.items():
            if key.lower() in text.lower():
                translation = value
                break
        
        # 提取关键词
        keywords = []
        for key, value in keywords_map.items():
            if key.lower() in text.lower():
                keywords.extend(value)
        
        # 如果没有找到关键词，使用默认关键词
        if not keywords:
            keywords = default_keywords
        
        # 限制关键词数量
        keywords = list(set(keywords))[:3]
        
        # 模拟 API 调用延迟
        await asyncio.sleep(0.1)
        
        return translation, keywords
    
    def translate_sync(self, text: str, direction: str = "zh_to_en") -> tuple[str, List[str]]:
        """同步版本的翻译方法"""
        return asyncio.run(self.translate_and_extract(text, direction))
    
    # 为了兼容性，添加 translate 方法作为 translate_and_extract 的别名
    async def translate(self, text: str, direction: str = "zh_to_en") -> tuple[str, List[str]]:
        """翻译方法（translate_and_extract 的别名）"""
        return await self.translate_and_extract(text, direction)


# 创建 AI 客户端实例
def create_ai_client(provider: Optional[str] = None):
    """创建 AI 客户端实例
    
    Args:
        provider: AI 提供商，可选值：deepseek, aliyun, mock
                如果为 None，则使用环境变量 AI_PROVIDER 的值
    """
    if provider is None:
        provider = os.getenv("AI_PROVIDER", "deepseek").lower()
    
    print(f"🔧 尝试创建 {provider} 客户端...")
    
    if provider == "deepseek":
        try:
            client = DeepSeekClient()
            print(f"✅ 使用 DeepSeek API 客户端 (模型: {client.model})")
            return client
        except ValueError as e:
            print(f"⚠️  DeepSeek 配置错误: {str(e)}，尝试其他提供商")
            return create_ai_client("aliyun")  # 尝试通义千问
        except Exception as e:
            print(f"⚠️  初始化 DeepSeek 客户端失败: {str(e)}，尝试其他提供商")
            return create_ai_client("aliyun")  # 尝试通义千问
    
    elif provider == "aliyun":
        try:
            client = AliyunQwenClient()
            print(f"✅ 使用通义千问 API 客户端 (模型: {client.model})")
            return client
        except ValueError as e:
            print(f"⚠️  通义千问配置错误: {str(e)}，尝试模拟客户端")
            return create_ai_client("mock")
        except Exception as e:
            print(f"⚠️  初始化通义千问客户端失败: {str(e)}，尝试模拟客户端")
            return create_ai_client("mock")
    
    else:  # mock 或默认
        client = MockAIClient()
        print(f"⚠️  使用模拟客户端")
        return client