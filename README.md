# Skills_is_all_you_need

一个面向 AI / 软件工程方向研究生的 Vibe Coding Agent skill 集合，包含论文审稿与审稿综合流程的规范化 Skill 文档。

## 使用方式

1. 在 Windows 命令行中创建目录联接：

```cmd
cmd /c mklink /J "%USERPROFILE%\.agents\skills" "<仓库目录>\SKills_is_all_you_need\skills"

cmd /c mklink /J "%USERPROFILE%\.codex\skills" "<仓库目录>\Skills_is_all_you_need\skills"
```

2. 之后在 Vibe Coding Agent 中即可直接调用以下 skill，例如：
   - `/paper-figure-workflow`
   - `/paper-progress-audit`

3. 若要移除联接，只需删除 `%USERPROFILE%\.agents\skills` 目录，不影响仓库内容。

