---
name: plot-data
description: 根据用户提供的实验数据、统计数据或表格数据，生成 Python 绘图代码（Matplotlib/Seaborn），并直接执行输出图片。当用户提到"画图"、"可视化"、"绘制"、"统计图"、"折线图"、"柱状图"、"散点图"、"热力图"、"科研图"、"数据图"时触发。即使用户只是粘贴了一段数据并说"帮我看看"，也应主动建议使用此 skill。
allowed-tools: Bash, Write
---

# Plot Data

将用户提供的数据生成高质量的科研/统计可视化图表。

## 工作流程

### 第一步：理解数据和需求

从用户输入中提取：
- **数据内容**：数值、表格、CSV、JSON 或自然语言描述的数据
- **图表类型**（如未指定，根据数据特征自动选择）：
  - 时间序列 / 趋势 → 折线图
  - 分类比较 → 柱状图
  - 分布 → 直方图 / 箱线图 / 小提琴图
  - 相关性 → 散点图 / 热力图
  - 占比 → 饼图 / 环形图
  - 多变量 → 配对图 / 平行坐标
- **输出要求**：标题、轴标签、图例、颜色风格、文件名

如果数据不清晰，先询问用户澄清，不要猜测数据含义。

### 第二步：生成绘图代码

生成完整可运行的 Python 脚本，遵循以下规范：

**科研风格（默认）：**
```python
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

# 科研风格设置
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 12,
    'axes.linewidth': 1.2,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})
```

**代码要求：**
- 数据直接硬编码在脚本中（不依赖外部文件）
- 包含清晰的中文/英文标签（根据用户语言）
- 颜色使用色盲友好的调色板（如 `tab10`、`Set2`、`colorblind`）
- 保存为 PNG 文件，同时调用 `plt.show()`
- 如需 Seaborn，在 import 时检查并给出安装提示

### 第三步：执行并输出

1. 将脚本写入临时文件 `/tmp/plot_<name>.py`
2. 用 `python3` 执行
3. 告知用户图片保存路径
4. 如果执行报错，自动修复后重试一次

### 第四步：提供调整建议

执行成功后，主动提示用户可以调整的方向：
- 图表类型、配色、字体大小
- 添加误差棒、显著性标注（`*`、`**`、`***`）
- 导出为 SVG/PDF（适合论文投稿）
- 多子图布局

## 常用模板

### 带误差棒的柱状图（科研常用）
```python
fig, ax = plt.subplots(figsize=(6, 4))
groups = ['Control', 'Treatment A', 'Treatment B']
means = [2.3, 4.1, 3.7]
stds = [0.3, 0.5, 0.4]
colors = ['#4878CF', '#6ACC65', '#D65F5F']
bars = ax.bar(groups, means, yerr=stds, capsize=5,
              color=colors, alpha=0.85, edgecolor='black', linewidth=0.8)
ax.set_ylabel('Value (unit)')
ax.set_title('Group Comparison')
plt.tight_layout()
plt.savefig('output.png')
```

### 多组折线图（时间序列）
```python
fig, ax = plt.subplots(figsize=(8, 4))
for label, (x, y) in data.items():
    ax.plot(x, y, marker='o', linewidth=2, markersize=5, label=label)
ax.legend(frameon=False)
ax.set_xlabel('Time')
ax.set_ylabel('Value')
plt.tight_layout()
plt.savefig('output.png')
```

## 注意事项

- 优先使用 Matplotlib，Seaborn 用于统计分布类图表
- 中文标签需要设置中文字体：`plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']`
- 论文投稿图建议 `dpi=300`，`format='pdf'` 或 `format='svg'`
- 不要生成交互式图表（如 Plotly），除非用户明确要求
