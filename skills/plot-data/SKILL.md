---
name: plot-data
description: 根据用户提供的实验数据、统计数据或表格数据，生成高质量科研可视化图表。当用户提到"画图"、"可视化"、"绘制"、"统计图"、"折线图"、"柱状图"、"散点图"、"热力图"、"科研图"、"数据图"、"帮我看看这个数据"时触发。即使用户只是粘贴了数据，也应主动建议可视化。
allowed-tools: Bash, Write
---

# Plot Data — 科研数据可视化

生成达到期刊投稿标准的高质量数据可视化图表。

---

## 核心原则

**你是一个有审美的科研绘图专家。** 不要等用户告诉你用什么颜色、什么风格——你应该主动做出最好的选择。每张图都应该达到 Nature/Science 子刊的视觉标准。

---

## 第一步：理解数据

从用户输入提取：
- 数据的**科学含义**（不只是数字，要理解它代表什么）
- 变量关系（时间序列？分组比较？相关性？分布？）
- 是否有误差/标准差/置信区间

**图表类型选择逻辑：**

| 数据特征 | 推荐图表 |
|---------|---------|
| 时间/连续变量趋势 | 折线图（带置信区间阴影） |
| 2-6 组均值比较 | 柱状图 + 误差棒 + 散点叠加 |
| 多组分布形态 | 小提琴图 或 箱线图 |
| 两变量相关 | 散点图 + 回归线 + R²/p值 |
| 多变量相关矩阵 | 热力图（下三角） |
| 占比/构成 | 环形图（不用饼图） |
| 高维数据降维 | PCA/UMAP 散点图 |
| 生存分析 | Kaplan-Meier 曲线 |
| 基因/蛋白表达 | 热力图 + 聚类树 |

---

## 第二步：生成代码

### 全局样式基础（每张图都要用）

```python
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib import rcParams

# ── 字体与基础样式 ──────────────────────────────────────────
rcParams.update({
    # 字体
    'font.family':        'sans-serif',
    'font.sans-serif':    ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size':          11,
    'axes.titlesize':     13,
    'axes.labelsize':     12,
    'xtick.labelsize':    10,
    'ytick.labelsize':    10,
    'legend.fontsize':    10,

    # 线条
    'axes.linewidth':     1.0,
    'xtick.major.width':  1.0,
    'ytick.major.width':  1.0,
    'xtick.major.size':   4,
    'ytick.major.size':   4,
    'lines.linewidth':    2.0,

    # 去掉上/右边框（半开放坐标轴）
    'axes.spines.top':    False,
    'axes.spines.right':  False,

    # 背景
    'axes.facecolor':     'white',
    'figure.facecolor':   'white',

    # 图例
    'legend.frameon':     False,
    'legend.borderpad':   0.4,

    # 输出
    'figure.dpi':         150,
    'savefig.dpi':        300,
    'savefig.bbox':       'tight',
    'savefig.pad_inches': 0.05,
})
```

### 配色方案（按场景选择）

```python
# ── 科研配色方案 ────────────────────────────────────────────

# 方案1：Nature 风格（2-5组，最常用）
NATURE_COLORS = ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F', '#8491B4']

# 方案2：Cell 风格（暖色系）
CELL_COLORS   = ['#D62728', '#FF7F0E', '#2CA02C', '#1F77B4', '#9467BD', '#8C564B']

# 方案3：冷色系（适合对照组/实验组）
COOL_COLORS   = ['#2166AC', '#4DAC26', '#D01C8B', '#F1B6DA', '#B8E186', '#92C5DE']

# 方案4：单色渐变（同一变量不同水平）
import matplotlib.cm as cm
SEQUENTIAL    = cm.Blues   # 或 cm.Reds, cm.Greens, cm.Purples

# 方案5：发散型（热力图，中心为0）
DIVERGING     = 'RdBu_r'   # 或 'coolwarm', 'bwr'

# 方案6：色盲友好（8色）
COLORBLIND    = ['#0072B2', '#E69F00', '#009E73', '#CC79A7',
                 '#56B4E9', '#D55E00', '#F0E442', '#000000']

# 默认使用 NATURE_COLORS，除非数据特征更适合其他方案
```

### 图表模板库

#### A. 柱状图 + 误差棒 + 数据点叠加（最常用）
```python
fig, ax = plt.subplots(figsize=(5, 4.5))

groups = [...]   # 分组名
means  = [...]   # 均值
sems   = [...]   # 标准误（或标准差）
data_points = [[...], [...], ...]  # 原始数据点（可选）

colors = NATURE_COLORS[:len(groups)]
x = np.arange(len(groups))

# 柱子
bars = ax.bar(x, means, width=0.55, color=colors, alpha=0.85,
              edgecolor='white', linewidth=0.8, zorder=2)

# 误差棒
ax.errorbar(x, means, yerr=sems, fmt='none', color='#333333',
            capsize=4, capthick=1.2, elinewidth=1.2, zorder=3)

# 叠加原始数据点（增加可信度）
for i, pts in enumerate(data_points):
    jitter = np.random.normal(0, 0.06, len(pts))
    ax.scatter(x[i] + jitter, pts, color='#333333', s=18,
               alpha=0.6, zorder=4, linewidths=0)

# 显著性标注
def significance_bar(ax, x1, x2, y, p):
    stars = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
    h = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.03
    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.0, color='#333333')
    ax.text((x1+x2)/2, y+h*1.1, stars, ha='center', va='bottom', fontsize=10)

ax.set_xticks(x)
ax.set_xticklabels(groups)
ax.set_ylabel('Value (unit)')
ax.set_title('Title', pad=10, fontweight='bold')
ax.set_ylim(bottom=0)

plt.tight_layout()
plt.savefig('output.png')
plt.show()
```

#### B. 折线图 + 置信区间阴影
```python
fig, ax = plt.subplots(figsize=(7, 4))

for i, (label, x, y, ci) in enumerate(series):
    color = NATURE_COLORS[i]
    ax.plot(x, y, color=color, linewidth=2.2, label=label,
            marker='o', markersize=5, markerfacecolor='white',
            markeredgewidth=1.8, markeredgecolor=color, zorder=3)
    # 置信区间阴影
    ax.fill_between(x, np.array(y)-ci, np.array(y)+ci,
                    color=color, alpha=0.15, zorder=2)

ax.legend(loc='best', handlelength=1.5)
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_title('Title', pad=10, fontweight='bold')

# 添加网格（淡）
ax.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig('output.png')
plt.show()
```

#### C. 散点图 + 回归线
```python
from scipy import stats

fig, ax = plt.subplots(figsize=(5, 5))

# 散点
ax.scatter(x, y, color=NATURE_COLORS[0], s=40, alpha=0.7,
           edgecolors='white', linewidths=0.5, zorder=3)

# 回归线 + 置信区间
slope, intercept, r, p, _ = stats.linregress(x, y)
x_line = np.linspace(min(x), max(x), 200)
y_line = slope * x_line + intercept

# 置信区间（bootstrap 或解析）
n = len(x)
se = np.sqrt(np.sum((y - (slope*np.array(x)+intercept))**2) / (n-2))
ci = 1.96 * se * np.sqrt(1/n + (x_line - np.mean(x))**2 / np.sum((np.array(x)-np.mean(x))**2))

ax.plot(x_line, y_line, color=NATURE_COLORS[0], linewidth=2, zorder=4)
ax.fill_between(x_line, y_line-ci, y_line+ci,
                color=NATURE_COLORS[0], alpha=0.15, zorder=2)

# 统计信息
p_str = f'p < 0.001' if p < 0.001 else f'p = {p:.3f}'
ax.text(0.05, 0.92, f'R² = {r**2:.3f}\n{p_str}',
        transform=ax.transAxes, fontsize=10,
        verticalalignment='top',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                  edgecolor='#cccccc', alpha=0.8))

ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_title('Title', pad=10, fontweight='bold')
ax.set_aspect('equal', adjustable='box')  # 如果x/y同单位

plt.tight_layout()
plt.savefig('output.png')
plt.show()
```

#### D. 热力图（相关矩阵）
```python
import seaborn as sns

fig, ax = plt.subplots(figsize=(7, 6))

# 只显示下三角
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)

sns.heatmap(corr_matrix, mask=mask, cmap='RdBu_r', center=0,
            vmin=-1, vmax=1, square=True, linewidths=0.5,
            linecolor='white', annot=True, fmt='.2f',
            annot_kws={'size': 9},
            cbar_kws={'shrink': 0.8, 'label': 'Pearson r'},
            ax=ax)

ax.set_title('Correlation Matrix', pad=12, fontweight='bold')
plt.tight_layout()
plt.savefig('output.png')
plt.show()
```

#### E. 小提琴图 + 箱线图叠加
```python
fig, ax = plt.subplots(figsize=(6, 5))

parts = ax.violinplot(data_list, positions=range(len(groups)),
                      showmeans=False, showmedians=False, showextrema=False)

for i, pc in enumerate(parts['bodies']):
    pc.set_facecolor(NATURE_COLORS[i])
    pc.set_alpha(0.7)
    pc.set_edgecolor('none')

# 叠加箱线图
bp = ax.boxplot(data_list, positions=range(len(groups)),
                widths=0.12, patch_artist=True,
                medianprops=dict(color='white', linewidth=2),
                boxprops=dict(facecolor='#333333', alpha=0.8),
                whiskerprops=dict(color='#333333'),
                capprops=dict(color='#333333'),
                flierprops=dict(marker='o', markersize=3,
                                markerfacecolor='#999999', alpha=0.5))

ax.set_xticks(range(len(groups)))
ax.set_xticklabels(groups)
ax.set_ylabel('Value (unit)')
ax.set_title('Distribution Comparison', pad=10, fontweight='bold')

plt.tight_layout()
plt.savefig('output.png')
plt.show()
```

#### F. 多子图布局
```python
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
# 或 fig, axes = plt.subplots(2, 2, figsize=(9, 8))

# 子图间距
plt.subplots_adjust(wspace=0.35, hspace=0.4)

# 子图标签 (a) (b) (c)
for i, ax in enumerate(axes.flat):
    ax.text(-0.12, 1.05, f'({chr(97+i)})', transform=ax.transAxes,
            fontsize=13, fontweight='bold', va='top')

plt.savefig('output.png')
plt.show()
```

---

## 第三步：执行

1. 将完整脚本写入 `/tmp/plot_<描述性名称>.py`
2. 执行：`python3 /tmp/plot_<name>.py`
3. 如果报错（缺包等），自动修复后重试
4. 告知用户图片保存路径

---

## 第四步：主动提供优化建议

执行成功后，根据图表类型主动提示：
- 是否需要添加显著性标注（p值/星号）
- 是否需要导出 PDF/SVG（论文投稿用）
- 是否需要调整图幅尺寸（单栏 ~88mm，双栏 ~180mm）
- 是否需要多子图拼图

---

## 中文支持

如果标签含中文，在样式设置中加入：
```python
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False
```

---

## 质量检查清单

生成代码前，确认：
- [ ] 坐标轴有单位标注
- [ ] 图例清晰（如有多组）
- [ ] 颜色对色盲友好（默认用 NATURE_COLORS 或 COLORBLIND）
- [ ] 字体大小适合印刷（≥10pt）
- [ ] 误差棒类型已标注（SEM / SD / 95% CI）
- [ ] 统计检验结果已标注（如有）
- [ ] 保存 DPI ≥ 300
