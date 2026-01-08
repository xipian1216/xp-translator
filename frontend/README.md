# XP Translator Frontend

Flutter 前端应用，用于中文到英文翻译和关键词提取，支持多模型切换、翻译方向选择和复制功能。

## 🚀 功能特性

### ✅ 核心功能
- **文本输入**：支持中英文多行文本输入
- **一键翻译**：调用后端 AI 模型进行翻译
- **结果显示**：清晰展示翻译结果和关键词
- **响应式设计**：适配不同屏幕尺寸和设备
- **主题支持**：自动适配系统深色/浅色主题

### 🎯 新增功能
- **复制功能**：翻译结果和关键词可一键复制
- **翻译方向选择**：中文→英文、英文→中文、自动检测三种模式
- **模型选择**：支持 DeepSeek 和通义千问自由切换
- **设置界面**：动态配置后端地址和连接测试
- **错误处理**：完善的网络错误和用户反馈
- **清空功能**：一键清空输入和结果

## 📱 界面预览

```
┌─────────────────────────────────────────────┐
│ XP Translator                    ⚙️         │
├─────────────────────────────────────────────┤
│ 模型: [DeepSeek ▼]                           │
│ 方向: [中文→英文 ▼]                          │
│                                               │
│ 输入文本                                      │
│ ┌─────────────────────────────────────────┐ │
│ │ 在这里输入要翻译的文本...                │ │
│ │                                         │ │
│ │                                         │ │
│ └─────────────────────────────────────────┘ │
│                                               │
│ [ 翻译 ]        [ 清空 ]                      │
│                                               │
│ 翻译结果                                      │
│ ┌─────────────────────────────────────────┐ │
│ │ Hello World                             │ │
│ │                                         │ │
│ │ 📋 复制翻译                             │ │
│ └─────────────────────────────────────────┘ │
│                                               │
│ 关键词                                        │
│ [hello] [world] [greeting]                   │
│ 📋 复制所有关键词                            │
└─────────────────────────────────────────────┘
```

## ⚡ 快速开始

### 1. 安装 Flutter

确保已安装 Flutter SDK：
```bash
flutter --version
```

如果未安装，请参考 [Flutter 官方安装指南](https://flutter.dev/docs/get-started/install)。

### 2. 安装依赖

```bash
cd frontend
flutter pub get
```

### 3. 配置后端连接

#### 默认配置
默认后端地址为 `http://127.0.0.1:1216`。

#### 修改配置方式
1. **应用内设置**：点击右上角设置图标 ⚙️，修改后端 API 地址
2. **环境变量**：运行应用时指定后端地址
3. **构建时配置**：构建发布版本时指定

#### 环境变量配置
```bash
# 运行应用时指定后端地址
flutter run --dart-define=BACKEND_URL=http://your-backend-url:port
```

### 4. 运行应用

#### 开发模式（热重载）
```bash
# 自动选择可用设备
flutter run

# 指定设备运行
flutter run -d macos      # macOS 桌面应用
flutter run -d chrome     # Web 浏览器
flutter run -d android    # Android 设备/模拟器
flutter run -d ios        # iOS 设备/模拟器
```

#### 推荐使用 macOS 桌面
```bash
flutter run -d macos
```

## 📁 项目结构

```
frontend/
├── lib/
│   └── main.dart              # 主应用入口，包含完整界面逻辑
├── pubspec.yaml               # Flutter 依赖配置
├── README.md                  # 本文档
├── test/widget_test.dart      # 前端测试文件
└── (平台特定目录)
    ├── android/               # Android 平台配置
    ├── ios/                   # iOS 平台配置
    ├── macos/                 # macOS 平台配置
    ├── linux/                 # Linux 平台配置
    ├── windows/               # Windows 平台配置
    └── web/                   # Web 平台配置
```

## 🔌 API 集成

### 后端接口要求

前端期望后端提供以下接口：

#### 1. 翻译接口
```
POST /translate
Content-Type: application/json

请求体:
{
  "text": "要翻译的文本",
  "direction": "zh_to_en",  // 可选：zh_to_en, en_to_zh, auto
  "provider": "deepseek"    // 可选：deepseek, aliyun
}

响应:
{
  "translation": "翻译结果",
  "keywords": ["关键词1", "关键词2", "关键词3"],
  "direction": "zh_to_en",
  "provider": "deepseek"
}
```

#### 2. 健康检查（可选）
```
GET /health

响应:
{
  "status": "healthy",
  "service": "xp-translator",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 3. API 信息（可选）
```
GET /

响应:
{
  "message": "XP Translator API",
  "version": "1.0.0",
  "endpoints": ["/translate", "/health", "/docs"]
}
```

### 配置说明

#### 1. 基础配置
在 `lib/main.dart` 中修改：
```dart
static const String defaultBackendUrl = 'http://127.0.0.1:1216';
```

#### 2. 运行时配置
通过应用内设置界面动态修改：
1. 点击右上角设置图标 ⚙️
2. 输入新的后端地址
3. 点击 "测试连接" 验证
4. 点击 "保存" 应用配置

#### 3. 构建时配置
```bash
# 生产环境构建
flutter build apk --release --dart-define=BACKEND_URL=https://api.example.com

# Web 构建
flutter build web --release --dart-define=BACKEND_URL=https://api.example.com

# macOS 构建
flutter build macos --release --dart-define=BACKEND_URL=https://api.example.com
```

## 🎨 界面设计

### 主要组件

#### 1. 应用栏 (AppBar)
- 应用标题：XP Translator
- 设置按钮：⚙️ 图标，打开设置对话框

#### 2. 控制面板
- **模型选择下拉菜单**：DeepSeek / 通义千问
- **翻译方向下拉菜单**：中文→英文 / 英文→中文 / 自动检测
- **输入提示文本**：根据选择的翻译方向动态变化

#### 3. 文本输入区域
- 多行文本输入框
- 支持中英文输入
- 自动调整高度
- 占位符文本提示

#### 4. 操作按钮
- **翻译按钮**：蓝色主按钮，触发翻译操作
- **清空按钮**：灰色次按钮，清空输入和结果

#### 5. 结果显示区域
- **翻译结果卡片**：白色背景，阴影效果
- **复制按钮**：📋 图标，一键复制翻译结果
- **关键词标签**：彩色圆角标签，显示提取的关键词
- **复制所有关键词按钮**：一键复制所有关键词

#### 6. 设置对话框
- 后端地址输入框
- 连接测试按钮
- 保存和取消按钮

### 状态管理

#### 应用状态
```dart
class _TranslationPageState extends State<TranslationPage> {
  String _inputText = '';                    // 输入文本
  String _translation = '';                  // 翻译结果
  List<String> _keywords = [];               // 关键词列表
  String _selectedModel = 'DeepSeek';        // 选择的模型
  String _selectedDirection = '中文→英文';    // 翻译方向
  String _backendUrl = defaultBackendUrl;    // 后端地址
  bool _isLoading = false;                   // 加载状态
  // ...
}
```

#### 状态更新
- **setState()**：更新界面状态
- **FutureBuilder**：处理异步操作
- **try-catch**：错误处理和用户反馈

### 主题和样式

#### 颜色方案
```dart
ColorScheme _colorScheme(BuildContext context) {
  return Theme.of(context).colorScheme;
}

// 主要颜色
primaryColor = Colors.blue.shade600;
secondaryColor = Colors.grey.shade300;
backgroundColor = Theme.of(context).scaffoldBackgroundColor;
textColor = Theme.of(context).textTheme.bodyLarge?.color;
```

#### 响应式设计
```dart
LayoutBuilder(
  builder: (context, constraints) {
    if (constraints.maxWidth > 600) {
      // 桌面/平板布局
      return _buildDesktopLayout(context);
    } else {
      // 手机布局
      return _buildMobileLayout(context);
    }
  },
)
```

## 🔧 开发指南

### 添加新功能

#### 1. 添加新的 API 调用
```dart
Future<Map<String, dynamic>> _callCustomEndpoint(String text) async {
  final response = await http.post(
    Uri.parse('$_backendUrl/custom'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'text': text}),
  );
  
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('API 调用失败: ${response.statusCode}');
  }
}
```

#### 2. 添加新的界面组件
```dart
Widget _buildNewFeature(BuildContext context) {
  return Card(
    child: Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          Text('新功能', style: Theme.of(context).textTheme.titleLarge),
          // 更多组件...
        ],
      ),
    ),
  );
}
```

#### 3. 添加新的设置选项
```dart
// 在设置对话框中添加
TextFormField(
  decoration: InputDecoration(
    labelText: '新设置选项',
    hintText: '请输入...',
  ),
  onChanged: (value) {
    // 更新状态
  },
),
```

### 代码结构

#### 主应用结构
```dart
void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'XP Translator',
      theme: ThemeData.light(),
      darkTheme: ThemeData.dark(),
      themeMode: ThemeMode.system,
      home: const TranslationPage(),
    );
  }
}
```

#### 翻译页面结构
```dart
class TranslationPage extends StatefulWidget {
  const TranslationPage({super.key});

  @override
  State<TranslationPage> createState() => _TranslationPageState();
}

class _TranslationPageState extends State<TranslationPage> {
  // 状态变量
  // 构建方法
  // 事件处理
  // 辅助方法
}
```

### 调试技巧

#### 1. 启用调试模式
```dart
// 在开发时添加调试输出
print('当前状态: inputText=$_inputText, isLoading=$_isLoading');

// 使用 Flutter DevTools
// flutter pub global activate devtools
// flutter pub global run devtools
```

#### 2. 网络请求调试
```dart
// 查看请求和响应
void _debugNetworkRequest(Uri url, Map<String, dynamic> body) {
  if (kDebugMode) {
    print('请求 URL: $url');
    print('请求体: $body');
  }
}

// 在 Chrome DevTools 中查看 Network 标签
```

#### 3. 状态监控
```dart
// 使用 Provider 或 Riverpod 进行状态管理（未来扩展）
// 当前使用简单的 setState 管理
```

## 📦 构建发布

### Android

#### APK 构建
```bash
flutter build apk --release
# 输出: build/app/outputs/flutter-apk/app-release.apk
```

#### App Bundle 构建
```bash
flutter build appbundle --release
# 输出: build/app/outputs/bundle/release/app-release.aab
```

#### 签名配置
在 `android/app/build.gradle` 中配置签名信息。

### iOS

#### 构建 IPA
```bash
flutter build ios --release
# 然后在 Xcode 中导出 IPA
```

#### 配置要求
- Apple Developer 账户
- 有效的证书和配置文件
- Xcode 13.0+

### Web

#### 构建 Web 应用
```bash
flutter build web --release
# 输出: build/web/
```

#### 部署到服务器
```bash
# 使用 nginx 或 Apache 部署
# 或部署到 Firebase Hosting、Netlify、Vercel 等
```

### macOS

#### 构建 macOS 应用
```bash
flutter build macos --release
# 输出: build/macos/Build/Products/Release/XP Translator.app
```

#### 打包 DMG
```bash
# 使用 create-dmg 工具
create-dmg 'XP Translator.app'
```

### 一键构建脚本
```bash
#!/bin/bash
# build_all.sh

echo "构建 Android APK..."
flutter build apk --release

echo "构建 Web 应用..."
flutter build web --release

echo "构建 macOS 应用..."
flutter build macos --release

echo "所有构建完成！"
```

## 🐛 故障排除

### 常见问题

#### 1. 后端连接失败
```bash
# 测试后端连接
curl http://127.0.0.1:1216/health

# 检查 CORS 配置
# 后端需要允许前端域名

# 检查防火墙设置
# macOS: 系统偏好设置 -> 安全性与隐私 -> 防火墙
```

#### 2. Flutter 依赖问题
```bash
# 清理缓存
flutter clean
flutter pub cache repair

# 重新安装依赖
flutter pub get

# 升级 Flutter
flutter upgrade
```

#### 3. 构建错误
```bash
# 检查 Flutter 版本
flutter doctor -v

# 检查依赖冲突
flutter pub deps

# 查看详细错误信息
flutter build apk --release --verbose
```

#### 4. macOS 特定问题
```bash
# Xcode 命令行工具
xcode-select --install

# 重置 Xcode 路径
sudo xcode-select --reset

# 授予网络权限
# 系统偏好设置 -> 安全性与隐私 -> 防火墙
```

### 网络问题解决方案

#### 方案1：使用 127.0.0.1 代替 localhost
```dart
// 修改后端地址
static const String defaultBackendUrl = 'http://127.0.0.1:1216';
```

#### 方案2：检查端口占用
```bash
# 查看端口占用情况
lsof -i :1216

# 如果端口被占用，更换端口
# 后端: --port 1217
# 前端: http://127.0.0.1:1217
```

#### 方案3：测试网络连接
```bash
# 测试后端是否运行
curl http://127.0.0.1:1216/health
curl http://localhost:1216/health

# 测试前端网络访问
# 在浏览器中打开 http://localhost:8080
```

### 调试网络请求

#### 1. 使用 Charles Proxy 或 Fiddler
- 监控 HTTP/HTTPS 请求
- 查看请求和响应详情
- 模拟网络延迟和错误

#### 2. 使用浏览器开发者工具
- 打开 Chrome DevTools (F12)
- 查看 Network 标签
- 检查请求头、响应体和状态码

#### 3. 添加日志记录
```dart
void _logNetworkRequest(String url, int statusCode, String responseBody) {
  if (kDebugMode) {
    print('=== 网络请求日志 ===');
    print('URL: $url');
    print('状态码: $statusCode');
    print('响应体: ${responseBody.substring(0, 100)}...');
    print('===================');
  }
}
```

## 🧪 测试

### 单元测试
```dart
// test/unit_test.dart
void main() {
  test('字符串处理测试', () {
    expect(trimText('  hello  '), 'hello');
  });
  
  test('URL 验证测试', () {
    expect(isValidUrl('http://example.com'), true);
    expect(isValidUrl('invalid-url'), false);
  });
}
```

### 部件测试
```dart
// test/widget_test.dart
void main() {
  testWidgets('翻译按钮测试', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());
    
    // 查找翻译按钮
    final translateButton = find.text('翻译');
    expect(translateButton, findsOneWidget);
    
    // 点击按钮
    await tester.tap(translateButton);
    await tester.pump();
    
    // 验证状态变化
    // ...
  });
}
```

### 集成测试
```dart
// test_driver/app_test.dart
void main() {
  test('完整翻译流程测试', () async {
    // 启动应用
    final FlutterDriver driver = await FlutterDriver.connect();
    
    // 输入文本
    await driver.tap(find.byValueKey('input_field'));
    await driver.enterText('你好');
    
    // 点击翻译按钮
    await driver.tap(find.byValueKey('translate_button'));
    
    // 等待结果
    await driver.waitFor(find.text('Hello'));
    
    // 关闭驱动
    driver.close();
  });
}
```

## 📊 项目完成状态

### ✅ 功能验证
前端已通过所有功能验证：
1. **文本输入**：支持中英文多行文本输入
2. **翻译按钮**：正常调用后端 API 进行翻译
3. **结果显示**：清晰展示翻译结果和关键词
4. **复制功能**：翻译结果和关键词可一键复制
5. **翻译方向选择**：中文→英文、英文→中文、自动检测三种模式
6. **模型选择**：支持 DeepSeek 和通义千问自由切换
7. **设置界面**：动态配置后端地址和连接测试
8. **错误处理**：完善的网络错误和用户反馈

### ✅ 与后端集成
- **API 兼容性**：完全兼容后端 FastAPI 接口
- **错误处理**：优雅处理网络错误和 API 错误
- **状态管理**：完善的加载状态和用户反馈
- **配置管理**：支持动态修改后端地址

### 🎯 快速验证
```bash
# 1. 确保后端服务运行
# 在另一个终端中运行：
cd backend
uv run uvicorn src.xp_translator.api:app --reload --host 127.0.0.1 --port 1216

# 2. 启动前端应用
cd frontend
flutter run -d macos

# 3. 测试功能
# - 输入文本并点击翻译按钮
# - 测试不同翻译方向
# - 测试不同 AI 模型
# - 测试复制功能
# - 测试设置界面
```

### ✅ 预期结果
- 前端界面正常显示
- 翻译功能正常工作
- 所有交互功能正常
- 错误处理机制有效

## 🔄 持续集成

### GitHub Actions 配置
```yaml
name: Frontend CI/CD

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
