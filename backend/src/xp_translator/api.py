"""
FastAPI 应用和路由定义
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .models import TranslationRequest, TranslationResponse
from .clients import create_ai_client

# 加载环境变量
load_dotenv()

# 创建 FastAPI 应用
app = FastAPI(
    title="XP Translator API",
    description="中文到英文翻译服务，提取关键词",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注意：不再使用全局 ai_client，而是在每个请求中根据 provider 创建


@app.get("/")
async def root():
    """根路径，返回 API 基本信息"""
    return {
        "message": "XP Translator API",
        "version": "1.0.0",
        "endpoints": {
            "POST /translate": "翻译中文文本并提取关键词",
            "GET /health": "健康检查"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "xp-translator"}


@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    翻译文本并提取关键词
    
    - **text**: 要翻译的文本
    - **direction**: 翻译方向，可选值：zh_to_en（中文到英文，默认）, en_to_zh（英文到中文）, auto（自动检测）
    - **provider**: AI 提供商，可选值：deepseek（DeepSeek，默认）, aliyun（通义千问）
    
    返回:
    - **translation**: 翻译结果
    - **keywords**: 关键词列表（最多3个）
    - **direction**: 实际使用的翻译方向
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="文本不能为空")
    
    try:
        # 根据 provider 创建 AI 客户端
        ai_client = create_ai_client(request.provider)
        
        # 调用 AI 服务进行翻译和关键词提取
        translation, keywords = await ai_client.translate_and_extract(
            request.text,
            direction=request.direction.value
        )
        
        return TranslationResponse(
            translation=translation,
            keywords=keywords,
            direction=request.direction,
            provider=request.provider
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"翻译服务错误: {str(e)}")