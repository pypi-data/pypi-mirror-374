#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .text_processor import remove_extra_spaces


def test_remove_extra_spaces():
    # 测试用例：验证各种空格移除功能
    test_text = "这 是  中文 测试  文本 ，  mixed  English  text  here ， 还 有   symbols :  ;  !  "
    expected_result = "这是中文测试文本，mixed English text here，还有 symbols:;!"
    result = remove_extra_spaces(test_text)

    print("原始文本:", test_text)
    print("处理结果:", result)
    print("预期结果:", expected_result)
    print("测试通过:", result == expected_result)
    
    return result == expected_result


if __name__ == "__main__":
    test_remove_extra_spaces()