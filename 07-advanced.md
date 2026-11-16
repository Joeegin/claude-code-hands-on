# 07 · 进阶玩法：从"一个对话"到"一个团队"

前六章用熟以后再看这一章。下面每一节都是独立的，挑你用得上的学。

---

## 1. 无头模式 `claude -p`：把 Claude 当成命令行工具

`-p` 表示执行完就退出，并且**可以接管道**。这是最被低估的功能之一。

```bash
# 分析日志
cat server.log | claude -p "找出所有 OOM 相关的报错，按时间列出，并猜测原因"

# 总结 diff
git diff main | claude -p "用 3 句话总结这次改动，指出潜在风险"

# 结构化输出，方便在脚本里用
claude -p "列出 benchkit 里所有公开函数" --output-format json | python3 -c "import json,sys; print(json.load(sys.stdin)['result'])"

# 批量处理
for f in logs/*.log; do
  claude -p "这个 benchmark 日志里 TPOT p99 是多少？只输出数字" < "$f"
done
```

几个常用参数：
- `--output-format json` / `stream-json`：给脚本解析
- `--allowedTools "Read,Grep"`：限制可用的工具（无人值守时更安全）
- `--max-budget-usd 1`：花费上限
- `--model haiku`：简单任务用更便宜、更快的模型

> 无头模式会跳过"信任此目录"的确认，只在你信任的目录里使用。

---

## 2. 后台任务：不被长命令卡住

- 编译、长时间测试、启动服务时，告诉它"放到后台运行，期间继续做 X"，或者在命令运行时按 `Ctrl+B` 把它转到后台。
- `/tasks` 查看后台运行的命令和子代理。
- `Ctrl+T` 显示它的待办清单（多步骤任务的进度）。
- `/btw 问题`：在它工作时问一个小问题，不打断主任务。只能根据已有上下文回答，不能读文件或跑命令。

```
用 10 万行数据跑一次 benchkit，放到后台。
在它运行的同时，用 cProfile 分析小数据集上的热点。两边都完成后汇总给我。
```

---

## 3. 并行：Git Worktree + 多个会话

同一个仓库，同时让两个 Claude 改不同的东西，**互不干扰**：

```bash
cd ~/benchkit-practice
claude -w fix-perf        # 终端 1：新建 worktree 和分支，在里面修性能问题
claude -w add-compare     # 终端 2：另一个 worktree，加 --compare 功能
```

- 每个 worktree 是独立的工作目录，有自己的分支，默认放在 `.claude/worktrees/<名字>/`。
- 做完后在主目录正常 `git merge`。
- 新的 worktree 是全新检出，`.gitignore` 里的文件（`.env`、大数据文件、模型权重）不会自动出现。需要的话可以在 `.worktreeinclude` 里列出要复制过去的文件。

**怎样并行才有收益：**
- ✅ 任务之间独立、改的文件不重叠
- ✅ 每个任务都有明确的验收标准（测试），你只需要最后验收
- ❌ 任务有先后依赖
- ❌ 你没有精力审查——并行 3 个任务意味着要审查 3 份 diff

**新手的实际节奏**：一个主会话做需要你思考的活，一个后台会话做"写测试 / 补文档"这类机械的活。先从 2 个开始。

> 还有 `claude --bg`（后台会话，用 `claude agents` 查看，用 `claude attach` 接入）和 Agent Teams（实验功能，多个会话之间可以互相通信）。先把 worktree 用熟。

---

## 4. 让它持续工作直到达成目标

- **`/goal 条件`**：设定一个可验证的目标，它会一轮接一轮地工作，直到条件满足。
  ```
  /goal tests/ 下所有测试通过，且 benchkit 的输出完全符合 README 规格每一条
  ```
  目标必须**能检验**。"把项目做好"不是一个目标。

- **`/loop 间隔 任务`**：在当前会话里定时重复执行。
  ```
  /loop 10m 检查 CI 状态，失败的话读日志告诉我原因；全部通过就停止
  ```
  一定要写**退出条件**。会话关闭后循环就会停止，所以它不是 cron。

---

## 5. 模型和推理强度：别所有任务都用最贵的

| 任务 | 选择 |
|---|---|
| 复杂架构设计、疑难 Bug、读大型陌生代码库 | 最强模型（Opus）+ 较高 `/effort` |
| 日常开发、写测试、一般重构 | 默认即可 |
| 简单机械的活、批量 `-p` 脚本、子代理搜索 | Sonnet / Haiku |

- `/model` 切换模型，`/effort` 调整推理强度。
- `/usage` 查看用量。
- 觉得慢时可以试试 `/fast`。

---

## 6. 大规模改动：`/batch`

跨几十个文件的机械迁移（比如把所有旧 API 调用换成新 API），`/batch` 会先调研并拆分任务，再在多个隔离的 worktree 里并行执行。小改动不要用它。

---

## 7. 云端审查：`/code-review` 和 `claude ultrareview`

- `/code-review`：在本地审查当前 diff，可以指定强度（`/code-review high`）。
- `claude ultrareview`：在云端用多个代理审查当前分支，适合重要的 PR 合并之前。

---

## 8. 把它接入团队流程

- **GitHub Actions**：在 issue 或 PR 里 `@claude`，让它自动修复或审查（在会话里运行 `/install-github-app` 设置）。
- **headless + CI**：在 CI 里用 `claude -p` 生成变更说明、检查文档是否同步。
- **共享配置**：把 `.claude/settings.json`、`.claude/skills/`、`.claude/agents/`、`CLAUDE.md` 提交到仓库。新同事 clone 下来就拥有同一套工作流。

---

## 练习

[08-练习营](08-exercises.md) 的**练习 9**。

下一章：[08 · 练习营](08-exercises.md)
