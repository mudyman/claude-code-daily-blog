---
layout: post
title: "每日博客：揭秘 Claude Code 的文件系统——你的 AI 助手是如何记忆与思考的？"
date: 2026-05-17
topic: claude-directory
categories: [daily-digest]
tags: [claude-code, claude-directory]
description: "你有没有想过，为什么 Claude Code 在某些项目里仿佛拥有“读心术”，完全懂你的代码规范，而在另一些项目里却像个刚入职的新人？秘密全藏在它的目录结构里。理解 Claude Code 的文件系统，就如同掌握了这位 AI 助手的“大脑结构”。今天，我们就来拆解 `.claude` 目录，看看如何精准地给它植入记忆、"
---

# 每日博客：揭秘 Claude Code 的文件系统——你的 AI 助手是如何记忆与思考的？

你有没有想过，为什么 Claude Code 在某些项目里仿佛拥有“读心术”，完全懂你的代码规范，而在另一些项目里却像个刚入职的新人？秘密全藏在它的目录结构里。理解 Claude Code 的文件系统，就如同掌握了这位 AI 助手的“大脑结构”。今天，我们就来拆解 `.claude` 目录，看看如何精准地给它植入记忆、设定规矩，让它真正成为懂你项目的专属搭档。

## 关键概念：项目级 vs 全局级

Claude Code 的配置文件分布在两个核心位置：

1. **项目目录（`.claude/` 或项目根目录）**：这里的配置跟随代码仓库，提交到 Git 后可以和整个团队共享。比如项目特有的代码规范、MCP 服务器配置。
2. **全局目录（`~/.claude/`）**：这是你的私人领地，配置对所有项目生效。比如你的个人快捷键、主题偏好。

简单来说：**团队共识放项目，个人习惯放全局**。另外，大多数开发者日常只需关注 `CLAUDE.md` 和 `settings.json`，其他都是按需添加的可选配置。



![Directory Tree Explorer](assets/images/screenshots/directory-tree-explorer.png)



## 实操演示：找到配置的正确归属

面对这么多文件，到底该改哪个？官方给了一个极其清晰的对照表，我们来挑几个最实用的场景看看：

| 你想要... | 应该编辑的文件 | 作用域 |
| :--- | :--- | :--- |
| 给 Claude 提供项目上下文和规范 | `CLAUDE.md` | 项目或全局 |
| 允许或拦截特定的工具调用 | `settings.json` 中的 `permissions` 或 `hooks` | 项目或全局 |
| 在工具调用前后运行脚本 | `settings.json` 中的 `hooks` | 项目或全局 |
| 添加用 `/name` 调用的提示词或能力 | `skills/<name>/SKILL.md` | 项目或全局 |
| 定义拥有专属工具的子代理 | `agents/*.md` | 项目或全局 |
| 保持个人覆盖配置不进入 Git | `settings.local.json` | 仅项目 |

**避坑指南**：如果你想覆盖某个配置但不想提交到代码库，千万别改 `settings.json`，用 `settings.local.json`，它会被自动忽略。如果你有私密的项目级偏好，可以手动创建 `CLAUDE.local.md` 并加入 `.gitignore`。

## 进阶技巧：明文存储与数据清理

除了你手动编写的配置，`~/.claude` 还存储了 Claude Code 工作时产生的数据：对话记录、提示历史、文件快照等。**这里有一个极其重要的安全提示：这些记录是明文存储的，没有加密！** 如果工具读取了包含密钥的 `.env` 文件，这些敏感信息会被写入 `projects/<project>/<session>.jsonl`。

为了降低敏感信息暴露风险，你可以：
- 缩短 `cleanupPeriodDays`（默认 30 天自动清理），减少记录保留时间。
- 设置环境变量 `CLAUDE_CODE_SKIP_PROMPT_HISTORY` 来跳过写入对话记录。
- 使用权限规则拒绝 Claude 读取凭证文件。

当项目终结，或者你想彻底清理历史痕迹时，不要去手动删文件，Claude Code 提供了专用的清理命令。

先预览清理计划（不实际删除）：

```bash
claude project purge ~/work/my-repo --dry-run
```

确认后执行删除（会有确认提示）：

```bash
claude project purge ~/work/my-repo
```

如果你要在脚本中使用，可以跳过确认提示：

```bash
claude project purge ~/work/my-repo --yes
```

如果你想清理所有项目的状态，可以使用 `--all` 参数；如果想一步步审查删除计划，加上 `-i` 参数进入交互模式。

## 明日预告

今天我们深入探讨了 Claude Code 的目录结构与数据存储，特别提到了明文存储带来的潜在风险。那么，在企业环境中，如何确保 AI 编程助手的使用不触碰法律红线？组织又如何强制推行安全合规的配置？明天我们将带来**《法律与合规》**，揭秘企业级的安全管控机制，敬请期待！