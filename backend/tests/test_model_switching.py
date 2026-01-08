#!/usr/bin/env python3
"""
测试模型切换功能
"""

import sys
import os
import json
import requests

def test_model_switching():
    """测试不同模型切换"""
    base_url = "http://127.0.0.1:1216"
    
    test_cases = [
        {
            "name": "DeepSeek 模型 - 中文到英文",
            "text": "你好世界",
            "direction": "zh_to_en",
            "provider": "deepseek"
        },
        {
            "name": "DeepSeek 模型 - 英文到中文",
            "text": "Hello world",
            "direction": "en_to_zh",
            "provider": "deepseek"
        },
        {
            "name": "通义千问模型 - 中文到英文",
            "text": "人工智能",
            "direction": "zh_to_en",
            "provider": "aliyun"
        },
        {
            "name": "通义千问模型 - 英文到中文",
            "text": "Artificial Intelligence",
            "direction": "en_to_zh",
            "provider": "aliyun"
        },
        {
            "name": "默认模型（不指定 provider）",
            "text": "测试文本",
            "direction": "auto",
            "provider": None  # 使用默认
        }
    ]
    
    print("测试模型切换功能...")
    print("=" * 60)
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print(f"文本: {test_case['text']}")
        print(f"方向: {test_case['direction']}")
        print(f"模型: {test_case['provider'] or '默认 (deepseek)'}")
        
        try:
            # 构建请求数据
            request_data = {
                "text": test_case["text"],
                "direction": test_case["direction"]
            }
            
            # 如果指定了 provider，添加到请求中
            if test_case["provider"]:
                request_data["provider"] = test_case["provider"]
            
            response = requests.post(
                f"{base_url}/translate",
                headers={"Content-Type": "application/json"},
                json=request_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功")
                print(f"   翻译: {data.get('translation', 'N/A')}")
                print(f"   关键词: {data.get('keywords', [])}")
                print(f"   方向: {data.get('direction', 'N/A')}")
            else:
                print(f"❌ 失败: HTTP {response.status_code}")
                print(f"   响应: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接失败: 请确保后端正在运行")
            print(f"   运行: cd backend && uv run uvicorn src.xp_translator.api:app --host 127.0.0.1 --port 1216")
            break
        except requests.exceptions.Timeout:
            print(f"❌ 请求超时: 可能是 API 响应较慢")
        except Exception as e:
            print(f"❌ 错误: {str(e)}")

def test_api_info():
    """测试 API 基本信息"""
    base_url = "http://127.0.0.1:1216"
    
    print("\n\n测试 API 基本信息...")
    print("=" * 60)
    
    try:
        # 测试根路径
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 根路径可访问")
            data = response.json()
            print(f"   消息: {data.get('message', 'N/A')}")
            print(f"   版本: {data.get('version', 'N/A')}")
        else:
            print(f"❌ 根路径不可访问: HTTP {response.status_code}")
            
        # 测试健康检查
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 健康检查通过")
            data = response.json()
            print(f"   状态: {data.get('status', 'N/A')}")
            print(f"   服务: {data.get('service', 'N/A')}")
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
            
        # 测试 API 文档页面
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API 文档可访问: http://127.0.0.1:1216/docs")
        else:
            print(f"❌ API 文档不可访问: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保后端正在运行")
    except Exception as e:
        print(f"❌ 错误: {str(e)}")

def check_environment():
    """检查环境变量配置"""
    print("\n\n检查环境变量配置...")
    print("=" * 60)
    
    env_vars = [
        "DEEPSEEK_API_KEY",
        "DEEPSEEK_BASE_URL",
        "DEEPSEEK_MODEL",
        "ALIYUN_API_KEY",
        "ALIYUN_BASE_URL",
        "ALIYUN_MODEL",
        "AI_PROVIDER"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # 隐藏敏感信息的部分内容
            if "API_KEY" in var and len(value) > 8:
                masked = value[:4] + "..." + value[-4:]
                print(f"✅ {var}: {masked}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: 未设置")

if __name__ == "__main__":
    print("XP-Translator 模型切换功能测试")
    print("=" * 60)
    
    # 检查环境变量
    check_environment()
    
    # 测试 API 基本信息
    test_api_info()
    
    # 测试模型切换
    test_model_switching()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("\n使用说明:")
    print("1. 启动后端: cd backend && uv run uvicorn src.xp_translator.api:app --host 127.0.0.1 --port 1216")
    print("2. 启动前端: cd frontend && flutter run -d chrome")
    print("3. 在前端界面中:")
    print("   - 选择 AI 模型: DeepSeek 或 通义千问")
    print("   - 选择翻译方向: 中文→英文、英文→中文、自动检测")
    print("   - 输入文本并点击翻译")
    print("4. 访问 API 文档: http://127.0.0.1:1216/docs")