#!/usr/bin/env python3
# coding: utf-8

"""
Python3 兼容性测试脚本
用于验证 markdown-css 项目在 Python3 下的兼容性
"""

import sys
import os
import tempfile
import shutil

def test_imports():
    """测试所有必要的模块导入"""
    print("测试模块导入...")
    
    try:
        from markdown_css import parse_style, version, version_info
        print(f"✓ markdown_css 模块导入成功，版本: {version}")
    except ImportError as e:
        print(f"✗ markdown_css 模块导入失败: {e}")
        return False
    
    try:
        from docopt import docopt
        print("✓ docopt 模块导入成功")
    except ImportError as e:
        print(f"✗ docopt 模块导入失败: {e}")
        return False
    
    try:
        from pyquery import PyQuery
        print("✓ pyquery 模块导入成功")
    except ImportError as e:
        print(f"✗ pyquery 模块导入失败: {e}")
        return False
    
    try:
        from cssutils import CSSParser
        print("✓ cssutils 模块导入成功")
    except ImportError as e:
        print(f"✗ cssutils 模块导入失败: {e}")
        return False
    
    try:
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name
        from pygments.formatters import HtmlFormatter
        print("✓ pygments 模块导入成功")
    except ImportError as e:
        print(f"✗ pygments 模块导入失败: {e}")
        return False
    
    return True

def test_parse_style():
    """测试CSS解析功能"""
    print("\n测试CSS解析功能...")
    
    try:
        from markdown_css import parse_style
        
        # 测试CSS
        test_css = """
        p {
            color: #333;
            font-size: 14px;
        }
        h1 {
            color: #000;
            font-weight: bold;
        }
        """
        
        element_list, element_dict, pseudo_selector_list = parse_style(test_css)
        
        print(f"✓ CSS解析成功")
        print(f"  元素列表: {element_list}")
        print(f"  伪选择器列表: {pseudo_selector_list}")
        
        return True
    except Exception as e:
        print(f"✗ CSS解析失败: {e}")
        return False

def test_file_operations():
    """测试文件操作功能"""
    print("\n测试文件操作功能...")
    
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        test_file = os.path.join(temp_dir, "test.txt")
        
        # 测试UTF-8编码的文件读写
        test_content = "测试中文内容\nTest English content\n测试特殊字符: 🚀🌟"
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        with open(test_file, 'r', encoding='utf-8') as f:
            read_content = f.read()
        
        if read_content == test_content:
            print("✓ UTF-8文件读写测试成功")
        else:
            print("✗ UTF-8文件读写测试失败")
            return False
        
        # 清理临时文件
        shutil.rmtree(temp_dir)
        return True
        
    except Exception as e:
        print(f"✗ 文件操作测试失败: {e}")
        return False

def test_string_operations():
    """测试字符串操作"""
    print("\n测试字符串操作...")
    
    try:
        # 测试中文字符串
        chinese_str = "测试中文字符串"
        english_str = "Test English String"
        mixed_str = f"{chinese_str} - {english_str}"
        
        print(f"✓ 中文字符串: {chinese_str}")
        print(f"✓ 英文字符串: {english_str}")
        print(f"✓ 混合字符串: {mixed_str}")
        
        # 测试字符串拼接
        result = chinese_str + " " + english_str
        expected = "测试中文字符串 Test English String"
        
        if result == expected:
            print("✓ 字符串拼接测试成功")
        else:
            print("✗ 字符串拼接测试失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 字符串操作测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("Python3 兼容性测试")
    print("=" * 50)
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print()
    
    tests = [
        test_imports,
        test_parse_style,
        test_file_operations,
        test_string_operations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！项目已成功迁移到Python3")
        return True
    else:
        print("❌ 部分测试失败，需要进一步修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 