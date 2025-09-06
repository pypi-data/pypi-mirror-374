#!/usr/bin/env python3
# coding: utf-8

from __future__ import absolute_import, print_function

import os
from docopt import docopt
from pyquery import PyQuery
from markdown_css import parse_style

from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_all_lexers
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name


def special_process_wechat_ol_ul(html):
    while len(html("ul")) > 0:
        result = []
        for li in html("ul").eq(0).find("li"):
            result.append(li.text())
        html("ul").eq(0).replaceWith('<p style="margin: 0; padding: 0; line-height: 1.6;">' + '<br/>'.join(result) + '</p>')

    while len(html("ol")) > 0:
        result = []
        for li in html("ol").eq(0).find("li"):
            result.append(li.text())
        html("ol").eq(0).replaceWith('<p style="margin: 0; padding: 0; line-height: 1.6;">' + '<br/>'.join(result) + '</p>')


def main():
    helpdoc = """markdown-css command line.
    Usage:
    markdown-css (-h | --help)
    markdown-css <input> [--out=<out>] [--name=<name>] [--style=<style>] [--render=<render>] [--codehighlight=<codehighlight>]

    Options:
    -h,  --help        Show help document
    --out=<out> Html out path [default: 'public']
    --name=<name> Out file name [default: <input>]
    --style=<style> Markdown css file [default: 'style.css']
    --render=<render> Html render by wechat or not [default: 'wechat']
    --codehighlight=<codehighlight> Highlight code yes or no [default: 'no']
    """
    rgs = docopt(helpdoc)
    input_file = rgs.get('<input>')
    out = rgs.get('--out')
    style = rgs.get('--style')
    name = rgs.get('--name')
    render = rgs.get('--render')
    codehighlight = rgs.get('--codehighlight')
    if not out:
        out = 'public'
    if not style:
        style = 'style.css'
    if not name:
        name = input_file
    if not render:
        render = 'wechat'
    if not codehighlight:
        codehighlight = 'no'

    # Import the main function from the original script
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bin'))
    from markdown_css.bin.markdown_css import main as original_main
    original_main(input_file, out, style, name, render, codehighlight)


if __name__ == '__main__':
    main()
