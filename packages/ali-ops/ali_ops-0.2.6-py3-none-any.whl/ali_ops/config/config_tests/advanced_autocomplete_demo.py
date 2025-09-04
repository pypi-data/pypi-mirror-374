#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级自动补全输入演示
使用 prompt_toolkit 实现更加优秀的用户输入自动补全功能
"""

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter, PathCompleter, NestedCompleter, Completion
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
import re


class SmartValidator(Validator):
    """智能验证器"""
    
    def __init__(self, validation_func=None, error_message="输入不符合要求"):
        self.validation_func = validation_func
        self.error_message = error_message
    
    def validate(self, document):
        text = document.text
        if self.validation_func and not self.validation_func(text):
            raise ValidationError(message=self.error_message)


def aliyun_region_autocomplete():
    """阿里云区域自动补全 - 支持模糊匹配"""
    print("=== 阿里云区域选择 (支持模糊匹配) ===")
    
    regions = {
        # 华东区域
        'cn-hangzhou': '华东1 (杭州)',
        'cn-shanghai': '华东2 (上海)', 
        'cn-nanjing': '华东5 (南京)',
        # 华北区域
        'cn-beijing': '华北2 (北京)',
        'cn-zhangjiakou': '华北3 (张家口)',
        'cn-huhehaote': '华北5 (呼和浩特)',
        # 华南区域
        'cn-shenzhen': '华南1 (深圳)',
        'cn-guangzhou': '华南2 (广州)',
        # 西南区域
        'cn-chengdu': '西南1 (成都)',
        # 海外区域
        'cn-hongkong': '香港',
        'ap-southeast-1': '新加坡',
        'ap-southeast-2': '澳大利亚 (悉尼)',
        'ap-southeast-3': '马来西亚 (吉隆坡)',
        'ap-northeast-1': '日本 (东京)',
        'us-east-1': '美国东部 (弗吉尼亚)',
        'us-west-1': '美国西部 (硅谷)',
        'eu-central-1': '德国 (法兰克福)',
        'eu-west-1': '英国 (伦敦)',
    }
    
    # 创建带描述的补全选项
    region_choices = [f"{code} - {desc}" for code, desc in regions.items()]
    
    # 使用模糊补全器
    completer = FuzzyCompleter(WordCompleter(region_choices, ignore_case=True))
    
    # 验证函数
    def validate_region(text):
        # 提取区域代码
        region_code = text.split(' - ')[0] if ' - ' in text else text
        return region_code in regions
    
    validator = SmartValidator(validate_region, "请选择有效的阿里云区域")
    
    try:
        result = prompt(
            "请选择阿里云区域 (支持模糊搜索): ",
            completer=completer,
            validator=validator,
            complete_style=CompleteStyle.MULTI_COLUMN,
            mouse_support=True,
        )
        
        # 提取区域代码
        region_code = result.split(' - ')[0] if ' - ' in result else result
        print(f"选择的区域: {region_code}")
        return region_code
        
    except KeyboardInterrupt:
        print("\n操作已取消")
        return None


def ecs_instance_type_autocomplete():
    """ECS 实例规格自动补全 - 分类显示"""
    print("\n=== ECS 实例规格选择 (分类补全) ===")
    
    # 嵌套补全器 - 按实例族分类
    instance_types = {
        'ecs.t5': {  # 突发性能实例
            'ecs.t5-lc1m1.small': '1核1GB - 突发性能',
            'ecs.t5-lc1m2.small': '1核2GB - 突发性能',
            'ecs.t5-lc1m4.large': '1核4GB - 突发性能',
        },
        'ecs.c5': {  # 计算型实例
            'ecs.c5.large': '2核4GB - 计算优化',
            'ecs.c5.xlarge': '4核8GB - 计算优化',
            'ecs.c5.2xlarge': '8核16GB - 计算优化',
            'ecs.c5.4xlarge': '16核32GB - 计算优化',
        },
        'ecs.g5': {  # 通用型实例
            'ecs.g5.large': '2核8GB - 通用型',
            'ecs.g5.xlarge': '4核16GB - 通用型',
            'ecs.g5.2xlarge': '8核32GB - 通用型',
            'ecs.g5.4xlarge': '16核64GB - 通用型',
        },
        'ecs.r5': {  # 内存型实例
            'ecs.r5.large': '2核16GB - 内存优化',
            'ecs.r5.xlarge': '4核32GB - 内存优化',
            'ecs.r5.2xlarge': '8核64GB - 内存优化',
            'ecs.r5.4xlarge': '16核128GB - 内存优化',
        }
    }
    
    # 创建嵌套补全器
    nested_completer = NestedCompleter.from_nested_dict(instance_types)
    
    try:
        result = prompt(
            "请选择ECS实例规格 (输入实例族如 ecs.c5 然后按Tab): ",
            completer=nested_completer,
            complete_style=CompleteStyle.MULTI_COLUMN,
        )
        
        print(f"选择的实例规格: {result}")
        return result
        
    except KeyboardInterrupt:
        print("\n操作已取消")
        return None


def file_path_autocomplete():
    """文件路径自动补全"""
    print("\n=== 文件路径选择 (路径补全) ===")
    
    completer = PathCompleter()
    
    try:
        result = prompt(
            "请输入文件路径: ",
            completer=completer,
            complete_style=CompleteStyle.READLINE_LIKE,
        )
        
        print(f"选择的路径: {result}")
        return result
        
    except KeyboardInterrupt:
        print("\n操作已取消")
        return None


def command_autocomplete():
    """命令行自动补全 - 多级命令"""
    print("\n=== 阿里云命令补全 (多级命令) ===")
    
    # 定义命令结构
    commands = {
        'ecs': {
            'create': {
                'instance': None,
                'image': None,
                'snapshot': None,
            },
            'list': {
                'instances': None,
                'images': None,
                'snapshots': None,
            },
            'delete': {
                'instance': None,
                'image': None,
                'snapshot': None,
            }
        },
        'vpc': {
            'create': {
                'vpc': None,
                'vswitch': None,
                'security-group': None,
            },
            'list': {
                'vpcs': None,
                'vswitches': None,
                'security-groups': None,
            }
        },
        'config': {
            'set': {
                'region': None,
                'access-key': None,
                'secret-key': None,
            },
            'get': {
                'region': None,
                'profile': None,
            }
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
        print(f"完整命令: {full_command}")
        return full_command
        
    except KeyboardInterrupt:
        print("\n操作已取消")
        return None


def smart_email_autocomplete():
    """智能邮箱自动补全"""
    print("\n=== 智能邮箱输入 (域名补全) ===")
    
    # 常见邮箱域名和完整邮箱示例
    email_suggestions = [
        'user@gmail.com', 'user@qq.com', 'user@163.com', 'user@126.com', 
        'user@sina.com', 'user@hotmail.com', 'user@outlook.com', 'user@yahoo.com',
        'user@aliyun.com', 'user@alibaba-inc.com'
    ]
    
    # 邮箱验证
    def validate_email(text):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, text) is not None
    
    validator = SmartValidator(validate_email, "请输入有效的邮箱地址")
    
    # 使用模糊补全器，支持部分匹配
    completer = FuzzyCompleter(WordCompleter(email_suggestions, ignore_case=True))
    
    try:
        result = prompt(
            "请输入邮箱地址 (输入用户名会自动提示域名): ",
            completer=completer,
            validator=validator,
            complete_style=CompleteStyle.MULTI_COLUMN,
        )
        
        print(f"输入的邮箱: {result}")
        return result
        
    except KeyboardInterrupt:
        print("\n操作已取消")
        return None


def styled_autocomplete():
    """带样式的自动补全"""
    print("\n=== 带样式的输入 (彩色补全) ===")
    
    # 定义样式
    style = Style.from_dict({
        'completion-menu.completion': 'bg:#008888 #ffffff',
        'completion-menu.completion.current': 'bg:#00aaaa #000000',
        'scrollbar.background': 'bg:#88aaaa',
        'scrollbar.button': 'bg:#222222',
    })
    
    # 服务类型选项
    services = [
        'ECS - 弹性计算服务',
        'RDS - 关系型数据库',
        'OSS - 对象存储服务', 
        'VPC - 专有网络',
        'SLB - 负载均衡',
        'CDN - 内容分发网络',
        'WAF - Web应用防火墙',
        'RAM - 访问控制',
    ]
    
    completer = FuzzyCompleter(WordCompleter(services, ignore_case=True))
    
    try:
        result = prompt(
            HTML('<ansigreen>请选择阿里云服务: </ansigreen>'),
            completer=completer,
            style=style,
            complete_style=CompleteStyle.MULTI_COLUMN,
        )
        
        service_code = result.split(' - ')[0] if ' - ' in result else result
        print(f"选择的服务: {service_code}")
        return service_code
        
    except KeyboardInterrupt:
        print("\n操作已取消")
        return None


def main():
    """主演示函数"""
    print("高级自动补全输入演示")
    print("=" * 50)
    
    # 1. 阿里云区域选择 - 模糊匹配
    aliyun_region_autocomplete()
    
    # 2. ECS实例规格选择 - 嵌套补全
    ecs_instance_type_autocomplete()
    
    # 3. 文件路径补全
    file_path_autocomplete()
    
    # 4. 命令行补全
    command_autocomplete()
    
    # 5. 智能邮箱补全
    smart_email_autocomplete()
    
    # 6. 带样式的补全
    styled_autocomplete()
    
    print("\n" + "=" * 50)
    print("所有自动补全演示完成！")


if __name__ == "__main__":
    main()