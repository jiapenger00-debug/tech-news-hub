#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
断点续传版主程序
支持关机后从上次位置继续执行
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
from state_manager import TaskStateManager


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


def fetch_news_task(config, state_manager):
    """抓取新闻任务（支持断点续传）"""
    if state_manager.is_task_completed("fetch_news"):
        print("✅ 新闻抓取任务已完成，跳过")
        return state_manager.get_fetched_news()
    
    print("\n" + "="*60)
    print("📰 任务 1/4: 抓取新闻")
    print("="*60)
    
    state_manager.update_task("fetch_news", status="running")
    all_news = []
    
    try:
        # 抓取中文新闻
        print("\n🔄 抓取中文新闻...")
        chinese_fetcher = ChineseNewsFetcher(config)
        chinese_news = chinese_fetcher.fetch()
        all_news.extend(chinese_news)
        print(f"   ✓ 获取 {len(chinese_news)} 条中文新闻")
        state_manager.update_task("fetch_news", progress=len(chinese_news), total=40)
        
        # 抓取英文新闻
        print("\n🔄 抓取英文新闻...")
        english_fetcher = EnglishNewsFetcher(config)
        english_news = english_fetcher.fetch()
        all_news.extend(english_news)
        print(f"   ✓ 获取 {len(english_news)} 条英文新闻")
        
        # 按时间排序
        all_news.sort(key=lambda x: x.get("published", ""), reverse=True)
        
        # 保存状态
        state_manager.set_fetched_news(all_news)
        state_manager.update_task("fetch_news", status="completed", progress=len(all_news), total=len(all_news))
        
        print(f"\n✅ 新闻抓取完成！总计 {len(all_news)} 条")
        return all_news
        
    except Exception as e:
        state_manager.update_task("fetch_news", status="failed", error=str(e))
        print(f"\n❌ 新闻抓取失败: {e}")
        raise


def summarize_task(news_list, config, state_manager):
    """生成摘要任务（支持断点续传）"""
    if not config["summarizer"]["enabled"]:
        print("\n⚙️  摘要功能已禁用，跳过")
        return news_list
    
    if state_manager.is_task_completed("summarize"):
        print("✅ 摘要生成任务已完成，跳过")
        return state_manager.get_summarized_news()
    
    print("\n" + "="*60)
    print("🤖 任务 2/4: 生成新闻摘要")
    print("="*60)
    
    state_manager.update_task("summarize", status="running", total=len(news_list))
    
    try:
        summarizer = NewsSummarizer(config)
        
        for i, news in enumerate(news_list):
            if not news.get("summary"):
                try:
                    summary = summarizer.summarize(news["title"], news.get("content", ""))
                    news["summary"] = summary
                    print(f"   [{i+1}/{len(news_list)}] {news['title'][:40]}...")
                except Exception as e:
                    print(f"   ⚠️  [{i+1}/{len(news_list)}] 摘要失败: {e}")
                    news["summary"] = news.get("content", "")[:200] + "..."
            
            # 每5条保存一次进度
            if (i + 1) % 5 == 0:
                state_manager.set_summarized_news(news_list)
                state_manager.update_task("summarize", progress=i+1)
        
        # 保存最终状态
        state_manager.set_summarized_news(news_list)
        state_manager.update_task("summarize", status="completed", progress=len(news_list))
        
        print(f"\n✅ 摘要生成完成！")
        return news_list
        
    except Exception as e:
        state_manager.update_task("summarize", status="failed", error=str(e))
        print(f"\n❌ 摘要生成失败: {e}")
        raise


def render_task(news_list, config, state_manager):
    """渲染网页任务（支持断点续传）"""
    if state_manager.is_task_completed("render"):
        print("✅ 网页渲染任务已完成，跳过")
        output_path = Path(config["output"]["output_dir"]) / "index.html"
        return str(output_path)
    
    print("\n" + "="*60)
    print("🎨 任务 3/4: 生成网页")
    print("="*60)
    
    state_manager.update_task("render", status="running")
    
    try:
        renderer = HTMLRenderer(config)
        output_path = renderer.render(news_list)
        
        state_manager.update_task("render", status="completed", progress=100, total=100)
        
        print(f"   ✓ 网页已生成: {output_path}")
        return output_path
        
    except Exception as e:
        state_manager.update_task("render", status="failed", error=str(e))
        print(f"\n❌ 网页生成失败: {e}")
        raise


def deploy_task(config, state_manager):
    """部署任务（支持断点续传）"""
    if state_manager.is_task_completed("deploy"):
        print("✅ 部署任务已完成，跳过")
        return True
    
    print("\n" + "="*60)
    print("🚀 任务 4/4: 部署到互联网")
    print("="*60)
    
    state_manager.update_task("deploy", status="running")
    
    # 部署功能待实现
    print("\n💡 部署功能需要手动配置:")
    print("   1. GitHub Pages: 将 output/ 推送到 GitHub")
    print("   2. Vercel: 导入 GitHub 仓库自动部署")
    print("   3. Netlify: 拖拽 output/ 文件夹上传")
    
    state_manager.update_task("deploy", status="completed")
    
    print("\n✅ 部署指南已显示")
    return True


def main():
    """主函数 - 支持断点续传"""
    print("\n" + "="*60)
    print("🚀 科技新闻聚合器 - Tech News Aggregator")
    print("   支持断点续传版")
    print("="*60)
    
    # 初始化状态管理器
    state_manager = TaskStateManager()
    state_manager.print_status()
    
    # 检查是否需要重置
    resume_point = state_manager.get_resume_point()
    
    if resume_point == "all_completed":
        print("\n✨ 所有任务已完成！")
        print("\n💡 如需重新运行，请删除 task_state.json 文件")
        output_path = Path(__file__).parent / "output" / "index.html"
        print(f"\n📄 网页位置: {output_path}")
        print("   请在浏览器中打开查看")
        return
    else:
        print(f"\n🔄 从 '{resume_point}' 继续执行...")
    
    # 标记运行开始
    state_manager.mark_run_start()
    
    # 加载配置
    config = load_config()
    
    # 确保目录存在
    ensure_directories()
    
    try:
        # 任务 1: 抓取新闻
        news_list = fetch_news_task(config, state_manager)
        
        # 任务 2: 生成摘要
        news_list = summarize_task(news_list, config, state_manager)
        
        # 任务 3: 渲染网页
        output_path = render_task(news_list, config, state_manager)
        
        # 任务 4: 部署
        deploy_task(config, state_manager)
        
        # 标记成功
        state_manager.mark_run_success()
        
        print("\n" + "="*60)
        print("✅ 所有任务完成！")
        print(f"📄 网页文件: {output_path}")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ 任务执行失败")
        print(f"   错误: {e}")
        print("\n💡 提示: 下次运行时会自动从断点继续")
        print("="*60)
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        print("💡 下次运行时会自动从断点继续")
    except Exception as e:
        print(f"\n\n❌ 程序出错: {e}")
        print("\n💡 下次运行时会自动从断点继续")
