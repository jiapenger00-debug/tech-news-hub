#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版主程序 - 支持 AI 摘要
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from fetchers.chinese import ChineseNewsFetcher
from summarizer import NewsSummarizer


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
    print("AI Tech Frontier - 新闻抓取")
    print("="*60)
    
    # 加载配置
    print("\n[1/4] 加载配置...")
    config = load_config()
    
    # 检查 API Key
    api_key = os.environ.get("OPENCLAW_API_KEY", "")
    if api_key:
        print(f"   API Key: 已设置 ({api_key[:10]}...)")
    else:
        print("   API Key: 未设置")
    
    # 确保目录存在
    print("[2/4] 确保目录存在...")
    ensure_directories()
    
    # 抓取新闻
    print("\n[3/4] 抓取新闻...")
    all_news = []
    
    try:
        fetcher = ChineseNewsFetcher(config)
        all_news = fetcher.fetch()
        print(f"\n   成功抓取 {len(all_news)} 条新闻")
    except Exception as e:
        print(f"\n   抓取失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 生成 AI 摘要
    print("\n[4/4] 生成摘要...")
    if config['summarizer']['enabled'] and all_news:
        summarizer = NewsSummarizer(config)
        for i, news in enumerate(all_news):
            try:
                print(f"   生成摘要 {i+1}/{len(all_news)}: {news['title'][:30]}...")
                summary = summarizer.summarize(
                    news['title'], 
                    news.get('summary', ''),
                    news.get('language', 'zh')
                )
                news['ai_summary'] = summary
                print(f"      ✓ {summary[:50]}...")
            except Exception as e:
                print(f"      ✗ 摘要失败: {e}")
                news['ai_summary'] = news.get('summary', '')[:150]
    
    # 生成网页
    print("\n生成网页...")
    
    # 复制静态文件
    import shutil
    if Path("static/css").exists():
        shutil.copytree("static/css", "output/css", dirs_exist_ok=True)
    if Path("static/js").exists():
        shutil.copytree("static/js", "output/js", dirs_exist_ok=True)
    
    # 生成 HTML
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
    
    for item in all_news[:20]:  # 最多显示20条
        title = item.get('title', '无标题')
        link = item.get('url', '#')
        summary = item.get('ai_summary', item.get('summary', '无摘要'))
        source = item.get('source', '未知')
        
        html += f"""
            <div class="news-item">
                <h3><a href="{link}" target="_blank">{title}</a></h3>
                <p class="summary">{summary[:200]}...</p>
                <span class="source">{source}</span>
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
    
    print(f"\n✅ 完成！共处理 {len(all_news)} 条新闻")
    print("   网页已生成到 output/index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
