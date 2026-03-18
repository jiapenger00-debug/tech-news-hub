#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文新闻抓取器 - 严格过滤AI和新能源车相关内容
"""

import feedparser
from .base import BaseNewsFetcher


class ChineseNewsFetcher(BaseNewsFetcher):
    """中文科技新闻抓取器 - 严格过滤"""
    
    def __init__(self, config):
        super().__init__(config)
        self.ai_keywords = config.get("categories", {}).get("ai_keywords", [])
        self.ev_keywords = config.get("categories", {}).get("ev_keywords", [])
        self.excluded_keywords = config.get("filter", {}).get("excluded_keywords", [])
        self.strict_mode = config.get("filter", {}).get("strict_mode", True)
    
    def is_relevant(self, title, summary=""):
        """判断新闻是否与AI或新能源车强相关"""
        text = (title + " " + summary).lower()
        
        # 检查排除关键词
        for keyword in self.excluded_keywords:
            if keyword.lower() in text:
                return False
        
        # 检查AI关键词
        ai_match = any(kw.lower() in text for kw in self.ai_keywords)
        
        # 检查新能源车关键词
        ev_match = any(kw.lower() in text for kw in self.ev_keywords)
        
        # 严格模式：必须匹配AI或新能源车
        if self.strict_mode:
            return ai_match or ev_match
        
        return True
    
    def fetch(self):
        """抓取中文新闻"""
        news_list = []
        sources = self.config["sources"]["chinese"]
        max_articles = self.config["fetch"]["max_articles_per_source"]
        
        for source in sources:
            if not source.get("enabled", True):
                continue
            
            try:
                if source["type"] == "rss":
                    articles = self._fetch_rss(source, max_articles)
                    # 过滤相关新闻
                    articles = [a for a in articles if self.is_relevant(a.get("title", ""), a.get("summary", ""))]
                    news_list.extend(articles)
                else:
                    articles = self._fetch_web(source, max_articles)
                    articles = [a for a in articles if self.is_relevant(a.get("title", ""), a.get("summary", ""))]
                    news_list.extend(articles)
            except Exception as e:
                print(f"   ⚠️  {source['name']} 抓取失败: {e}")
        
        return news_list
    
    def _fetch_rss(self, source, max_articles):
        """从 RSS 抓取"""
        news_list = []
        
        # 尝试常见的 RSS 路径
        rss_urls = [
            f"{source['url']}/feed",
            f"{source['url']}/rss",
            f"{source['url']}/rss.xml",
            source['url']
        ]
        
        for rss_url in rss_urls:
            try:
                feed = feedparser.parse(rss_url)
                if feed.entries:
                    for entry in feed.entries[:max_articles]:
                        news_list.append({
                            "title": entry.get("title", ""),
                            "url": entry.get("link", ""),
                            "summary": entry.get("summary", entry.get("description", ""))[:300],
                            "published": self.format_date(entry.get("published", "")),
                            "source": source["name"],
                            "language": "zh",
                            "category": source.get("category", "科技"),
                            "priority": source.get("priority", 5)
                        })
                    break
            except:
                continue
        
        return news_list
    
    def _fetch_web(self, source, max_articles):
        """从网页抓取（备用方案）"""
        news_list = []
        html = self.fetch_url(source["url"])
        
        if not html:
            return news_list
        
        soup = self.parse_html(html)
        
        # 这里可以根据具体网站结构定制抓取规则
        articles = soup.find_all("article", limit=max_articles)
        
        for article in articles:
            try:
                title_elem = article.find(["h1", "h2", "h3"])
                link_elem = article.find("a")
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    summary = article.get_text(strip=True)[:300]
                    
                    # 严格过滤
                    if self.is_relevant(title, summary):
                        news_list.append({
                            "title": title,
                            "url": link_elem.get("href", ""),
                            "summary": summary,
                            "published": "",
                            "source": source["name"],
                            "language": "zh",
                            "category": source.get("category", "科技"),
                            "priority": source.get("priority", 5)
                        })
            except:
                continue
        
        return news_list
