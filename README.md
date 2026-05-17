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

先说结论：GitHub Copilot（VS Code / Copilot CLI / cloud agent）不会因为仓库根目录存在 `skills/` 就自动发现它；它只会从约定路径扫描 skills。

对 VS Code GitHub Copilot 来说，常见扫描位置是：

- 个人级 skills 目录：`~/.copilot/skills`（推荐只保留这一处，避免候选列表出现重复项）
- 仓库级 skills 目录：`.github/skills`
- 兼容目录：`~/.agents/skills`、`.agents/skills`、`.claude/skills`（仅在你确实需要兼容其它 agent 时再用；如果同一份 skills 同时链接到多个入口，Copilot 的候选列表可能会出现重复）

下面给出“只保留 Copilot”的推荐安装方式。

### macOS / Linux

```bash
# GitHub Copilot in VS Code / Copilot CLI
mkdir -p "$HOME/.copilot"
rm -rf "$HOME/.copilot/skills"
ln -s "<仓库绝对路径>/skills" "$HOME/.copilot/skills"
```

如果你希望“打开当前仓库时 Copilot 立刻发现 skills”，还可以在仓库根目录创建仓库级入口：

```bash
rm -rf .github/skills
mkdir -p .github
ln -s "$(pwd)/skills" .github/skills
```

### Windows

在 Windows 上推荐创建 junction。下面的命令只创建 GitHub Copilot 所需的 `%USERPROFILE%\.copilot\skills`（推荐做法：只保留这一处，避免 Copilot 候选列表出现重复）。

注意：请在 PowerShell 或 CMD 中以管理员身份运行，或确保当前账户有创建联接的权限。

#### PowerShell

```powershell
# 将下面路径替换为你本地仓库的 skills 绝对路径
$repo = 'E:\path\to\repo\skills'

$copilotDir = "$env:USERPROFILE\.copilot"
$copilotSkills = "$env:USERPROFILE\.copilot\skills"

if (-not (Test-Path $copilotDir)) {
  New-Item -ItemType Directory -Path $copilotDir | Out-Null
}

if (Test-Path $copilotSkills) {
  Remove-Item -Recurse -Force -Path $copilotSkills
}

New-Item -ItemType Junction -Path $copilotSkills -Target $repo | Out-Null

# 可选（不推荐，除非你明确需要兼容其它 agent）：
# New-Item -ItemType Junction -Path "$env:USERPROFILE\.agents\skills" -Target $repo | Out-Null
# New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills" -Target $repo | Out-Null
```

如果你想做“仓库级”安装，在仓库根目录执行：

```powershell
if (-not (Test-Path '.github')) {
  New-Item -ItemType Directory -Path '.github' | Out-Null
}

if (Test-Path '.github\skills') {
  Remove-Item -Recurse -Force '.github\skills'
}

New-Item -ItemType Junction -Path '.github\skills' -Target (Join-Path (Get-Location) 'skills') | Out-Null
```

#### CMD

```cmd
set REPO=E:\path\to\repo\skills

if not exist "%USERPROFILE%\.copilot" mkdir "%USERPROFILE%\.copilot"

if exist "%USERPROFILE%\.copilot\skills" rmdir /S /Q "%USERPROFILE%\.copilot\skills"

cmd /c mklink /J "%USERPROFILE%\.copilot\skills" "%REPO%"

rem 可选（不推荐，除非你明确需要兼容其它 agent）：
rem if not exist "%USERPROFILE%\.agents" mkdir "%USERPROFILE%\.agents"
rem if not exist "%USERPROFILE%\.claude" mkdir "%USERPROFILE%\.claude"
rem if exist "%USERPROFILE%\.agents\skills" rmdir /S /Q "%USERPROFILE%\.agents\skills"
rem if exist "%USERPROFILE%\.claude\skills" rmdir /S /Q "%USERPROFILE%\.claude\skills"
rem cmd /c mklink /J "%USERPROFILE%\.agents\skills" "%REPO%"
rem cmd /c mklink /J "%USERPROFILE%\.claude\skills" "%REPO%"
```

如果你想做“仓库级”安装，在仓库根目录执行：

```cmd
if not exist ".github" mkdir ".github"
if exist ".github\skills" rmdir /S /Q ".github\skills"
cmd /c mklink /J ".github\skills" "%CD%\skills"
```

## 删除所有 links（清理/卸载）

下面的命令用于“删除 skills 的链接入口”（symlink/junction）。它们只会删除 link 本身，不会删除你的真实 `skills/` 目录内容。

> 什么时候需要：你发现 Copilot 候选出现重复（通常是同一份 skills 被同时链接到了多个入口目录），或者你想在新机器/新环境重新验证安装流程。

### macOS / Linux

个人级（推荐清理项）：

```bash
rm -rf "$HOME/.copilot/skills"
rm -rf "$HOME/.agents/skills"
rm -rf "$HOME/.claude/skills"
```

仓库级（在你的仓库根目录执行）：

```bash
rm -rf .github/skills
rm -rf .agents/skills
rm -rf .claude/skills
```

### Windows

#### PowerShell

```powershell
$paths = @(
  "$env:USERPROFILE\.copilot\skills",
  "$env:USERPROFILE\.agents\skills",
  "$env:USERPROFILE\.claude\skills",
  ".github\skills",
  ".agents\skills",
  ".claude\skills"
)

foreach ($p in $paths) {
  if (Test-Path $p) {
    $item = Get-Item -LiteralPath $p -Force
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
      # Junction / Symlink
      [System.IO.Directory]::Delete($p)
    } else {
      Write-Host "SKIP (not a link): $p"
    }
  }
}
```

#### CMD

```cmd
rmdir /S /Q "%USERPROFILE%\.copilot\skills"
rmdir /S /Q "%USERPROFILE%\.agents\skills"
rmdir /S /Q "%USERPROFILE%\.claude\skills"
rmdir /S /Q ".github\skills"
rmdir /S /Q ".agents\skills"
rmdir /S /Q ".claude\skills"
```

## VS Code 里如何确认生效

1. 确保使用的是 GitHub Copilot Chat 的 `Agent` 模式。
2. 重启 VS Code，或执行一次 `Developer: Reload Window`。
3. 如果你做的是个人级安装，确认目标目录下确实能看到 `~/.copilot/skills/<skill-name>/SKILL.md`。
4. 如果你做的是仓库级安装，确认当前仓库存在 `.github/skills/<skill-name>/SKILL.md`。
5. 在提问时明确提到 skill 覆盖的任务，例如“帮我把这组实验数据画成论文风格图表”，观察 Copilot 是否引用对应 skill。

## 为什么候选会出现重复

最常见的原因是：你把同一份 skills 同时链接到了多个入口目录（例如同时存在 `~/.copilot/skills`、`~/.agents/skills`、`~/.claude/skills`），Copilot 的候选列表可能不会去重，于是显示多条相同 skill（推荐只保留 `~/.copilot/skills`）。

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

