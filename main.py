#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序 - 支持中英文新闻抓取和 AI 摘要
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from fetchers.chinese import ChineseNewsFetcher
from fetchers.english import EnglishNewsFetcher
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
    print("\n[1/5] 加载配置...")
    config = load_config()
    
    # 检查 API Key
    api_key = os.environ.get("OPENCLAW_API_KEY", "")
    if api_key:
        print(f"   API Key: 已设置 ({api_key[:10]}...)")
    else:
        print("   API Key: 未设置")
    
    # 确保目录存在
    print("[2/5] 确保目录存在...")
    ensure_directories()
    
    # 抓取中文新闻
    print("\n[3/5] 抓取中文新闻...")
    all_news = []
    
    try:
        chinese_fetcher = ChineseNewsFetcher(config)
        chinese_news = chinese_fetcher.fetch()
        print(f"   中文新闻: {len(chinese_news)} 条")
        all_news.extend(chinese_news)
    except Exception as e:
        print(f"   中文新闻抓取失败: {e}")
    
    # 抓取英文新闻
    print("\n[4/5] 抓取英文新闻...")
    
    try:
        english_fetcher = EnglishNewsFetcher(config)
        english_news = english_fetcher.fetch()
        print(f"   英文新闻: {len(english_news)} 条")
        all_news.extend(english_news)
    except Exception as e:
        print(f"   英文新闻抓取失败: {e}")
    
    print(f"\n   总计: {len(all_news)} 条新闻")
    
    # 生成 AI 摘要
    print("\n[5/5] 生成 AI 摘要...")
    if config['summarizer']['enabled'] and all_news:
        summarizer = NewsSummarizer(config)
        for i, news in enumerate(all_news):
            try:
                print(f"   {i+1}/{len(all_news)}: {news['title'][:40]}...")
                summary = summarizer.summarize(
                    news['title'], 
                    news.get('summary', ''),
                    news.get('language', 'zh')
                )
                news['ai_summary'] = summary
                print(f"      -> {summary[:60]}...")
            except Exception as e:
                print(f"      摘要失败: {e}")
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
    <title>AI Tech Frontier - AI科技前沿</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <h1>AI科技前沿</h1>
        <p class="update-time">更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} | 共 {len(all_news)} 条新闻</p>
        <div class="news-list">
"""
    
    for item in all_news[:30]:  # 最多显示30条
        title = item.get('title', '无标题')
        link = item.get('url', '#')
        summary = item.get('ai_summary', item.get('summary', '无摘要'))
        source = item.get('source', '未知')
        lang = item.get('language', 'zh')
        lang_label = "🇨🇳" if lang == 'zh' else "🇺🇸"
        
        html += f"""
            <div class="news-item">
                <h3>{lang_label} <a href="{link}" target="_blank">{title}</a></h3>
                <p class="summary">{summary}</p>
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
    
    print(f"\n完成！共处理 {len(all_news)} 条新闻")
    print("网页已生成到 output/index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
