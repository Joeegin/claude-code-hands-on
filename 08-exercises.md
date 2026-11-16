# 08 · 练习营

## 准备

在本仓库根目录运行一次：

```bash
./setup.sh                  # 把 practice/ 复制到 ~/benchkit-practice，初始化 git，初始状态打标签 start
```

**每个练习开始前，从干净的初始状态开一个新分支：**

```bash
cd ~/benchkit-practice
git switch -c ex3 start     # ex3 换成练习编号；已存在就换个名字
```

## 自动验收

本仓库带了一个验收脚本，用独立的参考实现检查 benchkit 是否**真的**符合规格：

```bash
python3 <本仓库路径>/grader/check.py ~/benchkit-practice          # 正确性
python3 <本仓库路径>/grader/check.py ~/benchkit-practice --perf   # 加上 10 万行性能检查
```

> ⚠️ 验收脚本里就是标准答案。**不要**让 Claude 读它，也不要把它的输出之外的内容给 Claude 看。
> 练习目录放在仓库外面，就是为了让 Claude 在练习时碰不到它。
> 你可以把验收脚本的**输出**贴给 Claude（或用 `!` 运行它）——这就是"给它验证方式"的真实体验。

练习的重点不是"把 Bug 修好"，而是**练习指挥方式**。每个练习后面都有"复盘问题"，请认真回答。

> 🙈 **不要提前看文末答案**，也不要自己先去读代码找 Bug。

---

## 练习 1 · 探索（对应 02 章）｜10 分钟

1. 在 `practice/` 里启动 `claude`。
2. 只用**一句话**让它解释这个项目，要求它不改代码。
3. 用 `Ctrl+O` 看它调用了哪些工具。
4. 用 `!` 运行 `python -m benchkit data/sample.jsonl`，然后**不复制报错**，让它解释原因。
5. 用 `@README.md` 问它：规格里哪一条你觉得最容易被实现错？

**复盘：** 它读文件的顺序和你自己会读的顺序一样吗？

---

## 练习 2 · 闭环 + 打断 + 回退（对应 02 章）｜15 分钟

1. 让它"运行程序并修到能正常输出"，要求符合 README 规格。
2. 它修复过程中按一次 `Esc`，补充一句要求（比如"每个修复都加一个测试"），然后让它继续。
3. 修完以后用 `/diff` 查看改动。
4. 用 `Esc Esc`（或 `/rewind`）回退到最开始，`! git status` 确认代码已经恢复。

**复盘：** 程序"能正常输出"了，就说明结果正确吗？运行一下验收脚本看看。（提示：有些 Bug 不会导致崩溃。）

---

## 练习 3 · Prompt 对比实验（对应 03 章）｜20 分钟

同一个任务，用两种方式各做一次，比较结果。

**A 分支（`git switch -c ex3a start`）**，只说：
```
metrics.py 有 bug，帮我修一下
```

**B 分支（`git switch -c ex3b start`，先 `/clear`）**，用四要素写：
```
目标：让 benchkit/metrics.py 的所有计算都符合 @README.md 的"指标规格"第 1、2、5、6 条。
方法：每条规格先写一个能暴露问题的测试（tests/test_metrics.py），确认失败后再修实现。
边界：不要修改 parser.py 和 report.py；不要修改已有测试。
验收：python -m pytest -q 全部通过；最后列出你修了哪几处、每处对应哪条规格。
```

对比两个分支：`git diff ex3a ex3b --stat`，并在两个分支上分别运行验收脚本。

**复盘：**
- A 修了几个问题？B 呢？
- 哪个分支你更有把握"真的修对了"？为什么？
- B 的 prompt 你写了多久？节省了多少后续审查时间？

---

## 练习 4 · TDD 修剩下的 Bug（对应 04 章）｜20 分钟

在 B 分支的基础上继续（`git switch ex3b`）。

还有两条规格没有处理：**第 3 条（错误率与失败请求）** 和 **第 4 条（重复 id 取最后一次）**。

1. 第一轮 prompt：只写测试，确认测试失败，**不准修改实现**。
2. 检查测试是否真的表达了规格（这一步是你的工作）。
3. 第二轮 prompt：修改实现让测试通过，**不准修改测试**。
4. 运行验收脚本。目标：正确性全部 ✅。

**复盘：** 第 2 步里你发现测试有问题了吗？如果跳过第 2 步会怎样？

---

## 练习 5 · 计划模式做新功能（对应 04 章）｜25 分钟

在修好 Bug 的分支上做（`git switch -c ex5 ex3b`）。

1. 用 `/plan` 或者 `Shift+Tab` 进入计划模式。
2. 先用"访谈"句式：`我想加一个对比两份日志、发现性能回退的功能。先问我 5 个关键问题。`
3. 回答它的问题，然后让它出方案。
4. **审查方案**：至少提出一条修改意见（哪怕是"这一步不需要"）。
5. 批准执行，切到 accept edits 模式。
6. 验证：`python -m benchkit data/after_upgrade.jsonl --compare data/sample.jsonl`（参数形式按你们定的方案来）。

**复盘：** 它问的 5 个问题里，有哪个是你自己没想到的？

---

## 练习 6 · CLAUDE.md 与上下文（对应 05 章）｜15 分钟

1. `/init` 生成 CLAUDE.md。
2. **删减到 15 行以内**：逐行问"删掉这行它会犯错吗？"
3. 确保写进以下规则：README 规格是唯一需求来源；只用标准库；`data/big.jsonl` 不能整个读入。
4. `/context` 看看 CLAUDE.md 占了多少。
5. `/clear` 之后问："这个项目修 Bug 的规矩是什么？"——确认新会话知道这些规则。
6. 做一个"让 CLAUDE.md 生长"的动作：故意让它犯一个错，然后让它把教训写进 CLAUDE.md。

**复盘：** `/init` 生成的内容里，有哪些是"它自己看代码也能知道"的废话？

---

## 练习 7 · 写你的第一个 Skill 和子代理（对应 06 章）｜25 分钟

1. 让 Claude **帮你**创建一个 `spec-reviewer` 子代理（只审查不修改，对照 README 规格）。
2. 让它**帮你**创建 `/ship` skill（检查改动 → 测试 → 用 spec-reviewer 审查 → 提交，不 push）。
3. 在练习 5 的分支上运行 `/ship`。
4. 和 [`examples/.claude/`](examples/.claude/) 里的参考版本对比，看看差别。

**复盘：** spec-reviewer 有没有发现真实的问题？有没有误报？

---

## 练习 8 · Hook（对应 06 章）｜20 分钟

1. 让 Claude 帮你配置两个 Hook（或者从 `examples/.claude/` 复制过来）：
   - PreToolUse：禁止编辑 `data/*.jsonl`
   - PostToolUse：编辑 `.py` 文件后自动跑测试，失败时反馈给 Claude
2. **先手动测试 Hook 脚本**（`echo '{...}' | python3 ... ; echo $?`）。
3. 让它"把 data/sample.jsonl 里的第一条记录删掉"，观察它被阻止。
4. 让它故意改坏 `metrics.py` 里的一个函数，观察测试 Hook 把失败反馈给它，以及它的反应。
5. `/hooks` 查看生效的配置。

**复盘：** 哪些规则适合放在 CLAUDE.md（建议），哪些必须放在 Hook（强制）？

---

## 练习 9 · 进阶组合（对应 07 章）｜30 分钟

**9a 性能：**
```bash
python scripts/gen_data.py -n 100000 -o data/big.jsonl
time python -m benchkit data/big.jsonl
```
按 04 章的"性能套路"让它优化：先 profile → 只改最大的瓶颈 → 对比前后耗时。要求优化后结果和优化前**完全一致**（可以让它对比两次的 JSON 输出）。最后用 `check.py --perf` 验收。

**9b 并行：** 开两个终端：
```bash
claude -w perf      # 做 9a
claude -w csv       # 加一个 --format csv 输出
```
两边都完成后，在主目录合并两个分支。

**9c 无头模式：**
```bash
python -m benchkit data/sample.jsonl --format json > /tmp/a.json
python -m benchkit data/after_upgrade.jsonl --format json > /tmp/b.json
cat /tmp/a.json /tmp/b.json | claude -p "第一份是基线，第二份是升级后。哪些指标退化了？最可能是 prefill 还是 decode 出了问题？说明推理依据。"
```

**复盘：** 并行两个会话时，你的注意力够用吗？瓶颈在哪里？

---

## 练习 10 · 毕业：用在你的真实项目上

这才是真正的练习。挑一个你手头真实的仓库：

- [ ] 写一份 ≤ 30 行的 CLAUDE.md
- [ ] 配置权限白名单，把常用的只读命令和测试命令加进去
- [ ] 用"探索"套路搞懂一个你之前没看懂的模块
- [ ] 用"计划"套路完成一个真实需求
- [ ] 把你重复最多的一段 prompt 封装成 Skill
- [ ] 记录一周：每个任务你和它来回了几轮？你手动干预了几次？下一周对比一下

> 效率指标不是"它写了多少代码"，而是"**相同质量下，你花的注意力少了多少**"。

---

<details>
<summary>📖 答案：benchkit 里埋的问题（做完练习再看）</summary>

| # | 位置 | 问题 | 对应规格 | 表现 |
|---|---|---|---|---|
| 1 | `metrics.summarize` | 没有过滤 `status=="error"` 的请求，`first_token` 为 `None` | 第 3 条 | 崩溃：`TypeError` |
| 2 | `metrics.percentile` | `s[int(n*p/100)]` 不是 nearest-rank，p100 越界 | 第 5 条 | 崩溃：`IndexError`；其他分位数有偏差 |
| 3 | `metrics.tpot` | 除以 `output_tokens` 而不是 `output_tokens-1`；而且没有排除 `output_tokens<=1` 的请求 | 第 2 条 | 数值偏小；**正确修成 -1 之后**，如果没有排除 `output_tokens==1`，会出现除零 |
| 4 | `metrics.throughput` | 分母用每个请求耗时之和，而不是墙钟时间 | 第 6 条 | 数值严重偏小（并发越高越离谱） |
| 5 | `report.dedupe` | 保留第一次出现的记录而不是最后一次 | 第 4 条 | 不崩溃，结果有偏差 |
| 6 | `report.dedupe` | `id in list` 是 O(n²) | 性能 | 10 万行时明显变慢 |
| 7 | 整体 | 没有错误率输出 | 第 3 条 | 缺功能 |

**几个值得注意的点：**
- Bug 1、2 会崩溃，"修到能跑"就能发现；Bug 3、4、5 **不会崩溃**，只有对照规格写测试才能发现。这就是"给它验证方式"的意义。
- Bug 3 有陷阱：只改分母不处理边界，会引出新的崩溃。好的测试应该覆盖 `output_tokens == 1`。
- 修 Bug 1 时，如果直接在加载时丢掉 error 请求，错误率（第 3 条）就没法算了。把过滤放在哪里，是一个设计决策。
- 修 Bug 6 时，如果用 `dict` 的方式不对，可能会把 Bug 5 的行为一起改掉（或者恰好修好）——这就是为什么性能优化要求"结果完全一致"，以及为什么最好先修正确性、再优化性能。

</details>
