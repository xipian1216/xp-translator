#!/usr/bin/env python3
"""
XP-Translator 测试运行器

统一运行所有测试，支持多种运行方式：
1. 运行所有测试
2. 运行特定测试模块
3. 运行特定测试类
4. 运行特定测试方法
5. 生成测试报告
"""

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path
from typing import List, Optional

# 添加父目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def run_pytest_tests(
    test_paths: List[str] = None,
    verbose: bool = False,
    coverage: bool = False,
    html_report: bool = False,
    xml_report: bool = False,
    parallel: bool = False
) -> int:
    """
    使用 pytest 运行测试
    
    Args:
        test_paths: 测试路径列表，如果为 None 则运行所有测试
        verbose: 是否显示详细输出
        coverage: 是否生成覆盖率报告
        html_report: 是否生成 HTML 报告
        xml_report: 是否生成 XML 报告
        parallel: 是否并行运行测试
    
    Returns:
        退出代码
    """
    cmd = ["pytest"]
    
    # 添加测试路径
    if test_paths:
        cmd.extend(test_paths)
    else:
        cmd.append(".")
    
    # 添加选项
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=term", "--cov-report=html"])
    
    if html_report:
        cmd.append("--html=test_report.html")
    
    if xml_report:
        cmd.append("--junitxml=test_results.xml")
    
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # 添加其他有用选项
    cmd.extend(["--tb=short", "--strict-markers"])
    
    print(f"运行命令: {' '.join(cmd)}")
    print("=" * 60)
    
    # 运行测试
    result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
    return result.returncode


def run_unittest_tests(test_paths: List[str] = None, verbose: bool = False) -> int:
    """
    使用 unittest 运行测试
    
    Args:
        test_paths: 测试路径列表
        verbose: 是否显示详细输出
    
    Returns:
        退出代码
    """
    import unittest
    
    # 构建测试加载器
    loader = unittest.TestLoader()
    
    if test_paths:
        # 加载指定测试
        suite = unittest.TestSuite()
        for test_path in test_paths:
            if "::" in test_path:
                # 特定测试类或方法
                module_path, test_name = test_path.split("::", 1)
                module = __import__(module_path.replace("/", ".").replace(".py", ""))
                if "." in test_name:
                    # 测试方法
                    class_name, method_name = test_name.split(".", 1)
                    test_class = getattr(module, class_name)
                    suite.addTest(test_class(method_name))
                else:
                    # 测试类
                    test_class = getattr(module, test_name)
                    suite.addTests(loader.loadTestsFromTestCase(test_class))
            else:
                # 测试模块
                suite.addTests(loader.discover(start_dir=os.path.dirname(__file__), pattern=test_path))
    else:
        # 发现所有测试
        suite = loader.discover(start_dir=os.path.dirname(__file__), pattern="test_*.py")
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


def list_available_tests():
    """列出所有可用的测试"""
    test_dir = Path(__file__).parent
    
    print("可用的测试模块:")
    print("-" * 40)
    
    for test_file in test_dir.glob("test_*.py"):
        module_name = test_file.stem
        print(f"  {module_name}")
        
        # 尝试导入模块并列出测试类
        try:
            module = __import__(module_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and attr_name.startswith("Test"):
                    print(f"    - {attr_name}")
                    
                    # 列出测试方法
                    for method_name in dir(attr):
                        if method_name.startswith("test_"):
                            print(f"      * {method_name}")
        except ImportError:
            pass
    
    print()


def generate_test_report(exit_code: int):
    """生成测试报告"""
    report_file = "test_summary.json"
    
    # 收集测试结果信息
    report = {
        "timestamp": os.path.getmtime(__file__) if os.path.exists(__file__) else None,
        "exit_code": exit_code,
        "test_files": [],
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }
    }
    
    # 检查测试文件
    test_dir = Path(__file__).parent
    for test_file in test_dir.glob("test_*.py"):
        if test_file.name != "run_tests.py":
            report["test_files"].append(test_file.name)
    
    print("\n" + "=" * 60)
    print("测试报告摘要")
    print("=" * 60)
    print(f"测试文件数量: {len(report['test_files'])}")
    print(f"退出代码: {exit_code}")
    print(f"状态: {'✅ 通过' if exit_code == 0 else '❌ 失败'}")
    
    # 保存报告
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n详细报告已保存到: {report_file}")
    
    # 显示下一步建议
    if exit_code != 0:
        print("\n⚠️  测试失败！建议：")
        print("  1. 检查环境变量配置")
        print("  2. 确保后端服务未运行（测试会启动自己的实例）")
        print("  3. 运行特定测试以调试：python run_tests.py --module test_api")
        print("  4. 查看详细输出：python run_tests.py --verbose")
    else:
        print("\n✅ 所有测试通过！项目可以部署。")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="XP-Translator 测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                    # 运行所有测试
  %(prog)s --verbose          # 详细模式运行所有测试
  %(prog)s --coverage         # 运行测试并生成覆盖率报告
  %(prog)s --module test_api  # 只运行 test_api 模块
  %(prog)s --list             # 列出所有可用测试
  %(prog)s --unittest         # 使用 unittest 而不是 pytest
  %(prog)s test_api::TestAPIFunctionality  # 运行特定测试类
  %(prog)s test_api::TestAPIFunctionality::test_root_endpoint  # 运行特定测试方法
        """
    )
    
    parser.add_argument(
        "test_specifiers",
        nargs="*",
        help="测试指定器（模块、类或方法），例如：test_api 或 test_api::TestAPIFunctionality"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出"
    )
    
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="生成代码覆盖率报告"
    )
    
    parser.add_argument(
        "--html",
        action="store_true",
        help="生成 HTML 测试报告"
    )
    
    parser.add_argument(
        "--xml",
        action="store_true",
        help="生成 XML 测试报告（JUnit 格式）"
    )
    
    parser.add_argument(
        "-p", "--parallel",
        action="store_true",
        help="并行运行测试"
    )
    
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="列出所有可用测试"
    )
    
    parser.add_argument(
        "-u", "--unittest",
        action="store_true",
        help="使用 unittest 而不是 pytest"
    )
    
    parser.add_argument(
        "--module",
        help="运行特定模块的测试（已弃用，使用位置参数）"
    )
    
    args = parser.parse_args()
    
    # 列出测试
    if args.list:
        list_available_tests()
        return 0
    
    # 处理测试指定器
    test_paths = []
    if args.test_specifiers:
        test_paths = args.test_specifiers
    elif args.module:
        test_paths = [args.module + ".py"]
    
    # 转换模块名为文件路径
    for i, path in enumerate(test_paths):
        if not path.endswith(".py") and "::" not in path:
            test_paths[i] = path + ".py"
    
    print("XP-Translator 测试套件")
    print("=" * 60)
    
    # 检查测试环境
    print("检查测试环境...")
    
    # 检查必要的导入
    try:
        import pytest
        print("✅ pytest 可用")
    except ImportError:
        print("❌ pytest 未安装，请运行: pip install pytest")
        if not args.unittest:
            print("   或使用 --unittest 参数使用 unittest")
            return 1
    
    try:
        from src.xp_translator.api import app
        print("✅ 可以导入应用")
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("   请确保在正确的目录中运行测试")
        return 1
    
    # 运行测试
    if args.unittest:
        print("\n使用 unittest 运行测试...")
        exit_code = run_unittest_tests(test_paths, args.verbose)
    else:
        print("\n使用 pytest 运行测试...")
        exit_code = run_pytest_tests(
            test_paths=test_paths,
            verbose=args.verbose,
            coverage=args.coverage,
            html_report=args.html,
            xml_report=args.xml,
            parallel=args.parallel
        )
    
    # 生成报告
    generate_test_report(exit_code)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())