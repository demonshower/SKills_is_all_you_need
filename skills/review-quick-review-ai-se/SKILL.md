---
name: review-quick-review-ai-se
description: 读取论文 PDF 与审稿模板 Word，生成一份符合模板字段的审稿结果，避免机械复读和无依据结论。
allowed-tools: Read, Write
---

# Quick Paper Review AI-SE

帮助你根据 `paper.pdf`、`template.docx` 和可选 `example.docx` 生成标准化审稿 `.md`，适合 AI / 软件工程方向的论文审稿模拟与快速评估。

## 输入
- `paper.pdf`：待审论文
- `template.docx`：审稿模板，字段以该文件为准
- 可选：`example.docx`：已填写审稿示例，仅用于学习格式、信息量、语气
- 可选参数：
  - `model_name`：输出文件名，格式为 `review-<model_name>.md` 和 `review-<model_name>-cn.md`。
  - `strictness`：1–5，默认 3；数字越高，审稿越严格

## 目标
- 先读取模板，抽取必填字段、评分项目、选项和规则
- 再通读论文，记录研究问题、方法、实验、结果和潜在局限
- 输出2份自然、克制、内容具体、符合模板字段的审稿 Markdown，一份英文，一份对应的中文。

## 工作流
1. 先读取 `template.docx`，明确输出字段、评分项和评分规则。
2. 阅读论文 PDF，整理：
   - 研究问题与任务设定
   - 方法核心设计与新颖性
   - 实验设置、数据集、baseline、评价指标
   - 主要结果、作者 claim
   - 局限性、未验证 claim、可重复性与公平性问题
3. 如有 `example.docx`，仅学习其格式和信息密度，不复用原句。
4. 根据 `strictness` 调整 weakness 的数量与表达强度。
5. 按照模板字段输出 Markdown，不输出多余段落。

## 审稿原则
- 仅基于论文内容判断，不引用论文外事实。
- 避免空泛评价，weakness 必须具体且可操作。
- rating 与正文结论一致，不能正文强拒但评分接收。
- 默认 `Best Paper Candidate` 为 No，除非贡献、实验、写作均明显优秀。
- 不输出“作为 AI”“我无法”等元话语。

## 输出格式
严格按模板字段输出；若模板字段不同，以模板为准。常见格式如下：

```md
# ACM MM Review

## Strengths*
- ...

## Weaknesses*
- ...

## Review*
...

## Fit*
Score: X

## Fit Justification*
...

## Technical Quality*
Score: X (...)

## Technical Presentation*
Score: X (...)

## Rating*
Score: X (...)

## Confidence*
Score: X (...)

## Best Paper Candidate*
No/Yes. ...
```

## 推荐写法
- Strengths：3–6 条，围绕问题重要性、方法设计、实验结果、分析完整性、会议相关性。
- Weaknesses：strictness=2 时 4–6 条；strictness=4/5 时 6–9 条。
- Review：先概括论文，再评价贡献，最后集中讨论关键不足，并给出总体判断。
- 各评分后用一句话解释。
