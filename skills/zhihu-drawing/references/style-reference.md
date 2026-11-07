# 参考来源与通用提示词

## 首要视觉参考

本目录的 [approved-style.png](approved-style.png) 是用户在对话中明确认可的成图，主题为多 GPU 节点通过 InfiniBand 传输 KV cache。它由图像生成工具绘制，随本技能保存，后续不依赖临时文件或原对话即可查看。

可迁移的特征：纯白背景；灰色的大分组框；浅蓝设备模块；浅绿数据块或辅助模块；深色轮廓；灰色普通连接；绿色主传输箭头；少量粗体英文标签；整体对齐、疏朗。

图中的两个节点、每侧四块 GPU、HBM、PCIe、IB HCA、IB Switch 和 GPUDirect RDMA 都属于该示例的内容，不是技能的通用要求。该图是简化数据路径示意，也不是所有 GPU 服务器的物理拓扑。

## 用户提供的链接

- [知乎参考链接](https://zhuanlan.zhihu.com/p/647191585)
- 生成首张参考图时，该网页未能成功加载。因此，本技能记录的是用户认可的实际成图，不声称已复刻、检查或提取知乎原图的视觉规范。
- 链接仅保留为设计背景；使用本技能不需要反复访问。用户后续提供原图或要求对照链接时，再检查可访问内容。

## 通用风格提示词

将方括号替换为当前任务内容，删除不适用部分。使用英文标签与否由当前请求决定。

```text
Create a minimal technical schematic explaining [one specific relationship].
Use the attached approved diagram as a visual style reference only.

Pure white background, flat 2D textbook illustration, generous whitespace.
Simple rounded rectangles with consistent dark charcoal outlines.
Use light blue for primary components, restrained pastel colors for secondary
components, and gray rounded enclosures for meaningful groups.
Use thin gray lines for secondary connections and a single accent color for
the main data flow, with unmistakable arrowheads and connected endpoints.
Keep repeated components visually consistent and align them neatly.

Required entities: [entities and containment].
Required connections: [source, intermediate components, destination, direction].
Exact short labels: [labels].
Layout: [layout appropriate to the current system].
Text language: [English / Chinese / bilingual, as requested].

Very little text: a short title, component names, and essential link labels.
Keep the topology and semantics accurate; simplify decoration, not required
components or connections. No extra labels, invented specifications, logos,
photorealism, 3D rendering, decorative effects, or explanatory paragraphs.
```

原参考图的视觉重点是“分组内的少量模块 + 一条易追踪的主路径”。其他主题可以借用这种信息组织方式，也可以换成纵向、树状或多节点布局。
