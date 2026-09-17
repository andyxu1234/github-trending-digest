# GitHub Trending 日报 · 2026-08-16

> 数据来源 [github.com/trending](https://github.com/trending) ｜ 抓取时间 2026-08-16T09:29:21.131793+08:00 ｜ 共 13 个上榜项目

## 概览
- 本期上榜：**13** 个
- 本期新增：🆕 **5** 个（对比上一期同类型报告）
- 本期退榜：**9** 个

---

## 项目列表

### 1. [cordis](https://github.com/cordiverse/cordis) · TypeScript 🆕
⭐ 4.1k（今日 +599）
**简介**：一个 TypeScript 插件框架，把程序拆成「上下文 + 服务 + 插件」三层：每个插件占住上下文里的一个名字（比如 ctx.llm、ctx.tools），别的插件靠这个名字找它、靠声明依赖自动排出启动顺序，不用手写初始化流程。最大特点是可逆——注册的监听器、工具、适配器在卸载或热重载时会自动撤销，所以插件能在运行时随意插拔；DeepSeek 官方的 deepseek-harness 就是拿它当底座。

### 2. [diagram-design](https://github.com/cathrynlavery/diagram-design) · HTML
⭐ 18.6k（今日 +1,607）
**简介**：一个给 Claude Code / Codex / Pi 用的「画图技能包」，内置 27 种编辑级质量的图表（架构图、流程图、金字塔图等），直接生成自包含的 HTML+SVG，不用 Figma、不堆通用圆角框；还能把 draw.io / Mermaid 的图按你选的格式和精细度重画成统一风格，并读你的网站自动配色。

### 3. [plugins](https://github.com/cursor/plugins) · TypeScript
⭐ 3.0k（今日 +149）
**简介**：Cursor 官方的插件规范与一批官方插件仓库：每个插件都是根目录下的独立文件夹、带自己的 plugin.json 清单。涵盖团队工作流、深度代码/安全审查、PR 与文档可视化、CI 与本地自动化等开发工具相关的智能体能力。

### 4. [needle](https://github.com/cactus-compute/needle) · Python
⭐ 6.1k（今日 +547）
**简介**：一个极小的大模型（4500 万参数、整引擎 14MB），专为手机、手表、智能家居、机器人这类小设备做工具调用、设备操控和结构化抽取；单文件二进制、约 28MB 内存就能跑完整会话，还带置信度打分和工具自动检索。

### 5. [unsloth](https://github.com/unslothai/unsloth) · Python
⭐ 72.1k（今日 +434）
**简介**：一个本地桌面 App，让你不用写代码就能在图形界面里直接跑和微调大语言模型、扩散模型（Qwen、DeepSeek、Gemma、FLUX 等都能上），主打把模型训练和推理做成普通人点开安装包就能用的工具。

### 6. [public-apis](https://github.com/public-apis/public-apis) · Python 🆕
⭐ 460.2k（今日 +2,260）
**简介**：一份社区手工维护的免费公开 API 大清单，按天气、地图、金融、影视、开发工具等几十个分类罗列了数千个能直接调用的接口，每条都标了是否需要鉴权、是否支持 HTTPS 和跨域。写 demo、做练手项目或临时找数据源时，翻这个表比自己一个个搜要快得多。

### 7. [Soup](https://github.com/MakazhanAlpamys/Soup) · Python 🆕
⭐ 1.7k（今日 +297）
**简介**：一个做 LLM 微调和后训练的命令行工具，把模型、数据、超参全塞进一份 YAML，一条命令就跑起来，省掉租卡、连 SSH、调环境那套折腾。它的核心卖点是「逐层流式加载」——训练时只把当前需要的那一层权重搬进显存，所以 4GB 显存的笔记本显卡也能训 8B 规模的模型。

### 8. [spec-kit](https://github.com/github/spec-kit) · Python
⭐ 129.2k（今日 +892）
**简介**：GitHub 官方出的开源工具包，主打「规格驱动开发」——先写清楚要做什么（规格/设计/计划），再让任意 AI 编码智能体动手实现；提供现成流程也支持自己定制，可扩展、社区驱动，适合整个团队统一使用。

### 9. [holehe](https://github.com/megadose/holehe) · Python
⭐ 13.1k（今日 +382）
**简介**：一个 OSINT 小工具：输入一个邮箱，就靠各家网站的「找回密码」接口去探测它在 Twitter、Instagram、Imgur 等 120 多个站点是否注册过账号，且不会惊动对方，常用来做账号关联调查或安全自查。

### 10. [FluidVoice](https://github.com/altic-dev/FluidVoice) · Swift 🆕
⭐ 10.3k（今日 +104）
**简介**：一个开源的 macOS 语音转文字听写 App，在设备本地跑语音识别加自训练 AI 增强模型，主打隐私和离线可用，相当于 Wispr Flow 的开源平替；目前只支持 Mac，Windows 与 iOS 还在等名单里。

### 11. [ToolJet](https://github.com/ToolJet/ToolJet) · JavaScript
⭐ 39.5k（今日 +544）
**简介**：一个开源的低代码平台，用来搭企业内部工具、仪表盘、业务应用和工作流，并集成数据库、API、SaaS 和对象存储。社区版提供可视化拖拽 UI 编辑器，新版也把 AI Agent 的生成、查询和调试能力直接内置进来了。

### 12. [CLI-Anything](https://github.com/HKUDS/CLI-Anything) · Python 🆕
⭐ 47.4k（今日 +118）
**简介**：港大数据智能实验室的项目，思路是把各类桌面软件和在线服务统一包装成命令行工具，让 AI 智能体不用去点图形界面也能直接驱动它们干活，比如画 CAD 图纸、搭 3D 场景、出图表、压字幕。配套还做了一个 CLI-Hub，pip 安装后一条命令就能拉取社区贡献的各种软件封装，目前已覆盖十几款应用。

### 13. [ego-lite](https://github.com/citrolabs/ego-lite) · JavaScript
⭐ 11.0k（今日 +545）
**简介**：一个专门给 AI 智能体用的浏览器：你和 agent 并行工作，agent 在各自的「空间」里跑多个浏览器任务，而你的标签页保持不变、不会被打扰；还能把已登录的网页状态直接共享给 Codex / Claude Code 这类编码智能体，零成本、零配置就能做浏览器自动化。

---

## 退榜项目

- macro-inc/macro
- smicallef/spiderfoot
- holaboss-ai/holaOS
- lightningpixel/modly
- infiniflow/ragflow
- deepseek-ai/awesome-deepseek-agent
- semantica-agi/semantica
- rustdesk/rustdesk
- OpenCut-app/OpenCut
