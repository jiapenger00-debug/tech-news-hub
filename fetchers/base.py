#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础新闻抓取类
"""

from abc import ABC, abstractmethod
from datetime import datetime
import requests
from bs4 import BeautifulSoup


class BaseNewsFetcher(ABC):
    """新闻抓取基类"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config["fetch"]["user_agent"]
        })
    
    def fetch_url(self, url, timeout=None):
        """获取网页内容"""
        try:
            timeout = timeout or self.config["fetch"]["request_timeout"]
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"   ⚠️  获取失败 {url}: {e}")
            return None
    
    def parse_html(self, html):
        """解析 HTML"""
        return BeautifulSoup(html, "html.parser")
    
    @abstractmethod
    def fetch(self):
        """抓取新闻，子类必须实现"""
        pass
    
    def format_date(self, date_str):
        """格式化日期"""
        try:
            # 尝试多种日期格式
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%a, %d %b %Y %H:%M:%S %z"]:
                try:
                    return datetime.strptime(date_str, fmt).isoformat()
                except:
                    continue
            return date_str
        except:
            return datetime.now().isoformat()
