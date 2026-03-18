# 🤖 AI科技前沿 - AI Tech Frontier

> 专注VLM、VLA、具身智能、AI芯片、多模态大模型、新能源车等前沿科技资讯

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://jiapenger00-debug.github.io/tech-news-hub/)
[![Update](https://img.shields.io/badge/Update-Daily%2000:00-blue)](https://github.com/jiapenger00-debug/tech-news-hub/actions)
[![Language](https://img.shields.io/badge/Language-ZH%2FEN-orange)]()

---

## 🌐 在线访问

**网站地址**: https://jiapenger00-debug.github.io/tech-news-hub/

---

## 📋 项目简介

AI科技前沿是一个自动化科技新闻聚合平台，专注于以下领域：

- 👁️ **VLM (视觉语言模型)** - Vision-Language Model
- 🎬 **VLA (视觉语言动作)** - Vision-Language-Action
- 🦾 **具身智能** - Embodied AI、人形机器人
- 🔌 **AI芯片** - GPU、NPU、TPU、神经网络处理器
- 🌐 **多模态** - Multimodal、全模态
- 🧠 **大模型** - LLM、GPT、Claude、Gemini
- 🚗 **新能源车** - 比亚迪、特斯拉、蔚来、小鹏、理想

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🎯 **严格筛选** | 只保留AI强相关和新能源车强相关资讯 |
| 🔥 **热度排序** | AI芯片、具身智能等高优先级内容优先展示 |
| 🌐 **自动翻译** | 英文新闻一键翻译为中文 |
| 💡 **核心要点** | 每条新闻都有中文核心摘要 |
| 🏷️ **精准标签** | VLM/VLA/具身智能/AI芯片/多模态/新能源车品牌标签 |
| 📱 **响应式设计** | 完美适配手机、平板、电脑 |
| ⚡ **快速加载** | 静态页面，秒开体验 |

---

## 🗞️ 新闻来源

### AI领域
- **机器之心** - 专注AI领域的中文科技媒体
- **量子位** - 人工智能及前沿科技报道
- **AI科技评论** - AI技术深度报道
- **新智元** - AI产业资讯
- **TechCrunch AI** - 全球领先的科技媒体
- **MIT Technology Review** - 深度科技报道
- **OpenAI Blog** - OpenAI官方博客
- **NVIDIA Blog** - AI芯片技术
- **Google AI Blog** - Google AI研究

### 新能源车领域
- **高工智能汽车** - 专注智能驾驶
- **汽车之心** - 汽车科技媒体
- **Electrek** - 国际新能源车资讯
- **InsideEVs** - 电动车专业媒体

---

## 🔄 更新机制

### 自动更新
- **每天 00:00 (北京时间)** 自动抓取最新新闻
- **云端运行** - GitHub Actions自动执行，无需电脑开机
- **严格过滤** - 只保留与AI强相关和新能源车强相关的内容

### 更新流程
```
每天 00:00 (北京时间)
    ↓
GitHub Actions 自动运行
    ↓
抓取各RSS源最新新闻
    ↓
严格过滤（只保留AI/新能源车相关内容）
    ↓
生成中文核心摘要
    ↓
部署到 GitHub Pages
    ↓
网站自动更新
```

---

## 🛠️ 技术栈

- **后端**: Python 3.11+
  - `feedparser` - RSS解析
  - `requests` - HTTP请求
  - `beautifulsoup4` - HTML解析
  - `jinja2` - 模板引擎
  
- **前端**: 
  - HTML5 + CSS3
  - Vanilla JavaScript
  - Google Translate API

- **部署**: 
  - GitHub Pages (静态托管)
  - GitHub Actions (自动化)

---

## 📁 项目结构

```
tech-news-hub/
├── .github/
│   └── workflows/
│       └── update-news.yml    # 自动更新工作流
├── fetchers/                   # 新闻抓取器
│   ├── chinese.py             # 中文源抓取（严格过滤）
│   ├── english.py             # 英文源抓取（严格过滤）
│   └── base.py                # 基础类
├── templates/                  # HTML模板
│   └── index.html             # 主页模板
├── static/                     # 静态资源
│   ├── css/style.css          # 样式文件
│   └── js/app.js              # 交互脚本
├── output/                     # 生成的网页
├── config.json                # 配置文件（关键词、过滤规则）
├── main_resume.py             # 主程序
├── renderer.py                # HTML渲染器
├── requirements.txt           # 依赖列表
└── README.md                  # 本文件
```

---

## 🔍 过滤规则

### AI强相关关键词（必须匹配）
- VLM、VLA、具身智能、AI芯片、多模态
- 大模型、端到端、Transformer
- 自动驾驶、AGI

### 新能源车强相关关键词（必须匹配）
- 比亚迪、特斯拉、蔚来、小鹏、理想
- 电池、续航、充电、智能驾驶
- 800V、碳化硅、SiC

### 排除内容
- ❌ 手机、平板、手表等消费电子产品
- ❌ 游戏、视频流媒体
- ❌ 加密货币、区块链
- ❌ 时尚、服装

---

## 📝 添加自定义新闻源

在 `config.json` 中添加新的RSS源：

```json
{
  "name": "源名称",
  "url": "https://example.com/feed",
  "enabled": true,
  "type": "rss",
  "category": "AI",
  "priority": 8
}
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📜 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 🙏 致谢

- 感谢所有新闻源的优质内容
- 感谢开源社区的工具和框架

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/jiapenger00-debug">jiapenger00-debug</a>
</p>
