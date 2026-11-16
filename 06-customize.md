# 06 · 定制你的 Claude：一次投入，天天受益

前几章讲的是"怎么用"，这一章讲"怎么让它越用越顺手"。这是高手和普通用户拉开差距的地方。

> 本章所有配置的**完整可用版本**都在 [`examples/.claude/`](examples/.claude/)。
> 先读懂，再在练习里**让 Claude 帮你写**——这本身就是练习。

## 先搞清楚：五样东西各管什么

| 东西 | 一句话 | 谁来执行 | 例子 |
|---|---|---|---|
| **CLAUDE.md** | 长期的项目说明 | 它读了以后**参考** | "测试命令是 pytest -q" |
| **权限规则** | 哪些操作自动允许、哪些禁止 | 系统**强制** | 允许 pytest，禁止 git push |
| **Skill（技能）** | 可复用的工作流程 | 它按步骤**执行** | `/ship`：自审 → 测试 → 提交 |
| **Subagent（子代理）** | 有专门职责的独立助手 | 独立上下文中执行 | 只审查、不改代码的 reviewer |
| **Hook（钩子）** | 某个事件发生时**必定**运行的脚本 | 系统**强制** | 每次改完 .py 自动跑测试 |
| **MCP** | 连接外部系统 | 作为新工具提供 | 连接数据库、Jira、浏览器 |

判断用哪个：
- "希望它知道" → CLAUDE.md
- "必须这样，不能例外" → 权限 / Hook
- "这套流程我每周做好几次" → Skill
- "这件事需要独立的视角或者大量阅读" → Subagent

---

## 1. 权限：减少弹窗，但不放弃控制

被反复弹窗打断是效率杀手。解决办法是**精确授权**，而不是关掉所有确认。

**最简单的办法：** 弹窗时选"不再询问"，规则会自动保存。或者用 `/permissions` 查看和管理。

**手写配置**（`.claude/settings.json`，提交到 git 和团队共享）：

```json
{
  "permissions": {
    "allow": [
      "Bash(python -m pytest *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)"
    ],
    "ask":  ["Bash(git commit *)"],
    "deny": ["Bash(git push *)", "Bash(rm -rf *)", "Read(./.env)"]
  }
}
```

- `allow`：直接执行；`ask`：每次都问；`deny`：直接拒绝（优先级最高）。
- 个人偏好放 `.claude/settings.local.json`（不提交），全局偏好放 `~/.claude/settings.json`。
- 内置的 `/fewer-permission-prompts` 会分析你的历史记录，自动推荐一批只读命令加进白名单。用一段时间之后跑一次。

**分层原则：**

| 操作 | 建议 |
|---|---|
| 读文件、搜索、git status/diff/log | 放开 |
| 跑单元测试、lint、格式化 | 放开（写具体命令） |
| 编辑项目内文件 | 熟悉之后用 accept edits 模式 |
| 删除、git commit | 询问 |
| git push、部署、改生产数据、长时间占用 GPU | 禁止，或者每次都由你亲自确认 |

> ⚠️ `--dangerously-skip-permissions` 只在**没有重要数据的隔离容器**里用。不要在你的主力 WSL 上用它来"提效"。

---

## 2. Skill：把你的工作流程封装成命令

当你发现自己第三次打出同一段长 prompt 时，就该把它变成 Skill。

**结构：** `.claude/skills/<名字>/SKILL.md`（项目级）或 `~/.claude/skills/<名字>/SKILL.md`（所有项目通用）。

```markdown
---
name: ship
description: 提交前的自审与提交流程。用户说"收尾""提交""ship"时使用。
disable-model-invocation: true
---

# 收尾并提交
按顺序执行，任何一步失败都停下来报告：
1. git status / git diff，确认没有无关改动
2. 运行 python -m pytest -q
3. 用 spec-reviewer 子代理独立审查 diff
4. 有问题就修完回到第 2 步；没有问题就写中文 commit message 并提交
5. 汇报结果。不要 push。

附加说明：$ARGUMENTS
```

使用：`/ship` 或 `/ship 这次只改了文档，跳过审查`（`$ARGUMENTS` 会被替换成后面这段文字）。

要点：
- **`description` 决定它什么时候自动使用这个 Skill**。写清楚"什么情况下用"。
- `disable-model-invocation: true` 表示只能由你手动 `/ship` 触发——**有副作用的流程（比如提交）建议加上**。
- Skill 目录里可以放脚本、模板、参考文档，在 SKILL.md 中引用即可。用到时才会加载，不占常驻上下文。
- **先手动跑通几次，再封装。** 不要把一次性的 prompt 做成 Skill。

**适合做成 Skill 的场景**（以 LLM 推理工程为例）：分析 benchmark 结果、审查 CUDA kernel 改动、对比上游 PR、核对笔记中的源码引用、每天的学习记录模板。

---

## 3. Subagent：给它配几个专职助手

**内置的子代理**（不用配置，它会自动使用，你也可以点名）：
- **Explore**：快速只读搜索代码库
- **Plan**：计划模式下做调研
- **general-purpose**：通用任务

**自定义：** `.claude/agents/<名字>.md`

```markdown
---
name: spec-reviewer
description: 对照 README 规格严格审查代码改动。代码修改完成后、提交前使用。只审查不修改。
tools: Read, Grep, Glob, Bash
model: sonnet
---

你是一名严格的代码审查者……（具体审查方法、输出格式）
```

- `tools` 限制它能用的工具（审查者不需要 Edit）。
- `model` 可以选更便宜、更快的模型来做简单任务。
- 使用：`用 spec-reviewer 审查当前改动`，或者在输入框里输入 `@` 选择这个 agent。
- 也可以直接让 Claude 帮你写："帮我创建一个子代理，专门……"

**什么时候值得用子代理：**
- ✅ 需要大量阅读，但你只要结论（保护主上下文）
- ✅ 需要独立视角（审查者不应该是作者本人）
- ✅ 多个方向互相独立，可以并行调查
- ❌ 简单的小任务——委派和汇总都有成本

---

## 4. Hook：必须执行的事，交给系统而不是交给"自觉"

CLAUDE.md 里写"改完代码要跑测试"，它**大多数时候**会照做。Hook 能保证它**每次都**跑。

**例 1：每次编辑 .py 文件后自动跑测试，失败了让它看到**

`.claude/settings.json`：
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/run_tests.sh\"" }
        ]
      }
    ]
  }
}
```

`.claude/hooks/run_tests.sh`：
```bash
#!/usr/bin/env bash
event=$(cat)                                  # Claude Code 通过 stdin 传入事件 JSON
case "$event" in *'.py"'*) ;; *) exit 0 ;; esac   # 只对 .py 文件生效
cd "$CLAUDE_PROJECT_DIR" || exit 0
if out=$(python3 -m pytest -q -x 2>&1); then exit 0; fi
echo "$out" | tail -n 20 >&2                  # stderr 会反馈给 Claude
exit 2                                         # 退出码 2 = 要求 Claude 处理这个问题
```

**例 2：禁止修改测试数据**（PreToolUse 在工具执行**之前**运行，exit 2 会阻止这次操作）

见 [`examples/.claude/hooks/protect_data.py`](examples/.claude/hooks/protect_data.py)。

**退出码规则：**
- `0`：正常，继续
- `2`：阻止（PreToolUse）或者把问题反馈给 Claude（PostToolUse），stderr 的内容会发给 Claude
- 其他：非阻塞错误，只显示给你看

**其他常用事件**：`UserPromptSubmit`（你提交 prompt 时）、`Stop`（它准备结束回答时，可以检查"真的做完了吗"）、`Notification`（需要你操作时，可以接桌面通知）、`SessionStart`。

**建议：**
- Hook 要**快**（几秒以内）。全量测试、GPU 测试不要放进 Hook。
- 新写的 Hook 先手动测试：`echo '{"tool_input":{"file_path":"x.py"}}' | bash run_tests.sh; echo $?`
- `/hooks` 可以查看当前生效的 Hook。
- 不想自己写 JSON？直接说"帮我配一个 hook：每次编辑 python 文件后跑 ruff"——内置的 update-config skill 会帮你写。

---

## 5. MCP：连接外部系统

MCP 让它能使用新的工具，比如操作浏览器、查询数据库、读写 Jira 或 Notion。

```bash
claude mcp add <名字> -- <启动命令>              # 本地进程型（stdio）
claude mcp add --transport http <名字> <URL>     # 远程服务
claude mcp list
```

会话里用 `/mcp` 查看状态、登录认证。

**原则：本地有命令行工具就优先用命令行。** 比如 GitHub 用 `gh` 就够了（它天然会用）。每个 MCP 服务的工具描述都会占用上下文，而且第三方 MCP 意味着你把数据交给了第三方代码——只装你信任的。

---

## 6. 插件：一次装好一整套

插件 = Skill + 子代理 + Hook + MCP 的打包。用 `/plugin` 浏览和安装。团队可以把自己的工作流打包成插件分发。先把上面几样用熟，再考虑插件。

---

## 7. 顺手的小设置

- `/config`：主题、默认模型、**输出风格**（output style）。学习阶段可以试试 **Explanatory**（边做边解释原因）或 **Learning**（会留一些代码让你自己写）。
- `/statusline`：在底部显示模型、git 分支、上下文用量等。
- `~/.claude/CLAUDE.md` 里写你的个人偏好，例如：
  ```markdown
  - 用中文回复
  - 我在 WSL Ubuntu 上开发，主要用 Python 和 C++
  - 解释时优先给出 文件:行号
  ```

---

## 练习

[08-练习营](08-exercises.md) 的**练习 7、8**。

下一章：[07 · 进阶玩法](07-advanced.md)
