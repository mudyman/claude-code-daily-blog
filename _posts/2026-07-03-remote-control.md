---
layout: post
title: "告别工位绑定：Claude Code 远程控制让你随时随地继续编码"
date: 2026-07-03
topic: remote-control
categories: [daily-digest]
tags: [claude-code, remote-control]
description: "作为开发者，你是否经历过这样的场景：下班前让 AI 跑一个重构任务，刚坐上地铁却突然想到需要补充一个关键上下文？或者周末在咖啡厅用平板想查看一下本地项目的测试结果，却发现代码全在公司电脑里？"
---

# 告别工位绑定：Claude Code 远程控制让你随时随地继续编码

作为开发者，你是否经历过这样的场景：下班前让 AI 跑一个重构任务，刚坐上地铁却突然想到需要补充一个关键上下文？或者周末在咖啡厅用平板想查看一下本地项目的测试结果，却发现代码全在公司电脑里？

传统的做法是痛苦地配置内网穿透、SSH 隧道，或者干脆打道回府。但现在，Claude Code 的 **Remote Control（远程控制）** 功能彻底改变了游戏规则。它让你在工位上启动的本地会话，可以直接从手机、平板或任何浏览器无缝接管。

## 核心概念：你的本地环境，远程的窗口

Remote Control 最核心的设计理念是：**计算始终在本地，远程只是界面**。

与 Claude Code on the web（在 Anthropic 云端运行）不同，Remote Control 会话直接运行在你的机器上。你在浏览器或手机上的操作，实际上是在操控本地的 Claude Code 进程。这意味着：

- **完整的本地环境**：你的文件系统、MCP 服务器、项目配置全部可用，甚至在远程输入 `@` 时，自动补全的依然是你本地项目里的文件路径。
- **多端实时同步**：终端、浏览器、手机之间的对话完全同步，你可以随意在设备间切换发送消息。
- **断线自动重连**：笔记本合盖休眠或网络短暂断开都没关系，机器重新上线后会话会自动恢复。

## 实操演示：如何启动并连接

Remote Control 提供了多种启动方式，适应不同的工作流需求。

### 1. 纯服务器模式（适合长期挂机）

如果你只想把当前终端作为专用的远程服务节点，可以进入项目目录运行：

```bash
claude remote-control
```

此时终端会进入服务器模式并显示一个会话 URL。按下空格键，还能显示一个二维码，方便手机扫码直连。



![Remote Control Server Mode Qr](assets/images/screenshots/remote-control-server-mode-qr.png)



这个模式支持丰富的参数，例如使用 `--spawn worktree` 让每个远程连接使用独立的 git worktree，避免多端同时编辑同一文件产生冲突：

```bash
claude remote-control --name "My Project" --spawn worktree
```

### 2. 交互+远程双开模式（日常开发首选）

如果你既想在本地终端敲代码，又想保留随时被远程接管的能力，使用 `--remote-control`（或简写 `--rc`）标志：

```bash
claude --remote-control
```

或者直接指定会话名称：

```bash
claude --remote-control "My Project"
```

### 3. 会话中途开启远程

如果你已经在一个普通的 Claude Code 会话中，突然想出门，无需退出重启，直接输入斜杠命令即可：

```text
/remote-control
```

### 4. VS Code 扩展中开启

在 VS Code 的 Claude Code 扩展中，只需在输入框键入 `/remote-control` 或 `/rc`，连接成功后顶部会出现状态横幅，点击即可在浏览器中打开。

### 连接到远程会话

会话启动后，你可以通过以下方式从其他设备连接：
- 在任意浏览器打开会话 URL（指向 claude.ai/code）
- 用 Claude 手机 App 扫描终端显示的二维码
- 在 Claude App 的 "Code" 导航栏中，寻找带有绿色电脑图标的在线会话



![Mobile App Session List](assets/images/screenshots/mobile-app-session-list.png)



## 进阶技巧

### 手机推送通知：不错过任何关键节点

长任务跑完或者 AI 需要你确认权限时，Claude 可以直接给手机发推送！只需在终端运行 `/config`，开启 **Push when Claude decides**（AI 主动推送）或 **Push when actions required**（需人工干预时推送）。

你甚至可以在提示词中直接要求：“`notify me when the tests finish`（测试跑完通知我）”。



![Push Notification Config](assets/images/screenshots/push-notification-config.png)



### 受信设备（Trusted Devices）：企业级安全保障

对于 Team 和 Enterprise 计划，管理员可以在后台开启“受信设备”策略。开启后，员工必须通过 Face ID、Touch ID 或 Windows Hello 验证设备，才能查看或操控远程会话。这确保了即使账号被盗，没有生物识别验证也无法接管你的本地环境。

### 一劳永逸：默认开启远程控制

如果你希望每次启动 Claude Code 都自动带上远程控制功能，运行 `/config`，将 **Enable Remote Control for all sessions** 设置为 `true`。以后每个交互式进程都会自动注册一个远程会话。

## 避坑指南：常见问题排查

- **"Remote Control requires a claude.ai subscription"**：你使用了 API Key 登录。Remote Control 不支持 API Key，请运行 `claude auth login` 使用 claude.ai OAuth 登录。
- **"Remote Control is only available when using Claude via api.anthropic.com"**：你配置了第三方云服务（如 Bedrock、Vertex）或设置了 `ANTHROPIC_BASE_URL` 环境变量指向代理网关。取消该环境变量设置即可恢复。
- **"Remote Control is disabled by your organization's policy"**：Team/Enterprise 计划默认关闭此功能，需要组织 Owner 在管理后台手动开启。
- **连接凭据获取失败**：加上 `--verbose` 标志重新运行，查看详细网络错误，通常是防火墙拦截了向 Anthropic API 发起的 443 端口出站请求。

```bash
claude remote-control --verbose
```

## 明日预告

Remote Control 让我们打破了物理空间的限制，实现了从任何设备向本地 Claude Code 会话发号施令。但如果你想让 Claude 不仅仅响应你的指令，还能主动监听外部事件——比如 CI 跑挂了自动修复，或者 Telegram 里收到消息自动处理——该怎么办？明天我们将深入探讨 **第三方集成**，看看 Claude Code 如何与外部世界无缝对接。