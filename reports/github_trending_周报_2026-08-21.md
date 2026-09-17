# GitHub Trending 周报 · 2026-08-21

> 数据来源 [github.com/trending](https://github.com/trending) ｜ 抓取时间 2026-08-21T10:57:06.580511+08:00 ｜ 共 18 个上榜项目

## 概览
- 本期上榜：**18** 个
- 本期新增：🆕 **17** 个（对比上一期同类型报告）
- 本期退榜：**16** 个

---

## 项目列表

### 1. [diagram-design](https://github.com/cathrynlavery/diagram-design) · HTML 🆕
⭐ 24.4k（本周 +11,325）
**简介**：一个给 Claude Code / Codex / Pi 用的「画图技能包」，内置 27 种编辑级质量的图表（架构图、流程图、金字塔图等），直接生成自包含的 HTML+SVG，不用 Figma、不堆通用圆角框；还能把 draw.io / Mermaid 的图按你选的格式和精细度重画成统一风格，并读你的网站自动配色。

### 2. [OpenViking](https://github.com/volcengine/OpenViking) · Python 🆕
⭐ 31.1k（本周 +2,444）
**简介**：火山引擎开源的 AI Agent 上下文数据库，把记忆、资料和技能统一存成 viking:// 协议下的虚拟文件系统，Agent 能像人翻文件夹那样用 ls / tree / find 自己找上下文，而不是对着黑盒向量库瞎查。写入时会把内容切成摘要、概览、细节三层，按任务需要加载到对应深度以省 token，每次检索还会留下完整的翻找路径，结果不对时能直接回溯是哪一步出的错。

### 3. [omarchy](https://github.com/basecamp/omarchy) · Shell 🆕
⭐ 27.1k（本周 +2,395）
**简介**：DHH（Ruby on Rails 和 Basecamp 创始人）出品的一套「好看、现代、有主见」的桌面 Linux 发行版/配置方案，把窗口管理、主题、快捷键、剪贴板历史、提醒、AI 助手、终端与 Neovim 等都按他的审美预先调好，并配了一整本图文手册。适合想「开箱即用、少折腾」地用上优雅 Linux 桌面的人。

### 4. [needle](https://github.com/cactus-compute/needle) · Python 🆕
⭐ 8.2k（本周 +3,409）
**简介**：一个极小的大模型（4500 万参数、整引擎 14MB），专为手机、手表、智能家居、机器人这类小设备做工具调用、设备操控和结构化抽取；单文件二进制、约 28MB 内存就能跑完整会话，还带置信度打分和工具自动检索。

### 5. [semantica](https://github.com/semantica-agi/semantica) · Python
⭐ 9.9k（本周 +3,674）
**简介**：把企业里散落的各种数据吃进来，自动抽出关键实体和关系，建成一张「上下文知识图谱」，让 AI 智能体基于图去做推理和决策，而且每一步结论都能顺着图追溯出处。定位是开源自托管版的 Palantir，主打金融、医疗这类必须讲清楚「为什么这么判断」的强监管场景。

### 6. [Switchyard](https://github.com/NVIDIA-NeMo/Switchyard) · Rust 🆕
⭐ 2.0k（本周 +932）
**简介**：NVIDIA 出的一个 Rust 写的 LLM 流量代理 / 库：在多家模型厂商之间做路由、在 OpenAI 和 Anthropic 的 API 格式之间互转、记录运行指标，还能自己写路由算法；典型用法是把 Claude Code / Codex 指到开源模型而不改代码。

### 7. [modular](https://github.com/modular/modular) · Mojo 🆕
⭐ 28.0k（本周 +744）
**简介**：Modular 公司开源的整套 AI 开发与部署平台，核心是 Mojo 编程语言（专为 AI 设计、向下兼容 Python 的新语言）和 MAX 推理框架（能跑大模型、还能当 OpenAI 兼容的服务端）。这个仓库把 Mojo 编译器、标准库、MAX 的加速内核和推理服务都放一起，想用一套工具打通模型训练和上线。

### 8. [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) · Python 🆕
⭐ 113.1k（本周 +9,712）
**简介**：一个一站式 AI 短视频生成工具：你只给个主题或关键词，它就自动写出视频脚本、找素材、配字幕和背景音乐，最后合成一条高清短视频，带 Web 界面和 API，适合批量做抖音/B站类短视频。

### 9. [public-apis](https://github.com/public-apis/public-apis) · Python 🆕
⭐ 467.3k（本周 +11,259）
**简介**：一份社区手工维护的免费公开 API 大清单，按天气、地图、金融、影视、开发工具等几十个分类罗列了数千个能直接调用的接口，每条都标了是否需要鉴权、是否支持 HTTPS 和跨域。写 demo、做练手项目或临时找数据源时，翻这个表比自己一个个搜要快得多。

### 10. [holehe](https://github.com/megadose/holehe) · Python 🆕
⭐ 13.8k（本周 +1,632）
**简介**：一个 OSINT 小工具：输入一个邮箱，就靠各家网站的「找回密码」接口去探测它在 Twitter、Instagram、Imgur 等 120 多个站点是否注册过账号，且不会惊动对方，常用来做账号关联调查或安全自查。

### 11. [OpenLogi](https://github.com/AprilNEA/OpenLogi) · Rust 🆕
⭐ 12.0k（本周 +2,674）
**简介**：一个用 Rust 写的、本地运行的罗技（Logitech）外设配置工具，相当于开源版的 Logitech Options+。能重映射鼠标按键、调 DPI、设置 SmartShift 滚轮，走 HID++ 协议直接跟设备通信，不强制登录账号、不上传任何遥测数据，主打隐私和离线可用。

### 12. [modly](https://github.com/lightningpixel/modly) · TypeScript 🆕
⭐ 7.0k（本周 +1,855）
**简介**：一个开源桌面 App，把一张普通照片用本地 GPU 上的开源 AI 模型直接生成 3D 网格模型，全程离线不上云，支持 Windows、Linux 和苹果芯片 macOS，还带扩展系统可接外部模型。

### 13. [macro](https://github.com/macro-inc/macro) · Rust 🆕
⭐ 3.9k（本周 +1,456）
**简介**：一个想把 Slack、Notion、HubSpot 全塞进一个界面里的「团队操作系统」：邮件、聊天、文档、任务、AI Agent、电话、CRM 全打通，所有内容用 @ 互相链接、可全局搜索，团队和 Agent 共享一套记忆，省得来回切工具。用 SolidJS + Rust 写的。

### 14. [unsloth](https://github.com/unslothai/unsloth) · Python 🆕
⭐ 74.1k（本周 +3,300）
**简介**：一个本地桌面 App，让你不用写代码就能在图形界面里直接跑和微调大语言模型、扩散模型（Qwen、DeepSeek、Gemma、FLUX 等都能上），主打把模型训练和推理做成普通人点开安装包就能用的工具。

### 15. [ai-memory](https://github.com/akitaonrails/ai-memory) · Rust 🆕
⭐ 3.7k（本周 +1,952）
**简介**：给 AI 编程智能体用的「长期记忆」：你在 Claude Code 干到一半切到 Codex，它能把架构、试过的坑、遗留问题都带过去，新 agent 接着干不用你重新解释一遍，支持 Linux/macOS/WSL。

### 16. [omlx](https://github.com/jundot/omlx) · Python 🆕
⭐ 20.1k（本周 +1,388）
**简介**：一个专为苹果芯片 Mac 优化的本地 LLM 推理服务，带连续批处理和分层 KV 缓存，能钉住常用模型常驻内存，从菜单栏里就能开关和管理，主打在 Mac 上把大模型跑得既顺手又可控。

### 17. [llmfit](https://github.com/AlexsJones/llmfit) · Rust 🆕
⭐ 33.3k（本周 +1,842）
**简介**：一个一行命令就能「量你机器算力」的工具：它扫描你的硬件和显存，告诉你几百种大模型里哪些能跑、跑多快，还能在本地实测吞吐并把真实数据回传社区，帮你少走弯路选模型。

### 18. [freebuff](https://github.com/CodebuffAI/freebuff) · TypeScript 🆕
⭐ 10.3k（本周 +1,133）
**简介**：一个完全免费的 AI 编程智能体工具箱，不用订阅、不用 API key，自带一批模型额度（用文字广告换）。提供桌面端、命令行、网页、云端（直接挂到你的 GitHub 仓库跑）和聊天五种形态，能自己找文件、改代码、跑检查，帮你在终端或浏览器里写程序。

---

## 退榜项目

- PrimeIntellect-ai/prime-agent
- google/skills
- cloudflare/computer
- TencentCloud/TencentDB-Agent-Memory
- vitali87/code-graph-rag
- huangruiteng/loopx
- addyosmani/agent-skills
- drawdb-io/drawdb
- firecrawl/pdf-inspector
- LadybirdBrowser/ladybird
- esengine/DeepSeek-Reasonix
- 3b1b/manim
- zhaoxuya520/reverse-skill
- TapXWorld/ChinaTextbook
- virgiliojr94/book-to-skill
- Comfy-Org/ComfyUI
