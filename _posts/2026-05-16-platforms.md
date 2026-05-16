---
layout: post
title: "Claude Code 全平台指南：找到最适合你的开发工作流"
date: 2026-05-16
topic: platforms
categories: [daily-digest]
tags: [claude-code, platforms]
description: "你有没有经历过这样的场景：在终端里用 Claude Code 跑得好好的，突然需要去开会，只能无奈关掉电脑中断任务？或者你想在代码审查时直接看 Diff 视图，却只能在命令行里对着纯文本发呆？"
---

# Claude Code 全平台指南：找到最适合你的开发工作流

你有没有经历过这样的场景：在终端里用 Claude Code 跑得好好的，突然需要去开会，只能无奈关掉电脑中断任务？或者你想在代码审查时直接看 Diff 视图，却只能在命令行里对着纯文本发呆？

很多开发者以为 AI 编程助手就是一个单纯的聊天框，但 Claude Code 的设计哲学完全不同——**同一个核心引擎，多种交互界面**。今天我们就来拆解 Claude Code 的全平台生态，看看如何根据你的工作场景，选择最顺手的武器。

## 关键概念：一个引擎，多面出击

Claude Code 在所有平台上运行的都是同一个底层引擎，但每个平台都针对特定的工作方式做了调优。这意味着你不需要在不同工具间妥协，而是可以根据当前任务灵活切换。

### 本地运行平台对比

| 平台 | 最适合 | 你能得到什么 |
| :--- | :--- | :--- |
| **CLI** | 终端工作流、脚本、远程服务器 | 完整功能集、Agent SDK、macOS 上的 computer use (Pro/Max)、第三方提供商 |
| **Desktop** | 可视化审查、并行会话、托管配置 | Diff 查看器、应用预览、computer use 和 Dispatch (Pro/Max) |
| **VS Code** | 在 VS Code 内工作，无需切换终端 | 内联 Diff、集成终端、文件上下文 |
| **JetBrains** | 在 IntelliJ、PyCharm 等内工作 | Diff 查看器、选择共享、终端会话 |
| **Web** | 不需要太多干预的长时间任务，或离线后需继续的工作 | Anthropic 托管云，断开连接后继续运行 |
| **Mobile** | 离开电脑时启动和监控任务 | iOS/Android 应用的云会话、本地会话的 Remote Control、发送任务到 Desktop 的 Dispatch |



![Platforms Comparison Table](assets/images/screenshots/platforms-comparison-table.png)



**核心洞察**：CLI 是功能最全的终极形态，特别是脚本和 Agent SDK 仅限 CLI 使用。如果你需要使用 Bedrock 或 Foundry 等第三方提供商，CLI 或 VS Code 是首选。而 Desktop 和 IDE 扩展则是用部分 CLI 独占功能换取了更直观的可视化审查和编辑器集成。

最棒的是，**你可以在同一个项目上混合使用这些平台**。配置、项目记忆和 MCP 服务器在所有本地平台间都是共享的。

## 实操演示：连接你的工具链

平台只是起点，真正的生产力爆发在于将 Claude Code 接入你现有的工具生态。

### 外部服务集成

| 集成 | 功能 | 适用场景 |
| :--- | :--- | :--- |
| **Chrome** | 用你的登录会话控制浏览器 | 测试 Web 应用、填写表单、自动化没有 API 的网站 |
| **GitHub Actions** | 在 CI 流水线中运行 Claude | 自动 PR 审查、Issue 分类、定时维护 |
| **GitLab CI/CD** | 同 GitHub Actions，适用于 GitLab | GitLab 上的 CI 驱动自动化 |
| **Code Review** | 自动审查每个 PR | 在人工审查前捕获 Bug |
| **Slack** | 响应频道中的 `@Claude` 提及 | 将团队聊天中的 Bug 报告直接转化为 Pull Request |

如果你的工具不在列表中，别担心。通过 MCP 服务器和连接器，你可以接入几乎任何服务：Linear、Notion、Google Drive，甚至你自己的内部 API。

## 进阶技巧：离开终端也能干活

这是 Claude Code 最让我兴奋的特性之一。我们不可能 24 小时坐在电脑前，但开发任务往往需要跨时间推进。

| 方式 | 触发条件 | 运行位置 | 设置方式 | 最适合 |
| :--- | :--- | :--- | :--- | :--- |
| **Dispatch** | 从移动端 App 发送任务消息 | 你的机器 (Desktop) | 配对移动端与 Desktop | 离开时委派工作，设置最少 |
| **Remote Control** | 从浏览器或手机驱动运行中的会话 | 你的机器 (CLI/VS Code) | 运行 `claude remote-control` | 从其他设备操控进行中的工作 |
| **Channels** | 从 Telegram/Discord 等推送事件 | 你的机器 (CLI) | 安装频道插件或自建 | 响应外部事件如 CI 失败 |
| **Slack** | 在频道中 @Claude | Anthropic 云 | 安装 Slack App 并启用 Web 版 | 从团队聊天生成 PR 和审查 |
| **Scheduled tasks** | 设置时间计划 | CLI、Desktop 或云 | 选择频率 | 日常审查等周期性自动化 |



![Remote Dispatch Workflow](assets/images/screenshots/remote-dispatch-workflow.png)



**实战建议**：如果你经常需要外出但心里挂念着代码，**Dispatch** 是你的最佳选择。只需在手机上发个消息，它就能在你的电脑上启动一个 Desktop 会话干活。如果你更习惯在地铁上用手机微调正在跑的任务，**Remote Control** 配合 `claude remote-control` 命令会让你感觉像是在远程操控自己的终端。

## 总结

选择平台不需要从一而终。在深度编码时用 VS Code 扩展享受内联 Diff；跑长任务时扔到 Web 端让它自己跑；离开工位时用 Mobile 端的 Dispatch 远程派活。**按需切换，才是 AI 编程助手的正确打开方式。**

如果你还不确定从哪里开始，最简单的路径就是安装 CLI，在项目目录下跑起来。如果你不想碰终端，Desktop 提供了同样强大的图形界面。

---

**明日预告**：既然 Claude Code 可以跨平台共享配置和记忆，这些项目级别的设定到底存在哪里？明天我们将深入探讨 `.claude 目录`，揭秘如何通过它来固化项目规范、管理 MCP 服务器，让你的 AI 助手真正理解你的项目上下文。