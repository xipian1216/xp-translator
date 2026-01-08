/// 应用配置类
class AppConfig {
  /// 后端 API 基础 URL
  /// 开发环境默认使用 localhost:1216
  /// 生产环境应配置为实际的后端地址
  static const String baseUrl = String.fromEnvironment(
    'BACKEND_URL',
    defaultValue: 'http://localhost:1216',
  );

  /// 超时设置（秒）
  static const int connectTimeout = 10;
  static const int receiveTimeout = 30;

  /// 调试模式
  static const bool debug = bool.fromEnvironment('DEBUG', defaultValue: true);

  /// 获取完整的 API URL
  static String getApiUrl(String endpoint) {
    return '$baseUrl$endpoint';
  }

  /// 打印配置信息（仅调试模式）
  static void printConfig() {
    if (debug) {
      print('=== App Configuration ===');
      print('Backend URL: $baseUrl');
      print('Connect Timeout: ${connectTimeout}s');
      print('Receive Timeout: ${receiveTimeout}s');
      print('Debug Mode: $debug');
      print('=========================');
    }
  }
}

/// API 端点配置
class ApiEndpoints {
  static const String translate = '/translate';
  static const String health = '/health';
  
  /// 获取翻译接口 URL
  static String get translateUrl => AppConfig.getApiUrl(translate);
  
  /// 获取健康检查接口 URL
  static String get healthUrl => AppConfig.getApiUrl(health);
}