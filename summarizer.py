#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 新闻总结器 - 使用 Moonshot API 生成中文摘要
"""

import os
import re
import requests


class NewsSummarizer:
    """新闻总结器 - 使用 AI 生成中文摘要"""
    
    def __init__(self, config):
        self.config = config
        self.max_length = config["summarizer"]["max_summary_length"]
        self.use_ai = config["summarizer"].get("use_ai", False)
        self.api_key = os.environ.get("OPENCLAW_API_KEY", "")
        
    def summarize(self, title, content, language="zh"):
        """
        生成中文核心摘要
        """
        if not content:
            content = title
        
        # 清理内容
        content = self._clean_text(content)
        
        # 如果启用 AI 且有 API Key，使用 AI 生成摘要
        if self.use_ai and self.api_key:
            try:
                return self._ai_summarize(title, content)
            except Exception as e:
                print(f"   AI 摘要失败: {e}，使用本地摘要")
                return self._local_summary(title, content)
        else:
            return self._local_summary(title, content)
    
    def _ai_summarize(self, title, content):
        """使用 Moonshot API 生成摘要"""
        # 截取内容前 2000 字符
        truncated_content = content[:2000] if len(content) > 2000 else content
        
        prompt = f"""请为以下科技新闻生成一个简洁的中文核心摘要（不超过150字）：

标题: {title}

内容: {truncated_content}

要求：
1. 用中文总结核心要点
2. 突出技术亮点或重要意义
3. 不超过150字
4. 语言通顺自然

摘要："""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "moonshot-v1-8k",
            "messages": [
                {"role": "system", "content": "你是一个专业的科技新闻编辑，擅长提炼新闻核心要点。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 200
        }
        
        response = requests.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        summary = result["choices"][0]["message"]["content"].strip()
        
        # 限制长度
        if len(summary) > self.max_length:
            summary = summary[:self.max_length] + "..."
        
        return summary
    
    def _local_summary(self, title, content):
        """本地生成简单摘要（备用方案）"""
        # 提取内容前 150 字符作为摘要
        summary = content[:self.max_length] if len(content) > self.max_length else content
        return summary + "..." if len(content) > self.max_length else summary
    
    def _clean_text(self, text):
        """清理文本"""
        if not text:
            return ""
        # 移除 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
