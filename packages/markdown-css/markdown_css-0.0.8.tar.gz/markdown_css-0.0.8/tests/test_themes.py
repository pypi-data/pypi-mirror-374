#!/usr/bin/env python3
# coding: utf-8

"""
主题样式测试脚本
用于测试 markdown-css 工具与不同主题样式的兼容性
"""

import os
import sys
import subprocess
import glob
from pathlib import Path

def run_test(input_file, style_file, output_dir, test_name):
    """运行单个测试"""
    print(f"🧪 测试: {test_name}")
    print(f"   输入文件: {input_file}")
    print(f"   样式文件: {style_file}")
    
    # 构建命令
    cmd = [
        sys.executable, 
        'markdown_css/bin/markdown-css',
        input_file,
        '--style=' + style_file,
        '--out=' + output_dir,
        '--name=' + test_name + '.html',
        '--codehighlight=yes'
    ]
    
    try:
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            output_file = os.path.join(output_dir, test_name + '.html')
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"   ✅ 成功生成: {output_file} ({file_size} bytes)")
                return True
            else:
                print(f"   ❌ 输出文件不存在: {output_file}")
                return False
        else:
            print(f"   ❌ 命令执行失败:")
            print(f"      错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ 执行异常: {e}")
        return False

def test_all_themes():
    """测试所有主题"""
    print("=" * 60)
    print("🎨 markdown-css 主题样式测试")
    print("=" * 60)
    
    # 确保测试目录存在
    test_output_dir = "output/test_output"
    os.makedirs(test_output_dir, exist_ok=True)
    
    # 获取输入文件
    input_file = "themes/markdown.html"
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        return False
    
    # 获取所有CSS主题文件
    css_files = glob.glob("themes/*.css")
    if not css_files:
        print("❌ 未找到CSS主题文件")
        return False
    
    print(f"📁 测试目录: {test_output_dir}")
    print(f"📄 输入文件: {input_file}")
    print(f"🎨 找到 {len(css_files)} 个主题文件")
    print()
    
    # 运行测试
    success_count = 0
    total_count = len(css_files)
    
    for css_file in sorted(css_files):
        # 提取主题名称
        theme_name = os.path.splitext(os.path.basename(css_file))[0]
        test_name = f"test_{theme_name}"
        
        success = run_test(input_file, css_file, test_output_dir, test_name)
        if success:
            success_count += 1
        
        print()
    
    # 输出测试结果
    print("=" * 60)
    print(f"📊 测试结果: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("🎉 所有主题测试通过！")
        return True
    else:
        print("⚠️  部分主题测试失败")
        return False

def test_specific_theme(theme_name):
    """测试特定主题"""
    print(f"🎨 测试特定主题: {theme_name}")
    
    input_file = "themes/markdown.html"
    style_file = f"themes/{theme_name}.css"
    test_output_dir = "output/test_output"
    
    if not os.path.exists(style_file):
        print(f"❌ 主题文件不存在: {style_file}")
        return False
    
    return run_test(input_file, style_file, test_output_dir, f"test_{theme_name}")

def list_themes():
    """列出所有可用主题"""
    css_files = glob.glob("themes/*.css")
    print("🎨 可用主题列表:")
    for css_file in sorted(css_files):
        theme_name = os.path.splitext(os.path.basename(css_file))[0]
        file_size = os.path.getsize(css_file)
        print(f"   {theme_name:15} ({file_size:6} bytes)")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_themes()
        elif command == "test":
            if len(sys.argv) > 2:
                theme_name = sys.argv[2]
                test_specific_theme(theme_name)
            else:
                print("用法: python3 test_themes.py test <theme_name>")
                print("例如: python3 test_themes.py test simple")
        else:
            print("未知命令。可用命令:")
            print("  list  - 列出所有主题")
            print("  test  - 测试所有主题")
            print("  test <theme_name> - 测试特定主题")
    else:
        # 默认测试所有主题
        test_all_themes()

if __name__ == "__main__":
    main() 