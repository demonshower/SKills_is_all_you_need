# Skills_is_all_you_need

一个面向 AI / 软件工程方向研究生的 Vibe Coding Agent skill 集合，覆盖论文写作、审稿、科研可视化、代码理解等常见工作流。

## Skills 一览

| Skill | 说明 |
|-------|------|
| `plot-data` | 基于 matplotlib/seaborn 生成符合 Nature/Science 期刊标准的科研数据可视化 |
| `paper-figure-workflow` | 从 LaTeX、代码和规划文档生成/刷新完整的论文配图集 |
| `paper-progress-audit` | 对比文档、论文声明、代码实现与测试，生成科研项目进度审计报告 |
| `review-quick-review-ai-se` | 阅读论文 PDF 并按模板生成 AI/SE 会议标准审稿意见 |
| `review-multi-review-synthesis-ai-se` | 将多份 AI 生成的审稿意见综合为一份统一终审报告 |
| `code-explain` | 自顶向下地向初学者解释代码结构与逻辑 |
| `create-skill` | 交互式创建新的 Claude Code skill，生成标准 SKILL.md |

## 安装与使用

将本仓库的 `skills` 目录链接到 Agent 工具的 skills 搜索路径即可。根据你的操作系统选择对应方式：

### macOS / Linux

```bash
# Claude Code
ln -s "<仓库绝对路径>/skills" "$HOME/.claude/skills"

# Agents（如适用）
ln -s "<仓库绝对路径>/skills" "$HOME/.agents/skills"

# Codex（如适用）
ln -s "<仓库绝对路径>/skills" "$HOME/.codex/skills"
```

### Windows (CMD)

```cmd
cmd /c mklink /J "%USERPROFILE%\.claude\skills" "<仓库目录>\skills"

cmd /c mklink /J "%USERPROFILE%\.agents\skills" "<仓库目录>\skills"

cmd /c mklink /J "%USERPROFILE%\.codex\skills" "<仓库目录>\skills"
```

### Windows (PowerShell)

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills" -Target "<仓库目录>\skills"

New-Item -ItemType Junction -Path "$env:USERPROFILE\.agents\skills" -Target "<仓库目录>\skills"

New-Item -ItemType Junction -Path "$env:USERPROFILE\.codex\skills" -Target "<仓库目录>\skills"
```

> 移除链接只需删除对应的符号链接/联接目录，不会影响仓库内容。

## 调用示例

在支持 skill 的 Vibe Coding Agent 中直接使用斜杠命令：

```
/plot-data
/paper-figure-workflow
/paper-progress-audit
/review-quick-review-ai-se
/code-explain
```

## 贡献

欢迎提交新的 skill！可以使用 `/create-skill` 交互式生成标准模板，然后提 PR 即可。

