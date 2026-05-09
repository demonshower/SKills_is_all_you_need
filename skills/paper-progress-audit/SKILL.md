---
name: progress-audit
description: Generate a research-project progress audit by comparing local docs, paper LaTeX claims, repository implementation, tests, and current completion devlog.
agent: agent
---

# Research Progress Audit / 项目完成度评估

你现在要为当前 VS Code workspace 生成一份“项目完成度评估与下一步推进计划”文档。

这个任务的目标不是写代码，也不是泛泛总结，而是基于当前仓库的真实材料，生成一份可以指导下一阶段研发和论文推进的中间状态文档。

## 你必须读取和对齐的材料

优先检查以下位置；如果不存在，就在报告中标注“未找到”，不要编造：

1. `_docs/`、`docs/`、`paper/`、`papers/`、`tex/`、`manuscript/` 等目录下的需求文档、设计文档、bug taxonomy、evaluation plan、README。
2. `.tex` 论文文件，尤其是：
   - Abstract
   - Introduction
   - Contributions
   - Method
   - Evaluation
   - RQ / Table / Figure placeholders
   - `\pending`、`TODO`、`TBD`、`placeholder`
3. 当前代码仓库：
   - `src/`
   - `tools/`
   - `scripts/`
   - `tests/`
   - `examples/`
   - `configs/`
   - `requirements*`
   - `pyproject.toml` / `package.json` / `setup.py` 等
4. Git 当前状态：
   - 当前分支
   - 最近若干 commit
   - untracked / modified 文件
5. 测试与实验痕迹：
   - test 文件
   - logs
   - output
   - results
   - artifacts
   - benchmark / evaluation scripts

如果可用，请使用代码搜索、文件读取和终端命令；但不要进行大规模破坏性操作，不要修改业务代码。

## 输出位置

默认生成或更新：

`_docs/devlog/YYYY-MM-DD_progress_audit.md`

如果 `_docs/devlog/` 不存在，可以创建。

同时可生成或更新：

`_docs/devlog/latest_progress_audit.md`

作为最新状态软副本。

## 分析原则

1. 严格区分“论文中声明的贡献”“文档中规划的需求”“代码中已经实现的内容”“尚未验证的内容”“完全缺失的内容”。
2. 不要因为文件存在就判定完成。必须判断是否有实质逻辑、是否有端到端测试、是否能支撑论文实验。
3. 对每个判断尽量给出证据路径，例如文件路径、函数名、类名、测试脚本名、LaTeX section 名称。
4. 不要添油加醋，不要替项目发明不存在的功能。
5. 如果不能确定，标注为“待验证”，不要写成已完成。
6. 输出语言使用中文；技术术语保留必要英文。
7. 文档应紧凑、工程化、面向下一步执行，不要写成宣传稿。

## 推荐输出结构

# 项目开发进度评估与下一步推进计划

更新时间：YYYY-MM-DD  
当前仓库：repo name  
当前分支：branch name  
评估范围：docs / tex / code / tests / results

## 一、最终目标回顾

简要说明当前项目/论文的最终目标。

如果 `.tex` 中声明了贡献，必须列出论文贡献，并标注来源文件。

格式建议：

1. Contribution 1：……
2. Contribution 2：……
3. Contribution 3：……

然后给出一句判断：

> 当前仓库距离论文目标最核心的差距在于：……

## 二、当前实现完成度评估

### 2.1 按论文贡献维度评估

用表格输出：

| 论文贡献 | 对应文档/章节 | 对应代码模块 | 状态 | 证据 | 主要缺口 |
|---|---|---|---|---|---|

状态使用：

- ✅ 完成
- 🔶 结构完成但待验证
- 🟠 部分实现
- 🔴 缺失
- ⚪ 未找到证据

### 2.2 按代码模块评估

用表格输出：

| 模块 | 文件/目录 | 状态 | 实质逻辑判断 | 测试情况 | 风险 |
|---|---|---|---|---|---|

重点判断：
- 是否只是 wrapper / stub
- 是否有真实算法逻辑
- 是否有 schema 但没有执行闭环
- 是否有工具脚本但没有 evaluation result
- 是否有论文声称但代码未支撑

### 2.3 按实验与论文可发表性评估

用表格输出：

| 论文需要的证据 | 当前是否存在 | 缺失内容 | 优先级 |
|---|---|---|---|

必须检查：
- baseline 是否存在
- ablation 是否存在
- main result 是否存在
- dataset/corpus 是否稳定
- bug/failure 是否可复现
- analysis scripts 是否存在
- table/figure 是否仍为 placeholder

### 2.4 总体完成度估算

给出类似：

```text
基础设施 / 数据结构 / 适配层        ████████░░  80%
核心算法 / agent / RL / planning   ███░░░░░░░  30%
Oracle / evaluation / validation   ████░░░░░░  40%
论文实验与结果                    ██░░░░░░░░  20%

综合：距 paper-ready 约 XX%