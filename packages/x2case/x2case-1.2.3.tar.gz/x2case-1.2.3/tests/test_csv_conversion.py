#!/usr/bin/env python
# _*_ coding:utf-8 _*_
"""
CSV转换功能完整测试套件
包含所有CSV转换相关的测试用例
"""
import csv
import json
import logging
import os
import tempfile
from unittest.mock import patch

from x2case.func import XmindZenParser
from x2case.jira import xmind_to_jira_csv_file, gen_case_row
from x2case.com import TestSuite, TestCase, TestStep
from x2case import const

logging.basicConfig(level=logging.INFO)


class CSVConversionTester:
    """CSV转换功能测试器"""
    
    def __init__(self):
        self.test_results = []
    
    def create_test_data(self):
        """创建测试数据"""
        # 创建多个测试步骤
        steps = []
        for i in range(1, 4):
            step = TestStep()
            step.step_number = i
            step.actions = f"执行第{i}步操作"
            step.expected_results = f"第{i}步预期结果"
            steps.append(step)
        
        # 创建多个测试用例，测试不同的优先级和类型
        testcases = []
        
        # 高优先级手动测试用例
        testcase1 = TestCase()
        testcase1.case_id = "TC001"
        testcase1.name = "高优先级手动测试用例"
        testcase1.version = 1
        testcase1.summary = "这是一个高优先级的手动测试用例"
        testcase1.preconditions = "系统已启动，用户已准备"
        testcase1.steps = steps
        testcase1.importance = 1  # High priority
        testcase1.execution_type = 1  # Manual
        testcase1.result = 0  # Non-execution
        testcases.append(testcase1)
        
        # 中优先级自动化测试用例
        testcase2 = TestCase()
        testcase2.case_id = "TC002"
        testcase2.name = "中优先级自动化测试用例"
        testcase2.version = 1
        testcase2.summary = "这是一个中优先级的自动化测试用例"
        testcase2.preconditions = "自动化环境已配置"
        testcase2.steps = steps[:2]  # 只有2个步骤
        testcase2.importance = 2  # Medium priority
        testcase2.execution_type = 2  # Automation
        testcase2.result = 1  # Pass
        testcases.append(testcase2)
        
        # 低优先级测试用例
        testcase3 = TestCase()
        testcase3.case_id = "TC003"
        testcase3.name = "低优先级测试用例"
        testcase3.version = 1
        testcase3.summary = "这是一个低优先级的测试用例"
        testcase3.preconditions = "基础条件满足"
        testcase3.steps = [steps[0]]  # 只有1个步骤
        testcase3.importance = 3  # Low priority
        testcase3.execution_type = 1  # Manual
        testcase3.result = 2  # Failed
        testcases.append(testcase3)
        
        # 创建测试套件
        testsuite = TestSuite()
        testsuite.name = "综合功能测试套件"
        testsuite.details = "包含不同优先级和类型的测试用例"
        testsuite.testcase_list = testcases
        testsuite.epic_link = "EPIC-123"
        
        return [testsuite]
    
    def test_csv_generation(self):
        """测试CSV文件生成"""
        print("=== 测试CSV文件生成 ===")
        
        test_suites = self.create_test_data()
        
        # 创建临时XMind文件
        with tempfile.NamedTemporaryFile(suffix='.xmind', delete=False) as temp_file:
            temp_xmind_file = temp_file.name
        
        try:
            # 模拟XmindZenParser的get_xmind_testcase_list方法
            def mock_get_testcase_list(self):
                testcases = []
                for testsuite in test_suites:
                    product = testsuite.name
                    epic_link = getattr(testsuite, 'epic_link', '')
                    if hasattr(testsuite, 'testcase_list') and testsuite.testcase_list:
                        for case in testsuite.testcase_list:
                            case_data = case.to_dict()
                            case_data['product'] = product
                            case_data['suite'] = testsuite.name
                            case_data['epic_link'] = epic_link
                            testcases.append(case_data)
                return testcases
            
            # 使用patch来模拟方法
            with patch.object(XmindZenParser, 'get_xmind_testcase_list', mock_get_testcase_list):
                # 测试CSV文件生成
                csv_file = xmind_to_jira_csv_file(temp_xmind_file)
                
                print(f"✓ CSV文件生成成功: {csv_file}")
                
                # 验证CSV文件内容
                if os.path.exists(csv_file):
                    with open(csv_file, 'r', encoding='utf8') as f:
                        reader = csv.reader(f)
                        rows = list(reader)
                        
                    print(f"✓ CSV文件读取成功，总行数: {len(rows)}")
                    print(f"✓ 表头行: {len(rows[0])} 个字段")
                    print(f"✓ 数据行: {len(rows) - 1} 条记录")
                    
                    # 验证表头
                    expected_header = const.JIRA_HEAD
                    actual_header = rows[0]
                    if actual_header == expected_header:
                        print("✓ CSV表头验证通过")
                        self.test_results.append("CSV表头验证: PASS")
                    else:
                        print("✗ CSV表头验证失败")
                        self.test_results.append("CSV表头验证: FAIL")
                    
                    # 验证数据行
                    print("\n=== CSV数据行验证 ===")
                    for i, row in enumerate(rows[1:], 1):
                        print(f"\n数据行 {i}:")
                        print(f"  用例标识: {row[0]}")
                        print(f"  摘要: {row[2]}")
                        print(f"  测试类型: {row[7]}")
                        print(f"  应用程序: {row[8]}")
                        print(f"  优先级: {row[11]}")
                        print(f"  标签: {row[14]}")
                        print(f"  前置条件: {row[22]}")
                        print(f"  Epic链接: {row[27]}")
                    
                    # 清理生成的CSV文件
                    os.unlink(csv_file)
                    print(f"\n✓ 清理临时CSV文件: {csv_file}")
                    self.test_results.append("CSV生成测试: PASS")
                    
                else:
                    print("✗ CSV文件未生成")
                    self.test_results.append("CSV生成测试: FAIL")
                    
        finally:
            # 清理临时XMind文件
            if os.path.exists(temp_xmind_file):
                os.unlink(temp_xmind_file)
    
    def test_edge_cases(self):
        """测试边界情况"""
        print("\n=== 测试边界情况 ===")
        
        # 测试空步骤的情况
        empty_step = TestStep()
        empty_step.step_number = 1
        empty_step.actions = ""
        empty_step.expected_results = ""
        
        testcase = TestCase()
        testcase.case_id = "TC999"
        testcase.name = "空步骤测试用例"
        testcase.summary = "测试空步骤的处理"
        testcase.preconditions = ""
        testcase.steps = [empty_step]
        testcase.importance = 999  # 不在映射范围内
        testcase.execution_type = 999  # 不在映射范围内
        
        case_data = testcase.to_dict()
        case_data['product'] = "测试产品"
        case_data['suite'] = "测试套件"
        case_data['epic_link'] = ""
        
        try:
            row = gen_case_row(case_data)
            print("✓ 边界情况处理成功")
            print(f"  优先级（默认值）: {row[11]}")
            print(f"  测试类型（默认值）: {row[7]}")
            print(f"  操作步骤处理: '{row[3]}'")
            print(f"  预期结果处理: '{row[5]}'")
            self.test_results.append("边界情况测试: PASS")
            
        except Exception as e:
            print(f"✗ 边界情况处理失败: {e}")
            self.test_results.append("边界情况测试: FAIL")
    
    def verify_csv_format(self):
        """验证CSV格式符合JIRA导入要求"""
        print("\n=== 验证CSV格式 ===")
        
        # 检查常量定义
        header_count = len(const.JIRA_HEAD)
        print(f"✓ JIRA表头字段数: {header_count}")
        
        # 显示关键字段位置
        key_fields = {
            'Test Case Identifier*': 0,
            'Summary*': 2, 
            'Action*': 3,
            'Expected Result': 5,
            'Test Type': 7,
            'Priority': 11,
            'Pre-Condition': 22,
            'Epic Link': 27
        }
        
        print("✓ 关键字段位置映射:")
        all_correct = True
        for field, pos in key_fields.items():
            if pos < len(const.JIRA_HEAD):
                actual_field = const.JIRA_HEAD[pos]
                if actual_field == field:
                    print(f"  {field}: 位置 {pos} ✓")
                else:
                    print(f"  {field}: 位置 {pos} - 实际为 '{actual_field}' ✗")
                    all_correct = False
            else:
                print(f"  {field}: 位置 {pos} - 超出范围 ✗")
                all_correct = False
        
        if all_correct:
            self.test_results.append("CSV格式验证: PASS")
        else:
            self.test_results.append("CSV格式验证: FAIL")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("CSV转换功能完整测试套件")
        print("=" * 60)
        
        self.test_csv_generation()
        self.test_edge_cases()
        self.verify_csv_format()
        
        print(f"\n" + "=" * 60)
        print("测试结果汇总:")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for result in self.test_results:
            print(f"  {result}")
            if "PASS" in result:
                passed += 1
            else:
                failed += 1
        
        print(f"\n总计: {len(self.test_results)} 项测试")
        print(f"通过: {passed} 项")
        print(f"失败: {failed} 项")
        
        if failed == 0:
            print("🎉 所有测试通过！")
        else:
            print("⚠️  存在测试失败")
        
        return failed == 0


def main():
    """主函数"""
    tester = CSVConversionTester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())