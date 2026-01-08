import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const XPTranslatorApp());
}

class XPTranslatorApp extends StatelessWidget {
  const XPTranslatorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'XP Translator',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      home: const TranslationPage(),
    );
  }
}

class TranslationPage extends StatefulWidget {
  const TranslationPage({super.key});

  @override
  State<TranslationPage> createState() => _TranslationPageState();
}

class _TranslationPageState extends State<TranslationPage> {
  final TextEditingController _textController = TextEditingController();
  final FocusNode _textFocusNode = FocusNode();
  String _translation = '';
  List<String> _keywords = [];
  bool _isLoading = false;
  String _errorMessage = '';
  // macOS 上使用 localhost 通常比 127.0.0.1 有更好的网络权限兼容性
  String _backendUrl = 'http://localhost:1216';
  // 翻译方向：zh_to_en（中文到英文），en_to_zh（英文到中文），auto（自动检测）
  String _translationDirection = 'zh_to_en';
  // AI 模型选择：deepseek, aliyun
  String _aiProvider = 'deepseek';

  @override
  void initState() {
    super.initState();
    // 延迟获取焦点
    Future.delayed(const Duration(milliseconds: 100), () {
      _textFocusNode.requestFocus();
    });
  }

  @override
  void dispose() {
    _textFocusNode.dispose();
    super.dispose();
  }

  Future<bool> _testBackendConnection() async {
    print('测试后端连接: $_backendUrl/health');
    try {
      final response = await http.get(
        Uri.parse('$_backendUrl/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 5));
      
      print('连接响应: ${response.statusCode} ${response.body}');
      return response.statusCode == 200;
    } catch (e) {
      print('连接错误: $e');
      return false;
    }
  }

  Future<void> _translateText() async {
    final text = _textController.text.trim();
    if (text.isEmpty) {
      setState(() {
        _errorMessage = '请输入要翻译的文本';
      });
      return;
    }

    // 测试连接
    print('开始翻译，先测试后端连接...');
    final isBackendAvailable = await _testBackendConnection();
    if (!isBackendAvailable) {
      // 尝试使用 localhost 测试
      final testUrl = _backendUrl.contains('127.0.0.1')
          ? _backendUrl.replaceAll('127.0.0.1', 'localhost')
          : _backendUrl.replaceAll('localhost', '127.0.0.1');
      
      print('尝试备用地址: $testUrl');
      
      setState(() {
        _errorMessage = '''
后端连接失败！

当前地址: $_backendUrl
备用地址: $testUrl

macOS 网络权限问题解决方案：

1. 🔧 检查后端是否运行：
 cd backend && uv run uvicorn src.xp_translator.api:app --host 127.0.0.1 --port 1216

2. 🔍 测试连接（在终端中运行）：
 curl http://127.0.0.1:1216/health

3. 🔓 如果 curl 成功但 Flutter 失败，可能是 macOS 网络权限问题：
 - 打开「系统偏好设置」→「安全性与隐私」→「防火墙」
 - 确保 Flutter 应用有网络访问权限
 - 或临时关闭防火墙测试

4. 🌐 尝试使用 localhost 代替 127.0.0.1：
 - 在设置中修改后端地址为：http://localhost:1216

5. 📱 替代方案：使用 Web 浏览器运行
 - 安装 Chrome：brew install --cask google-chrome
 - 运行：flutter run -d chrome

6. 📋 查看控制台输出获取详细错误信息
''';
        _isLoading = false;
      });
      return;
    }
    
    print('后端连接成功，开始翻译...');

    setState(() {
      _isLoading = true;
      _errorMessage = '';
      _translation = '';
      _keywords = [];
    });

    try {
      final response = await http.post(
        Uri.parse('$_backendUrl/translate'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'text': text,
          'direction': _translationDirection,
          'provider': _aiProvider,
        }),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _translation = data['translation'] ?? '';
          _keywords = List<String>.from(data['keywords'] ?? []);
        });
      } else {
        setState(() {
          _errorMessage = '翻译失败: HTTP ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = '错误: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _clearAll() {
    setState(() {
      _textController.clear();
      _translation = '';
      _keywords = [];
      _errorMessage = '';
      _translationDirection = 'zh_to_en'; // 重置为默认方向
      _aiProvider = 'deepseek'; // 重置为默认模型
      _textFocusNode.requestFocus();
    });
  }

  void _updateBackendUrl(String url) {
    setState(() {
      _backendUrl = url;
    });
  }

  Future<void> _copyToClipboard(String text, String label, BuildContext context) async {
    await Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('已复制 $label 到剪贴板'),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  Future<void> _copyKeywordsToClipboard(BuildContext context) async {
    final keywordsText = _keywords.join(', ');
    await Clipboard.setData(ClipboardData(text: keywordsText));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('已复制所有关键词到剪贴板'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  String _getHintText() {
    switch (_translationDirection) {
      case 'zh_to_en':
        return '请输入要翻译的中文文本...';
      case 'en_to_zh':
        return '请输入要翻译的英文文本...';
      case 'auto':
        return '请输入要翻译的文本（自动检测语言）...';
      default:
        return '请输入要翻译的文本...';
    }
  }

  String _getTranslationTitle() {
    switch (_translationDirection) {
      case 'zh_to_en':
        return '英文翻译';
      case 'en_to_zh':
        return '中文翻译';
      case 'auto':
        return '翻译结果';
      default:
        return '翻译结果';
    }
  }

  String _getEmptyStateText() {
    switch (_translationDirection) {
      case 'zh_to_en':
        return '输入中文文本并点击翻译';
      case 'en_to_zh':
        return '输入英文文本并点击翻译';
      case 'auto':
        return '输入文本并点击翻译（自动检测语言）';
      default:
        return '输入文本并点击翻译';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('XP Translator'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => _showSettingsDialog(context),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 输入区域
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 第一行：标题和模型选择
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          '输入文本',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        DropdownButton<String>(
                          value: _aiProvider,
                          onChanged: _isLoading
                              ? null
                              : (String? newValue) {
                                  if (newValue != null) {
                                    setState(() {
                                      _aiProvider = newValue;
                                    });
                                  }
                                },
                          items: const [
                            DropdownMenuItem(
                              value: 'deepseek',
                              child: Row(
                                children: [
                                  Icon(Icons.memory, size: 16),
                                  SizedBox(width: 4),
                                  Text('DeepSeek'),
                                ],
                              ),
                            ),
                            DropdownMenuItem(
                              value: 'aliyun',
                              child: Row(
                                children: [
                                  Icon(Icons.cloud, size: 16),
                                  SizedBox(width: 4),
                                  Text('通义千问'),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 8),
                    
                    // 第二行：翻译方向选择
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '翻译方向',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[700],
                          ),
                        ),
                        DropdownButton<String>(
                          value: _translationDirection,
                          onChanged: _isLoading
                              ? null
                              : (String? newValue) {
                                  if (newValue != null) {
                                    setState(() {
                                      _translationDirection = newValue;
                                    });
                                  }
                                },
                          items: const [
                            DropdownMenuItem(
                              value: 'zh_to_en',
                              child: Row(
                                children: [
                                  Icon(Icons.translate, size: 14),
                                  SizedBox(width: 4),
                                  Text('中文 → 英文'),
                                ],
                              ),
                            ),
                            DropdownMenuItem(
                              value: 'en_to_zh',
                              child: Row(
                                children: [
                                  Icon(Icons.translate, size: 14),
                                  SizedBox(width: 4),
                                  Text('英文 → 中文'),
                                ],
                              ),
                            ),
                            DropdownMenuItem(
                              value: 'auto',
                              child: Row(
                                children: [
                                  Icon(Icons.auto_awesome, size: 14),
                                  SizedBox(width: 4),
                                  Text('自动检测'),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _textController,
                      focusNode: _textFocusNode,
                      maxLines: 4,
                      decoration: InputDecoration(
                        hintText: _getHintText(),
                        border: const OutlineInputBorder(),
                        suffixIcon: IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: () {
                            _textController.clear();
                            _textFocusNode.requestFocus();
                          },
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: _isLoading ? null : _translateText,
                            icon: _isLoading
                                ? const SizedBox(
                                    width: 16,
                                    height: 16,
                                    child: CircularProgressIndicator(strokeWidth: 2),
                                  )
                                : const Icon(Icons.translate),
                            label: Text(_isLoading ? '翻译中...' : '翻译'),
                          ),
                        ),
                        const SizedBox(width: 8),
                        OutlinedButton.icon(
                          onPressed: _clearAll,
                          icon: const Icon(Icons.clear_all),
                          label: const Text('清空'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // 错误信息
            if (_errorMessage.isNotEmpty)
              Card(
                color: Colors.red[50],
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: [
                      const Icon(Icons.error, color: Colors.red),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _errorMessage,
                          style: const TextStyle(color: Colors.red),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

            const SizedBox(height: 16),

            // 翻译结果
            if (_translation.isNotEmpty)
              Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            _getTranslationTitle(),
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.content_copy, size: 20),
                            onPressed: () => _copyToClipboard(_translation, '翻译结果', context),
                            tooltip: '复制翻译结果',
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      GestureDetector(
                        onTap: () => _copyToClipboard(_translation, '翻译结果', context),
                        child: Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.grey[100],
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.grey[300]!),
                          ),
                          child: Text(
                            _translation,
                            style: const TextStyle(fontSize: 16),
                          ),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '点击文本或复制按钮可复制',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
              ),

            const SizedBox(height: 16),

            // 关键词
            if (_keywords.isNotEmpty)
              Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            '关键词',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Row(
                            children: [
                              IconButton(
                                icon: const Icon(Icons.content_copy, size: 20),
                                onPressed: () => _copyKeywordsToClipboard(context),
                                tooltip: '复制所有关键词',
                              ),
                              IconButton(
                                icon: const Icon(Icons.copy_all, size: 20),
                                onPressed: () {
                                  final allText = '翻译: $_translation\n关键词: ${_keywords.join(', ')}';
                                  _copyToClipboard(allText, '完整结果', context);
                                },
                                tooltip: '复制翻译和关键词',
                              ),
                            ],
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: _keywords.map((keyword) {
                          return GestureDetector(
                            onTap: () => _copyToClipboard(keyword, '关键词 "$keyword"', context),
                            child: Chip(
                              label: Text(keyword),
                              backgroundColor: Colors.blue[100],
                              deleteIcon: const Icon(Icons.content_copy, size: 14),
                              onDeleted: () => _copyToClipboard(keyword, '关键词 "$keyword"', context),
                            ),
                          );
                        }).toList(),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '点击关键词或复制按钮可复制',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
              ),

            // 空状态
            if (_translation.isEmpty && _keywords.isEmpty && !_isLoading && _errorMessage.isEmpty)
              Container(
                margin: const EdgeInsets.only(top: 40),
                child: Column(
                  children: [
                    Icon(
                      Icons.translate,
                      size: 64,
                      color: Colors.grey[400],
                    ),
                    const SizedBox(height: 16),
                    Text(
                      _getEmptyStateText(),
                      style: TextStyle(
                        fontSize: 18,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
      floatingActionButton: _isLoading
          ? null
          : FloatingActionButton(
              onPressed: _translateText,
              tooltip: '翻译',
              child: const Icon(Icons.translate),
            ),
    );
  }

  void _showSettingsDialog(BuildContext context) {
    final urlController = TextEditingController(text: _backendUrl);

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('设置'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '后端 API 地址',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: urlController,
                  decoration: const InputDecoration(
                    hintText: 'http://127.0.0.1:1216',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                const Text(
                  '常用地址：',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    ActionChip(
                      label: const Text('127.0.0.1:1216'),
                      onPressed: () {
                        urlController.text = 'http://127.0.0.1:1216';
                      },
                    ),
                    ActionChip(
                      label: const Text('localhost:1216'),
                      onPressed: () {
                        urlController.text = 'http://localhost:1216';
                      },
                    ),
                    ActionChip(
                      label: const Text('0.0.0.0:1216'),
                      onPressed: () {
                        urlController.text = 'http://0.0.0.0:1216';
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                const Text(
                  'macOS 网络权限提示：',
                  style: TextStyle(fontWeight: FontWeight.bold, color: Colors.orange),
                ),
                const SizedBox(height: 8),
                const Text(
                  '如果遇到 "Operation not permitted" 错误：\n'
                  '1. 尝试切换 127.0.0.1 和 localhost\n'
                  '2. 检查系统防火墙设置\n'
                  '3. 或使用 Web 浏览器运行',
                  style: TextStyle(fontSize: 12, color: Colors.grey),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('取消'),
            ),
            ElevatedButton(
              onPressed: () {
                _updateBackendUrl(urlController.text.trim());
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('设置已保存')),
                );
              },
              child: const Text('保存'),
            ),
          ],
        );
      },
    );
  }
}
