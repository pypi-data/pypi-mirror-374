#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整的自动补全演示
展示 prompt_toolkit 在阿里云CLI工具中的实际应用
"""

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter, PathCompleter
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.history import InMemoryHistory
import re
import json


class ConfigValidator(Validator):
    """配置验证器"""
    
    def __init__(self, validation_type="text"):
        self.validation_type = validation_type
    
    def validate(self, document):
        text = document.text.strip()
        
        if self.validation_type == "email":
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', text):
                raise ValidationError(message="请输入有效的邮箱地址")
        
        elif self.validation_type == "access_key":
            if len(text) < 16:
                raise ValidationError(message="Access Key 长度至少16位")
        
        elif self.validation_type == "region":
            valid_regions = [
                'cn-hangzhou', 'cn-shanghai', 'cn-beijing', 'cn-shenzhen',
                'cn-guangzhou', 'cn-chengdu', 'cn-hongkong', 'ap-southeast-1'
            ]
            if text not in valid_regions:
                raise ValidationError(message="请选择有效的阿里云区域")


def demo_region_selection():
    """演示：阿里云区域选择"""
    print("\n" + "="*60)
    print("🌏 阿里云区域选择演示")
    print("="*60)
    
    # 区域数据
    regions_data = {
        'cn-hangzhou': '华东1 (杭州)',
        'cn-shanghai': '华东2 (上海)',
        'cn-beijing': '华北2 (北京)',
        'cn-shenzhen': '华南1 (深圳)',
        'cn-guangzhou': '华南2 (广州)',
        'cn-chengdu': '西南1 (成都)',
        'cn-hongkong': '香港',
        'ap-southeast-1': '新加坡',
        'ap-southeast-2': '澳大利亚 (悉尼)',
        'us-east-1': '美国东部 (弗吉尼亚)',
        'eu-central-1': '德国 (法兰克福)',
    }
    
    # 创建带描述的选项
    region_options = [f"{code} - {desc}" for code, desc in regions_data.items()]
    
    # 模糊补全器
    completer = FuzzyCompleter(WordCompleter(region_options, ignore_case=True))
    
    print("可用区域:")
    for code, desc in regions_data.items():
        print(f"  • {code} - {desc}")
    
    print("\n💡 提示: 支持模糊搜索，如输入 'hang' 可匹配杭州")
    
    try:
        result = prompt(
            "请选择阿里云区域: ",
            completer=completer,
            complete_style=CompleteStyle.MULTI_COLUMN,
        )
        
        # 提取区域代码
        region_code = result.split(' - ')[0] if ' - ' in result else result
        print(f"✅ 选择的区域: {region_code}")
        return region_code
        
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None


def demo_instance_type_selection():
    """演示：ECS实例规格选择"""
    print("\n" + "="*60)
    print("💻 ECS实例规格选择演示")
    print("="*60)
    
    # 实例规格数据
    instance_types = {
        # 突发性能型
        'ecs.t5-lc1m1.small': '1核1GB - 突发性能型 - ¥0.06/小时',
        'ecs.t5-lc1m2.small': '1核2GB - 突发性能型 - ¥0.09/小时',
        'ecs.t5-lc1m4.large': '1核4GB - 突发性能型 - ¥0.15/小时',
        
        # 计算优化型
        'ecs.c5.large': '2核4GB - 计算优化型 - ¥0.31/小时',
        'ecs.c5.xlarge': '4核8GB - 计算优化型 - ¥0.62/小时',
        'ecs.c5.2xlarge': '8核16GB - 计算优化型 - ¥1.24/小时',
        
        # 通用型
        'ecs.g5.large': '2核8GB - 通用型 - ¥0.38/小时',
        'ecs.g5.xlarge': '4核16GB - 通用型 - ¥0.76/小时',
        'ecs.g5.2xlarge': '8核32GB - 通用型 - ¥1.52/小时',
        
        # 内存优化型
        'ecs.r5.large': '2核16GB - 内存优化型 - ¥0.52/小时',
        'ecs.r5.xlarge': '4核32GB - 内存优化型 - ¥1.04/小时',
        'ecs.r5.2xlarge': '8核64GB - 内存优化型 - ¥2.08/小时',
    }
    
    # 创建带描述的选项
    instance_options = [f"{code} - {desc}" for code, desc in instance_types.items()]
    
    # 模糊补全器
    completer = FuzzyCompleter(WordCompleter(instance_options, ignore_case=True))
    
    print("可用实例规格:")
    print("\n突发性能型 (适合轻量级应用):")
    for code, desc in list(instance_types.items())[:3]:
        print(f"  • {code} - {desc}")
    
    print("\n计算优化型 (适合CPU密集型应用):")
    for code, desc in list(instance_types.items())[3:6]:
        print(f"  • {code} - {desc}")
    
    print("\n通用型 (均衡的计算、内存和网络资源):")
    for code, desc in list(instance_types.items())[6:9]:
        print(f"  • {code} - {desc}")
    
    print("\n内存优化型 (适合内存密集型应用):")
    for code, desc in list(instance_types.items())[9:]:
        print(f"  • {code} - {desc}")
    
    print("\n💡 提示: 输入 'c5' 匹配计算型，'large' 匹配所有large规格")
    
    try:
        result = prompt(
            "请选择ECS实例规格: ",
            completer=completer,
            complete_style=CompleteStyle.MULTI_COLUMN,
        )
        
        # 提取实例代码
        instance_code = result.split(' - ')[0] if ' - ' in result else result
        print(f"✅ 选择的实例规格: {instance_code}")
        return instance_code
        
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None


def demo_config_setup():
    """演示：配置文件设置"""
    print("\n" + "="*60)
    print("⚙️ 阿里云配置设置演示")
    print("="*60)
    
    config = {}
    
    # 1. Access Key ID 输入
    print("\n1. 设置 Access Key ID")
    try:
        access_key = prompt(
            "请输入 Access Key ID: ",
            validator=ConfigValidator("access_key"),
        )
        config['access_key_id'] = access_key
        print(f"✅ Access Key ID: {access_key[:8]}...")
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None
    
    # 2. Access Key Secret 输入（隐藏）
    print("\n2. 设置 Access Key Secret")
    try:
        secret_key = prompt(
            "请输入 Access Key Secret: ",
            is_password=True,
        )
        config['access_key_secret'] = secret_key
        print("✅ Access Key Secret 已设置")
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None
    
    # 3. 区域选择（带验证）
    print("\n3. 设置默认区域")
    regions = ['cn-hangzhou', 'cn-shanghai', 'cn-beijing', 'cn-shenzhen']
    completer = WordCompleter(regions, ignore_case=True)
    
    try:
        region = prompt(
            "请选择默认区域: ",
            completer=completer,
            validator=ConfigValidator("region"),
        )
        config['region_id'] = region
        print(f"✅ 默认区域: {region}")
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None
    
    # 4. 配置文件路径选择
    print("\n4. 选择配置文件保存路径")
    try:
        config_path = prompt(
            "请输入配置文件路径 (默认: ~/.aliops/config.json): ",
            completer=PathCompleter(),
            default="~/.aliops/config.json",
        )
        print(f"✅ 配置文件路径: {config_path}")
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None
    
    # 显示完整配置
    print("\n" + "="*40)
    print("📋 配置摘要:")
    print("="*40)
    print(f"Access Key ID: {config['access_key_id'][:8]}...")
    print(f"Access Key Secret: {'*' * len(config['access_key_secret'])}")
    print(f"默认区域: {config['region_id']}")
    print(f"配置文件: {config_path}")
    
    return config


def demo_command_builder():
    """演示：命令构建器"""
    print("\n" + "="*60)
    print("🔧 阿里云命令构建器演示")
    print("="*60)
    
    # 服务选择
    services = [
        'ecs - 弹性计算服务',
        'vpc - 专有网络',
        'rds - 关系型数据库',
        'oss - 对象存储',
        'slb - 负载均衡',
        'cdn - 内容分发网络',
    ]
    
    print("1. 选择阿里云服务")
    completer = FuzzyCompleter(WordCompleter(services, ignore_case=True))
    
    try:
        service_result = prompt(
            "请选择服务: ",
            completer=completer,
            complete_style=CompleteStyle.MULTI_COLUMN,
        )
        service = service_result.split(' - ')[0]
        print(f"✅ 选择的服务: {service}")
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None
    
    # 操作选择
    operations = {
        'ecs': ['create', 'list', 'delete', 'start', 'stop', 'reboot'],
        'vpc': ['create', 'list', 'delete', 'modify'],
        'rds': ['create', 'list', 'delete', 'backup', 'restore'],
        'oss': ['create', 'list', 'delete', 'upload', 'download'],
        'slb': ['create', 'list', 'delete', 'modify'],
        'cdn': ['create', 'list', 'delete', 'refresh'],
    }
    
    print(f"\n2. 选择 {service} 操作")
    ops = operations.get(service, ['create', 'list', 'delete'])
    completer = WordCompleter(ops, ignore_case=True)
    
    try:
        operation = prompt(
            f"请选择 {service} 操作: ",
            completer=completer,
        )
        print(f"✅ 选择的操作: {operation}")
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None
    
    # 构建最终命令
    final_command = f"ali {service} {operation}"
    
    print("\n" + "="*40)
    print("🎯 生成的命令:")
    print("="*40)
    print(f"命令: {final_command}")
    print(f"描述: 对 {service_result.split(' - ')[1]} 执行 {operation} 操作")
    
    return final_command


def demo_styled_input():
    """演示：带样式的输入"""
    print("\n" + "="*60)
    print("🎨 带样式的输入演示")
    print("="*60)
    
    # 定义样式
    style = Style.from_dict({
        'completion-menu.completion': 'bg:#008888 #ffffff',
        'completion-menu.completion.current': 'bg:#00aaaa #000000',
        'scrollbar.background': 'bg:#88aaaa',
        'scrollbar.button': 'bg:#222222',
        'prompt': 'ansigreen bold',
        'input': 'ansiblue',
    })
    
    # 环境选择
    environments = [
        'development - 开发环境',
        'testing - 测试环境',
        'staging - 预发布环境',
        'production - 生产环境',
    ]
    
    completer = FuzzyCompleter(WordCompleter(environments, ignore_case=True))
    
    try:
        result = prompt(
            HTML('<ansigreen><b>请选择部署环境: </b></ansigreen>'),
            completer=completer,
            style=style,
            complete_style=CompleteStyle.MULTI_COLUMN,
        )
        
        env = result.split(' - ')[0]
        print(f"✅ 选择的环境: {env}")
        return env
        
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        return None


def demo_history_input():
    """演示：带历史记录的输入"""
    print("\n" + "="*60)
    print("📚 历史记录输入演示")
    print("="*60)
    
    # 创建历史记录
    history = InMemoryHistory()
    history.append_string("cn-hangzhou")
    history.append_string("cn-shanghai")
    history.append_string("cn-beijing")
    history.append_string("cn-shenzhen")
    
    regions = ['cn-hangzhou', 'cn-shanghai', 'cn-beijing', 'cn-shenzhen', 'cn-guangzhou']
    completer = WordCompleter(regions, ignore_case=True)
    
    print("💡 提示: 使用上下箭头键浏览历史记录")
    print("历史记录: cn-hangzhou, cn-shanghai, cn-beijing, cn-shenzhen")
    
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


def main():
    """主演示函数"""
    print("🚀 阿里云CLI工具 - 自动补全功能完整演示")
    print("展示在实际项目中如何使用 prompt_toolkit")
    print("=" * 80)
    
    demos = [
        ("🌏 区域选择", demo_region_selection),
        ("💻 实例规格选择", demo_instance_type_selection),
        ("⚙️ 配置设置", demo_config_setup),
        ("🔧 命令构建器", demo_command_builder),
        ("🎨 样式化输入", demo_styled_input),
        ("📚 历史记录", demo_history_input),
    ]
    
    results = {}
    
    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n{'='*20} 演示 {i}/{len(demos)}: {name} {'='*20}")
        
        try:
            result = demo_func()
            results[name] = result
            
            if result is not None:
                print(f"\n✅ 演示完成")
                if i < len(demos):
                    input("按回车键继续下一个演示...")
            else:
                print("❌ 演示被跳过")
                
        except KeyboardInterrupt:
            print(f"\n演示被中断，跳过剩余 {len(demos) - i} 个演示")
            break
        except Exception as e:
            print(f"❌ 演示出错: {e}")
            continue
    
    # 显示结果摘要
    print("\n" + "="*80)
    print("📊 演示结果摘要")
    print("="*80)
    
    for name, result in results.items():
        status = "✅ 完成" if result is not None else "❌ 跳过"
        print(f"{name}: {status}")
        if result and isinstance(result, str) and len(result) < 50:
            print(f"  └─ 结果: {result}")
    
    print("\n🎉 所有演示完成！")
    print("这些功能可以直接集成到 ali-ops 项目中，提供更好的用户体验。")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        import traceback
        traceback.print_exc()