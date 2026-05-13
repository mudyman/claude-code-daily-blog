---
layout: post
title: "Claude Code 实战：让 AI 接管你的鼠标，终端里的 GUI 自动化革命"
date: 2026-05-13
topic: computer-use
categories: [daily-digest]
tags: [claude-code, computer-use]
description: "作为开发者，我们习惯了在终端里挥斥方遒，但总有些时刻不得不放下键盘，拿起鼠标：验证一个原生 macOS 应用的界面、在 iOS 模拟器里走一遍注册流程、或者调试那个只在特定窗口大小下才会出现的 CSS 截断问题。这种在 CLI 和 GUI 之间的上下文切换，不仅打断心流，更是自动化链条上的断层。"
---

# Claude Code 实战：让 AI 接管你的鼠标，终端里的 GUI 自动化革命

作为开发者，我们习惯了在终端里挥斥方遒，但总有些时刻不得不放下键盘，拿起鼠标：验证一个原生 macOS 应用的界面、在 iOS 模拟器里走一遍注册流程、或者调试那个只在特定窗口大小下才会出现的 CSS 截断问题。这种在 CLI 和 GUI 之间的上下文切换，不仅打断心流，更是自动化链条上的断层。

今天我们要探讨的 Claude Code `computer-use` 功能，正是为了填平这道鸿沟。它让 Claude 能够像你一样看着屏幕、移动鼠标、敲击键盘，把原本需要人工干预的 GUI 操作，无缝编织进终端里的对话流中。

## 关键概念：何时需要 Computer Use？

Claude Code 并不是一个只会挥舞“屏幕控制”这把锤子的工具。在调用 `computer-use` 之前，Claude 会智能地优先选择更精准的工具：

1. **MCP 服务器**：如果你配置了对应服务的 MCP，Claude 会优先通过结构化 API 交互。
2. **Bash 命令**：如果是命令行能搞定的任务，绝不碰 GUI。
3. **Chrome 集成**：如果是浏览器任务，且配置了 Claude in Chrome，它会接管浏览器。
4. **Computer Use**：只有当前面三种方式都触达不到时——比如原生应用、模拟器、没有 API 的专有软件，Claude 才会祭出屏幕控制这个“终极武器”。

## 实操演示：开启你的第一次 GUI 自动化

`computer-use` 在 CLI 中是作为一个内置的 MCP 服务器存在的，默认关闭。开启它只需要简单几步：

在交互式的 Claude Code 会话中输入：

```text
/mcp
```

在弹出的服务器列表中找到 `computer-use`，此时它的状态是禁用的。选中它并选择 **Enable**。这个设置是按项目持久化的，一次开启，该项目下永久生效。



![Mcp Computer Use Enable](assets/images/screenshots/mcp-computer-use-enable.png)



首次触发时，macOS 会弹出权限请求，你需要授予两项权限：
- **辅助功能（Accessibility）**：允许 Claude 点击、输入和滚动。
- **屏幕录制（Screen Recording）**：允许 Claude 查看你的屏幕内容。

授权后（macOS 可能要求你重启 Claude Code），你就可以发号施令了：

```text
Build the app target, launch it, and click through each tab to make
sure nothing crashes. Screenshot any error states you find.
```

## 安全与信任边界：Claude 在你屏幕上的行为准则

让 AI 控制桌面难免让人心生警惕。与运行在沙箱中的 Bash 工具不同，`computer-use` 运行在你真实的桌面环境中。为此，Claude Code 设计了严密的防护网：

**会话级应用审批**：Claude 不会获得所有应用的通行证。当它首次需要控制某个应用时，终端会显示它想控制的应用列表、请求的额外权限（如剪贴板）以及隐藏的其他应用数量。你必须选择 **Allow for this session** 才能放行。



![App Approval Prompt](assets/images/screenshots/app-approval-prompt.png)



**高危应用哨兵警告**：对于权限过大的应用，系统会给出额外警告：
- **等同于 Shell 访问**：Terminal, iTerm, VS Code 等 IDE。
- **可读写任何文件**：Finder。
- **可更改系统设置**：系统设置。

**终端窗口隔离**：你的终端窗口永远会被排除在截图之外。这意味着 Claude 看不到自己的输出，有效防止了屏幕上的提示词反向注入模型。

**全局逃生舱**：当 Claude 接管屏幕时，macOS 会弹出通知。你可以随时按下 `Esc` 键或终端里的 `Ctrl+C`，Claude 会立即释放锁、恢复隐藏的应用并将控制权交还给你。

## 进阶技巧：真实场景下的工作流

### 1. 复现诡异的布局 Bug
视觉 Bug 最难搞的就是复现条件苛刻。现在你可以直接甩给 Claude：

```text
The settings modal clips its footer on narrow windows. Resize the app
window down until you can reproduce it, screenshot the clipped state,
then check the CSS for the modal container.
```

Claude 会像真人一样缩小窗口，捕获崩溃瞬间，然后自己去翻 CSS 代码找原因。



![Layout Bug Reproduction](assets/images/screenshots/layout-bug-reproduction.png)



### 2. 无需 XCTest 的模拟器测试
不想为了走一遍流程写一堆测试脚手架？没问题：

```text
Open the iOS Simulator, launch the app, tap through the onboarding
screens, and tell me if any screen takes more than a second to load.
```

### 3. 端到端原生应用验证
从编译到 UI 验收，一口气搞定：

```text
Build the MenuBarStats target, launch it, open the preferences window,
and verify the interval slider updates the label. Screenshot the
preferences window when you're done.
```

**💡 小贴士**：Claude 会自动将高分辨率屏幕（如 Retina 屏）的截图等比例缩小后再发送给模型。你无需手动调低分辨率。如果界面上的某些文字太小导致 Claude 识别不清，最好的办法是在应用内调大字体，而不是改动显示器设置。

## 明日预告

今天我们掌握了如何让 Claude 在本地 GUI 世界里大显身手。但在实际开发中，我们的目标环境往往不在本地，而是在远端服务器或云端实例上。如何突破本地的物理限制，让 Claude Code 的能力延伸到远程机器？明天我们将深入探讨 **远程控制**，看看 Claude Code 如何跨越网络边界，敬请期待！