---
name: pptx-pdf-export
description: 将任意 PowerPoint PPTX 高保真导出为 PDF，逐页裁剪白边，并在画质要求内尽量减小文件体积。适用于整份演示文稿、指定页或逐页独立导出。
---

# PPTX 高保真 PDF 导出

使用本 skill 处理 PPTX→PDF、自动裁剪白边、保留原图像素或控制导出体积的请求。默认导出**整份 PPTX 为一个 PDF**；只有用户要求时才选择页码或拆成独立文件。随附的 [导出脚本](scripts/pptx2pdf_lossless.py) 在 Windows 上通过 PowerPoint 保留文字和矢量对象，再用 PPTX 中的原始图片像素替换被 PowerPoint 降采样的图片。每页根据文字、图形和图片的边界单独裁剪，输出使用无损 Flate 压缩。

## 运行条件

- Windows、Microsoft PowerPoint、Python 3.11。
- Python 包：`pymupdf`、`Pillow`、`pywin32`。

## 导出流程

1. 确定用户要整份 PDF、指定页组成一个 PDF，还是每页各一个 PDF；确认输出位置和可接受的体积或画质要求。源 PPTX 的文字、章节号和图形内容保持原样。
2. 优先用脚本的默认高保真模式生成候选 PDF。默认导出全部幻灯片，`--slides` 仅在需要选择页码时使用。白边裁剪默认留 2 pt 安全边距；需要更紧时调整 `--margin` 并检查边缘。不要把裁剪视为显著缩小文件体积的方法。
3. 检查每页是否完整、文字是否清晰、图形与图片是否错位、页面比例和裁剪边缘是否合适，并核对页数、可提取文字及脚本报告中的图片替换和未匹配数量。
4. 记录文件大小。若高保真 PDF 过大，先尝试不改变像素的 PDF 优化；仍过大时，可用 `--no-replace` 生成较小的 PowerPoint 原生候选，按实际使用尺寸比较文字、细线、截图和照片。只选择满足用户画质要求的最小候选；有明确无损要求时保留原图像素版本。必要的有损压缩或降采样应依据用户给定的体积与画质目标决定。
5. 在候选 PDF 验证完成后再替换已有文件。报告页数、裁剪尺寸、体积及采用的画质方案。

## 命令

```powershell
# 整份 PPTX，逐页裁白边，保留原图像素
py -3.11 "<skill目录>\scripts\pptx2pdf_lossless.py" "<输入>.pptx" -o "<输出>.pdf"

# 仅导出指定的连续页到一个 PDF
py -3.11 "<skill目录>\scripts\pptx2pdf_lossless.py" "<输入>.pptx" -o "<输出>.pdf" --slides 2-5 --margin 1

# 体积优先时生成对照候选；需与高保真版本比较后决定
py -3.11 "<skill目录>\scripts\pptx2pdf_lossless.py" "<输入>.pptx" -o "<候选>.pdf" --no-replace
```

若用户要求逐页独立文件，对需要的每一页分别使用 `--slides N` 和不同输出路径。不要假定页数固定。
