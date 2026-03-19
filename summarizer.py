#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 新闻总结器 - 强制输出通顺的中文核心摘要
"""

import re


class NewsSummarizer:
    """新闻总结器 - 所有输出强制为中文"""
    
    def __init__(self, config):
        self.config = config
        self.max_length = config["summarizer"]["max_summary_length"]
    
    def summarize(self, title, content, language="zh"):
        """
        生成中文核心摘要
        无论原文是什么语言，都返回通顺的中文摘要
        """
        if not content:
            content = title
        
        # 清理内容
        content = self._clean_text(content)
        
        # 强制生成中文摘要
        return self._force_chinese_summary(title, content, language)
    
    def _force_chinese_summary(self, title, content, language):
        """强制生成通顺的中文摘要"""
        
        # 完整的英文到中文翻译映射
        translations = {
            # 公司
            'OpenAI': 'OpenAI',
            'Google': '谷歌',
            'Microsoft': '微软',
            'Meta': 'Meta',
            'Apple': '苹果',
            'Amazon': '亚马逊',
            'NVIDIA': '英伟达',
            'Intel': '英特尔',
            'AMD': 'AMD',
            'Tesla': '特斯拉',
            'BYD': '比亚迪',
            'NIO': '蔚来',
            'XPeng': '小鹏',
            'Li Auto': '理想',
            'CATL': '宁德时代',
            'DeepMind': 'DeepMind',
            'Anthropic': 'Anthropic',
            
            # 技术/产品
            'GPT': 'GPT',
            'ChatGPT': 'ChatGPT',
            'Claude': 'Claude',
            'Gemini': 'Gemini',
            'Llama': 'Llama',
            'VLM': 'VLM视觉语言模型',
            'VLA': 'VLA视觉语言动作模型',
            'LLM': '大语言模型',
            'AGI': '通用人工智能',
            'AI': '人工智能',
            'GPU': 'GPU',
            'NPU': 'NPU',
            'TPU': 'TPU',
            'FSD': 'FSD完全自动驾驶',
            'EV': '电动车',
            
            # 动作
            'announced': '宣布',
            'announces': '宣布',
            'launch': '发布',
            'launches': '发布',
            'launched': '发布了',
            'release': '推出',
            'releases': '推出',
            'released': '推出了',
            'unveil': ' unveiled',
            'unveils': ' unveiled',
            'unveiled': ' unveiled',
            'introduce': '推出',
            'introduces': '推出',
            'introduced': '推出了',
            'partner': '合作',
            'partners': '与...合作',
            'partnership': '建立合作',
            'acquire': '收购',
            'acquires': '收购',
            'acquired': '收购了',
            'raise': '融资',
            'raises': '融资',
            'raised': '融资',
            'fund': '融资',
            'funding': '融资',
            'invest': '投资',
            'invests': '投资',
            'invested': '投资',
            'investment': '投资',
            'expand': '扩展',
            'expands': '扩展',
            'expanded': '扩展了',
            
            # 形容词
            'new': '新',
            'first': '首个',
            'latest': '最新',
            'autonomous': '自动驾驶',
            'self-driving': '自动驾驶',
            'electric': '电动',
            'solid-state': '固态',
            'multimodal': '多模态',
            'embodied': '具身智能',
            'humanoid': '人形',
            
            # 名词
            'robot': '机器人',
            'robots': '机器人',
            'vehicle': '汽车',
            'vehicles': '汽车',
            'car': '汽车',
            'cars': '汽车',
            'battery': '电池',
            'batteries': '电池',
            'chip': '芯片',
            'chips': '芯片',
            'model': '模型',
            'models': '模型',
            'system': '系统',
            'systems': '系统',
            'technology': '技术',
            'technologies': '技术',
            'platform': '平台',
            'platforms': '平台',
            
            # 单位/数字
            'billion': '十亿美元',
            'million': '百万美元',
            'percent': '%',
            'km': '公里',
            'miles': '英里',
        }
        
        text = title + ". " + content
        
        # 步骤1: 翻译所有英文关键词
        translated = text
        for eng, chn in sorted(translations.items(), key=lambda x: -len(x[0])):
            translated = re.sub(r'\b' + re.escape(eng) + r'\b', chn, translated, flags=re.IGNORECASE)
        
        # 步骤2: 提取关键句子（前2句）
        sentences = re.split(r'[.!?。！？]', translated)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if not sentences:
            return self._create_simple_summary(title, translations)
        
        # 步骤3: 组合成通顺的中文摘要
        key_sentences = sentences[:2]
        summary = "；".join(key_sentences)
        
        # 步骤4: 清理和优化
        # 移除多余空格
        summary = re.sub(r'\s+', ' ', summary)
        # 移除英文单词（保留已翻译的）
        summary = re.sub(r'\b[a-zA-Z]{2,}\b', '', summary)
        # 清理多余空格
        summary = re.sub(r'\s+', ' ', summary).strip()
        
        # 步骤5: 确保长度合适
        if len(summary) > 120:
            summary = summary[:120] + "..."
        
        # 步骤6: 确保以句号结尾
        if not summary.endswith('。') and not summary.endswith('...'):
            summary += '。'
        
        # 如果摘要太短，使用备用方案
        if len(summary) < 30:
            return self._create_simple_summary(title, translations)
        
        return summary
    
    def _create_simple_summary(self, title, translations):
        """创建简单的中文摘要"""
        # 翻译标题
        translated_title = title
        for eng, chn in sorted(translations.items(), key=lambda x: -len(x[0])):
            translated_title = re.sub(r'\b' + re.escape(eng) + r'\b', chn, translated_title, flags=re.IGNORECASE)
        
        # 移除剩余英文
        translated_title = re.sub(r'\b[a-zA-Z]{2,}\b', '', translated_title)
        translated_title = re.sub(r'\s+', ' ', translated_title).strip()
        
        # 添加通用后缀
        if translated_title:
            return f"{translated_title}。关注该领域的最新进展。"
        
        return "该新闻涉及人工智能或新能源车领域的最新动态。"
    
    def _clean_text(self, text):
        """清理文本"""
        if not text:
            return ""
        # 移除 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符
        text = re.sub(r'[\n\r\t]', ' ', text)
        return text.strip()
    
    def get_core_insights(self, title, content, language="zh"):
        """获取核心洞察 - 强制中文"""
        summary = self.summarize(title, content, language)
        
        # 识别分类标签
        text = (title + " " + content).lower()
        
        ai_keywords = self.config.get("categories", {}).get("ai_keywords", [])
        ev_keywords = self.config.get("categories", {}).get("ev_keywords", [])
        
        tags = []
        for keyword in ai_keywords:
            if keyword.lower() in text:
                tags.append("AI")
                break
        
        for keyword in ev_keywords:
            if keyword.lower() in text:
                tags.append("新能源车")
                break
        
        is_byd = any(k in text for k in ['byd', '比亚迪', '刀片电池', 'dm-i'])
        if is_byd:
            tags.append("比亚迪")
        
        return {
            "summary": summary,  # 强制中文
            "tags": tags,
            "is_ai_related": "AI" in tags,
            "is_ev_related": "新能源车" in tags,
            "is_byd_related": is_byd
        }
