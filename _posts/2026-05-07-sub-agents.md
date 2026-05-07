---
layout: post
title: "Claude Code 进阶：用子代理打造专属 AI 开发特种部队"
date: 2026-05-07
topic: sub-agents
categories: [daily-digest]
tags: [claude-code, sub-agents]
description: "你是否遇到过这样的情况：让 AI 帮你排查一个复杂的 Bug，它输出了成百上千行的日志和代码搜索结果，等它终于找到原因时，你的上下文窗口已经被塞满，连之前讨论的架构设计都忘了？"
---

# Claude Code 进阶：用子代理打造专属 AI 开发特种部队

你是否遇到过这样的情况：让 AI 帮你排查一个复杂的 Bug，它输出了成百上千行的日志和代码搜索结果，等它终于找到原因时，你的上下文窗口已经被塞满，连之前讨论的架构设计都忘了？

这就是 Claude Code **子代理** 要解决的核心痛点。子代理是在独立上下文窗口中运行的专用 AI 助手。它们在你的主对话之外默默工作，只把最终的精炼结论带回给你。今天我们就来深入拆解这个强大的功能。

## 关键概念：为什么需要子代理？

简单来说，子代理帮你实现四件事：

* **保护上下文**：把海量日志、搜索结果隔离在主对话之外，只保留摘要。
* **强制约束**：限制代理只能使用特定工具（比如只读不写）。
* **行为专业化**：通过定制系统提示词，打造特定领域的专家。
* **控制成本**：将简单任务路由到 Haiku 等更快速、更便宜的模型。

Claude Code 内置了几个开箱即用的子代理：**Explore**（使用 Haiku 模型快速搜索代码库）、**Plan**（规划模式下的研究代理）和 **general-purpose**（处理需要探索与修改的复杂多步任务）。



![Built In Subagents List](assets/images/screenshots/built-in-subagents-list.png)



## 实操演示：创建你的第一个子代理

创建子代理最简单的方式是使用 `/agents` 命令。假设我们要创建一个全平台通用的代码审查代理：

1. 在 Claude Code 中运行 `/agents`。
2. 切换到 **Library** 标签，选择 **Create new agent**，然后选择 **Personal**（这会将其保存到 `~/.claude/agents/`，所有项目通用）。
3. 选择 **Generate with Claude**，输入描述：

```text
A code improvement agent that scans files and suggests improvements
for readability, performance, and best practices. It should explain
each issue, show the current code, and provide an improved version.
```

4. 取消勾选除 **Read-only tools** 之外的所有工具，确保它只看不写。
5. 模型选择 **Sonnet**，平衡能力与速度。
6. 选择颜色以便在 UI 中识别，选择 **User scope** 开启跨会话的持久化记忆。
7. 保存后，立即可以这样使用：

```text
Use the code-improver agent to suggest improvements in this project
```



![Agents Creation Wizard](assets/images/screenshots/agents-creation-wizard.png)



## 进阶技巧：手写配置与精细化控制

当你需要更精细的控制时，直接编写 Markdown 文件是更好的选择。子代理文件使用 YAML frontmatter 定义配置，正文作为系统提示词。

### 1. 工具限制与模型选择

下面是一个只读研究代理，它只能读取和搜索，无法修改任何文件：

```yaml
---
name: safe-researcher
description: Research agent with restricted capabilities
tools: Read, Grep, Glob, Bash
---
```

如果你想继承所有工具但禁止写入，可以使用 `disallowedTools`：

```yaml
---
name: no-writes
description: Inherits every tool except file writes
disallowedTools: Write, Edit
---
```

### 2. 通过 Hooks 实现条件约束

有时简单的工具黑白名单不够用。比如你需要一个能执行 Bash 的代理，但只允许运行 `SELECT` 查询。这时可以结合 `PreToolUse` 钩子：

```yaml
---
name: db-reader
description: Execute read-only database queries
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---
```

对应的验证脚本如下，当检测到写操作时以退出码 `2` 阻止执行：

```bash
#!/bin/bash
# ./scripts/validate-readonly-query.sh

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Block SQL write operations (case-insensitive)
if echo "$COMMAND" | grep -iE '\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b' > /dev/null; then
  echo "Blocked: Only SELECT queries are allowed" >&2
  exit 2
fi

exit 0
```

### 3. 持久化记忆：让代理越用越聪明

通过 `memory` 字段，子代理可以在跨会话中积累知识：

```yaml
---
name: code-reviewer
description: Reviews code for quality and best practices
memory: user
---

You are a code reviewer. As you review code, update your agent memory with
patterns, conventions, and recurring issues you discover.
```

`memory` 支持三种作用域：`user`（全局跨项目）、`project`（项目级，可提交至版本控制）和 `local`（项目级但不入库）。启用后，代理会自动在 `~/.claude/agent-memory/` 或项目对应目录下维护 `MEMORY.md` 文件。

### 4. 作用域与优先级管理

子代理可以存在于不同位置，优先级从高到低为：

1. **托管设置**（组织级强制部署）
2. **`--agents` CLI 标志**（当前会话临时生效，适合自动化脚本）
3. **`.claude/agents/`**（项目级，推荐提交到 Git 与团队共享）
4. **`~/.claude/agents/`**（用户级，个人跨项目通用）
5. **插件的 `agents/` 目录**（最低优先级）

其中，通过 CLI 标志定义的临时代理非常适合 CI/CD 场景：

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  },
  "debugger": {
    "description": "Debugging specialist for errors and test failures.",
    "prompt": "You are an expert debugger. Analyze errors, identify root causes, and provide fixes."
  }
}'
```

### 5. 分支：继承主对话的轻量级派生

如果你开启了实验性环境变量 `CLAUDE_CODE_FORK_SUBAGENT=1`，你可以使用 `/fork` 命令创建分支。与普通子代理不同，分支会继承当前主对话的完整历史记录和系统提示词，但工具调用结果仍被隔离。这在你需要让 AI 基于当前讨论上下文去并行尝试几种方案时非常有用：

```text
/fork draft unit tests for the parser changes so far
```



![Fork Subagent Panel](assets/images/screenshots/fork-subagent-panel.png)



## 明日预告

今天我们深入探讨了如何通过子代理将复杂任务拆解、隔离并分配给专门的 AI 代理。无论是保护上下文、限制权限还是积累领域知识，子代理都让 Claude Code 从一个全能助手进化成了一支特种部队。但如果你想让这些代理在 CI/CD 流水线中自动运行，或者通过代码编程式地调度它们，该怎么做呢？明天我们将开启 **Agent SDK 概览**，看看如何用代码驱动 Claude Code 实现自动化工作流。