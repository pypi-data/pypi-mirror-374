#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
终极自动补全演示
展示 prompt_toolkit 的各种高级自动补全功能
"""

from prompt_toolkit import prompt
from prompt_toolkit.completion import (
    WordCompleter, FuzzyCompleter, PathCompleter, 
    NestedCompleter, DynamicCompleter
)
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.history import InMemoryHistory
import re
import os


class AdvancedValidator(Validator):
    """高级验证器"""
    
    def __init__(self, validation_func, error_message="输入不符合要求"):
        self.validation_func = validation_func
        self.error_message = error_message
    
    def validate(self, document):
        if not self.validation_func(document.text):
            raise ValidationError(message=self.error_message)


def demo_1_basic_word_completion():
    """演示1: 基础单词补全"""
    print("\n" + "="*60)
    print("演示1: 基础单词补全 - 阿里云区域选择")
    print("提示: 输入前几个字母然后按Tab键")
    print("="*60)
    
    regions = [
        'cn-hangzhou',    # 华东1 (杭州)
        'cn-shanghai',    # 华东2 (上海)
        'cn-beijing',     # 华北2 (北京)
        'cn-shenzhen',    # 华南1 (深圳)
        'cn-guangzhou',   # 华南2 (广州)
        'cn-chengdu',     # 西南1 (成都)
        'cn-hongkong',    # 香港
        'ap-southeast-1', # 新加坡
        'us-east-1',      # 美国东部
        'eu-central-1',   # 德国法兰克福
    ]
    
    completer = WordCompleter(regions, ignore_case=True)
    
    try:
        result = prompt(
            "请选择阿里云区域: ",
            completer=completer,
            complete_style=CompleteStyle.READLINE_LIKE,
        )
        print(f"✅ 选择的区域: {result}")
        return result
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None


def demo_2_fuzzy_completion():
    """演示2: 模糊匹配补全"""
    print("\n" + "="*60)
    print("演示2: 模糊匹配补全 - ECS实例规格选择")
    print("提示: 输入部分字符，支持不连续匹配，如输入 'c5' 可匹配所有c5实例")
    print("="*60)
    
    instance_types = [
        'ecs.t5-lc1m1.small (1核1GB) - 突发性能型',
        'ecs.t5-lc1m2.small (1核2GB) - 突发性能型',
        'ecs.c5.large (2核4GB) - 计算优化型',
        'ecs.c5.xlarge (4核8GB) - 计算优化型',
        'ecs.c5.2xlarge (8核16GB) - 计算优化型',
        'ecs.g5.large (2核8GB) - 通用型',
        'ecs.g5.xlarge (4核16GB) - 通用型',
        'ecs.r5.large (2核16GB) - 内存优化型',
        'ecs.r5.xlarge (4核32GB) - 内存优化型',
    ]
    
    completer = FuzzyCompleter(WordCompleter(instance_types, ignore_case=True))
    
    try:
        result = prompt(
            "请选择ECS实例规格: ",
            completer=completer,
            complete_style=CompleteStyle.MULTI_COLUMN,
        )
        print(f"✅ 选择的实例规格: {result.split(' ')[0]}")
        return result
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None


def demo_3_nested_completion():
    """演示3: 嵌套补全"""
    print("\n" + "="*60)
    print("演示3: 嵌套补全 - 阿里云CLI命令")
    print("提示: 输入 'ecs' 然后按Tab，再输入子命令")
    print("="*60)
    
    # 定义嵌套命令结构
    commands = {
        'ecs': {
            'create': ['instance', 'image', 'snapshot', 'disk'],
            'list': ['instances', 'images', 'snapshots', 'disks'],
            'delete': ['instance', 'image', 'snapshot', 'disk'],
            'start': ['instance'],
            'stop': ['instance'],
            'reboot': ['instance'],
        },
        'vpc': {
            'create': ['vpc', 'vswitch', 'security-group', 'route-table'],
            'list': ['vpcs', 'vswitches', 'security-groups', 'route-tables'],
            'delete': ['vpc', 'vswitch', 'security-group', 'route-table'],
        },
        'rds': {
            'create': ['instance', 'database', 'account'],
            'list': ['instances', 'databases', 'accounts'],
            'delete': ['instance', 'database', 'account'],
        },
        'config': {
            'set': ['region', 'access-key', 'secret-key', 'profile'],
            'get': ['region', 'profile', 'all'],
            'list': ['profiles'],
        }
    }
    
    completer = NestedCompleter.from_nested_dict(commands)
    
    try:
        result = prompt(
            "ali ",  # 命令前缀
            completer=completer,
            complete_style=CompleteStyle.MULTI_COLUMN,
        )
        full_command = f"ali {result}"
        print(f"✅ 完整命令: {full_command}")
        return full_command
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None


def demo_4_path_completion():
    """演示4: 路径补全"""
    print("\n" + "="*60)
    print("演示4: 文件路径补全")
    print("提示: 输入路径，支持Tab补全文件和目录")
    print("="*60)
    
    completer = PathCompleter()
    
    try:
        result = prompt(
            "请输入配置文件路径: ",
            completer=completer,
            complete_style=CompleteStyle.READLINE_LIKE,
        )
        print(f"✅ 选择的路径: {result}")
        return result
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None


def demo_5_validation_with_completion():
    """演示5: 带验证的补全"""
    print("\n" + "="*60)
    print("演示5: 带验证的补全 - 邮箱输入")
    print("提示: 输入邮箱地址，会自动验证格式")
    print("="*60)
    
    # 常见邮箱域名
    email_domains = [
        'example@gmail.com',
        'example@qq.com', 
        'example@163.com',
        'example@126.com',
        'example@sina.com',
        'example@hotmail.com',
        'example@outlook.com',
        'example@aliyun.com',
    ]
    
    completer = FuzzyCompleter(WordCompleter(email_domains, ignore_case=True))
    
    # 邮箱验证函数
    def validate_email(text):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, text) is not None
    
    validator = AdvancedValidator(validate_email, "请输入有效的邮箱地址")
    
    try:
        result = prompt(
            "请输入邮箱地址: ",
            completer=completer,
            validator=validator,
        )
        print(f"✅ 输入的邮箱: {result}")
        return result
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None


def demo_6_styled_completion():
    """演示6: 带样式的补全"""
    print("\n" + "="*60)
    print("演示6: 带样式的补全 - 阿里云服务选择")
    print("提示: 彩色的补全菜单")
    print("="*60)
    
    # 定义样式
    style = Style.from_dict({
        'completion-menu.completion': 'bg:#008888 #ffffff',
        'completion-menu.completion.current': 'bg:#00aaaa #000000',
        'scrollbar.background': 'bg:#88aaaa',
        'scrollbar.button': 'bg:#222222',
        'prompt': 'ansigreen bold',
    })
    
    services = [
        'ECS - 弹性计算服务',
        'RDS - 关系型数据库服务',
        'OSS - 对象存储服务',
        'VPC - 专有网络',
        'SLB - 负载均衡',
        'CDN - 内容分发网络',
        'WAF - Web应用防火墙',
        'RAM - 访问控制',
        'ACK - 容器服务',
        'FC - 函数计算',
    ]
    
    completer = FuzzyCompleter(WordCompleter(services, ignore_case=True))
    
    try:
        result = prompt(
            HTML('<ansigreen><b>请选择阿里云服务: </b></ansigreen>'),
            completer=completer,
            style=style,
            complete_style=CompleteStyle.MULTI_COLUMN,
        )
        service_code = result.split(' - ')[0]
        print(f"✅ 选择的服务: {service_code}")
        return service_code
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None


def demo_7_history_completion():
    """演示7: 带历史记录的补全"""
    print("\n" + "="*60)
    print("演示7: 带历史记录的补全")
    print("提示: 使用上下箭头键浏览历史记录")
    print("="*60)
    
    # 创建历史记录
    history = InMemoryHistory()
    history.append_string("cn-hangzhou")
    history.append_string("cn-shanghai")
    history.append_string("cn-beijing")
    
    regions = ['cn-hangzhou', 'cn-shanghai', 'cn-beijing', 'cn-shenzhen']
    completer = WordCompleter(regions, ignore_case=True)
    
    try:
        result = prompt(
            "请选择区域 (支持历史记录): ",
            completer=completer,
            history=history,
        )
        print(f"✅ 选择的区域: {result}")
        return result
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None


def demo_8_dynamic_completion():
    """演示8: 动态补全"""
    print("\n" + "="*60)
    print("演示8: 动态补全 - 根据输入动态生成选项")
    print("提示: 输入数字会生成对应数量的实例规格")
    print("="*60)
    
    def get_dynamic_completer():
        """动态生成补全选项"""
        def get_completions(document, complete_event):
            # 这里可以根据当前输入动态生成补全选项
            text = document.text
            
            # 示例：根据输入的数字生成实例规格
            if text.isdigit():
                num = int(text)
                if 1 <= num <= 8:
                    return [f"ecs.c5.{num}xlarge - {num*4}核{num*8}GB"]
            
            # 默认选项
            return [
                'ecs.t5.small - 1核2GB',
                'ecs.c5.large - 2核4GB', 
                'ecs.g5.xlarge - 4核16GB',
                'ecs.r5.2xlarge - 8核64GB'
            ]
        
        return WordCompleter(get_completions(None, None), ignore_case=True)
    
    completer = DynamicCompleter(get_dynamic_completer)
    
    try:
        result = prompt(
            "请输入实例规格 (试试输入数字1-8): ",
            completer=completer,
        )
        print(f"✅ 选择的规格: {result}")
        return result
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None


def main():
    """主演示函数"""
    print("🚀 终极自动补全演示")
    print("展示 prompt_toolkit 的各种高级自动补全功能")
    print("按 Ctrl+C 可以跳过任何演示")
    
    demos = [
        demo_1_basic_word_completion,
        demo_2_fuzzy_completion,
        demo_3_nested_completion,
        demo_4_path_completion,
        demo_5_validation_with_completion,
        demo_6_styled_completion,
        demo_7_history_completion,
        demo_8_dynamic_completion,
    ]
    
    results = []
    
    for i, demo_func in enumerate(demos, 1):
        try:
            result = demo_func()
            results.append(result)
            
            if result is not None:
                input(f"\n按回车键继续下一个演示... ({i}/{len(demos)})")
            else:
                print("跳过当前演示")
        except KeyboardInterrupt:
            print(f"\n演示被中断，跳过剩余 {len(demos) - i} 个演示")
            break
    
    print("\n" + "="*60)
    print("🎉 演示完成！")
    print("="*60)
    
    # 显示结果摘要
    print("\n📊 演示结果摘要:")
    demo_names = [
        "基础单词补全",
        "模糊匹配补全", 
        "嵌套补全",
        "路径补全",
        "带验证的补全",
        "带样式的补全",
        "历史记录补全",
        "动态补全"
    ]
    
    for i, (name, result) in enumerate(zip(demo_names, results)):
        status = "✅ 完成" if result is not None else "❌ 跳过"
        print(f"{i+1}. {name}: {status}")


if __name__ == "__main__":
    main()