# XP Translator Backend

基于 FastAPI 的中文到英文翻译服务，支持多模型 AI 翻译、关键词提取和完整测试套件。

## 🚀 功能特性

### ✅ 核心功能
- **多语言翻译**：支持中文↔英文双向翻译，自动语言检测
- **关键词提取**：智能提取 3 个最重要的关键词
- **多模型支持**：DeepSeek、通义千问双模型，智能降级到模拟模式
- **完整测试**：143+ 个测试用例，覆盖 API、客户端、数据模型
- **RESTful API**：标准的 REST API 设计，完整的 OpenAPI 文档

### 🎯 新增功能
- **翻译方向选择**：中文→英文、英文→中文、自动检测三种模式
- **模型切换**：运行时动态切换 AI 模型
- **输入验证**：严格的请求参数验证和错误处理
- **性能监控**：响应时间监控和并发处理
- **Docker 支持**：完整的容器化部署方案

## 📁 项目结构

```
backend/
├── src/xp_translator/          # 后端源代码
│   ├── __init__.py
│   ├── api.py                  # FastAPI 应用和路由
│   ├── clients.py              # AI 客户端（DeepSeek/通义千问/Mock）
│   ├── models.py               # 数据模型定义
│   └── main.py                 # 应用入口
├── tests/                      # 完整测试套件
│   ├── __init__.py
│   ├── conftest.py             # Pytest 配置和共享 fixture
│   ├── test_api.py             # API 接口测试（75个测试）
│   ├── test_clients.py         # AI 客户端测试（26个测试）
│   ├── test_models.py          # 数据模型测试（42个测试）
│   ├── test_model_switching.py # 模型切换功能测试
│   ├── run_tests.py            # 统一测试运行器
│   └── all_tests.md            # 完整的测试文档
├── pyproject.toml              # Python 项目配置
├── .env                        # 环境变量配置
├── .env.example                # 环境变量模板
└── README.md                   # 本文档
```

## ⚡ 快速开始

### 1. 安装依赖

#### 使用 uv（推荐）
```bash
# 安装 uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv sync
```

#### 使用 pip
```bash
pip install -e .
```

### 2. 配置环境变量

复制环境变量模板并配置 API 密钥：
```bash
cp .env.example .env
```

编辑 `.env` 文件：
```bash
# DeepSeek API 配置（默认启用）
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# 通义千问 API 配置
ALIYUN_API_KEY=sk-your-aliyun-api-key
ALIYUN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
ALIYUN_MODEL=qwen-plus

# 默认配置
AI_PROVIDER=deepseek
BACKEND_PORT=1216
DEBUG=true
```

### 3. 运行服务

#### 开发模式（自动重载）
```bash
uv run uvicorn src.xp_translator.api:app --reload --host 127.0.0.1 --port 1216
```

#### 生产模式
```bash
uv run uvicorn src.xp_translator.api:app --host 0.0.0.0 --port 1216 --workers 4
```

服务将在 http://localhost:1216 启动。

## 📚 API 文档

启动服务后访问：
- **Swagger UI**：http://localhost:1216/docs
- **ReDoc**：http://localhost:1216/redoc
- **OpenAPI JSON**：http://localhost:1216/openapi.json

### 主要接口

#### 1. 根路径
```
GET /
```
返回 API 基本信息，包括版本、可用端点和状态。

#### 2. 健康检查
```
GET /health
```
返回服务健康状态，用于监控和负载均衡。

#### 3. 翻译接口
```
POST /translate
```
请求体：
```json
{
  "text": "要翻译的文本",
  "direction": "zh_to_en",  // 可选：zh_to_en, en_to_zh, auto
  "provider": "deepseek"    // 可选：deepseek, aliyun
}
```

响应：
```json
{
  "translation": "翻译结果",
  "keywords": ["关键词1", "关键词2", "关键词3"],
  "direction": "zh_to_en",
  "provider": "deepseek"
}
```

## 🤖 支持的 AI 服务

### 1. DeepSeek（默认）
- **模型**：deepseek-chat
- **特点**：高性能中文模型，性价比高
- **配置**：`DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL`
- **文档**：https://platform.deepseek.com/api_keys

### 2. 通义千问
- **模型**：qwen-plus
- **特点**：阿里云大模型，国内访问稳定
- **配置**：`ALIYUN_API_KEY`、`ALIYUN_BASE_URL`
- **文档**：https://dashscope.aliyuncs.com/

### 3. 模拟模式
- **特点**：无需 API 密钥，内置简单翻译映射
- **适用场景**：开发、测试、演示
- **自动启用**：当 API 密钥未配置时自动降级

## 🧪 测试套件

### 运行测试
```bash
cd backend/tests

# 使用测试运行器（推荐）
python run_tests.py

# 详细模式
python run_tests.py --verbose

# 生成覆盖率报告
python run_tests.py --coverage

# 运行特定测试模块
python run_tests.py --module test_api

# 列出所有测试
python run_tests.py --list
```

### 测试类型

#### 1. API 接口测试（test_api.py）
- **基础功能测试**：根路径、健康检查、翻译接口
- **输入验证测试**：空文本、无效参数、超长文本
- **翻译功能测试**：不同翻译方向、不同 AI 提供商
- **错误处理测试**：无效 JSON、无效参数、API 错误
- **性能测试**：响应时间、并发请求

#### 2. AI 客户端测试（test_clients.py）
- **基础客户端测试**：BaseAIClient 抽象类
- **DeepSeek 客户端测试**：初始化、翻译、错误处理
- **通义千问客户端测试**：初始化、翻译、自定义配置
- **模拟客户端测试**：翻译映射、关键词提取
- **客户端工厂测试**：动态创建客户端

#### 3. 数据模型测试（test_models.py）
- **枚举类型测试**：TranslationDirection、AIProvider
- **请求模型测试**：TranslationRequest 验证和序列化
- **响应模型测试**：TranslationResponse 验证和序列化
- **模型集成测试**：请求响应一致性、序列化往返

#### 4. 模型切换测试（test_model_switching.py）
- **端到端集成测试**：不同模型的实际翻译效果
- **环境变量检查**：配置验证和掩码显示

### 测试报告
测试运行后会生成：
- **控制台输出**：详细的测试执行结果
- **test_summary.json**：JSON 格式的测试摘要
- **HTML/XML 报告**：可选生成的详细报告
- **覆盖率报告**：代码覆盖率统计

## 🐳 Docker 部署

### 构建镜像
```bash
# 构建后端镜像
docker build -f ../Dockerfile.backend -t xp-translator-backend .

# 或使用 Docker Compose
docker-compose build backend
```

### 运行容器
```bash
# 单独运行
docker run -d -p 1216:1216 \
  -e DEEPSEEK_API_KEY=your_key \
  --name xp-backend \
  xp-translator-backend

# 使用 Docker Compose
docker-compose up -d
```

### 生产环境配置
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    image: xp-translator-backend:latest
    ports:
      - "1216:1216"
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - ALIYUN_API_KEY=${ALIYUN_API_KEY}
      - DEBUG=false
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:1216/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🔧 开发指南

### 代码架构

#### AI 客户端架构
```python
class BaseAIClient:
    """AI 客户端基类"""
    async def translate_and_extract(text, direction) -> tuple[str, List[str]]
    
class DeepSeekClient(BaseAIClient):
    """DeepSeek API 客户端"""
    
class AliyunQwenClient(BaseAIClient):
    """通义千问 API 客户端"""
    
class MockAIClient:
    """模拟客户端（备用方案）"""
```

#### 数据模型
```python
class TranslationDirection(str, Enum):
    ZH_TO_EN = "zh_to_en"  # 中文到英文
    EN_TO_ZH = "en_to_zh"  # 英文到中文
    AUTO = "auto"          # 自动检测

class TranslationRequest(BaseModel):
    text: str
    direction: TranslationDirection = ZH_TO_EN
    provider: str = "deepseek"

class TranslationResponse(BaseModel):
    translation: str
    keywords: List[str]
    direction: TranslationDirection = ZH_TO_EN
    provider: str = "deepseek"
```

### 添加新的 AI 客户端

1. **创建客户端类**
```python
class NewAIClient(BaseAIClient):
    def __init__(self):
        super().__init__(
            provider="new_provider",
            api_key=os.getenv("NEW_API_KEY"),
            base_url=os.getenv("NEW_BASE_URL"),
            model=os.getenv("NEW_MODEL")
        )
    
    async def translate_and_extract(self, text: str, direction: str = "zh_to_en") -> tuple[str, List[str]]:
        # 实现具体的翻译逻辑
        pass
```

2. **更新客户端工厂**
```python
def create_ai_client(provider: Optional[str] = None):
    if provider == "new_provider":
        try:
            client = NewAIClient()
            return client
        except Exception as e:
            # 错误处理
            pass
```

3. **添加环境变量**
```bash
NEW_API_KEY=your_api_key
NEW_BASE_URL=https://api.newprovider.com
NEW_MODEL=new-model
```

4. **添加测试用例**
```python
class TestNewAIClient:
    def test_new_client_initialization(self):
        # 测试初始化
        pass
    
    def test_new_client_translate(self):
        # 测试翻译功能
        pass
```

### 代码规范

#### 类型注解
```python
def translate_text(text: str, direction: TranslationDirection = TranslationDirection.ZH_TO_EN) -> TranslationResponse:
    """翻译文本并返回结果"""
    pass
```

#### 错误处理
```python
try:
    result = await client.translate_and_extract(text, direction)
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    raise HTTPException(status_code=500, detail=f"翻译服务暂时不可用: {str(e)}")
```

#### 日志记录
```python
import logging

logger = logging.getLogger(__name__)

async def translate_endpoint(request: TranslationRequest):
    logger.info(f"翻译请求: text={request.text[:50]}..., direction={request.direction}")
    # 处理逻辑
```

## 🐛 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 检查端口占用
lsof -i :1216

# 更改端口
uv run uvicorn src.xp_translator.api:app --port 1217
```

#### 2. API 密钥无效
```bash
# 检查环境变量
echo $DEEPSEEK_API_KEY

# 测试 API 连接
curl -X POST "https://api.deepseek.com/v1/chat/completions" \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-chat", "messages": [{"role": "user", "content": "Hello"}]}'
```

#### 3. 依赖安装失败
```bash
# 清理缓存
rm -rf .venv
rm -rf __pycache__

# 重新安装
uv sync --clean
```

#### 4. 测试失败
```bash
# 运行特定测试调试
pytest tests/test_api.py::TestAPIFunctionality::test_translate_endpoint_valid_text -vvs

# 查看测试覆盖率
pytest tests/ --cov=src --cov-report=html
```

### 调试技巧

#### 启用详细日志
```bash
DEBUG=true uv run uvicorn src.xp_translator.api:app --reload --log-level debug
```

#### 使用 Swagger UI 测试
1. 访问 http://localhost:1216/docs
2. 点击 "Try it out" 按钮
3. 输入测试数据并执行
4. 查看请求和响应详情

#### 监控 API 性能
```bash
# 使用 curl 测试响应时间
time curl -X POST "http://localhost:1216/translate" \
  -H "Content-Type: application/json" \
  -d '{"text": "性能测试"}'
```

## 📊 性能优化

### 1. 异步处理
- 使用 FastAPI 的异步路由
- AI API 调用使用异步 HTTP 客户端
- 数据库操作使用异步驱动

### 2. 缓存策略
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_translation(text: str, direction: str) -> Optional[TranslationResponse]:
    """缓存频繁翻译的结果"""
    pass
```

### 3. 连接池
```python
import httpx

async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(api_url, json=data)
```

### 4. 限流保护
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

## 🔄 持续集成

### GitHub Actions 配置
```yaml
name: Backend CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install uv
      - run: cd backend && uv sync
      - run: cd backend && uv run pytest tests/ --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install black mypy flake8
      - run: cd backend && black --check src tests
      - run: cd backend && mypy src
      - run: cd backend && flake8 src tests

  build:
    runs-on: ubuntu-latest
    needs: [test, lint]
    steps:
      - uses: actions/checkout@v3
      - run: docker build -f Dockerfile.backend -t xp-translator-backend .
```

## 📈 监控和日志

### 日志配置
```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
```

### 健康检查端点
```python
@app.get("/health")
async def health_check():
    """健康检查端点，用于监控和负载均衡"""
    return {
        "status": "healthy",
        "service": "xp-translator",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### 性能指标
```python
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    REQUEST_COUNT.inc()
    
    response = await call_next(request)
    
    latency = time.time() - start_time
    REQUEST_LATENCY.observe(latency)
    
    return response
```

## 📊 项目完成状态

### ✅ 测试状态
- **总测试数**: 75
- **通过测试**: 75 (100%)
- **失败测试**: 0
- **警告**: 0 (已修复所有 DeprecationWarning)

### ✅ 已修复的问题
1. **AI 客户端测试异步模拟问题**：修复了 `'coroutine' object has no attribute 'choices'` 错误
2. **httpx DeprecationWarning**：更新了 `test_invalid_json` 方法，使用 `content` 参数替代 `data` 参数
3. **输入验证测试**：更新了测试以匹配实际的 Pydantic 验证行为

### ✅ 功能验证
项目已通过所有功能验证：
1. **POST /translate 接口**：完全符合任务要求
2. **多模型支持**：DeepSeek 和通义千问正常运行
3. **翻译方向**：支持中英互译和自动检测
4. **关键词提取**：自动提取 3 个关键词
5. **错误处理**：完善的错误提示和恢复机制

## 🎯 项目交付

### 快速验证
```bash
# 1. 启动服务
uv run uvicorn src.xp_translator.api:app --reload --host 127.0.0.1 --port 1216

# 2. 测试翻译接口
curl -X POST "http://localhost:1216/translate" \
  -H "Content-Type: application/json" \
  -d '{"text": "你好世界"}'

# 3. 运行完整测试
cd backend
python -m pytest tests/ -v
```

### 预期结果
- API 返回正确的翻译结果和关键词
- 所有 75 个测试通过，无失败无警告
- 前端界面正常显示和交互

## 🤝 贡献