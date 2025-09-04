#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re


def remove_extra_spaces(text: str) -> str:
    """
    移除混合字符串中多余的空格
    """
    # 移除中文字符（包括符号）之间的空格
    pattern1 = r"(?<=[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef])\s+(?=[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef])"
    
    # 移除中英文字符（包括符号）之间的空格
    pattern2 = r"(?<=[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef])\s+(?=[a-zA-Z])|(?<=[a-zA-Z])\s+(?=[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef])"
    
    # 移除中文字符与英文符号之间的空格（扩展支持更多符号）
    pattern3 = r"(?<=[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef])\s+(?=[\[\]\(\)\{\}\"\'\:\;\?\!\,\.\`\~])|(?<=[\[\]\(\)\{\}\"\'\:\;\?\!\,\.\`\~])\s+(?=[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef])"
    
    # 处理英文单词与标点之间的空格
    # 单词和后面的标点应该是紧挨着的（无空格）
    # 标点后面的单词之间应该有且仅有一个空格
    pattern4a = r"(\w)\s+([^\w\s])"     # 单词和标点之间（移除空格）
    pattern4b = r"([^\w\s])\s+(\w)"     # 标点和单词之间（保留一个空格）
    pattern4c = r"(\w)\s{2,}(\w)"       # 单词和单词之间多余的空格（替换为一个空格）
    
    # 处理英文符号之间的多余空格（确保符号之间只有一个空格）
    pattern5 = r"([^\w\s])\s{2,}([^\w\s])"
    # 移除英文标点之间的空格
    pattern7 = r"([^\w\s])\s+([^\w\s])"
    # 处理英文符号和中文之间的空格问题
    # pattern6 = r"([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef])([^\w\s])|([^\w\s])([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef])"
    
    # 按顺序处理各种空格
    # 先处理中英文之间的空格
    text = re.sub(pattern2, "", text)
    # 再处理中文之间的空格
    text = re.sub(pattern1, "", text)
    # 然后处理中文与英文符号之间的空格
    text = re.sub(pattern3, "", text)
    # 处理英文单词和标点之间的空格
    text = re.sub(pattern4a, r"\1\2", text)      # 单词和标点之间无空格
    text = re.sub(pattern4b, r"\1 \2", text)     # 标点和单词之间保留一个空格
    text = re.sub(pattern4c, r"\1 \2", text)     # 单词间多余空格替换为一个空格
    # 处理英文符号之间的多余空格
    text = re.sub(pattern5, r"\1\2", text)
    # 处理英文符号和中文之间的空格（确保有空格）
    text = re.sub(pattern7, r"\1\2", text)
    
    return text