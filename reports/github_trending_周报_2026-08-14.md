# GitHub Trending 周报 · 2026-08-14

> 数据来源 [github.com/trending](https://github.com/trending) ｜ 抓取时间 2026-08-14T08:51:48.786632+08:00 ｜ 共 17 个上榜项目

## 概览
- 本期上榜：**17** 个
- 本期新增：🆕 **8** 个（对比上一期同类型报告）
- 本期退榜：**9** 个

---

## 项目列表

### 1. [prime-agent](https://github.com/PrimeIntellect-ai/prime-agent) · TypeScript 🆕
⭐ 15.5k（本周 +12,476）
**简介**：一个会自我改进的强化学习智能体（RLM），面向编码任务与长时自主运行，附带可在本地或云端跑的 coding-agent 与训练/验证框架。

### 2. [semantica](https://github.com/semantica-agi/semantica) · Python 🆕
⭐ 6.7k（本周 +4,073）
**简介**：把企业里散落的各种数据吃进来，自动抽出关键实体和关系，建成一张「上下文知识图谱」，让 AI 智能体基于图去做推理和决策，而且每一步结论都能顺着图追溯出处。定位是开源自托管版的 Palantir，主打金融、医疗这类必须讲清楚「为什么这么判断」的强监管场景。

### 3. [skills](https://github.com/google/skills) · Python
⭐ 18.1k（本周 +2,359）
**简介**：Google 官方维护的 Agent Skills 集合，提供面向 Google Cloud 等产品的智能体技能（如认证、上云脚手架），可用 npx skills add 安装。

### 4. [computer](https://github.com/cloudflare/computer) · TypeScript 🆕
⭐ 8.0k（本周 +3,599）
**简介**：Cloudflare 出的一个「给 AI 智能体配电脑」的运行环境：它在一个 Durable Object 里用 SQLite 存着一份虚拟文件系统作为唯一真相源，并提供三种执行后端——把状态挂成真实 Linux 沙箱容器的 FUSE 文件系统、在边缘 Worker 里跑纯 bash 命令、或在 Worker 里跑一段 JS 模块。等于给 Agent 一个既能存文件、又能真正执行代码和命令的「工作台」。

### 5. [TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory) · TypeScript
⭐ 21.2k（本周 +5,388）
**简介**：腾讯云出的给 AI Agent 用的「团队记忆库」，把聊天记录、文档和代码沉淀成可复用的记忆/技能，让多个 Agent 共享上下文。

### 6. [code-graph-rag](https://github.com/vitali87/code-graph-rag) · Python
⭐ 4.2k（本周 +1,628）
**简介**：面向单体大仓库（monorepo）的 RAG 工具，用知识图谱把多语言代码结构化，让你用自然语言查询、理解甚至改动整个代码库。

### 7. [loopx](https://github.com/huangruiteng/loopx) · Python 🆕
⭐ 4.6k（本周 +1,967）
**简介**：LoopX 是一个不绑定具体厂商的「长任务托管内核」：它把目标、待办、证据、配额、交接这些信息持久化下来，让 Codex、Claude Code、Cursor 这类编码智能体在它的管理下分小步干活，随时可复盘也可重启。说白了就是把会干活的 Agent 接成了一个可管理、可追责、能持续改进的数字员工。

### 8. [agent-skills](https://github.com/addyosmani/agent-skills) · JavaScript 🆕
⭐ 87.0k（本周 +4,562）
**简介**：Addy Osmani 整理的一套「给 AI 编码智能体用的工程能力包」，把资深工程师的需求定义、规划、构建、测试、评审、发布流程沉淀成可复用的 skill。

### 9. [drawdb](https://github.com/drawdb-io/drawdb) · JavaScript
⭐ 39.0k（本周 +693）
**简介**：网页版数据库表结构设计工具，拖拽画 ER 图并自动生成建表 SQL，免费、好上手。

### 10. [pdf-inspector](https://github.com/firecrawl/pdf-inspector) · Rust
⭐ 15.3k（本周 +3,251）
**简介**：用 Rust 写的 PDF 处理库，能智能识别一份 PDF 是扫描件还是纯文本，并提取带位置信息的文字，方便后续做 OCR 或检索时的路由决策。

### 11. [ladybird](https://github.com/LadybirdBrowser/ladybird) · C++ 🆕
⭐ 65.6k（本周 +775）
**简介**：从零手写的浏览器，渲染引擎、JS 引擎、WebAssembly、TLS 全都自己造，没有套 Chromium 或 Firefox 的壳。多进程架构，每个标签页、图片解码、网络请求都跑在独立沙箱进程里。目前还是 pre-alpha，日常上网别指望，主要给开发者折腾。

### 12. [DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix) · Go
⭐ 34.5k（本周 +2,419）
**简介**：一个跑在终端里的 AI 编程助手，基于 DeepSeek，主打长时间挂着也稳定（前缀缓存友好），帮你写代码。

### 13. [manim](https://github.com/3b1b/manim) · Python 🆕
⭐ 90.9k（本周 +1,530）
**简介**：3Blue1Brown 作者做的数学动画引擎（ManimGL 版）。用 Python 代码精确控制每一帧画面，专门用来做讲解数学概念的视频；后来社区另起了一个更稳定、好上手的 ManimCommunity 版本，两者是同源不同线。

### 14. [reverse-skill](https://github.com/zhaoxuya520/reverse-skill) · PowerShell
⭐ 24.9k（本周 +5,270）
**简介**：面向逆向工程与授权渗透测试的安全技能工具包，用 AI 路由自动挑选并临时拉起所需工具链，辅助安全研究。

### 15. [ChinaTextbook](https://github.com/TapXWorld/ChinaTextbook) · Roff 🆕
⭐ 79.3k（本周 +2,369）
**简介**：一个把全国小学、初中、高中到大学的 PDF 教材全部收集并开源的仓库，初衷是让免费教育资源不再被私人水印和倒卖垄断，方便普通人获取，也让海外华人的孩子能接着学国内课本。

### 16. [book-to-skill](https://github.com/virgiliojr94/book-to-skill) · Python
⭐ 21.2k（本周 +3,789）
**简介**：把任意技术书或文档文件夹转成一个可直接调用的 AI Agent 技能包，边工作边查、边学，支持 Claude Code 等终端。

### 17. [ComfyUI](https://github.com/Comfy-Org/ComfyUI) · Python
⭐ 127.4k（本周 +3,122）
**简介**：最流行的模块化扩散模型（Stable Diffusion 等）可视化引擎，用节点图搭工作流做图像 / 视频生成，提供 GUI、API 与后端。

---

## 退榜项目

- lyogavin/airllm
- microsoft/AI-For-Beginners
- usekaneo/kaneo
- unclebob/swarm-forge
- iv-org/invidious
- goauthentik/authentik
- livekit/agents
- embabel/embabel-agent
- donnemartin/system-design-primer
