#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科技新闻聚合器主程序
自动抓取中英文科技新闻，AI 总结，生成网页
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 设置 Windows 控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from fetchers.chinese import ChineseNewsFetcher
from fetchers.english import EnglishNewsFetcher
from summarizer import NewsSummarizer
from renderer import HTMLRenderer


def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_directories():
    """确保必要的目录存在"""
    dirs = ["output", "static/css", "static/js", "templates"]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


def fetch_all_news(config):
    """抓取所有新闻"""
    all_news = []
    
    print("🔄 开始抓取新闻...")
    
    # 抓取中文新闻
    print("📰 抓取中文新闻...")
    chinese_fetcher = ChineseNewsFetcher(config)
    chinese_news = chinese_fetcher.fetch()
    all_news.extend(chinese_news)
    print(f"   ✓ 获取 {len(chinese_news)} 条中文新闻")
    
    # 抓取英文新闻
    print("📰 抓取英文新闻...")
    english_fetcher = EnglishNewsFetcher(config)
    english_news = english_fetcher.fetch()
    all_news.extend(english_news)
    print(f"   ✓ 获取 {len(english_news)} 条英文新闻")
    
    # 按时间排序
    all_news.sort(key=lambda x: x.get("published", ""), reverse=True)
    
    return all_news


def summarize_news(news_list, config):
    """使用 AI 总结新闻"""
    if not config["summarizer"]["enabled"]:
        return news_list
    
    print("🤖 正在生成新闻摘要...")
    summarizer = NewsSummarizer(config)
    
    for i, news in enumerate(news_list):
        if not news.get("summary"):
            try:
                summary = summarizer.summarize(news["title"], news.get("content", ""))
                news["summary"] = summary
                print(f"   [{i+1}/{len(news_list)}] {news['title'][:50]}...")
            except Exception as e:
                print(f"   ⚠️  摘要生成失败: {e}")
                news["summary"] = news.get("content", "")[:200] + "..."
    
    return news_list


def generate_website(news_list, config):
    """生成网页"""
    print("🎨 生成网页...")
    renderer = HTMLRenderer(config)
    output_path = renderer.render(news_list)
    print(f"   ✓ 网页已生成: {output_path}")
    return output_path


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 科技新闻聚合器 - Tech News Aggregator")
    print("=" * 60)
    print()
    
    # 加载配置
    config = load_config()
    
    # 确保目录存在
    ensure_directories()
    
    # 抓取新闻
    news_list = fetch_all_news(config)
    
    if not news_list:
        print("❌ 未获取到任何新闻")
        return
    
    print(f"\n📊 总计获取 {len(news_list)} 条新闻")
    print()
    
    # 生成摘要
    news_list = summarize_news(news_list, config)
    print()
    
    # 生成网页
    output_path = generate_website(news_list, config)
    
    print()
    print("=" * 60)
    print("✅ 完成！")
    print(f"📄 网页文件: {output_path}")
    print(f"🌐 请在浏览器中打开查看")
    print("=" * 60)


if __name__ == "__main__":
    main()
