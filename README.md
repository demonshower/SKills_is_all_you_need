# Skills_is_all_you_need

一个面向 AI / 软件工程方向研究生的 Vibe Coding Agent skill 集合，覆盖论文写作、审稿、科研可视化、代码理解等常见工作流。

## Skills 一览

这套 skills 主要覆盖 4 类高频任务：科研图表与论文配图、论文阅读与审稿、代码理解与编码约束、以及 skill 自举创建。下面的表格列出了仓库当前包含的全部 skills，方便按工作流快速挑选。

| Skill | 说明 |
|-------|------|
| `plot-data` | 基于 matplotlib/seaborn 生成符合 Nature/Science 期刊标准的科研数据可视化 |
| `paper-figure-workflow` | 从 LaTeX、代码和规划文档生成/刷新完整的论文配图集 |
| `paper-progress-audit` | 对比文档、论文声明、代码实现与测试，生成科研项目进度审计报告 |
| `paper-translator` | 面向论文精读场景的英↔中学术翻译，附术语表与难点注释 |
| `review-quick-review-ai-se` | 阅读论文 PDF 并按模板生成 AI/SE 会议标准审稿意见 |
| `review-multi-review-synthesis-ai-se` | 将多份 AI 生成的审稿意见综合为一份统一终审报告 |
| `code-explain` | 自顶向下地向初学者解释代码结构与逻辑 |
| `karpathy-guidelines` | 约束编码过程不过度设计、只做外科手术式修改，并要求可验证成功标准 |
| `create-skill` | 交互式创建新的 Claude Code skill，生成标准 SKILL.md |

## 安装与使用

### macOS / Linux

```bash
REPO_SKILLS="$(pwd)/skills"
mkdir -p "$HOME/.agents"
rm -f "$HOME/.copilot/skills" "$HOME/.agents/skills"
ln -s "$REPO_SKILLS" "$HOME/.agents/skills"
```

如需给 Claude 使用，再单独执行：

```bash
REPO_SKILLS="$(pwd)/skills"
mkdir -p "$HOME/.claude"
rm -f "$HOME/.claude/skills"
ln -s "$REPO_SKILLS" "$HOME/.claude/skills"
```

### Windows

在 Windows 上推荐创建 junction。

注意：请在 CMD 中运行下面命令；如果你之前按旧文档创建过 `.copilot\skills`，下面的命令会先删掉旧 link，避免重复。

#### CMD

```cmd
set "REPO_SKILLS=%CD%\skills"
if not exist "%USERPROFILE%\.agents" mkdir "%USERPROFILE%\.agents"
if exist "%USERPROFILE%\.copilot\skills" rmdir "%USERPROFILE%\.copilot\skills"
if exist "%USERPROFILE%\.agents\skills" rmdir "%USERPROFILE%\.agents\skills"
mklink /J "%USERPROFILE%\.agents\skills" "%REPO_SKILLS%"
```

如需给 Claude 使用，再单独执行：

```cmd
if not exist "%USERPROFILE%\.claude" mkdir "%USERPROFILE%\.claude"
if exist "%USERPROFILE%\.claude\skills" rmdir "%USERPROFILE%\.claude\skills"
mklink /J "%USERPROFILE%\.claude\skills" "%CD%\skills"
```

## 删除所有 links（清理/卸载）

下面的命令只删除 link 本身，不会删除真实的 `skills/` 目录内容。

### macOS / Linux

```bash
[ -L "$HOME/.copilot/skills" ] && rm "$HOME/.copilot/skills"
[ -L "$HOME/.agents/skills" ] && rm "$HOME/.agents/skills"
[ -L "$HOME/.claude/skills" ] && rm "$HOME/.claude/skills"
```

### Windows

#### CMD

```cmd
if exist "%USERPROFILE%\.copilot\skills" rmdir "%USERPROFILE%\.copilot\skills"
if exist "%USERPROFILE%\.agents\skills" rmdir "%USERPROFILE%\.agents\skills"
if exist "%USERPROFILE%\.claude\skills" rmdir "%USERPROFILE%\.claude\skills"
```

## 贡献

欢迎提交新的 skill！可以使用 `/create-skill` 交互式生成标准模板，然后提 PR 即可。

