---
layout: post
title: "告别手搓工具循环：用 Claude Agent SDK 构建生产级 AI 代理"
date: 2026-05-08
topic: agent-sdk/overview
categories: [daily-digest]
tags: [claude-code, agent-sdk-overview]
description: "作为开发者，你可能已经体验过用大模型 API 搭建应用的过程：写 Prompt、解析返回、判断是否调用工具、执行工具、再把结果喂回模型……这个无尽的 `while` 循环写起来既枯燥又容易出错。如果有一个 SDK，能直接把 Claude Code 强大的文件读写、命令执行和上下文管理能力打包成库，让你只需关注业务逻辑，"
---

# 告别手搓工具循环：用 Claude Agent SDK 构建生产级 AI 代理

作为开发者，你可能已经体验过用大模型 API 搭建应用的过程：写 Prompt、解析返回、判断是否调用工具、执行工具、再把结果喂回模型……这个无尽的 `while` 循环写起来既枯燥又容易出错。如果有一个 SDK，能直接把 Claude Code 强大的文件读写、命令执行和上下文管理能力打包成库，让你只需关注业务逻辑，那该多好？

今天，Anthropic 正式将 Claude Code SDK 更名为 **Claude Agent SDK**。它不仅是一个改名，更是对生产级 AI 代理开发范式的一次升级——让你用 Python 或 TypeScript，几行代码就能构建出能自主读文件、跑命令、改代码的智能体。

## 关键概念：Agent SDK 带来了什么？

Agent SDK 的核心价值在于：**它内置了 Claude Code 的工具执行循环**。你不再需要手动实现工具路由和状态管理，只需定义目标，代理就会自主规划并执行。

让我们快速上手，看看有多简单。

### 第一步：安装与认证

根据你的技术栈选择安装方式：

```bash
# TypeScript
npm install @anthropic-ai/claude-agent-sdk
```

```bash
# Python
pip install claude-agent-sdk
```

> 💡 **小贴士**：TypeScript SDK 会将原生 Claude Code 二进制文件作为可选依赖打包进来，你无需再单独安装 Claude Code CLI。



![Install Command](assets/images/screenshots/install-command.png)



安装完成后，设置你的 API Key：

```bash
export ANTHROPIC_API_KEY=your-api-key
```

如果你使用云厂商的 API，SDK 也原生支持：
- **Amazon Bedrock**：设置 `CLAUDE_CODE_USE_BEDROCK=1` 并配置 AWS 凭证
- **Google Vertex AI**：设置 `CLAUDE_CODE_USE_VERTEX=1` 并配置 GCP 凭证
- **Microsoft Azure**：设置 `CLAUDE_CODE_USE_FOUNDRY=1` 并配置 Azure 凭证

### 第二步：你的第一个代理

只需几行代码，就能创建一个可以列出当前目录文件的代理：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="What files are in this directory?",
        options=ClaudeAgentOptions(allowed_tools=["Bash", "Glob"]),
    ):
        if hasattr(message, "result"):
            print(message.result)

asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "What files are in this directory?",
  options: { allowedTools: ["Bash", "Glob"] }
})) {
  if ("result" in message) console.log(message.result);
}
```

注意到 `allowed_tools` 了吗？通过它，你可以精确控制代理的权限边界。

## 实操演示：内置工具与核心能力

Agent SDK 开箱即用，提供了丰富的内置工具，覆盖了开发者的日常操作：

| 工具 | 作用 |
| --- | --- |
| **Read** | 读取工作目录中的任意文件 |
| **Write** | 创建新文件 |
| **Edit** | 对现有文件进行精确编辑 |
| **Bash** | 运行终端命令、脚本、Git 操作 |
| **Glob** | 按模式匹配查找文件 |
| **Grep** | 使用正则搜索文件内容 |
| **WebSearch** | 搜索互联网获取最新信息 |
| **WebFetch** | 抓取并解析网页内容 |

比如，你想让代理扫描代码库中所有的 TODO 注释并生成摘要：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="Find all TODO comments and create a summary",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"]),
    ):
        if hasattr(message, "result"):
            print(message.result)

asyncio.run(main())
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Find all TODO comments and create a summary",
  options: { allowedTools: ["Read", "Glob", "Grep"] }
})) {
  if ("result" in message) console.log(message.result);
}
```



![Todo Finder Agent Output](assets/images/screenshots/todo-finder-agent-output.png)



## 进阶技巧：从原型到生产

仅仅能跑通循环是不够的，生产级的代理需要更精细的控制。Agent SDK 提供了四大进阶能力：

### 1. Hooks（生命周期钩子）

在代理执行的关键节点注入自定义逻辑，比如审计、拦截或转换。以下示例在每次文件修改后记录审计日志：

```python
import asyncio
from datetime import datetime
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher

async def log_file_change(input_data, tool_use_id, context):
    file_path = input_data.get("tool_input", {}).get("file_path", "unknown")
    with open("./audit.log", "a") as f:
        f.write(f"{datetime.now()}: modified {file_path}\n")
    return {}

async def main():
    async for message in query(
        prompt="Refactor utils.py to improve readability",
        options=ClaudeAgentOptions(
            permission_mode="acceptEdits",
            hooks={
                "PostToolUse": [
                    HookMatcher(matcher="Edit|Write", hooks=[log_file_change])
                ]
            },
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)

asyncio.run(main())
```

### 2. 子代理（Subagents）

让主代理派生出专门的子代理处理聚焦任务。子代理执行完毕后会将结果汇报给主代理，消息中带有 `parent_tool_use_id` 字段方便追踪：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Use the code-reviewer agent to review this codebase",
  options: {
    allowedTools: ["Read", "Glob", "Grep", "Agent"],
    agents: {
      "code-reviewer": {
        description: "Expert code reviewer for quality and security reviews.",
        prompt: "Analyze code quality and suggest improvements.",
        tools: ["Read", "Glob", "Grep"]
      }
    }
  }
})) {
  if ("result" in message) console.log(message.result);
}
```

### 3. MCP 集成

通过模型上下文协议（MCP），你可以将代理连接到数据库、浏览器、API 等外部系统。例如接入 Playwright 实现浏览器自动化：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="Open example.com and describe what you see",
        options=ClaudeAgentOptions(
            mcp_servers={
                "playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]}
            }
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)

asyncio.run(main())
```

### 4. 会话恢复（Session Resume）

代理能够跨多次交互保持上下文。第一次查询后捕获 `session_id`，下次查询时传入即可恢复完整的对话历史和文件记忆：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

let sessionId: string | undefined;

// First query: capture the session ID
for await (const message of query({
  prompt: "Read the authentication module",
  options: { allowedTools: ["Read", "Glob"] }
})) {
  if (message.type === "system" && message.subtype === "init") {
    sessionId = message.session_id;
  }
}

// Resume with full context from the first query
for await (const message of query({
  prompt: "Now find all places that call it", // "it" = auth module
  options: { resume: sessionId }
})) {
  if ("result" in message) console.log(message.result);
}
```

## Agent SDK vs 其他工具：该怎么选？

很多开发者会问：这和我直接用 Client SDK 有什么区别？核心差异在于**谁来管理工具循环**：

```python
# Client SDK: 你自己实现工具循环
response = client.messages.create(...)
while response.stop_reason == "tool_use":
    result = your_tool_executor(response.tool_use)
    response = client.messages.create(tool_result=result, **params)

# Agent SDK: Claude 自主处理工具调用
async for message in query(prompt="Fix the bug in auth.py"):
    print(message)
```

简单来说：CLI 适合交互式开发和一次性任务，而 SDK 适合 CI/CD 流水线、自定义应用和生产自动化。很多团队的黄金路径是：**用 CLI 日常开发，用 SDK 构建生产级自动化**。

---

## 明日预告

今天我们了解了 Agent SDK 的全貌，知道了如何用代码构建具备文件操作、子代理和会话恢复能力的智能体。但在日常开发中，我们大部分时间都在 IDE 里写代码。如何将这些强大的代理能力无缝融入编辑器工作流？明天我们将深入探讨 **VS Code 集成**，看看 Claude Code 如何在你的编辑器中发挥最大威力。敬请期待！