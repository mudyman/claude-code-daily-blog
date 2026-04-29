---
layout: post
title: "Claude Code CLI 速查手册：从交互式到全自动的进阶之路"
date: 2026-04-29
topic: cli-reference
categories: [daily-digest]
tags: [claude-code, cli-reference]
description: "作为开发者，我们每天都在终端里度过大量时间。如果每次想让 AI 帮忙，都要切出命令行去打开网页或者 IDE 插件，那体验绝对是割裂的。Claude Code 的核心魅力就在于：**它原生地活在你的终端里**。"
---

# Claude Code CLI 速查手册：从交互式到全自动的进阶之路

作为开发者，我们每天都在终端里度过大量时间。如果每次想让 AI 帮忙，都要切出命令行去打开网页或者 IDE 插件，那体验绝对是割裂的。Claude Code 的核心魅力就在于：**它原生地活在你的终端里**。

今天，我们将深入剖析 Claude Code 的命令行接口（CLI）。掌握这些命令和参数，你就能把 AI 无缝嵌入到现有的开发流中，从简单的问答到复杂的 CI/CD 自动化，统统不在话下。



![Cli Help Output](assets/images/screenshots/cli-help-output.png)



## 一、核心命令：开启你的 AI 结对编程

Claude Code 的命令设计非常直觉。最简单的，输入 `claude` 就能启动一个交互式会话，就像和坐在旁边的同事聊天一样。

但真正的效率提升，在于灵活运用以下命令：

| 命令 | 说明 | 示例 |
| :--- | :--- | :--- |
| `claude` | 启动交互式会话 | `claude` |
| `claude "query"` | 带初始提示词启动交互会话 | `claude "explain this project"` |
| `claude -p "query"` | 非交互式查询，输出后退出（脚本神器） | `claude -p "explain this function"` |
| `cat file \| claude -p "query"` | 管道传入内容进行处理 | `cat logs.txt \| claude -p "explain"` |
| `claude -c` | 继续当前目录最近一次对话 | `claude -c` |
| `claude -r "<session>" "query"` | 根据 ID 或名称恢复特定会话 | `claude -r "auth-refactor" "Finish this PR"` |

**实战场景**：你刚拉取了同事的代码，想快速了解某个核心模块。不用进交互模式再贴代码，直接一行搞定：

```bash
cat src/auth/login.ts | claude -p "explain the security implications of this module"
```

如果你昨天改了一半的代码，今天想接着干，`claude -c` 能瞬间帮你找回上下文，连昨天没说完的半句话都能接上。

除了日常开发，CLI 还提供了完善的管理命令，比如更新版本（`claude update`）、安装特定版本（`claude install stable`）、管理认证状态（`claude auth status`）等。如果你手滑敲错了命令，比如 `claude udpate`，它还会贴心地提示 `Did you mean claude update?`，不会直接报错退出。

## 二、关键参数：精调你的 AI 助手

如果说命令是方向盘，那参数就是换挡拨片。`claude --help` 并不会列出所有参数，所以这份隐藏菜单值得你收藏。

### 1. 模型与上下文控制

*   `--model`: 指定模型，支持别名（如 `sonnet`, `opus`）或全称。
*   `--effort`: 设置努力级别（`low`, `medium`, `high`, `xhigh`, `max`）。遇到简单格式化任务可以用 `low`，复杂架构重构直接拉满到 `max`。
*   `--add-dir`: 添加额外工作目录。当你的项目跨越多个代码仓时，这个参数能让 Claude 读取和编辑其他路径的文件。

### 2. 系统提示词定制

这是定制化 AI 行为的核心。Claude Code 提供了四个参数，分为**替换**和**追加**两类：

| 参数 | 行为 | 示例 |
| :--- | :--- | :--- |
| `--system-prompt` | 替换整个默认提示词 | `claude --system-prompt "You are a Python expert"` |
| `--system-prompt-file` | 用文件内容替换默认提示词 | `claude --system-prompt-file ./prompts/review.txt` |
| `--append-system-prompt` | 在默认提示词后追加内容 | `claude --append-system-prompt "Always use TypeScript"` |
| `--append-system-prompt-file` | 追加文件内容 | `claude --append-system-prompt-file ./style-rules.txt` |

**进阶建议**：大多数情况下，**请使用追加（append）参数**。追加模式会保留 Claude Code 的内置能力（如文件读写、代码搜索），只叠加你的特定规则。只有在你需要完全掌控 AI 行为边界时，才使用替换模式。

### 3. 非交互式与自动化（脚本必备）

当你在写 Git Hook 或者 CI 流水线时，`-p` (print mode) 是你的好搭档，配合以下参数威力无穷：

*   `--max-turns`: 限制代理的执行轮数，防止死循环耗尽 Token。
*   `--max-budget-usd`: 设置单次任务的最大花费上限，财务安全的第一道防线。
*   `--output-format`: 指定输出格式（`text`, `json`, `stream-json`），方便后续程序解析。
*   `--json-schema`: 强制输出符合特定 JSON Schema 的结构化数据，这在提取特定信息时极为好用。

```bash
claude -p --max-turns 3 --max-budget-usd 1.00 --output-format json "Check for type errors"
```



![Cli Automation Script](assets/images/screenshots/cli-automation-script.png)



### 4. 权限与安全

AI 自动执行命令虽然爽，但安全不能忘：

*   `--permission-mode`: 直接指定权限模式（如 `plan` 只规划不执行，`auto` 自动放行安全操作）。
*   `--allowedTools`: 白名单工具，比如只允许执行 `git log` 和读取文件：`"Bash(git log *)" "Read"`。
*   `--dangerously-skip-permissions`: 跳过所有权限提示。**警告**：仅在绝对安全的环境（如沙箱 CI）中使用。

## 三、实操演示：打造你的专属 Code Review 机器人

了解了参数，我们来组合出拳。假设你想在提交 PR 前，让 Claude 用公司内部的代码规范进行自动审查，并输出结构化结果：

```bash
claude -p \
  --append-system-prompt-file ./company-code-style.md \
  --allowedTools "Read" "Bash(git diff *)" \
  --output-format json \
  --max-budget-usd 0.50 \
  "Review the current git diff against the company code style and output a list of violations"
```

这条命令做了几件事：
1.  追加了公司规范文件作为审查依据。
2.  限制了工具权限，只允许读文件和看 diff，绝不乱改代码。
3.  限制预算，避免意外消耗。
4.  输出 JSON，方便集成到其他通知系统。

如果你只是想快速审查某个 PR，官方也内置了更专业的工具 `ultrareview`：

```bash
claude ultrareview 1234 --json
```

它会以非交互方式运行，成功退出码为 0，失败为 1，非常适合卡在 CI 流水线的把关节点上。

## 四、进阶技巧：并行开发与远程控制

*   **Git Worktree 并行开发**：使用 `--worktree`（或 `-w`）参数，Claude 会在隔离的 git worktree 中工作。这意味着你可以让一个终端跑重构，另一个终端继续写新功能，互不干扰。配合 `--tmux` 还能自动开启分屏。
*   **远程控制**：通过 `claude remote-control` 启动服务，你可以在手机或平板的 Claude.app 上直接控制电脑终端里的 Claude Code，实现跨设备协作。



![Cli Worktree Parallel](assets/images/screenshots/cli-worktree-parallel.png)



## 明日预告

今天我们盘点了 CLI 的各种命令和参数，你已经掌握了操控 Claude Code 的"语法"。但工具的威力只有在具体场景中才能显现。明天，我们将进入实战环节，探讨 **常用工作流**——看看如何把这些零散的命令组合成解决代码重构、Bug 修复、多仓协作等真实痛点的高效流水线。敬请期待！