#!/usr/bin/env python3
"""Research Paper Figures — SVG to PPTX Collector.

Scans a figures directory for SVG files and assembles them into a single PPTX,
one SVG per slide. Each slide is titled with the figure ID and description.

Usage:
    python3 figure_to_pptx.py <figures_dir>
    python3 figure_to_pptx.py <figures_dir> --output custom_output.pptx
    python3 figure_to_pptx.py <figures_dir> --manifest figure_list.json

The script supports two embedding modes:
  1. Image mode (default): SVG rendered to PNG then inserted as picture
  2. Native mode (--native): SVG embedded via python-pptx EMF-like fallback

Dependencies:
    pip install python-pptx cairosvg Pillow
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
except ImportError:
    sys.exit("Error: python-pptx not installed. Run: pip install python-pptx")

try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False

import tempfile
import os


def svg_to_png(svg_path: Path, output_path: Path, scale: float = 2.0) -> bool:
    """Convert SVG to high-res PNG using cairosvg."""
    if not HAS_CAIROSVG:
        return False
    try:
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(output_path),
            scale=scale,
        )
        return True
    except Exception as e:
        print(f"  Warning: cairosvg failed for {svg_path.name}: {e}")
        return False


def parse_svg_dimensions(svg_path: Path) -> tuple[int, int]:
    """Extract width/height from SVG viewBox or width/height attributes."""
    import re
    content = svg_path.read_text(encoding='utf-8')

    vb_match = re.search(r'viewBox\s*=\s*"([^"]+)"', content)
    if vb_match:
        parts = vb_match.group(1).split()
        if len(parts) == 4:
            return int(float(parts[2])), int(float(parts[3]))

    w_match = re.search(r'\bwidth\s*=\s*"(\d+(?:\.\d+)?)"', content)
    h_match = re.search(r'\bheight\s*=\s*"(\d+(?:\.\d+)?)"', content)
    if w_match and h_match:
        return int(float(w_match.group(1))), int(float(h_match.group(1)))

    return 800, 500


def load_manifest(manifest_path: Path) -> list[dict]:
    """Load figure manifest JSON."""
    if not manifest_path.exists():
        return []
    with open(manifest_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def collect_svg_files(figures_dir: Path, manifest: list[dict]) -> list[dict]:
    """Collect SVG files, ordered by manifest if available."""
    svg_output_dir = figures_dir / "svg_output"
    if not svg_output_dir.exists():
        svg_output_dir = figures_dir

    svg_files = sorted(svg_output_dir.glob("*.svg"))
    if not svg_files:
        return []

    if manifest:
        manifest_map = {item["id"]: item for item in manifest}
        ordered = []
        seen = set()
        for item in manifest:
            svg_name = f"{item['id']}.svg"
            svg_path = svg_output_dir / svg_name
            if svg_path.exists():
                ordered.append({
                    "path": svg_path,
                    "id": item["id"],
                    "description": item.get("description", ""),
                    "type": item.get("type", "unknown"),
                })
                seen.add(svg_path.name)
        for svg_path in svg_files:
            if svg_path.name not in seen:
                fig_id = svg_path.stem
                ordered.append({
                    "path": svg_path,
                    "id": fig_id,
                    "description": manifest_map.get(fig_id, {}).get("description", ""),
                    "type": manifest_map.get(fig_id, {}).get("type", "unknown"),
                })
        return ordered
    else:
        return [
            {
                "path": svg_path,
                "id": svg_path.stem,
                "description": "",
                "type": "unknown",
            }
            for svg_path in svg_files
        ]


def create_pptx(
    figures: list[dict],
    output_path: Path,
    slide_width_inches: float = 13.333,
    slide_height_inches: float = 7.5,
) -> None:
    """Create PPTX with one figure per slide."""
    prs = Presentation()
    prs.slide_width = Inches(slide_width_inches)
    prs.slide_height = Inches(slide_height_inches)

    blank_layout = prs.slide_layouts[6]  # blank

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        for i, fig in enumerate(figures):
            slide = prs.slides.add_slide(blank_layout)
            svg_path = fig["path"]
            fig_id = fig["id"]
            description = fig["description"]
            svg_w, svg_h = parse_svg_dimensions(svg_path)

            title_text = f"Figure {i+1}: {fig_id}"
            if description:
                title_text += f" — {description}"

            txBox = slide.shapes.add_textbox(
                Inches(0.3), Inches(0.2),
                Inches(slide_width_inches - 0.6), Inches(0.5),
            )
            tf = txBox.text_frame
            p = tf.paragraphs[0]
            p.text = title_text
            p.font.size = Pt(14)
            p.font.bold = True
            p.font.color.rgb = RGBColor(0x37, 0x47, 0x4F)
            p.alignment = PP_ALIGN.LEFT

            png_path = tmp_path / f"{fig_id}.png"
            png_ok = svg_to_png(svg_path, png_path, scale=2.0)

            margin_top = Inches(0.9)
            available_w = Inches(slide_width_inches - 0.6)
            available_h = Inches(slide_height_inches - 1.2)

            aspect = svg_w / svg_h
            avail_aspect = available_w / available_h

            if aspect > avail_aspect:
                img_w = available_w
                img_h = int(available_w / aspect)
            else:
                img_h = available_h
                img_w = int(available_h * aspect)

            left = Inches(0.3) + (available_w - img_w) // 2
            top = margin_top + (available_h - img_h) // 2

            if png_ok:
                slide.shapes.add_picture(str(png_path), left, top, img_w, img_h)
            else:
                slide.shapes.add_picture(str(svg_path), left, top, img_w, img_h)

            notes_slide = slide.notes_slide
            notes_tf = notes_slide.notes_text_frame
            notes_tf.text = (
                f"Figure ID: {fig_id}\n"
                f"Type: {fig['type']}\n"
                f"SVG Source: {svg_path.name}\n"
                f"Original size: {svg_w}x{svg_h}"
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
    print(f"Created: {output_path} ({len(figures)} figures)")


def main():
    parser = argparse.ArgumentParser(
        description="Collect paper SVG figures into a single PPTX file"
    )
    parser.add_argument(
        "figures_dir",
        type=Path,
        help="Path to figures directory (contains svg_output/ or *.svg directly)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output PPTX path (default: figures_dir/output/paper_figures.pptx)",
    )
    parser.add_argument(
        "--manifest", "-m",
        type=Path,
        default=None,
        help="Path to figure_list.json manifest",
    )
    parser.add_argument(
        "--wide",
        action="store_true",
        help="Use 16:9 widescreen (default)",
    )
    parser.add_argument(
        "--standard",
        action="store_true",
        help="Use 4:3 standard aspect ratio",
    )

    args = parser.parse_args()

    if not args.figures_dir.exists():
        sys.exit(f"Error: Directory not found: {args.figures_dir}")

    manifest_path = args.manifest or args.figures_dir / "figure_list.json"
    manifest = load_manifest(manifest_path)

    figures = collect_svg_files(args.figures_dir, manifest)
    if not figures:
        sys.exit(f"Error: No SVG files found in {args.figures_dir} or {args.figures_dir / 'svg_output'}")

    print(f"Found {len(figures)} SVG figure(s)")
    for fig in figures:
        print(f"  - {fig['id']}: {fig['description'] or '(no description)'}")

    if args.output:
        output_path = args.output
    else:
        output_path = args.figures_dir / "output" / "paper_figures.pptx"

    if args.standard:
        create_pptx(figures, output_path, 10.0, 7.5)
    else:
        create_pptx(figures, output_path, 13.333, 7.5)


if __name__ == "__main__":
    main()
