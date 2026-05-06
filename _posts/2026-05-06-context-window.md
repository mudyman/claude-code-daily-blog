---
layout: post
title: "Claude Code 隐形战场：彻底搞懂上下文窗口的生存法则"
date: 2026-05-06
topic: context-window
categories: [daily-digest]
tags: [claude-code, context-window]
description: "你是否遇到过这种情况：用 Claude Code 开发到一半，它突然像失忆了一样，忘了之前的约定，甚至开始胡言乱语？这往往不是 AI 变笨了，而是**上下文窗口（Context Window）**被塞满了。"
---

# Claude Code 隐形战场：彻底搞懂上下文窗口的生存法则

你是否遇到过这种情况：用 Claude Code 开发到一半，它突然像失忆了一样，忘了之前的约定，甚至开始胡言乱语？这往往不是 AI 变笨了，而是**上下文窗口（Context Window）**被塞满了。

对于开发者而言，上下文窗口就是 AI 的“短期记忆”。每一次文件读取、每一句对话，都在默默消耗这块宝贵的空间。理解它的运作机制，是从“会用”到“精通” Claude Code 的关键分水岭。今天，我们就来扒一扒这个隐形战场的生存法则。

## 关键概念：上下文里到底装了什么？

Claude Code 的上下文窗口不仅包含你在终端里看到的输入和输出，还隐藏了大量你未必察觉的信息。一个真实的会话生命周期是这样的：

1. **启动前（你没敲键盘时）**：`CLAUDE.md`、自动记忆（auto memory）、MCP 工具名称以及技能（skill）描述，已经悄悄加载到了上下文中。如果你还配置了输出风格（output style）或使用了 `--append-system-prompt`，它们也会作为系统提示词占据一席之地。
2. **工作中**：Claude 每读取一个文件，上下文就会增加；带有 `paths:` 作用域的规则会随着匹配文件自动加载；每次编辑后，`PostToolUse` 钩子（hook）也会触发。
3. **后续提示**：当你让 Claude 去调研时，子代理（subagent）会在**独立的上下文窗口**中工作，只有最终的摘要和小部分元数据会返回到你的主窗口，从而保护了主上下文不被海量文件读取撑爆。



![Context Window Timeline Simulation](assets/images/screenshots/context-window-timeline-simulation.png)



## 实操演示：压缩（Compaction）后的记忆大逃杀

当会话过长，上下文即将耗尽时，Claude Code 会执行压缩（`/compact`），用结构化的摘要替换冗长的对话历史。但这不是简单的“浓缩”，而是一场残酷的“记忆大逃杀”——不同机制加载的内容，命运截然不同：

| 机制 | 压缩后的命运 |
| :--- | :--- |
| 系统提示词和输出风格 | **不变**；不属于消息历史，不受影响 |
| 项目根目录的 CLAUDE.md 和无作用域规则 | 从磁盘**重新注入** |
| 自动记忆（Auto memory） | 从磁盘**重新注入** |
| 带有 `paths:` frontmatter 的规则 | **丢失**，直到再次读取匹配的文件 |
| 子目录中的嵌套 CLAUDE.md | **丢失**，直到再次读取该子目录的文件 |
| 调用过的技能体（Skill bodies） | **重新注入**，但每个技能上限 5000 tokens，总计上限 25000 tokens；超出时优先丢弃最旧的 |
| 钩子（Hooks） | **不适用**；作为代码运行，不占上下文 |

**实战避坑指南**：
- **关键规则别用 `paths:`**：如果你有一条极其重要的规则必须贯穿整个长会话，千万别加 `paths:` 作用域限制，否则一压缩就没了。把它移到项目根目录的 `CLAUDE.md` 中才是稳妥之举。
- **技能文件头重脚轻**：因为技能体重新注入时有 token 上限，且截断时**保留文件开头**，所以写 `SKILL.md` 时，务必把最核心的指令放在文件最前面！



![Compact Command Output](assets/images/screenshots/compact-command-output.png)



## 进阶技巧：掌控你的上下文

文档里的模拟数据仅供参考，想要精准掌控你的上下文，你需要这两把“手术刀”：

1. **实时监控**：随时输入 `/context`，你会看到按类别划分的实时上下文占用情况，甚至还有优化建议。
2. **记忆检查**：输入 `/memory`，确认启动时到底加载了哪些 `CLAUDE.md` 和自动记忆文件，避免无用信息偷偷吃掉你的额度。



![Context Usage Breakdown](assets/images/screenshots/context-usage-breakdown.png)



在日常开发中，**管理上下文就是管理你的主要约束条件**。把上下文当成你电脑的内存：不要同时打开几百个不用的标签页，该用子代理隔离的任务就隔离，该清理的冗余记忆就清理。保持上下文的“清爽”，Claude Code 才能始终保持敏锐。

## 明日预告

今天我们提到了子代理（subagent）能在独立上下文中处理调研任务，从而保护主窗口。但这只是它能力的冰山一角。如何优雅地委派任务？子代理还能解决哪些架构难题？明天我们将深入探讨 **子代理** 的奇妙用法，敬请期待！