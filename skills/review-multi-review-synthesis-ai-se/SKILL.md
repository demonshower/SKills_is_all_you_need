---
name: review-multi-review-synthesis-ai-se
description: 根据同一论文的多份 review Markdown，生成一份统一、连贯、证据支持的最终审稿意见。
allowed-tools: Read, Write
---

# Multi Review Synthesis AI-SE

将多份模型生成的审稿结果整合成一份最终审稿，适合 AI / 软件工程方向的多轮审稿综合与决策支持。

## 输入
- `paper.pdf`：原论文，用于核对争议点
- `template.docx`：目标审稿模板，字段以该文件为准
- `reviews/*.md` 或若干 `review-*.md`：多个模型生成的初稿
- 可选参数：
  - `strictness`：1–5，默认 3
  - `target_rating`：指定倾向评分，若使用必须让正文理由支撑该评分
  - `output_name`：默认 `review-final.md`

## 目标
- 抽取多个 review 的共识与分歧
- 剔除误读、重复、模板化句子
- 生成一份像单个审稿人写出的统一、连贯、基于证据的最终意见

## 工作流
1. 读取 `template.docx`，确定最终输出结构和字段。
2. 读取所有初稿，抽取：
   - 共识 strengths
   - 共识 weaknesses
   - 独有但有价值的观点
   - 评分分布与分歧原因
3. 回到论文 PDF 核对关键争议，删除无依据或过度泛化的意见。
4. 合并要点时优先保留：
   - 对 acceptance 决策影响最大的技术问题
   - 可被论文证据直接支撑的问题
   - 可操作、可复现、可要求作者回应的问题
5. 根据 `strictness` 决定语气与评分。
6. 输出一份统一、连贯、无拼接痕迹的 `review-final.md`。

## 合并原则
- 不按多数票机械决定；以论文证据和顶会标准为准。
- 相同问题只写一次，并合并成更强、更具体的表述。
- 冲突观点优先保留论文原文支持的一方。
- 避免明显模板化、重复句和模型自述。
- 最终评分必须与 weaknesses 严重程度一致。
- 证据不足时，可写 “the paper does not clearly show...”，避免确定性结论。

## 输出格式
严格按模板字段输出；常见格式如下：

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

## 推荐综合策略
- Strengths：保留 3–5 个最稳定优点。
- Weaknesses：保留 5–8 个关键问题，按严重性排序。
- Review：不要逐条复述 weakness，写成自然审稿段落。
- 分数：优先取“正文证据支持的中位判断”，再按 strictness 微调。
- 最后一段明确总体立场：Reject / Weak Reject / Borderline / Weak Accept / Accept。
