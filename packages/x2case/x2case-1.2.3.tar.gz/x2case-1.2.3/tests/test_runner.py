#!/usr/bin/env python
# _*_ coding:utf-8 _*_
"""
测试运行器
统一管理和运行所有测试
"""
import sys
import os
import subprocess
import time
from pathlib import Path


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.tests_dir = Path(__file__).parent
        self.test_files = [
            'test_csv_conversion.py',
            'test_func_fix.py'
        ]
        self.debug_files = [
            'debug_tools.py'
        ]
    
    def run_single_test(self, test_file):
        """运行单个测试文件"""
        test_path = self.tests_dir / test_file
        if not test_path.exists():
            print(f"✗ 测试文件不存在: {test_file}")
            return False
        
        print(f"\\n{'='*60}")
        print(f"运行测试: {test_file}")
        print(f"{'='*60}")
        
        try:
            # 设置PYTHONPATH确保能够导入x2case模块
            env = os.environ.copy()
            project_root = self.tests_dir.parent
            env['PYTHONPATH'] = str(project_root)
            
            result = subprocess.run(
                [sys.executable, str(test_path)],
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                env=env
            )
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            
            success = result.returncode == 0
            if success:
                print(f"✓ {test_file} 测试通过")
            else:
                print(f"✗ {test_file} 测试失败 (返回码: {result.returncode})")
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"✗ {test_file} 测试超时")
            return False
        except Exception as e:
            print(f"✗ {test_file} 运行异常: {e}")
            return False
    
    def run_debug_tool(self, debug_file):
        """运行调试工具"""
        debug_path = self.tests_dir / debug_file
        if not debug_path.exists():
            print(f"✗ 调试文件不存在: {debug_file}")
            return False
        
        print(f"\\n{'='*60}")
        print(f"运行调试工具: {debug_file}")
        print(f"{'='*60}")
        
        try:
            # 设置PYTHONPATH确保能够导入x2case模块
            env = os.environ.copy()
            project_root = self.tests_dir.parent
            env['PYTHONPATH'] = str(project_root)
            
            result = subprocess.run(
                [sys.executable, str(debug_path)],
                capture_output=True,
                text=True,
                timeout=120,  # 2分钟超时
                env=env
            )
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            
            print(f"✓ {debug_file} 运行完成")
            return True
            
        except subprocess.TimeoutExpired:
            print(f"✗ {debug_file} 运行超时")
            return False
        except Exception as e:
            print(f"✗ {debug_file} 运行异常: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行所有测试...")
        
        passed_tests = 0
        failed_tests = 0
        total_tests = len(self.test_files)
        
        for test_file in self.test_files:
            success = self.run_single_test(test_file)
            if success:
                passed_tests += 1
            else:
                failed_tests += 1
        
        return passed_tests, failed_tests, total_tests
    
    def run_debug_tools(self):
        """运行所有调试工具"""
        print("\\n🔧 运行调试工具...")
        
        for debug_file in self.debug_files:
            self.run_debug_tool(debug_file)
    
    def generate_test_report(self, passed, failed, total):
        """生成测试报告"""
        print("\\n" + "="*60)
        print("测试报告")
        print("="*60)
        print(f"总计测试: {total}")
        print(f"通过测试: {passed}")
        print(f"失败测试: {failed}")
        print(f"成功率: {(passed/total*100):.1f}%" if total > 0 else "0%")
        
        if failed == 0:
            print("\\n🎉 所有测试通过！")
            print("✅ 项目功能正常，修复成功！")
        else:
            print(f"\\n⚠️  有 {failed} 个测试失败")
            print("❌ 需要进一步检查和修复")
        
        print("="*60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='X2Case 测试运行器')
    parser.add_argument('--tests-only', action='store_true', help='只运行测试，不运行调试工具')
    parser.add_argument('--debug-only', action='store_true', help='只运行调试工具')
    parser.add_argument('--test', type=str, help='运行指定的测试文件')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.test:
        # 运行指定测试
        success = runner.run_single_test(args.test)
        return 0 if success else 1
    
    elif args.debug_only:
        # 只运行调试工具
        runner.run_debug_tools()
        return 0
    
    elif args.tests_only:
        # 只运行测试
        passed, failed, total = runner.run_all_tests()
        runner.generate_test_report(passed, failed, total)
        return 0 if failed == 0 else 1
    
    else:
        # 运行所有测试和调试工具
        passed, failed, total = runner.run_all_tests()
        runner.run_debug_tools()
        runner.generate_test_report(passed, failed, total)
        return 0 if failed == 0 else 1


if __name__ == '__main__':
    exit(main())