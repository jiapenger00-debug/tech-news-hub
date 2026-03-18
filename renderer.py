#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 渲染器
生成美观的新闻聚合网页
"""

import json
import shutil
import re
from datetime import datetime
from pathlib import Path
from jinja2 import Template


class HTMLRenderer:
    """HTML 渲染器"""
    
    def __init__(self, config):
        self.config = config
        self.template_path = Path(config["output"]["template"])
        self.output_dir = Path(config["output"]["output_dir"])
        self.static_dir = Path(config["output"]["static_dir"])
        self.ai_keywords = config.get("categories", {}).get("ai_keywords", [])
        self.ev_keywords = config.get("categories", {}).get("ev_keywords", [])
    
    def get_ai_subtype(self, title, summary=""):
        """获取AI子类型"""
        text = (title + " " + summary).lower()
        
        # VLM
        if any(k in text for k in ['vlm', 'vision-language model', '视觉语言模型']):
            return 'VLM'
        
        # VLA
        if any(k in text for k in ['vla', 'vision-language-action', '视觉语言动作']):
            return 'VLA'
        
        # 具身智能
        if any(k in text for k in ['embodied', '具身智能', '人形机器人', 'humanoid robot']):
            return '具身智能'
        
        # AI芯片
        if any(k in text for k in ['ai chip', 'ai芯片', 'gpu', 'npu', 'tpu', '神经网络处理器']):
            return 'AI芯片'
        
        # 多模态
        if any(k in text for k in ['multimodal', '多模态', '全模态', 'omni-modal']):
            return '多模态'
        
        # 大模型
        if any(k in text for k in ['llm', 'large language model', '大模型', 'gpt', 'claude', 'gemini']):
            return '大模型'
        
        # 自动驾驶
        if any(k in text for k in ['autonomous', '自动驾驶', 'fsd', '智能驾驶']):
            return '自动驾驶'
        
        return 'AI'
    
    def is_ev_focused(self, title, summary=""):
        """判断新闻是否属于新能源车领域"""
        text = (title + " " + summary).lower()
        keywords = [k.lower() for k in self.ev_keywords]
        return any(keyword in text for keyword in keywords)
    
    def get_ev_brand(self, title, summary=""):
        """获取新能源车品牌"""
        text = (title + " " + summary).lower()
        
        brands = {
            '比亚迪': ['byd', '比亚迪', '刀片电池', 'dm-i', '仰望', '腾势', '方程豹'],
            '特斯拉': ['tesla', '特斯拉', 'model 3', 'model y', 'model s', 'cybertruck'],
            '蔚来': ['nio', '蔚来', 'et7', 'es8', 'ec6'],
            '小鹏': ['xpeng', '小鹏', 'g6', 'g9', 'p7'],
            '理想': ['li auto', '理想', 'l7', 'l8', 'l9', 'mega']
        }
        
        for brand, keywords in brands.items():
            if any(k in text for k in keywords):
                return brand
        
        return None
    
    def is_byd_related(self, title, summary=""):
        """判断是否比亚迪相关"""
        text = (title + " " + summary).lower()
        byd_keywords = ['byd', '比亚迪', '刀片电池', 'dm-i', '仰望', '腾势', '方程豹']
        return any(keyword in text for keyword in byd_keywords)
    
    def translate_title(self, title):
        """翻译英文标题为中文（简化版本）"""
        # 常见术语翻译映射
        translations = {
            r'\bAI\b': 'AI',
            r'\bOpenAI\b': 'OpenAI',
            r'\bGPT\b': 'GPT',
            r'\bLLM\b': '大语言模型',
            r'\bautonomous\b': '自动驾驶',
            r'\bself-driving\b': '自动驾驶',
            r'\belectric vehicle\b': '电动车',
            r'\bEV\b': '电动车',
            r'\bTesla\b': '特斯拉',
            r'\bBYD\b': '比亚迪',
            r'\bNIO\b': '蔚来',
            r'\bannounces\b': '宣布',
            r'\blaunches\b': '发布',
            r'\breleases\b': '推出',
            r'\bunveils\b': ' unveiling',
            r'\bpartnership\b': '合作',
            r'\bacquires\b': '收购',
            r'\binvestment\b': '投资',
        }
        
        translated = title
        for eng, chn in translations.items():
            translated = re.sub(eng, chn, translated, flags=re.IGNORECASE)
        
        return translated
    
    def calculate_priority(self, news):
        """计算新闻热度优先级"""
        priority = news.get("priority", 5)  # 基础优先级
        title = news.get("title", "")
        summary = news.get("summary", "")
        text = (title + " " + summary).lower()
        
        # AI 相关新闻加分
        if self.is_ai_focused(title, summary):
            priority += 2
        
        # 新能源车相关加分
        if self.is_ev_focused(title, summary):
            priority += 1
        
        # 比亚迪相关加分
        if self.is_byd_related(title, summary):
            priority += 1
        
        # 热门关键词加分
        hot_keywords = ['gpt', 'openai', 'launch', 'new', 'first', 'breakthrough', 'billion', 'million']
        for kw in hot_keywords:
            if kw in text:
                priority += 0.5
        
        # 限制最大优先级为 10
        return min(int(priority), 10)
    
    def render(self, news_list):
        """渲染 HTML 页面"""
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制静态资源
        self._copy_static_files()
        
        # 加载模板
        template_content = self._get_default_template()
        if self.template_path.exists():
            with open(self.template_path, "r", encoding="utf-8") as f:
                template_content = f.read()
        
        template = Template(template_content)
        
        # 处理每条新闻
        for news in news_list:
            title = news.get("title", "")
            summary = news.get("summary", "")
            
            # 添加分类标签
            news["ai_subtype"] = self.get_ai_subtype(title, summary)
            news["is_ai_focused"] = news["ai_subtype"] is not None
            news["is_ev_focused"] = self.is_ev_focused(title, summary)
            news["ev_brand"] = self.get_ev_brand(title, summary)
            news["is_byd_related"] = self.is_byd_related(title, summary)
            
            # 计算热度优先级
            news["priority"] = self.calculate_priority(news)
            news["is_hot"] = news["priority"] >= 8
            
            # 翻译英文标题
            if news.get("language") == "en":
                news["translated_title"] = self.translate_title(title)
            
            # 确保有核心摘要
            if not news.get("core_summary"):
                news["core_summary"] = summary[:150] + "..." if len(summary) > 150 else summary
        
        # 准备数据
        context = {
            "site": self.config["site"],
            "news_list": news_list,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "news_count": len(news_list),
        }
        
        # 渲染 HTML
        html = template.render(**context)
        
        # 保存文件
        output_path = self.output_dir / "index.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        return str(output_path)
    
    def _copy_static_files(self):
        """复制静态资源到输出目录"""
        # 如果 static 目录存在，复制所有文件
        if self.static_dir.exists():
            # 复制 CSS
            css_src = self.static_dir / "css"
            css_dst = self.output_dir / "css"
            if css_src.exists():
                css_dst.mkdir(exist_ok=True)
                for f in css_src.glob("*"):
                    shutil.copy2(f, css_dst / f.name)
            
            # 复制 JS
            js_src = self.static_dir / "js"
            js_dst = self.output_dir / "js"
            if js_src.exists():
                js_dst.mkdir(exist_ok=True)
                for f in js_src.glob("*"):
                    shutil.copy2(f, js_dst / f.name)
        else:
            # 使用默认样式
            self._create_default_static_files()
    
    def _create_default_static_files(self):
        """创建默认静态文件"""
        # CSS
        css_dir = self.output_dir / "css"
        css_dir.mkdir(exist_ok=True)
        
        css_content = self._get_default_css()
        with open(css_dir / "style.css", "w", encoding="utf-8") as f:
            f.write(css_content)
        
        # JS
        js_dir = self.output_dir / "js"
        js_dir.mkdir(exist_ok=True)
        
        js_content = self._get_default_js()
        with open(js_dir / "app.js", "w", encoding="utf-8") as f:
            f.write(js_content)
    
    def _get_default_template(self):
        """获取默认 HTML 模板"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ site.title }}</title>
    <meta name="description" content="{{ site.description }}">
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <h1 class="logo">🤖 {{ site.title }}</h1>
            <p class="tagline">{{ site.description }}</p>
            <div class="meta">
                <span class="update-time">🕐 更新时间: {{ update_time }}</span>
                <span class="total-news">📰 共 {{ news_count }} 条新闻</span>
            </div>
        </div>
    </header>

    <nav class="nav">
        <div class="container">
            <div class="nav-left">
                <button class="nav-btn active" data-filter="all">全部</button>
                <button class="nav-btn" data-filter="zh">🇨🇳 中文</button>
                <button class="nav-btn" data-filter="en">🇺🇸 英文</button>
                <button class="nav-btn" data-filter="ai">🤖 AI</button>
                <button class="nav-btn" data-filter="ev">🚗 新能源</button>
            </div>
        </div>
    </nav>

    <main class="main">
        <div class="container">
            <div class="news-grid">
                {% for news in news_list %}
                <article class="news-card" 
                         data-lang="{{ news.language }}"
                         data-category="{% if news.is_ai_focused %}ai{% endif %}{% if news.is_ev_focused %} ev{% endif %}">
                    <div class="news-header">
                        <span class="news-source">{{ news.source }}</span>
                        <span class="news-lang">{% if news.language == 'zh' %}🇨🇳{% else %}🇺🇸{% endif %}</span>
                        {% if news.is_ai_focused %}
                        <span class="tag ai-tag">🤖 AI</span>
                        {% endif %}
                        {% if news.is_ev_focused %}
                        <span class="tag ev-tag">🚗 新能源</span>
                        {% endif %}
                        {% if news.is_byd_related %}
                        <span class="tag byd-tag">🔋 比亚迪</span>
                        {% endif %}
                    </div>
                    
                    <h2 class="news-title">
                        <a href="{{ news.url }}" target="_blank" rel="noopener">
                            {% if news.language == 'en' %}
                            🌐 {{ news.translated_title or news.title }}
                            {% else %}
                            {{ news.title }}
                            {% endif %}
                        </a>
                    </h2>
                    
                    <div class="core-content">
                        <div class="core-label">💡 核心要点</div>
                        <p class="news-summary">{{ news.core_summary or news.summary }}</p>
                    </div>
                    
                    {% if news.language == 'en' %}
                    <div class="original-link">
                        <span class="lang-indicator">🇺🇸 原文</span>
                        <a href="{{ news.url }}" target="_blank" class="read-more">查看英文原文 →</a>
                    </div>
                    {% endif %}
                    
                    <div class="news-footer">
                        <span class="news-time">{{ news.published[:10] if news.published else '今日' }}</span>
                        <a href="{{ news.url }}" target="_blank" class="read-more">阅读全文 →</a>
                    </div>
                </article>
                {% endfor %}
            </div>
        </div>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; {{ site.title }} - 自动生成于 {{ update_time }}</p>
            <p>🤖 AI | 🚗 新能源车 | 🔋 比亚迪 | 🦾 具身智能 | 👁️ VLA/VLM</p>
        </div>
    </footer>

    <script src="js/app.js"></script>
</body>
</html>'''
    
    def _get_default_css(self):
        """获取默认 CSS"""
        return '''/* 基础样式 */
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans SC", sans-serif; line-height: 1.6; color: #333; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); min-height: 100vh; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
.header { background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(10px); padding: 40px 0; text-align: center; box-shadow: 0 2px 20px rgba(0,0,0,0.1); }
.logo { font-size: 2.5rem; margin-bottom: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.tagline { color: #666; font-size: 1.1rem; margin-bottom: 20px; }
.meta { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; font-size: 0.9rem; color: #888; }
.nav { background: rgba(255, 255, 255, 0.95); padding: 15px 0; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.nav .container { display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 10px; }
.nav-left { display: flex; gap: 5px; flex-wrap: wrap; justify-content: center; }
.nav-btn { background: transparent; border: 2px solid #667eea; color: #667eea; padding: 8px 16px; border-radius: 25px; cursor: pointer; transition: all 0.3s; font-size: 0.85rem; font-weight: 500; }
.nav-btn:hover, .nav-btn.active { background: #667eea; color: white; }
.main { padding: 40px 0; }
.news-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 25px; }
.news-card { background: rgba(255, 255, 255, 0.98); border-radius: 16px; padding: 25px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); transition: transform 0.3s, box-shadow 0.3s; display: flex; flex-direction: column; border: 1px solid rgba(102, 126, 234, 0.1); }
.news-card:hover { transform: translateY(-5px); box-shadow: 0 12px 40px rgba(0,0,0,0.15); border-color: rgba(102, 126, 234, 0.3); }
.news-header { display: flex; justify-content: flex-start; align-items: center; margin-bottom: 15px; gap: 8px; flex-wrap: wrap; }
.news-source { font-size: 0.8rem; color: #667eea; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.news-lang { font-size: 1.1rem; }
.tag { font-size: 0.7rem; padding: 3px 10px; border-radius: 12px; font-weight: 600; }
.ai-tag { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.ev-tag { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; }
.byd-tag { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }
.news-title { font-size: 1.15rem; margin-bottom: 15px; line-height: 1.5; }
.news-title a { color: #333; text-decoration: none; transition: color 0.3s; }
.news-title a:hover { color: #667eea; }
.core-content { background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); border-radius: 12px; padding: 15px; margin-bottom: 15px; border-left: 4px solid #667eea; }
.core-label { font-size: 0.8rem; color: #667eea; font-weight: 600; margin-bottom: 8px; display: flex; align-items: center; gap: 5px; }
.news-summary { color: #444; font-size: 0.95rem; line-height: 1.7; margin: 0; }
.original-link { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; margin-bottom: 10px; border-bottom: 1px dashed #ddd; }
.lang-indicator { font-size: 0.8rem; color: #888; background: #f0f0f0; padding: 3px 10px; border-radius: 15px; }
.news-footer { display: flex; justify-content: space-between; align-items: center; padding-top: 15px; margin-top: auto; font-size: 0.85rem; }
.news-time { color: #999; }
.read-more { color: #667eea; text-decoration: none; font-weight: 600; transition: all 0.3s; }
.read-more:hover { color: #764ba2; transform: translateX(3px); }
.footer { background: rgba(0, 0, 0, 0.9); color: #fff; padding: 40px 0; text-align: center; margin-top: 40px; }
.footer p { margin: 8px 0; font-size: 0.9rem; color: #aaa; }
@media (max-width: 768px) { .logo { font-size: 1.8rem; } .news-grid { grid-template-columns: 1fr; } .meta { flex-direction: column; gap: 10px; } .nav-btn { padding: 6px 12px; font-size: 0.8rem; } .news-title { font-size: 1.05rem; } }
.hidden { display: none !important; }
'''
    
    def _get_default_js(self):
        """获取默认 JS"""
        return '''document.addEventListener('DOMContentLoaded', function() {
    const navBtns = document.querySelectorAll('.nav-btn');
    const newsCards = document.querySelectorAll('.news-card');
    
    navBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            navBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const filter = this.dataset.filter;
            
            newsCards.forEach(card => {
                let shouldShow = false;
                if (filter === 'all') shouldShow = true;
                else if (filter === 'zh' || filter === 'en') shouldShow = card.dataset.lang === filter;
                else if (filter === 'ai') shouldShow = card.dataset.category && card.dataset.category.includes('ai');
                else if (filter === 'ev') shouldShow = card.dataset.category && card.dataset.category.includes('ev');
                
                if (shouldShow) { card.classList.remove('hidden'); card.style.animation = 'fadeIn 0.5s'; }
                else { card.classList.add('hidden'); }
            });
        });
    });
});
const style = document.createElement('style');
style.textContent = `@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } } .news-card { animation: fadeIn 0.5s ease-out; } .news-card.hidden { display: none; }`;
document.head.appendChild(style);
'''
