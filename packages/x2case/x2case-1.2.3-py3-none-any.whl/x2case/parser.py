#!/usr/bin/env python
# _*_ coding:utf-8 _*_
"""
面向对象重构的XMind解析器

该模块提供了Xmind2Case类，用于将XMind思维导图文件转换为测试用例。
采用面向对象的设计模式，提供更好的代码组织和可维护性。

"""

import copy
import logging
from typing import List, Dict, Any, Generator, Optional

from x2case.com import TestSuite, TestCase, TestStep


class Xmind2Case:
    """XMind文件转换为测试用例的核心处理类
    
    该类封装了XMind文件解析和测试用例生成的所有逻辑，
    提供了面向对象的接口来处理XMind到测试用例的转换。
    
    Attributes:
        config: 配置字典，控制解析行为
        case_id_counter: 测试用例ID计数器
    """
    
    # 默认配置
    DEFAULT_CONFIG = {
        'sep': ' ',
        'valid_sep': '&>+/-',
        'precondition_sep': '\n----\n',
        'summary_sep': '\n----\n',
        'ignore_char': '#!！'
    }
    
    def __init__(self, custom_config: Optional[Dict[str, Any]] = None):
        """初始化Xmind2Case实例
        
        Args:
            custom_config: 自定义配置字典，会与默认配置合并
        """
        self.config = self.DEFAULT_CONFIG.copy()
        if custom_config:
            self.config.update(custom_config)
        self.case_id_counter = 1
    
    def convert_xmind_to_suites(self, xmind_content_dict: List[Dict[str, Any]]) -> List[TestSuite]:
        """将XMind内容字典转换为TestSuite列表
        
        Args:
            xmind_content_dict: XMind解析后的内容字典
            
        Returns:
            TestSuite对象列表
        """
        self.case_id_counter = 1
        suites = []

        for sheet in xmind_content_dict:

            root_topic = sheet['rootTopic']  # for zen rootTopic
            sub_topics = root_topic.get('children', [])

            if sub_topics:
                root_topic['topics'] = self._filter_content_children(sub_topics)
            else:
                logging.warning(f'This is a blank sheet({sheet["title"]}), should have at least 1 sub topic(test suite)')
            
            suite = self._convert_sheet_to_suite(root_topic)
            suite.sheet_name = sheet['title']  # root testsuite has a sheet_name attribute

            suites.append(suite)

        return suites
    
    def _filter_content_children(self, children: Any) -> List[Dict[str, Any]]:
        """过滤空白或以忽略字符开头的子节点"""
        if isinstance(children, dict):
            attached = children.pop('attached', [])
            result = [child for child in attached if not (
                    child.get('title') is None or
                    child.get('title', '').strip() == '' or
                    (child.get('title', '') and child['title'][0] in self.config['ignore_char']))]

            for topic in result:
                sub_children = topic.get('children', [])
                topic['topics'] = self._filter_content_children(sub_children)

            return result
        else:
            return []
    
    def _filter_topics(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤空白或以忽略字符开头的主题"""
        result = [topic for topic in topics if not (
                topic.get('title') is None or
                topic.get('title', '').strip() == '' or
                (topic.get('title', '') and topic['title'][0] in self.config['ignore_char']))]

        for topic in result:
            sub_topics = topic.get('topics', [])
            topic['topics'] = self._filter_topics(sub_topics)

        return result
    
    def _filter_element(self, values: List[Any]) -> List[str]:
        """过滤所有空白或忽略的XMind元素，特别是notes、comments、labels元素"""
        result = []
        for value in values:
            if (isinstance(value, str) and 
                value.strip() != '' and 
                value[0] not in self.config['ignore_char']):
                result.append(value.strip())
        return result
    
    def _filter_precondition(self, values: List[Any]) -> List[str]:
        """过滤前置条件"""
        result = []
        for value in values:
            content = value['plain']['content'] if isinstance(value, dict) else value
            if (isinstance(content, str) and 
                content.strip() != '' and 
                content[0] not in self.config['ignore_char']):
                result.append(content.strip())
        return result
    
    def _convert_sheet_to_suite(self, root_topic: Dict[str, Any]) -> TestSuite:
        """将XMind工作表转换为TestSuite实例"""
        suite = TestSuite()
        root_title = root_topic['title']
        separator = root_title[-1] if root_title else ''

        if separator in self.config['valid_sep']:

            self.config['sep'] = separator  # set the separator for the testcase's title
            root_title = root_title[:-1]
        else:
            self.config['sep'] = '-'

        suite.name = root_title
        suite.details = root_topic.get('notes', '')
        labels = root_topic.get('labels', [])
        suite.epic_link = labels[0] if labels else ''
        suite.sub_suites = []

        for suite_dict in root_topic.get('topics', []):
            suite.sub_suites.append(self._parse_testsuite(suite_dict))

        return suite
    
    def _parse_testsuite(self, suite_dict: Dict[str, Any]) -> TestSuite:
        """解析测试套件"""
        testsuite = TestSuite()
        testsuite.name = suite_dict['title']
        testsuite.details = suite_dict.get('notes', '')
        testsuite.testcase_list = []


        for cases_dict in suite_dict.get('topics', []):
            for case in self._recurse_parse_testcase(cases_dict):
                testsuite.testcase_list.append(case)


        return testsuite
    
    def _recurse_parse_testcase(self, case_dict: Dict[str, Any], 
                               parent: Optional[List[Dict[str, Any]]] = None) -> Generator[TestCase, None, None]:
        """递归解析测试用例"""
        if self._is_testcase_topic(case_dict):
            case = self._parse_a_testcase(case_dict, parent)
            case_id = "{:04d}".format(self.case_id_counter)
            self.case_id_counter += 1

            if not case.steps:
                case.case_id = case_id
                case.steps = [TestStep(step_number=1, actions=' ', expected_results=' ')]
                yield case
            else:
                for step in case.steps:
                    split_case: TestCase = copy.deepcopy(case)
                    split_case.case_id = case_id
                    split_case.steps = [step]
                    split_case.result = step.result
                    yield split_case
        else:
            if not parent:
                parent = []

            parent.append(case_dict)

            for child_dict in case_dict.get('topics', []):
                for case in self._recurse_parse_testcase(child_dict, parent):
                    yield case

            parent.pop()
    
    def _is_testcase_topic(self, case_dict: Dict[str, Any]) -> bool:
        """判断是否为测试用例主题"""
        priority = self._get_priority(case_dict)
        if priority:
            return True

        children = case_dict.get('topics', [])
        if children:
            return False

        return True
    
    def _parse_a_testcase(self, case_dict: Dict[str, Any], 
                         parent: Optional[List[Dict[str, Any]]]) -> TestCase:
        """解析单个测试用例"""
        testcase = TestCase()
        topics = parent + [case_dict] if parent else [case_dict]

        # DEBUG: 输出层级信息



        # 生成测试用例标题（限制层级避免过度连接）
        title_result = self._generate_testcase_title(topics)

        testcase.name = title_result


        preconditions = self._generate_testcase_preconditions(topics)
        testcase.preconditions = preconditions if preconditions else '无'

        summary = self._generate_testcase_summary(topics)
        testcase.summary = summary if summary else testcase.name
        testcase.execution_type = self._get_execution_type(topics)
        testcase.importance = self._get_priority(case_dict) or 2

        # 关键修改：处理层级结构映射到测试步骤
        step_dict_list = case_dict.get('topics', [])
        if step_dict_list:
            # 如果当前节点有子节点，尝试解析为测试步骤
            testcase.steps = self._parse_test_steps_with_hierarchy(step_dict_list, topics)
        else:
            # 如果没有子节点，检查是否可以从父级层级中提取步骤信息
            testcase.steps = self._extract_steps_from_hierarchy(topics)

        # the result of the testcase take precedence over the result of the teststep
        testcase.result = self._get_test_result(case_dict.get('markers', ''))

        if testcase.result == 0 and testcase.steps:
            for step in testcase.steps:
                if step.result == 2:
                    testcase.result = 2
                    break
                if step.result == 3:
                    testcase.result = 3
                    break
                testcase.result = step.result  # there is no need to judge where test step are ignored


        return testcase
    
    def _generate_testcase_title(self, topics: List[Dict[str, Any]]) -> str:
        """根据层级结构生成测试用例标题"""
        titles = [topic['title'] for topic in topics]
        titles = self._filter_element(titles)

        # DEBUG: 输出调试信息




        # 根据层级数量决定怎么生成标题
        if len(titles) >= 5:

            titles = titles[:2]
        elif len(titles) == 4:

            titles = titles[:2]
        else:

            pass  # 保持所有 titles
        

        
        # 使用分隔符连接，不添加额外空格
        separator = self.config['sep']
        result = separator.join(titles)


        return result
    
    def _get_execution_type(self, topics: List[Dict[str, Any]]) -> int:
        """获取执行类型"""
        labels = [topic.get('labels', '') for topic in topics]
        labels = [label[0] for label in labels if label]
        labels = self._filter_element(labels)
        exe_type = 1
        for item in labels[::-1]:
            if item.lower() in ['自动', 'auto', 'automate', 'automation']:
                exe_type = 2
                break
            if item.lower() in ['手动', '手工', 'manual']:
                exe_type = 1
                break
        return exe_type
    
    def _get_priority(self, case_dict: Dict[str, Any]) -> int:
        """获取主题优先级（等同于测试用例的重要性）"""
        markers = case_dict.get('markers')
        if isinstance(markers, list):
            for marker in markers:
                return int(marker.get('markerId', '0')[-1])
        return 0
    
    def _generate_testcase_preconditions(self, topics: List[Dict[str, Any]]) -> str:
        """生成测试用例前置条件"""
        notes = [topic.get('notes', '') for topic in topics]
        notes = self._filter_precondition(notes)
        return self.config['precondition_sep'].join(notes)
    
    def _generate_testcase_summary(self, topics: List[Dict[str, Any]]) -> str:
        """生成测试用例摘要"""
        comments = [topic.get('comment', '') for topic in topics]
        comments = self._filter_element(comments)
        return self.config['summary_sep'].join(comments)
    
    def _parse_test_steps_with_hierarchy(self, step_dict_list: List[Dict[str, Any]], 
                                        topics: List[Dict[str, Any]]) -> List[TestStep]:
        """解析测试步骤，考虑层级结构映射"""
        steps = []
        if len(topics) >= 4:
            action_text = topics[2]['title'] if len(topics) > 2 else ''
            expected_text = topics[3]['title'] if len(topics) > 3 else ''
            step = TestStep(
                step_number=1, actions=action_text, expected_results=expected_text,
                execution_type=1, result=0
            )
            steps.append(step)
        else:
            for step_num, step_dict in enumerate(step_dict_list, 1):
                test_step = self._parse_a_test_step(step_dict)
                test_step.step_number = step_num
                steps.append(test_step)
        return steps
    
    def _extract_steps_from_hierarchy(self, topics: List[Dict[str, Any]]) -> List[TestStep]:
        """从层级结构中提取测试步骤信息"""
        steps = []
        if len(topics) >= 4:
            action_text = topics[2]['title']
            expected_text = topics[3]['title']
            step = TestStep(
                step_number=1, actions=action_text, expected_results=expected_text,
                execution_type=1, result=0
            )
            steps.append(step)
        else:
            step = TestStep(
                step_number=1, actions=' ', expected_results=' ',
                execution_type=1, result=0
            )
            steps.append(step)
        return steps
    
    def _parse_a_test_step(self, step_dict: Dict[str, Any]) -> TestStep:
        """解析单个测试步骤"""
        test_step = TestStep()
        test_step.actions = step_dict['title']
        expected_topics = step_dict.get('topics', [])
        if expected_topics:
            expected_topic = expected_topics[0]
            test_step.expected_results = expected_topic['title']
            markers = expected_topic.get('markers', 0)
            test_step.result = self._get_test_result(markers)
        else:
            markers = step_dict.get('markers', 0)
            test_step.result = self._get_test_result(markers)

        return test_step
    
    def _get_test_result(self, markers: Any) -> int:
        """获取测试结果状态"""
        if isinstance(markers, list):
            if 'symbol-right' in markers or 'c_simbol-right' in markers:
                result = 1
            elif 'symbol-wrong' in markers or 'c_simbol-wrong' in markers:
                result = 2
            elif 'symbol-pause' in markers or 'c_simbol-pause' in markers:
                result = 3
            elif 'symbol-minus' in markers or 'c_simbol-minus' in markers:
                result = 4
            else:
                result = 0
        else:
            result = 0
        return result
