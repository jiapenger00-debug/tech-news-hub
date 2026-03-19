#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务状态管理器 - 支持断点续传
"""

import json
import os
from datetime import datetime
from pathlib import Path


class TaskStateManager:
    """任务状态管理器"""
    
    STATE_FILE = "task_state.json"
    
    def __init__(self):
        self.state_file = Path(__file__).parent / self.STATE_FILE
        self.state = self.load_state()
    
    def load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return self._get_default_state()
    
    def save_state(self):
        """保存状态"""
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def _get_default_state(self):
        """获取默认状态"""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "last_run": None,
            "last_successful_run": None,
            "tasks": {
                "fetch_news": {
                    "status": "pending",  # pending, running, completed, failed
                    "progress": 0,
                    "total": 0,
                    "last_error": None
                },
                "summarize": {
                    "status": "pending",
                    "progress": 0,
                    "total": 0,
                    "last_error": None
                },
                "render": {
                    "status": "pending",
                    "progress": 0,
                    "total": 0,
                    "last_error": None
                },
                "deploy": {
                    "status": "pending",
                    "progress": 0,
                    "total": 0,
                    "last_error": None
                }
            },
            "fetched_news": [],
            "summarized_news": [],
            "config": {}
        }
    
    def update_task(self, task_name, status=None, progress=None, total=None, error=None):
        """更新任务状态"""
        if task_name in self.state["tasks"]:
            if status:
                self.state["tasks"][task_name]["status"] = status
            if progress is not None:
                self.state["tasks"][task_name]["progress"] = progress
            if total is not None:
                self.state["tasks"][task_name]["total"] = total
            if error:
                self.state["tasks"][task_name]["last_error"] = error
            self.save_state()
    
    def get_task_status(self, task_name):
        """获取任务状态"""
        return self.state["tasks"].get(task_name, {})
    
    def is_task_completed(self, task_name):
        """检查任务是否已完成"""
        task = self.get_task_status(task_name)
        return task.get("status") == "completed"
    
    def is_task_pending(self, task_name):
        """检查任务是否待执行"""
        task = self.get_task_status(task_name)
        return task.get("status") in ["pending", "failed"]
    
    def reset_task(self, task_name):
        """重置任务状态"""
        self.update_task(task_name, status="pending", progress=0, error=None)
    
    def reset_all(self):
        """重置所有任务"""
        for task_name in self.state["tasks"]:
            self.reset_task(task_name)
        self.state["fetched_news"] = []
        self.state["summarized_news"] = []
        self.save_state()
    
    def set_fetched_news(self, news_list):
        """保存抓取的新闻"""
        self.state["fetched_news"] = news_list
        self.save_state()
    
    def get_fetched_news(self):
        """获取已抓取的新闻"""
        return self.state.get("fetched_news", [])
    
    def set_summarized_news(self, news_list):
        """保存已总结的新闻"""
        self.state["summarized_news"] = news_list
        self.save_state()
    
    def get_summarized_news(self):
        """获取已总结的新闻"""
        return self.state.get("summarized_news", [])
    
    def mark_run_start(self):
        """标记运行开始"""
        self.state["last_run"] = datetime.now().isoformat()
        self.save_state()
    
    def mark_run_success(self):
        """标记运行成功"""
        self.state["last_successful_run"] = datetime.now().isoformat()
        self.save_state()
    
    def get_resume_point(self):
        """获取恢复点"""
        tasks = self.state["tasks"]
        
        # 按顺序检查任务状态
        if tasks["fetch_news"]["status"] != "completed":
            return "fetch_news"
        elif tasks["summarize"]["status"] != "completed":
            return "summarize"
        elif tasks["render"]["status"] != "completed":
            return "render"
        elif tasks["deploy"]["status"] != "completed":
            return "deploy"
        else:
            return "all_completed"
    
    def print_status(self):
        """打印当前状态"""
        print("\n" + "="*60)
        print("📊 任务状态概览")
        print("="*60)
        
        for task_name, task in self.state["tasks"].items():
            status = task["status"]
            progress = task["progress"]
            total = task["total"]
            
            # 状态图标
            icons = {
                "pending": "⏳",
                "running": "🔄",
                "completed": "✅",
                "failed": "❌"
            }
            icon = icons.get(status, "❓")
            
            # 进度条
            if total > 0:
                pct = int((progress / total) * 100)
                bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
                progress_str = f" [{bar}] {pct}% ({progress}/{total})"
            else:
                progress_str = ""
            
            print(f"{icon} {task_name:15} {status:12}{progress_str}")
        
        print("="*60)
        
        if self.state["last_run"]:
            print(f"🕐 上次运行: {self.state['last_run'][:19]}")
        if self.state["last_successful_run"]:
            print(f"✅ 上次成功: {self.state['last_successful_run'][:19]}")
        
        resume_point = self.get_resume_point()
        if resume_point != "all_completed":
            print(f"\n🔄 恢复点: 从 '{resume_point}' 继续执行")
        else:
            print(f"\n✨ 所有任务已完成！")
        
        print("="*60 + "\n")
