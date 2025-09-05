# -*- coding: utf-8 -*-
import json
import re


def normalize_json_string(raw_string):
    """
    将包含转义字符的原始字符串转换为正常的JSON字符串

    Args:
        raw_string (str): 原始字符串，格式如 '{"file": "...", "content": "....."}'

    Returns:
        str: 正常的JSON字符串
    """
    try:
        # 方法1: 使用json.loads和json.dumps进行标准化
        # 先解析原始字符串，再重新序列化
        parsed_data = json.loads(raw_string)

        # 如果content字段存在，对其进行特殊处理
        if 'content' in parsed_data:
            # 确保content字段的内容被正确转义
            content = parsed_data['content']
            # 重新赋值以确保正确的JSON编码
            parsed_data['content'] = content

        # 返回标准化的JSON字符串
        return json.dumps(parsed_data, ensure_ascii=False, indent=None)

    except json.JSONDecodeError as e:
        # 如果直接解析失败，尝试手动修复常见的转义问题
        return fix_and_normalize_json(raw_string)


def fix_and_normalize_json(raw_string):
    """
    手动修复和标准化JSON字符串
    """
    try:
        # 处理常见的转义字符问题
        # 替换双反斜杠后跟n为单个反斜杠n（\\n -> \n）
        fixed_string = re.sub(r'\\\\n', r'\\n', raw_string)

        # 处理其他常见的转义字符
        # 但要注意不要过度处理

        # 尝试解析修复后的字符串
        parsed_data = json.loads(fixed_string)
        return json.dumps(parsed_data, ensure_ascii=False, indent=None)

    except json.JSONDecodeError:
        # 如果还是失败，尝试更激进的修复
        return aggressive_fix_json(raw_string)


def aggressive_fix_json(raw_string):
    """
    更激进的JSON修复方法
    """
    # 转义字符串中的特殊字符
    escaped_string = raw_string.encode('unicode_escape').decode('utf-8')

    # 尝试解析
    try:
        parsed_data = json.loads(raw_string)
        return json.dumps(parsed_data, ensure_ascii=False, indent=None)
    except json.JSONDecodeError:
        # 最后的尝试：手动构建JSON
        return manual_json_fix(raw_string)


def manual_json_fix(raw_string):
    """
    手动修复JSON字符串的最后手段
    """
    # 简单的模式匹配和修复
    # 这里可以根据具体需求进行定制

    # 尝试直接返回原始字符串（假设它已经是有效的）
    return raw_string


# 更简单直接的方法
def simple_normalize_json(raw_string):
    """
    简单直接的标准化方法
    """
    try:
        # 直接解析然后重新序列化
        data = json.loads(raw_string)
        return json.dumps(data, ensure_ascii=False)
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return None


# 处理特殊情况的完整方法
def robust_normalize_json(raw_string):
    """
    健壮的JSON字符串标准化方法
    """
    try:
        # 首先尝试直接解析
        data = json.loads(raw_string)
        return json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    except json.JSONDecodeError as e:
        print(f"原始字符串解析失败: {e}")
        print(f"原始字符串: {raw_string}")

        # 尝试一些常见的修复
        try:
            # 替换一些常见的问题字符
            fixed_string = raw_string.replace('\\n', '\n').replace('\\t', '\t')
            data = json.loads(fixed_string)
            return json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        except json.JSONDecodeError:
            print("修复后仍然无法解析")
            return None


# 示例使用
if __name__ == "__main__":
    with open('./err.json', 'r', encoding='utf-8') as f:
        raw_string = f.read()


    print(f"原始: {raw_string}")
    result = robust_normalize_json(raw_string)
    if result:
        print(f"结果: {result}")

        # 验证结果是否可以被正确解析
        try:
            json.loads(result)
            print("✓ 验证通过")
        except json.JSONDecodeError:
            print("✗ 验证失败")
    else:
        print("处理失败")
