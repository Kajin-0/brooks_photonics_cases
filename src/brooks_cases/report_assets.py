"""Image assets and data loading for Case 001 reports."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

INK = "#172033"
PURPLE = "#6A3FA0"
ORANGE = "#C35B2A"


def _font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = ["DejaVuSans-Bold.ttf"] if bold else ["DejaVuSans.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _range_text(values: list[int]) -> str:
    if not values:
        return "none"
    if values == list(range(min(values), max(values) + 1)):
        return f"{min(values)} to {max(values)}"
    return ", ".join(map(str, values))


def _build_report_hero(source: Path, destination: Path) -> Path:
    """Build a clean three-panel cover image from the first interval map row."""
    image = Image.open(source).convert("RGB")
    width, height = image.size
    boxes = [
        (0.0086, 0.0655, 0.2381, 0.2780),
        (0.3655, 0.0655, 0.5950, 0.2780),
        (0.7242, 0.0655, 0.9524, 0.2780),
    ]
    labels = ["Affected interval 0", "Nominal control", "Affected minus control"]
    panels = [
        image.crop(
            (
                round(left * width),
                round(top * height),
                round(right * width),
                round(bottom * height),
            )
        )
        for left, top, right, bottom in boxes
    ]
    target_height = 520
    panels = [
        panel.resize(
            (round(panel.width * target_height / panel.height), target_height),
            Image.Resampling.LANCZOS,
        )
        for panel in panels
    ]
    gap = 24
    label_height = 52
    margin = 18
    canvas_width = sum(panel.width for panel in panels) + 2 * gap + 2 * margin
    canvas_height = label_height + target_height + 2 * margin
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(canvas)
    font = _font(24, bold=True)
    x_position = margin
    for panel, label in zip(panels, labels, strict=True):
        text_box = draw.textbbox((0, 0), label, font=font)
        text_width = text_box[2] - text_box[0]
        draw.text(
            (x_position + (panel.width - text_width) / 2, margin),
            label,
            fill=INK,
            font=font,
        )
        canvas.paste(panel, (x_position, margin + label_height))
        x_position += panel.width + gap
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, quality=95)
    return destination


def _build_client_spatial_figure(source: Path, destination: Path) -> Path:
    """Reduce the full 12-panel map figure to three decision-relevant stages."""
    image = Image.open(source).convert("RGB")
    width, height = image.size
    row_boxes = {
        "Interval 0: strong spatial gradient": (0.025, 0.286),
        "Interval 6: spatially subtle, temporally elevated": (0.520, 0.768),
        "Interval 10: nominal late-ramp behavior": (0.765, 0.998),
    }
    column_boxes = {
        "Affected exposure": (0.000, 0.285),
        "Affected minus control": (0.704, 0.995),
    }
    crops: list[tuple[str, list[Image.Image]]] = []
    for row_label, (top, bottom) in row_boxes.items():
        row_panels = []
        for left, right in column_boxes.values():
            row_panels.append(
                image.crop(
                    (
                        round(left * width),
                        round(top * height),
                        round(right * width),
                        round(bottom * height),
                    )
                )
            )
        crops.append((row_label, row_panels))

    panel_width = 940
    scaled_rows: list[tuple[str, list[Image.Image]]] = []
    for row_label, row_panels in crops:
        scaled = []
        for panel in row_panels:
            new_height = round(panel.height * panel_width / panel.width)
            scaled.append(panel.resize((panel_width, new_height), Image.Resampling.LANCZOS))
        scaled_rows.append((row_label, scaled))

    margin = 24
    gap = 28
    row_gap = 22
    header_height = 54
    panel_height = max(panel.height for _, panels in scaled_rows for panel in panels)
    canvas_width = 2 * panel_width + gap + 2 * margin
    canvas_height = (
        header_height
        + len(scaled_rows) * panel_height
        + (len(scaled_rows) - 1) * row_gap
        + 2 * margin
    )
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(canvas)
    header_font = _font(27, bold=True)
    draw.text(
        (margin + panel_width / 2, margin),
        "Affected exposure",
        fill=ORANGE,
        font=header_font,
        anchor="ma",
    )
    draw.text(
        (margin + panel_width + gap + panel_width / 2, margin),
        "Affected minus control",
        fill=PURPLE,
        font=header_font,
        anchor="ma",
    )
    y = margin + header_height
    for _row_label, panels in scaled_rows:
        canvas.paste(panels[0], (margin, y))
        canvas.paste(panels[1], (margin + panel_width + gap, y))
        y += panel_height + row_gap
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, quality=95)
    return destination


def _load_context(case_dir: Path) -> dict[str, object]:
    derived = case_dir / "data" / "derived"
    summary = json.loads((derived / "case_summary.json").read_text(encoding="utf-8"))
    return {
        "summary": summary,
        "comparison": summary["comparison"],
        "scattered": summary["scattered"],
        "nominal": summary["nominal"],
        "bootstrap": json.loads(
            (derived / "bootstrap_metrics.json").read_text(encoding="utf-8")
        ),
        "flt": json.loads(
            (derived / "flt_reconstruction_metrics.json").read_text(encoding="utf-8")
        ),
        "source": json.loads(
            (derived / "source_mask_metrics.json").read_text(encoding="utf-8")
        ),
        "inventory": json.loads(
            (case_dir / "data" / "raw" / "inventory.json").read_text(encoding="utf-8")
        ),
    }
