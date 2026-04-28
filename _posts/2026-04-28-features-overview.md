---
layout: post
title: "告别“裸奔”的 AI 编程：Claude Code 扩展体系全景解析"
date: 2026-04-28
topic: features-overview
categories: [daily-digest]
tags: [claude-code, features-overview]
description: "你有没有遇到过这样的情况：AI 助手总是忘记你的项目用 pnpm 而不是 npm？每次部署都要把长篇大论的 Checklist 复制粘贴进对话框？或者让 AI 做个全局代码搜索，结果把你的上下文窗口(context window)塞满，导致主对话直接“失忆”？"
---

# 告别“裸奔”的 AI 编程：Claude Code 扩展体系全景解析

你有没有遇到过这样的情况：AI 助手总是忘记你的项目用 pnpm 而不是 npm？每次部署都要把长篇大论的 Checklist 复制粘贴进对话框？或者让 AI 做个全局代码搜索，结果把你的上下文窗口(context window)塞满，导致主对话直接“失忆”？

这些痛点的本质，是你没有为 AI 建立合适的**扩展与自动化体系**。今天我们就来拆解 Claude Code 的七大核心扩展功能，看看它们如何各司其职，把你的 AI 编程助手从“懂语法的打字员”升级为“深谙项目规范的架构师”。

## 关键概念：七大扩展，各司其职

Claude Code 的扩展层插入了 AI 代理循环的不同节点，它们分别解决不同维度的问题：

- **CLAUDE.md**：每次对话必加载的持久化上下文，项目的“宪法”。
- **Skills（技能）**：可复用的知识与工作流，支持按需调用（如 `/deploy`）。
- **MCP**：连接外部服务的桥梁（数据库、Slack、浏览器等）。
- **Subagents（子代理）**：在隔离上下文中独立运行，只返回摘要，保护主对话不被海量日志污染。
- **Agent teams（代理团队）**：多个独立的 Claude Code 会话协同工作，适合复杂并行任务。
- **Hooks（钩子）**：生命周期事件的绝对触发器，如每次编辑后必跑 ESLint。
- **Plugins（插件）**：打包分发上述功能的集合体。



![Features Overview Table](assets/images/screenshots/features-overview-table.png)



## 实操演示：按需生长的配置哲学

不要试图一开始就配置所有东西。优秀的开发环境是随着痛点自然生长的。官方给出了一个非常实用的“触发器指南”：

| 触发场景 | 应该添加的功能 |
| :--- | :--- |
| Claude 连续两次搞错项目规范 | 写进 **CLAUDE.md** |
| 你总是输入相同的 Prompt 来启动任务 | 保存为用户调用的 **Skill** |
| 你第三次把多步操作手册粘贴进对话框 | 封装为 **Skill** |
| 你总是从浏览器复制 Claude 看不到的数据 | 接入 **MCP 服务器** |
| 侧线任务的大量输出快把主对话撑爆了 | 交给 **Subagent** 处理 |
| 你希望某件事每次都自动发生，无需提醒 | 写个 **Hook** |
| 另一个仓库需要完全相同的配置 | 打包成 **Plugin** |

**核心原则：重复犯错改 CLAUDE.md，手动流程化 Skill，强制定规用 Hook。**

### 易混淆功能大比拼

很多开发者容易把 Skills 和 Subagents，或者 CLAUDE.md 和 Skills 搞混。我们来看核心区别：

**Skill vs Subagent**
- **Skill** 是装载到当前上下文的“知识”，是参考资料或动作指南。
- **Subagent** 是独立运行的“打工人”，它自己有个隔离的上下文窗口，干完活只把结论汇报给你。当你需要读取几十个文件但不想占用主对话 Token 时，Subagent 是不二之选。

**CLAUDE.md vs Skill**
- **CLAUDE.md** 是“永远要遵守的规则”，每次会话自动加载。经验法则：保持在 200 行以内。
- **Skill** 是“按需查阅的手册”，通过描述触发或 `/name` 唤起。把臃肿的 API 参考文档从 CLAUDE.md 移到 Skill 里，能大幅节省上下文成本。

**Hook vs Skill**
- **Hook** 是确定性的，只要触发就必执行，零上下文消耗（除非有输出）。“绝对不能编辑 `.env`”这种红线，写在 CLAUDE.md 里只是“请求”，写成 `PreToolUse` Hook 才是“强制执行”。
- **Skill** 是推理性的，由 Claude 判断如何应用。



![Feature Comparison Diagram](assets/images/screenshots/feature-comparison-diagram.png)



## 进阶技巧：组合拳与上下文成本控制

真正的生产力爆发在于功能的**组合**：

| 组合模式 | 工作原理 | 实际案例 |
| :--- | :--- | :--- |
| **Skill + MCP** | MCP 提供连接，Skill 教 Claude 怎么用好它 | MCP 连接数据库，Skill 提供表结构与查询范式 |
| **Skill + Subagent** | Skill 启动 Subagent 进行并行工作 | `/audit` 技能同时派生安全、性能、风格三个子代理 |
| **CLAUDE.md + Skills** | 前者管总则，后者存细则 | CLAUDE.md 写“遵循 API 规范”，Skill 存完整的 API Style Guide |
| **Hook + MCP** | Hook 触发 MCP 执行外部动作 | 编辑核心文件后，Hook 自动发 Slack 通知 |

**警惕上下文通胀**

每加一个功能，都在消耗 Claude 的注意力。理解加载时机至关重要：
- **CLAUDE.md**：每次请求都占上下文，必须精简。
- **Skills**：启动时只加载描述，调用时才加载全文（设置 `disable-model-invocation: true` 可完全隐藏，直到手动 `/` 调用，实现零成本）。
- **MCP**：闲置时仅占极小 Token，但连接可能静默断开，遇到工具失灵记得跑一下 `/mcp` 检查。
- **Hooks**：外部执行，默认零侵入。

## 明日预告

掌握了扩展体系的全景图后，我们要开始落地实操了。明天我们将深入 Claude Code 的**CLI 命令参考**，详细拆解那些让你在终端里呼风唤雨的命令行指令，敬请期待！