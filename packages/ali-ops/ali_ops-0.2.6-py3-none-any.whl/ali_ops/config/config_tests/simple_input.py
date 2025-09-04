#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的 prompt_toolkit 输入提示示例
不使用复杂的 TUI 界面，只提供基础的输入功能
"""

from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import input_dialog, message_dialog, yes_no_dialog
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.completion import WordCompleter
import re


class SimpleValidator(Validator):
    """简单的输入验证器"""
    
    def __init__(self, pattern=None, message="输入格式不正确"):
        self.pattern = pattern
        self.message = message
    
    def validate(self, document):
        text = document.text
        if self.pattern and not re.match(self.pattern, text):
            raise ValidationError(message=self.message)


def simple_text_input(prompt_text="请输入: ", default=""):
    """简单文本输入"""
    try:
        result = prompt(prompt_text, default=default)
        return result
    except KeyboardInterrupt:
        return None


def password_input(prompt_text="请输入密码: "):
    """密码输入（隐藏显示）"""
    try:
        result = prompt(prompt_text, is_password=True)
        return result
    except KeyboardInterrupt:
        return None


def validated_input(prompt_text="请输入: ", pattern=None, error_msg="输入格式不正确"):
    """带验证的输入"""
    validator = SimpleValidator(pattern, error_msg) if pattern else None
    try:
        result = prompt(prompt_text, validator=validator)
        return result
    except KeyboardInterrupt:
        return None


def autocomplete_input(prompt_text="请选择: ", choices=None):
    """带自动补全的输入"""
    if choices is None:
        choices = []
    
    completer = WordCompleter(choices, ignore_case=True)
    try:
        result = prompt(prompt_text, completer=completer)
        return result
    except KeyboardInterrupt:
        return None


def email_input():
    """邮箱输入（带验证）"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return validated_input(
        "请输入邮箱地址: ",
        pattern=email_pattern,
        error_msg="请输入有效的邮箱地址"
    )


def phone_input():
    """手机号输入（带验证）"""
    phone_pattern = r'^1[3-9]\d{9}$'
    return validated_input(
        "请输入手机号: ",
        pattern=phone_pattern,
        error_msg="请输入有效的手机号码"
    )


def region_input():
    """阿里云区域选择（带自动补全）"""
    regions = [
        "cn-hangzhou", "cn-shanghai", "cn-beijing", "cn-shenzhen",
        "cn-guangzhou", "cn-chengdu", "cn-hongkong", "ap-southeast-1",
        "ap-southeast-2", "ap-southeast-3", "ap-northeast-1", "us-east-1",
        "us-west-1", "eu-central-1", "eu-west-1"
    ]
    
    return autocomplete_input(
        "请选择阿里云区域 (支持自动补全): ",
        choices=regions
    )


def instance_type_input():
    """ECS 实例规格选择（带自动补全）"""
    instance_types = [
        "ecs.t5-lc1m1.small", "ecs.t5-lc1m2.small", "ecs.t5-lc1m4.large",
        "ecs.c5.large", "ecs.c5.xlarge", "ecs.c5.2xlarge", "ecs.c5.4xlarge",
        "ecs.g5.large", "ecs.g5.xlarge", "ecs.g5.2xlarge", "ecs.g5.4xlarge",
        "ecs.r5.large", "ecs.r5.xlarge", "ecs.r5.2xlarge", "ecs.r5.4xlarge"
    ]
    
    return autocomplete_input(
        "请选择 ECS 实例规格 (支持自动补全): ",
        choices=instance_types
    )


def demo():
    """演示所有输入功能"""
    print("=== 简单 Prompt Toolkit 输入演示 ===\n")
    
    # 1. 基础文本输入
    print("1. 基础文本输入")
    name = simple_text_input("请输入您的姓名: ", "默认用户")
    print(f"输入的姓名: {name}\n")
    
    # 2. 密码输入
    print("2. 密码输入")
    password = password_input("请输入密码: ")
    print(f"密码长度: {len(password) if password else 0}\n")
    
    # 3. 邮箱输入（带验证）
    print("3. 邮箱输入（带验证）")
    email = email_input()
    print(f"输入的邮箱: {email}\n")
    
    # 4. 手机号输入（带验证）
    print("4. 手机号输入（带验证）")
    phone = phone_input()
    print(f"输入的手机号: {phone}\n")
    
    # 5. 区域选择（带自动补全）
    print("5. 阿里云区域选择（带自动补全）")
    region = region_input()
    print(f"选择的区域: {region}\n")
    
    # 6. 实例规格选择（带自动补全）
    print("6. ECS 实例规格选择（带自动补全）")
    instance_type = instance_type_input()
    print(f"选择的实例规格: {instance_type}\n")
    
    print("演示完成！")


if __name__ == "__main__":
    demo()