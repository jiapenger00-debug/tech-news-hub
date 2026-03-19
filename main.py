#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版主程序 - 用于测试
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from fetchers.chinese import ChineseNewsFetcher
from renderer import HTMLRenderer


def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_directories():
    """确保必要的目录存在"""
    dirs = ["output", "static/css", "static/js"]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


def main():
    """主函数"""
    print("="*60)
    print("AI Tech Frontier - 简化版新闻抓取")
    print("="*60)
    
    # 加载配置
    print("\n[1/3] 加载配置...")
    config = load_config()
    
    # 确保目录存在
    print("[2/3] 确保目录存在...")
    ensure_directories()
    
    # 只抓取一个中文源进行测试
    print("\n[3/3] 抓取新闻...")
    print("测试：只抓取机器之心一个源")
    
    # 临时修改配置，只保留一个源
    config['sources']['chinese'] = [config['sources']['chinese'][0]]
    config['sources']['english'] = []  # 禁用英文源
    config['fetch']['max_articles_per_source'] = 5
    
    try:
        fetcher = ChineseNewsFetcher(config)
        news = fetcher.fetch()
        print(f"\n成功抓取 {len(news)} 条新闻")
        
        # 生成简单网页
        print("\n生成网页...")
        
        # 复制静态文件
        import shutil
        if Path("static/css").exists():
            shutil.copytree("static/css", "output/css", dirs_exist_ok=True)
        if Path("static/js").exists():
            shutil.copytree("static/js", "output/js", dirs_exist_ok=True)
        
        # 生成简单 HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Tech Frontier</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <h1>AI科技前沿</h1>
        <p class="update-time">更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        <div class="news-list">
"""
        
        for item in news[:10]:
            html += f"""
            <div class="news-item">
                <h3><a href="{item.get('link', '#')}" target="_blank">{item.get('title', '无标题')}</a></h3>
                <p class="summary">{item.get('summary', '无摘要')[:200]}...</p>
                <span class="source">{item.get('source', '未知')}</span>
                <span class="date">{item.get('published', '')}</span>
            </div>
"""
        
        html += """
        </div>
    </div>
</body>
</html>
"""
        
        with open("output/index.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        print("\n✅ 完成！网页已生成到 output/index.html")
        return 0
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
