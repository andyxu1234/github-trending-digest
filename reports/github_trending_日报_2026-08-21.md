# GitHub Trending 日报 · 2026-08-21

> 数据来源 [github.com/trending](https://github.com/trending) ｜ 抓取时间 2026-08-21T11:06:39.004049+08:00 ｜ 共 17 个上榜项目

## 概览
- 本期上榜：**17** 个
- 本期新增：🆕 **11** 个（对比上一期同类型报告）
- 本期退榜：**7** 个

---

## 项目列表

### 1. [modular](https://github.com/modular/modular) · Mojo 🆕
⭐ 28.0k（今日 +268）
**简介**：Modular 公司开源的整套 AI 开发与部署平台，核心是 Mojo 编程语言（专为 AI 设计、向下兼容 Python 的新语言）和 MAX 推理框架（能跑大模型、还能当 OpenAI 兼容的服务端）。这个仓库把 Mojo 编译器、标准库、MAX 的加速内核和推理服务都放一起，想用一套工具打通模型训练和上线。

### 2. [skills](https://github.com/mattpocock/skills) · Shell
⭐ 226.8k（今日 +2,192）
**简介**：一位资深工程师把自己 .agents 配置里真正在用的 AI 技能直接开源出来，面向「真干活的程序员」。

### 3. [OpenLogi](https://github.com/AprilNEA/OpenLogi) · Rust 🆕
⭐ 12.0k（今日 +1,545）
**简介**：一个用 Rust 写的、本地运行的罗技（Logitech）外设配置工具，相当于开源版的 Logitech Options+。能重映射鼠标按键、调 DPI、设置 SmartShift 滚轮，走 HID++ 协议直接跟设备通信，不强制登录账号、不上传任何遥测数据，主打隐私和离线可用。

### 4. [superpowers](https://github.com/obra/superpowers) · Shell
⭐ 275.0k（今日 +727）
**简介**：一套给 AI 编程智能体用的「软件开发方法论 + 技能包」。它不急着让 agent 上手写代码，而是先逼着它问清楚你到底要做啥、把需求拆成能看懂的小块让你确认，再产出一份连「没经验的 junior」都挑不出刺的实现计划，强调测试驱动、YAGNI、DRY，最后用一群子 agent 分头干活并互相 review。等于把资深工程师带人的那套流程沉淀成了可复用技能。

### 5. [plugins](https://github.com/cursor/plugins) · TypeScript 🆕
⭐ 4.1k（今日 +449）
**简介**：Cursor 官方的插件规范与一批官方插件仓库：每个插件都是根目录下的独立文件夹、带自己的 plugin.json 清单。涵盖团队工作流、深度代码/安全审查、PR 与文档可视化、CI 与本地自动化等开发工具相关的智能体能力。

### 6. [career-ops](https://github.com/santifer/career-ops) · JavaScript
⭐ 66.8k（今日 +816）
**简介**：一个开源的 AI 求职系统：自动扫招聘网站、用 A-F 评分给岗位打分、帮你改简历、追踪投递进度，全程在你本地的 AI 编程工具里跑，相当于把「用 AI 筛公司」这件事交给了候选人自己。

### 7. [ai-memory](https://github.com/akitaonrails/ai-memory) · Rust 🆕
⭐ 3.7k（今日 +332）
**简介**：给 AI 编程智能体用的「长期记忆」：你在 Claude Code 干到一半切到 Codex，它能把架构、试过的坑、遗留问题都带过去，新 agent 接着干不用你重新解释一遍，支持 Linux/macOS/WSL。

### 8. [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) · Python
⭐ 113.1k（今日 +2,761）
**简介**：一个一站式 AI 短视频生成工具：你只给个主题或关键词，它就自动写出视频脚本、找素材、配字幕和背景音乐，最后合成一条高清短视频，带 Web 界面和 API，适合批量做抖音/B站类短视频。

### 9. [substrate](https://github.com/agent-substrate/substrate) · Go 🆕
⭐ 1.4k（今日 +22）
**简介**：一个专门用来「大规模跑 AI 智能体」的运行底座：它在 Kubernetes 之上加一层控制面，把大量大部分时间在闲着的 agent 多路复用到少量机器/容器上，还能在亚秒级把某个 agent 暂停或唤醒。支持 microVM 和 gVisor 多种沙箱，但它本身不是写 agent 的框架，而是负责把成百上千个 agent 高效、低成本地托管运行起来的系统。

### 10. [munder-difflin](https://github.com/chaitanyagiri/munder-difflin) · TypeScript
⭐ 3.2k（今日 +507）
**简介**：一个跑在自己电脑上的多智能体「办公室」桌面应用，把你已经订阅的终端编程 CLI（Claude Code、Codex、Grok、Kimi、Qwen、Copilot CLI 等）分别包装成有长期记忆和收件箱的 agent。每个 agent 在 2D 办公室里对应一个会走动的小人，由一个模仿你本人的「克隆体」负责派活和转交，你出门后它们还能接着干。

### 11. [posthog](https://github.com/PostHog/posthog) · Python 🆕
⭐ 38.0k（今日 +60）
**简介**：一个开源的「产品数据分析 + 智能体可观测」一体化平台：把事件分析、会话回放、功能开关、A/B 实验、错误追踪、日志这些做产品要用到的工具全打包在一起，还加了 AI 可观测能力（让 agent 自己诊断问题、发现机会、自动修）。可以在 Slack、网页、桌面端或 MCP 里直接操控，号称帮你造「自动驾驶」的产品。

### 12. [google-timeline-visualizer](https://github.com/mahlernim/google-timeline-visualizer) · Kotlin 🆕
⭐ 1.7k（今日 +657）
**简介**：一个把你在 Google 地图里的「时间线 / 位置历史」变成动画旅行视频的小工具：导出 Timeline.json 后，选好日期区间和镜头运动方式，就能自动生成一段记录你这一年去过哪里的 MP4 视频。安卓有 App，iPhone 用网页版（数据不上传），主打隐私和随手做年度旅行回顾。

### 13. [OpenViking](https://github.com/volcengine/OpenViking) · Python
⭐ 31.1k（今日 +950）
**简介**：火山引擎开源的 AI Agent 上下文数据库，把记忆、资料和技能统一存成 viking:// 协议下的虚拟文件系统，Agent 能像人翻文件夹那样用 ls / tree / find 自己找上下文，而不是对着黑盒向量库瞎查。写入时会把内容切成摘要、概览、细节三层，按任务需要加载到对应深度以省 token，每次检索还会留下完整的翻找路径，结果不对时能直接回溯是哪一步出的错。

### 14. [caveman](https://github.com/JuliusBrussee/caveman) · Go 🆕
⭐ 99.7k（今日 +258）
**简介**：一个给 AI 编程智能体用的「省 token 技能包」：让 agent 像原始人一样说话——能用几个词说清就不啰嗦，实测能把发给模型的输入 token 砍掉约三成、整体对话 token 省掉六成多。它不改你的 agent，只是包一层提示词让上下文变小、脑子不变，目前已适配 Claude Code、Cursor 等 30 多个编码工具。

### 15. [plane](https://github.com/makeplane/plane) · TypeScript 🆕
⭐ 56.6k（今日 +98）
**简介**：一个开源的项目管理平台，对标 Jira、Linear、Monday 这些商业工具：能管任务、跑周期（sprint）、写文档、做需求分流，自带网页界面也能自己部署到服务器上。主打「少折腾、把工具本身的管理成本降到最低」，适合想自己掌控数据又不想被收费墙卡住的团队。

### 16. [AI-Infra-Guard](https://github.com/Tencent/AI-Infra-Guard) · Python 🆕
⭐ 5.0k（今日 +50）
**简介**：腾讯开源的一套「AI 安全红队 / 攻防评测」平台：专门用来给 AI 系统挑毛病，能扫智能体本体（Agent Scan）、扫技能包、扫 MCP 连接、扫底层 AI 基础设施，还会做大模型越狱测试。等于把检查一个 AI 应用有没有安全漏洞这件事做成了一站式平台，开发者上线前能拿它兜底。

### 17. [turbovec](https://github.com/RyanCodrai/turbovec) · Rust 🆕
⭐ 16.0k（今日 +230）
**简介**：一个用 Rust 写、带 Python 接口的向量检索库，底层基于 Google 的 TurboQuant 量化算法：同样的 1000 万条向量，普通 float32 要 31GB 内存，它只要 4GB，而且搜索比 FAISS 还快。特点是「在线灌入」——加向量即时索引、不用预训练也不用重训，还能增量落盘，做 RAG 或向量搜索时能省一大笔资源。

---

## 退榜项目

- mukul975/Anthropic-Cybersecurity-Skills
- nautechsystems/nautilus_trader
- jundot/omlx
- immich-app/immich
- amadeusprotocol/node
- marceloprates/prettymaps
- genlayerlabs/genlayer-project-boilerplate
