#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试自动补全功能
"""

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from prompt_toolkit.shortcuts import CompleteStyle

def test_basic_autocomplete():
    """测试基础自动补全"""
    print("=== 基础自动补全测试 ===")
    
    regions = [
        'cn-hangzhou', 'cn-shanghai', 'cn-beijing', 'cn-shenzhen',
        'cn-guangzhou', 'cn-chengdu', 'cn-hongkong'
    ]
    
    completer = WordCompleter(regions, ignore_case=True)
    
    try:
        result = prompt(
            "请选择区域 (支持Tab补全): ",
            completer=completer,
        )
        print(f"选择的区域: {result}")
        return result
    except KeyboardInterrupt:
        print("\n操作已取消")
        return None

def test_fuzzy_autocomplete():
    """测试模糊自动补全"""
    print("\n=== 模糊自动补全测试 ===")
    
    instance_types = [
        'ecs.t5-lc1m1.small - 1核1GB突发性能',
        'ecs.c5.large - 2核4GB计算优化',
        'ecs.g5.xlarge - 4核16GB通用型',
        'ecs.r5.2xlarge - 8核64GB内存优化'
    ]
    
    completer = FuzzyCompleter(WordCompleter(instance_types, ignore_case=True))
    
    try:
        result = prompt(
            "请选择实例规格 (支持模糊搜索): ",
            completer=completer,
            complete_style=CompleteStyle.MULTI_COLUMN,
        )
        print(f"选择的实例: {result}")
        return result
    except KeyboardInterrupt:
        print("\n操作已取消")
        return None

if __name__ == "__main__":
    print("自动补全功能测试")
    print("=" * 30)
    
    # 测试基础补全
    test_basic_autocomplete()
    
    # 测试模糊补全
    test_fuzzy_autocomplete()
    
    print("\n测试完成！")