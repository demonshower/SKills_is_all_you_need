# -*- coding: utf-8 -*-
"""
pptx2pdf_lossless.py — high-fidelity PPTX→PDF converter for publication figures.

Why not just "Save As PDF"?
    PowerPoint's native PDF export re-samples every embedded image to ~150–220
    ppi, so screenshots and logos end up visibly compressed.  This tool takes
    a different route:

    - it exports layout/vectors/text through PowerPoint COM (print intent),
    - then replaces each down-sampled image XObject in that PDF with the
      *original, untouched* pixel data extracted directly from the .pptx zip,
      honouring PowerPoint's effect layers (a14:imgLayer, e.g. background
      removal carried in .wdp files) and source crops (a:srcRect),
    - and finally sets every page's CropBox to the tight content bounding
      box (images + drawings + text) plus a small margin, so the figure PDF has
      no surrounding white margin.

Requirements (Windows):
    - Microsoft PowerPoint installed (COM automation)
    - py -3.11 -m pip install pymupdf Pillow pywin32
    - PowerShell 5.1 (built-in on Windows) for .wdp → .png decoding

Usage:
    py -3.11 pptx2pdf_lossless.py figure.pptx
    py -3.11 pptx2pdf_lossless.py figure.pptx -o out.pdf --slides 1 --margin 1.0
"""

import argparse
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import zipfile
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# dependency check
# ---------------------------------------------------------------------------
def _ensure_imports() -> None:
    import importlib

    missing = []
    for mod, pkg, hint in [
        ("pymupdf", "pymupdf", "pip install pymupdf"),
        ("PIL", "Pillow", "pip install Pillow"),
        ("win32com.client", "pywin32", "pip install pywin32"),
    ]:
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append(f"  {pkg}  ({hint})")
    if missing:
        sys.exit(
            "Missing Python packages:\n"
            + "\n".join(missing)
            + "\n\nInstall with:\n"
            + "    py -3.11 -m pip install pymupdf Pillow pywin32"
        )


# ---------------------------------------------------------------------------
# .wdp (HD Photo / JPEG XR) → .png via PowerShell 5.1 + WPF
# ---------------------------------------------------------------------------
_HELPER_PS1: Optional[Path] = None


def _wdp_helper_script() -> Path:
    """Materialize the small PowerShell helper that decodes .wdp with WIC/WPF."""
    global _HELPER_PS1
    if _HELPER_PS1 is None:
        h = tempfile.NamedTemporaryFile(
            mode="w", suffix=".ps1", delete=False, encoding="utf-8"
        )
        h.write(
            textwrap.dedent(
                """\
                param([Parameter(Mandatory=$true)][string]$ListFile)
                Add-Type -AssemblyName PresentationCore, WindowsBase
                Get-Content -LiteralPath $ListFile | ForEach-Object {
                    $p = $_.Trim()
                    if (-not $p) { return }
                    $parts = $p -split '\\|', 2
                    $inp = $parts[0]; $outp = $parts[1]
                    try {
                        $fs = [System.IO.File]::OpenRead($inp)
                        $dec = New-Object System.Windows.Media.Imaging.WmpBitmapDecoder(
                            $fs,
                            [System.Windows.Media.Imaging.BitmapCreateOptions]::PreservePixelFormat,
                            [System.Windows.Media.Imaging.BitmapCacheOption]::OnLoad
                        )
                        $frame = $dec.Frames[0]
                        $enc = New-Object System.Windows.Media.Imaging.PngBitmapEncoder
                        $enc.Frames.Add([System.Windows.Media.Imaging.BitmapFrame]::Create($frame))
                        $ofs = [System.IO.File]::Create($outp)
                        $enc.Save($ofs)
                        $ofs.Close(); $fs.Close()
                    } catch {
                        Write-Error "FAIL|$inp|$_"
                    }
                }
                """
            )
        )
        h.close()
        _HELPER_PS1 = Path(h.name)
    return _HELPER_PS1


def decode_wdp_batch(pairs: List[Tuple[Path, Path]]) -> None:
    """Decode a batch of (src.wdp, dst.png) pairs in one PowerShell run."""
    if not pairs:
        return
    # pass the pairs via a list file: '|' is special in PowerShell CLI parsing
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".lst", delete=False, encoding="utf-8"
    ) as lf:
        lf.write("\n".join(f"{s}|{d}" for s, d in pairs))
        list_file = lf.name
    try:
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", str(_wdp_helper_script()), "-ListFile", list_file],
            capture_output=True, text=True, shell=False,
        )
    finally:
        os.unlink(list_file)
    if proc.returncode != 0:
        print(f"[WARN] powershell exited {proc.returncode}: {proc.stderr[-300:]}",
              file=sys.stderr)
    for line in proc.stderr.splitlines():
        if line.startswith("FAIL|"):
            parts = line.split("|")
            print(f"[WARN] WDP decode failed {parts[1]}: {'|'.join(parts[2:])}",
                  file=sys.stderr)


# ---------------------------------------------------------------------------
# OOXML parsing helpers
# ---------------------------------------------------------------------------
NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "a14": "http://schemas.microsoft.com/office/drawing/2010/main",
}


def q(tag: str) -> str:
    pfx, local = tag.split(":")
    return "{%s}%s" % (NS[pfx], local)


EMU_PER_PT = 12700.0


@dataclass
class PicInfo:
    """One <p:pic> picture, with coordinates accumulated into slide space."""
    bbox_pt: Tuple[float, float, float, float]      # (x0, y0, x1, y1) in pt
    media_path: str                                  # zip path of base image
    img_layer_path: Optional[str]                    # zip path of effect layer
    src_rect: Optional[Tuple[int, int, int, int]]    # (l, t, r, b) in permille
    rot_deg: float


def load_rel_map(zf: zipfile.ZipFile, slide_num: int):
    import xml.etree.ElementTree as ET

    rels = ET.fromstring(zf.read(f"ppt/slides/_rels/slide{slide_num}.xml.rels"))
    return {rel.get("Id"): rel.get("Target").replace("../", "ppt/")
            for rel in rels}


def parse_pics(zf: zipfile.ZipFile, slide_num: int) -> List[PicInfo]:
    """All pictures of a slide; group transforms accumulated recursively."""
    import xml.etree.ElementTree as ET

    rel_map = load_rel_map(zf, slide_num)
    root = ET.fromstring(zf.read(f"ppt/slides/slide{slide_num}.xml"))
    sp_tree = root.find(".//p:spTree", NS)
    if sp_tree is None:
        return []

    out: List[PicInfo] = []

    def walk(el, ox, oy, sx, sy, grp_rot):
        for child in list(el):
            if child.tag == q("p:grpSp"):
                xfrm = child.find("./p:grpSpPr/a:xfrm", NS)
                off, ext, cho, che = (0, 0), (1, 1), (0, 0), (1, 1)
                rot = 0
                if xfrm is not None:
                    o = xfrm.find("a:off", NS)
                    e = xfrm.find("a:ext", NS)
                    co = xfrm.find("a:chOff", NS)
                    ce = xfrm.find("a:chExt", NS)
                    if o is not None:
                        off = (int(o.get("x", 0)), int(o.get("y", 0)))
                    if e is not None:
                        ext = (int(e.get("cx", 1)), int(e.get("cy", 1)))
                    if co is not None:
                        cho = (int(co.get("x", 0)), int(co.get("y", 0)))
                    if ce is not None:
                        che = (int(ce.get("cx", 1)), int(ce.get("cy", 1)))
                    rot = int(xfrm.get("rot", 0))
                nsx = sx * ext[0] / che[0] if che[0] else 1.0
                nsy = sy * ext[1] / che[1] if che[1] else 1.0
                nox = ox + sx * off[0] - nsx * cho[0]
                noy = oy + sy * off[1] - nsy * cho[1]
                walk(child, nox, noy, nsx, nsy, grp_rot + rot)

            elif child.tag == q("p:pic"):
                blip = child.find("./p:blipFill/a:blip", NS)
                if blip is None:
                    continue
                rid = blip.get(q("r:embed"))
                base = rel_map.get(rid) if rid else None
                if base is None:
                    continue

                layer_el = child.find(
                    "./p:blipFill/a:blip/a:extLst/a:ext/a14:imgProps/a14:imgLayer",
                    NS,
                )
                layer_path = None
                if layer_el is not None:
                    lrid = layer_el.get(q("r:embed"))
                    layer_path = rel_map.get(lrid) if lrid else None

                src_el = child.find("./p:blipFill/a:srcRect", NS)
                src_rect = None
                if src_el is not None and len(src_el.attrib) > 0:
                    src_rect = (
                        int(src_el.get("l", 0)),
                        int(src_el.get("t", 0)),
                        int(src_el.get("r", 0)),
                        int(src_el.get("b", 0)),
                    )

                xfrm = child.find("./p:spPr/a:xfrm", NS)
                off, ext, rot = (0, 0), (0, 0), 0
                if xfrm is not None:
                    o = xfrm.find("a:off", NS)
                    e = xfrm.find("a:ext", NS)
                    if o is not None:
                        off = (int(o.get("x", 0)), int(o.get("y", 0)))
                    if e is not None:
                        ext = (int(e.get("cx", 0)), int(e.get("cy", 0)))
                    rot = int(xfrm.get("rot", 0))

                x0 = ox + sx * off[0]
                y0 = oy + sy * off[1]
                w = sx * ext[0]
                h = sy * ext[1]
                out.append(PicInfo(
                    bbox_pt=(x0 / EMU_PER_PT, y0 / EMU_PER_PT,
                             (x0 + w) / EMU_PER_PT, (y0 + h) / EMU_PER_PT),
                    media_path=base,
                    img_layer_path=layer_path,
                    src_rect=src_rect,
                    rot_deg=(grp_rot + rot) / 60000.0,
                ))

    walk(sp_tree, 0.0, 0.0, 1.0, 1.0, 0)
    return out


# ---------------------------------------------------------------------------
# PDF image replacement (lossless, low-level xref editing)
# ---------------------------------------------------------------------------
def _split_alpha(im):
    """Return (rgb_bytes, alpha_bytes_or_None, w, h)."""
    if im.mode in ("P", "LA", "PA"):
        im = im.convert("RGBA")
    if im.mode not in ("RGB", "RGBA", "L"):
        im = im.convert("RGBA")

    rgb_im = im
    alpha = None
    if im.mode == "RGBA":
        a = im.split()[-1]
        if a.getextrema() == (255, 255):
            rgb_im = im.convert("RGB")
        else:
            alpha = a.tobytes()
            rgb_im = im.convert("RGB")
    elif im.mode == "L":
        pass
    w, h = im.size
    rgb = rgb_im.tobytes("raw", "RGB")
    return rgb, alpha, w, h


def replace_xref_image(doc, xref: int, im) -> None:
    """Overwrite the image XObject at *xref* with lossless Flate RGB data,
    creating or reusing an /SMask for alpha channels. PyMuPDF's
    ``update_stream`` compresses uncompressed input itself, so pass raw pixel
    bytes rather than pre-compressing them."""
    rgb, alpha, w, h = _split_alpha(im)

    # base image stream
    doc.update_stream(xref, rgb)
    doc.xref_set_key(xref, "Type", "/XObject")
    doc.xref_set_key(xref, "Subtype", "/Image")
    doc.xref_set_key(xref, "Width", str(w))
    doc.xref_set_key(xref, "Height", str(h))
    doc.xref_set_key(xref, "ColorSpace", "/DeviceRGB")
    doc.xref_set_key(xref, "BitsPerComponent", "8")
    doc.xref_set_key(xref, "Filter", "/FlateDecode")
    doc.xref_set_key(xref, "DecodeParms", "null")
    doc.xref_set_key(xref, "Decode", "null")

    if alpha is not None:
        # Reuse an existing SMask object if present, else create a new one.
        sm = doc.xref_get_key(xref, "SMask")[1]
        m = re.match(r"(\d+)\s+0\s+R", sm) if sm and sm != "null" else None
        if m:
            sm_xref = int(m.group(1))
        else:
            sm_xref = doc.get_new_xref()
            doc.update_object(sm_xref, "<< >>")
        doc.update_stream(sm_xref, alpha)
        doc.xref_set_key(sm_xref, "Type", "/XObject")
        doc.xref_set_key(sm_xref, "Subtype", "/Image")
        doc.xref_set_key(sm_xref, "Width", str(w))
        doc.xref_set_key(sm_xref, "Height", str(h))
        doc.xref_set_key(sm_xref, "ColorSpace", "/DeviceGray")
        doc.xref_set_key(sm_xref, "BitsPerComponent", "8")
        doc.xref_set_key(sm_xref, "Filter", "/FlateDecode")
        doc.xref_set_key(sm_xref, "DecodeParms", "null")
        doc.xref_set_key(sm_xref, "Decode", "null")
        # Original media provides straight RGBA, so the COM PDF's matte value
        # must not be applied to these source pixels.
        doc.xref_set_key(sm_xref, "Matte", "null")
        doc.xref_set_key(xref, "SMask", f"{sm_xref} 0 R")
    else:
        # Keep any PDF-generated mask (for example, a PowerPoint background
        # removal layer), but scale it to match the restored source image.
        sm = doc.xref_get_key(xref, "SMask")[1]
        m = re.match(r"(\d+)\s+0\s+R", sm) if sm and sm != "null" else None
        if m:
            sm_xref = int(m.group(1))
            sw = int(doc.xref_get_key(sm_xref, "Width")[1])
            sh = int(doc.xref_get_key(sm_xref, "Height")[1])
            if (sw, sh) != (w, h):
                from PIL import Image as PILImage

                mask_data = doc.xref_stream(sm_xref)
                if len(mask_data) != sw * sh:
                    try:
                        mask_data = zlib.decompress(mask_data)
                    except zlib.error:
                        pass
                if len(mask_data) != sw * sh:
                    raise ValueError(
                        f"Cannot decode SMask {sm_xref}: expected {sw * sh} "
                        f"pixels, got {len(mask_data)} bytes"
                    )
                mask = PILImage.frombytes("L", (sw, sh), mask_data)
                mask = mask.resize((w, h), PILImage.Resampling.LANCZOS)
                doc.update_stream(sm_xref, mask.tobytes())
                doc.xref_set_key(sm_xref, "Width", str(w))
                doc.xref_set_key(sm_xref, "Height", str(h))
                doc.xref_set_key(sm_xref, "ColorSpace", "/DeviceGray")
                doc.xref_set_key(sm_xref, "BitsPerComponent", "8")
                doc.xref_set_key(sm_xref, "Filter", "/FlateDecode")
                doc.xref_set_key(sm_xref, "DecodeParms", "null")
                doc.xref_set_key(sm_xref, "Decode", "null")


def page_content_bbox(page, margin: float):
    """Tight bounding box of images + drawings + text, expanded by margin.
    Full-page, near-white rectangles (slide background) are excluded so they
    do not defeat the crop."""
    pg = page.rect
    page_area = pg.width * pg.height
    rects = []
    for d in page.get_drawings():
        r = d["rect"]
        # slide background rectangle: covers almost the whole page and is
        # filled with (near-)white → not content
        if r.width * r.height >= page_area * 0.9 and d.get("fill"):
            fr, fg, fb = d["fill"]
            if fr > 0.9 and fg > 0.9 and fb > 0.9:
                continue
        rects.append(r)
    for b in page.get_text("blocks"):
        if len(b) >= 4:
            rects.append((b[0], b[1], b[2], b[3]))
    # tighter: use character-level bboxes so line/block padding is not kept
    try:
        raw = page.get_text("rawdict")
        for blk in raw["blocks"]:
            for ln in blk.get("lines", []):
                for sp in ln["spans"]:
                    for ch in sp["chars"]:
                        rects.append(tuple(ch["bbox"]))
    except Exception:
        pass
    for info in page.get_image_info(xrefs=True):
        rects.append(tuple(info["bbox"]))
    if not rects:
        return pg
    x0 = min(r[0] for r in rects)
    y0 = min(r[1] for r in rects)
    x1 = max(r[2] for r in rects)
    y1 = max(r[3] for r in rects)
    return (x0 - margin, y0 - margin, x1 + margin, y1 + margin)


# ---------------------------------------------------------------------------
# main pipeline
# ---------------------------------------------------------------------------
def process(input_path: str, output_path: str, slide_spec: Optional[str],
            margin: float, no_replace: bool, no_crop: bool, keep_temp: bool) -> Path:
    import pymupdf
    from PIL import Image as PILImage
    import pythoncom
    import win32com.client as wc

    pythoncom.CoInitialize()

    src = Path(input_path).resolve()
    out = Path(output_path).resolve()
    if not src.exists():
        sys.exit(f"Input file not found: {src}")
    print(f"Input : {src}")
    print(f"Output: {out}")

    tmpdir = Path(tempfile.mkdtemp(prefix="pptx2pdf_"))
    raw_pdf = tmpdir / "raw_export.pdf"
    wdp_dir = tmpdir / "wdp"
    wdp_dir.mkdir()

    with zipfile.ZipFile(src) as zf:
        slides_in_pptx = max(
            (int(m.group(1)) for name in zf.namelist()
             if (m := re.match(r"ppt/slides/slide(\d+)\.xml$", name))),
            default=0,
        )

        # ---- slide selection ----
        selected = list(range(1, slides_in_pptx + 1))
        if slide_spec:
            selected = []
            for part in slide_spec.split(","):
                part = part.strip()
                if "-" in part:
                    a, b = part.split("-", 1)
                    selected.extend(range(int(a), int(b) + 1))
                else:
                    selected.append(int(part))
            selected = sorted(set(selected) & set(range(1, slides_in_pptx + 1)))
            if not selected:
                sys.exit(f"--slides {slide_spec!r} matches nothing (1–{slides_in_pptx} available)")
        print(f"Slides : {len(selected)} page(s): {', '.join(str(s) for s in selected)}")

        # ---- 1. PowerPoint COM export ----
        print("Exporting via PowerPoint COM ... ", end="", flush=True)
        existing_app = None
        try:
            existing_app = wc.GetActiveObject("PowerPoint.Application")
        except Exception:
            pass
        app = existing_app or wc.DispatchEx("PowerPoint.Application")

        pres = app.Presentations.Open(str(src), ReadOnly=-1, Untitled=0, WithWindow=0)

        export_range, range_type = None, 1  # 1 = ppPrintAll
        if len(selected) < slides_in_pptx:
            if selected[-1] - selected[0] + 1 != len(selected):
                print("  [WARN] non-contiguous --slides; COM exports the whole deck "
                      "(unused pages are dropped later by --slides handling). "
                      "Prefer a contiguous range.")
            else:
                range_type = 4  # ppPrintSlideRange
                export_range = pres.PrintOptions.Ranges.Add(selected[0], selected[-1])

        pres.ExportAsFixedFormat(
            str(raw_pdf),  # path
            2,             # ppFixedFormatTypePDF
            2,             # ppFixedFormatIntentPrint
            0,             # frame slides: msoFalse
            1,             # handout order
            1,             # output type: slides
            0,             # print hidden slides: msoFalse
            export_range,  # print range / None
            range_type,    # range type
            "",            # slide show name
            0, 0, 0, 0, 0, # props / IRM / tags / bmp fonts / pdf-a
        )
        pres.Close()
        if existing_app is None:
            app.Quit()
        print(f"done ({raw_pdf.stat().st_size / 1024:.0f} KB).")

        doc = pymupdf.open(str(raw_pdf))

        # Drop exported pages we do not want (defensive; normally 1:1)
        wanted_pages = [selected.index(s) for s in selected]
        if len(doc) > len(wanted_pages):
            doc.select(wanted_pages)

        # ---- 2. replace down-sampled images with originals ----
        if not no_replace:
            print("Replacing images with original media ...", end="", flush=True)

            # pre-decode .wdp effect layers
            wdp_cache: dict[str, Path] = {}
            to_decode: List[Tuple[Path, Path]] = []
            for sl in selected:
                for pic in parse_pics(zf, sl):
                    lp = pic.img_layer_path
                    if lp and lp.endswith(".wdp") and lp not in wdp_cache:
                        dsrc = wdp_dir / Path(lp).name
                        ddst = wdp_dir / (Path(lp).name + ".png")
                        dsrc.write_bytes(zf.read(lp))
                        wdp_cache[lp] = ddst
                        to_decode.append((dsrc, ddst))
            if to_decode:
                decode_wdp_batch(to_decode)
                print(f" [decoded {len(to_decode)} .wdp]", end=", ", flush=True)

            total_xrefs = 0
            n_replaced = 0
            n_unmatched = 0
            for idx, page in enumerate(doc):
                slide_no = selected[idx] if idx < len(selected) else idx + 1
                pics = parse_pics(zf, slide_no) if slide_no in selected else []
                centers = [
                    ((p.bbox_pt[0] + p.bbox_pt[2]) / 2,
                     (p.bbox_pt[1] + p.bbox_pt[3]) / 2, i)
                    for i, p in enumerate(pics)
                ]

                # group PDF image infos by xref; match each unique xref once
                xref_infos: dict[int, tuple] = {}
                for inf in page.get_image_info(xrefs=True):
                    if inf["xref"] not in xref_infos:
                        xref_infos[inf["xref"]] = inf
                total_xrefs += len(xref_infos)

                used_pic = set()
                for xref, inf in xref_infos.items():
                    bx0, by0, bx1, by1 = inf["bbox"]
                    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
                    best, best_d = None, 25.0
                    for pcx, pcy, pi in centers:
                        if pi in used_pic:
                            continue
                        d = ((pcx - cx) ** 2 + (pcy - cy) ** 2) ** 0.5
                        if d < best_d:
                            best_d, best = d, pi
                    if best is None:
                        n_unmatched += 1
                        continue
                    used_pic.add(best)
                    pic = pics[best]

                    # source pixel data: effect layer if any, else base image
                    data = None
                    if pic.img_layer_path:
                        sp = pic.img_layer_path
                        if sp in wdp_cache and wdp_cache[sp].exists():
                            data = wdp_cache[sp].read_bytes()
                        if data is None:
                            data = zf.read(sp)
                    try:
                        im = PILImage.open(io.BytesIO(data if data else zf.read(pic.media_path)))
                        im.load()
                    except Exception:
                        # unusable effect layer → fall back to the base image
                        im = PILImage.open(io.BytesIO(zf.read(pic.media_path)))
                        im.load()
                    if pic.src_rect:
                        l, t, r, b = pic.src_rect
                        w, h = im.size
                        box = (l * w // 100000, t * h // 100000,
                               w - r * w // 100000, h - b * h // 100000)
                        if box[2] > box[0] and box[3] > box[1]:
                            im = im.crop(box)

                    replace_xref_image(doc, xref, im)
                    n_replaced += 1
            print(f"done ({n_replaced}/{total_xrefs} xrefs replaced, "
                  f"{n_unmatched} unmatched).")

        # ---- 3. crop to content ----
        if not no_crop:
            print("Cropping white margin ... ", end="", flush=True)
            for page in doc:
                box = page_content_bbox(page, margin)
                # clip back to the original page rect (never enlarge)
                pg = page.rect
                box = (max(box[0], pg.x0), max(box[1], pg.y0),
                       min(box[2], pg.x1), min(box[3], pg.y1))
                if box[2] - box[0] < 0.1 or box[3] - box[1] < 0.1:
                    box = (pg.x0, pg.y0, pg.x1, pg.y1)
                page.set_cropbox(pymupdf.Rect(box))
            print("done.")

        print(f"Saving -> {out} ... ", end="", flush=True)
        doc.save(str(out), garbage=4, deflate=True)
        doc.close()
        print(f"done ({out.stat().st_size / 1024:.0f} KB).")

    if not keep_temp:
        shutil.rmtree(tmpdir, ignore_errors=True)
    return out


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(
        description="High-fidelity PPTX→PDF (lossless images + auto white-margin crop).",
        epilog="Windows + PowerPoint required.",
    )
    ap.add_argument("input", help="path to .pptx")
    ap.add_argument("-o", "--output", default=None,
                    help="output PDF (default: same name, .pdf next to input)")
    ap.add_argument("--slides", default=None,
                    help="slides to keep, e.g. '1' or '1-3' (default: all)")
    ap.add_argument("--margin", type=float, default=2.0,
                    help="crop margin in pt (default 2.0)")
    ap.add_argument("--no-replace", action="store_true",
                    help="skip original-image replacement (COM export only)")
    ap.add_argument("--no-crop", action="store_true",
                    help="skip white-margin cropping")
    ap.add_argument("--keep-temp", action="store_true",
                    help="keep temporary export files")
    args = ap.parse_args()

    _ensure_imports()

    if args.output is None:
        p = Path(args.input)
        args.output = str(p.with_suffix(".pdf"))

    process(args.input, args.output, args.slides, args.margin,
            args.no_replace, args.no_crop, args.keep_temp)


if __name__ == "__main__":
    main()
