# Claude Code 高效上手手册

> 写给：有一定编程基础、已经"用过"Claude Code，但感觉自己只是在"跟它聊天"，而别人在"指挥它干活"的工程师。
>
> 基于 Claude Code 2.1.x 编写（2026-11）。命令细节以 `/help` 和[官方文档](https://code.claude.com/docs)为准。
>
> 这是一份社区学习材料，与 Anthropic 官方无关。

**特点：** 不罗列功能，而是边读边练。配套一个**故意埋了 Bug 的练习项目**和一个**自动验收脚本**，你练的不是"修 Bug"，而是"怎么指挥 agent 把 Bug 修对"。

## 快速开始

```bash
git clone https://github.com/Joeegin/claude-code-hands-on.git
cd claude-code-hands-on
./setup.sh                       # 准备练习项目到 ~/benchkit-practice（需要 python3、git）
```

然后从 [01-心智模型](01-mindset.md) 开始读，读到 [02](02-quickstart.md) 时打开练习项目动手。

需要：已安装 [Claude Code](https://code.claude.com/docs)、Python 3.9+、git；练习里的测试需要 `pip install pytest`。

## 为什么别人用得比你好？

差距通常不是"会不会写 prompt"，而是这三件事：

1. **心智模型不同**：你把它当"更聪明的搜索框/补全"，他们把它当"一个能自己跑命令、读代码、验证结果的同事"。
2. **工作流不同**：你一句话让它写完；他们让它 *先探索 → 再计划 → 再写 → 自己验证*。
3. **环境投资不同**：他们花过半小时写 `CLAUDE.md`、配权限、写几个自定义命令，之后每天都在吃红利。

这份手册就按这三件事组织。

## 学习路线（建议 1 周，每天 30~60 分钟）

| 天 | 读 | 练 | 你会得到 |
|---|---|---|---|
| D1 | [01-心智模型](01-mindset.md) + [02-30分钟上手](02-quickstart.md) | 练习 1、2 | 敢放手让它干活，知道基本操作 |
| D2 | [03-怎么下指令](03-prompting.md) | 练习 3 | 一次说清楚，少返工 |
| D3 | [04-核心工作流](04-workflows.md) | 练习 4、5 | 探索-计划-实现-验证 的闭环 |
| D4 | [05-上下文管理](05-context.md) | 练习 6 | 长任务不"变笨"，会写 CLAUDE.md |
| D5 | [06-定制你的 Claude](06-customize.md) | 练习 7、8 | 自定义命令 / 子代理 / Hook |
| D6 | [07-进阶玩法](07-advanced.md) | 练习 9 | 并行、无头模式、脚本化 |
| D7 | 把以上用在**你真实的工作项目**上 | — | 形成自己的习惯 |

- 练习题在 [08-练习营](08-exercises.md)，配套练习项目在 [`practice/`](practice/)。
- 随时查：[速查表 cheatsheet](00-cheatsheet.md)。

## 目录结构

```
claude-code-hands-on/
├── README.md            ← 你在这里
├── 00-cheatsheet.md     速查表
├── 01-mindset.md        心智模型
├── 02-quickstart.md     30 分钟上手（纯动手）
├── 03-prompting.md      怎么下指令
├── 04-workflows.md      五个核心工作流
├── 05-context.md        上下文管理 & CLAUDE.md
├── 06-customize.md      权限 / Skill / 子代理 / Hook / MCP
├── 07-advanced.md       无头模式 / 并行 / 后台 / 模型选择
├── 08-exercises.md      10 个练习 + 答案
├── setup.sh             把练习项目复制到独立目录并初始化 git
├── practice/            练习项目 benchkit 的模板（埋了 Bug，别直接在这里改）
├── grader/check.py      自动验收脚本（含标准答案，别给 Claude 看）
└── examples/.claude/    第 06 章配置的参考答案（settings.json、hooks、skills、agents）
```

## 怎么用这份手册（Meta 技巧）

**用 Claude Code 来学 Claude Code。** 在本仓库目录启动它：

```bash
cd claude-code-hands-on
claude
```

然后可以直接问：

- "读一下 04-workflows.md，给我讲讲套路 ③ 的要点"
- "我对 05 里的 /compact 和 /clear 区别还是不太懂，结合例子讲讲"
- "出 5 道题考考我对 06 的掌握程度"

不懂某个功能时，也可以直接问它："Claude Code 的 hooks 怎么配？"——它内置了查询自身文档的能力。

> 注意：在本仓库里启动的 Claude 能看到 `grader/` 里的答案。**做练习时请在 `~/benchkit-practice` 里启动**。

## 只记一句话

> **给它目标 + 上下文 + 验证方式，然后让它自己跑闭环；你负责审查和决策。**

## 贡献

发现内容过时、命令变化或有更好的练习设计，欢迎提 Issue / PR。修改练习项目后请确认：

```bash
./setup.sh /tmp/bk && python3 grader/check.py /tmp/bk   # 模板版本应当验收失败（Bug 还在）
```

## License

[MIT](LICENSE)
