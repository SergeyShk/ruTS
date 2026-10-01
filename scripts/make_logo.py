"""
Знак ruTS: docs/img/ruts.svg и прозрачный docs/img/ruts.png из одного исходника

Надпись ruTS - глифы PT Sans Bold (ParaType, SIL Open Font License), переведенные
в контуры, поэтому файл не зависит от шрифтов у читателя. Имя созвучно roots:
ствол T уходит под строку и ветвится корнями светлым оттенком того же тона

Запуск: uv run python scripts/make_logo.py (PNG - через rsvg-convert)
"""

import hashlib
import io
import math
import subprocess
import urllib.request
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT_URL = (
    "https://raw.githubusercontent.com/google/fonts/"
    "90abd17b4f97671435798b6147b698aa9087612f/ofl/ptsans/PT_Sans-Web-Bold.ttf"
)
FONT_SHA256 = "3128bd5ecf01816e59a23d54c57a7a6b14615b07db53ff277c77376010265b05"
IMG_DIR = Path(__file__).resolve().parent.parent / "docs" / "img"
TEXT = "ruTS"
LETTERS = "#388e3c"
ROOTS = "#66bb6a"
MARGIN = 40
PNG_WIDTH = 1200

Point = tuple[float, float]
Curve = tuple[Point, Point, Point, Point]


def load_font() -> TTFont:
    with urllib.request.urlopen(FONT_URL) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != FONT_SHA256:
        raise RuntimeError(f"Контрольная сумма шрифта не совпала: {FONT_URL}")
    return TTFont(io.BytesIO(data))


def letters(font: TTFont) -> tuple[list[str], list[tuple[float, float, float, float]], float]:
    """Контуры букв в координатах SVG (базовая линия на высоте прописной) и их рамки"""
    cmap = font.getBestCmap()
    glyphs = font.getGlyphSet()
    cap = font["OS/2"].sCapHeight
    x = 0.0
    paths, boxes = [], []
    for char in TEXT:
        glyph = glyphs[cmap[ord(char)]]
        pen = SVGPathPen(glyphs)
        glyph.draw(TransformPen(pen, (1, 0, 0, -1, x, cap)))
        bounds = BoundsPen(glyphs)
        glyph.draw(bounds)
        xmin, ymin, xmax, ymax = bounds.bounds
        paths.append(pen.getCommands())
        boxes.append((x + xmin, cap - ymax, x + xmax, cap - ymin))
        x += glyph.width
    return paths, boxes, cap


def bezier(p0: Point, p1: Point, p2: Point, p3: Point, t: float) -> Point:
    u = 1 - t
    x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
    y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
    return x, y


def tapered(curve: Curve, w0: float, w1: float, steps: int = 48) -> list[Point]:
    """Контур кривой, ширина которой линейно меняется от w0 до w1"""
    points = [bezier(*curve, i / steps) for i in range(steps + 1)]
    left, right = [], []
    for i, (x, y) in enumerate(points):
        ax, ay = points[max(i - 1, 0)]
        bx, by = points[min(i + 1, steps)]
        norm = math.hypot(bx - ax, by - ay) or 1.0
        nx, ny = -(by - ay) / norm, (bx - ax) / norm
        half = (w0 + (w1 - w0) * i / steps) / 2
        left.append((x + nx * half, y + ny * half))
        right.append((x - nx * half, y - ny * half))
    return left + right[::-1]


def path_data(outline: list[Point]) -> str:
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in outline) + " Z"


def root(
    start: Point, angles: tuple[float, float], length: float, width: float
) -> tuple[Curve, float]:
    """Корень: углы от вертикали в начале и в конце, к концу он загибается вниз"""
    a0, a1 = angles
    mid = (a0 + a1) / 2
    end = (start[0] + math.sin(mid) * length, start[1] + math.cos(mid) * length)
    c1 = (start[0] + math.sin(a0) * length * 0.45, start[1] + math.cos(a0) * length * 0.45)
    c2 = (end[0] - math.sin(a1) * length * 0.4, end[1] - math.cos(a1) * length * 0.4)
    return (start, c1, c2, end), width


def roots(x0: float, base: float, stem: float, depth: float) -> list[list[Point]]:
    """Ствол под строкой, пять корней и по корешку у каждого, кроме среднего"""
    shapes = []
    collar = (x0, base + 0.24 * depth)
    trunk = ((x0, base - 2), (x0, base + 0.1 * depth), (x0, base + 0.18 * depth), collar)
    shapes.append(tapered(trunk, stem, stem * 0.7))
    fork = (x0, base + 0.17 * depth)
    main = [
        ((-1.3, -0.6), 1.2, 0.52, -1),
        ((-0.6, -0.15), 1.0, 0.5, -1),
        ((0.04, 0.0), 0.86, 0.46, 0),
        ((0.62, 0.17), 1.0, 0.5, 1),
        ((1.3, 0.6), 1.2, 0.52, 1),
    ]
    for angles, length, share, side in main:
        curve, width = root(fork, angles, length * depth, stem * share)
        shapes.append(tapered(curve, width, width * 0.08))
        if side:
            t = 0.5
            point = bezier(*curve, t)
            before = bezier(*curve, t - 0.02)
            heading = math.atan2(point[0] - before[0], point[1] - before[1])
            turn = 0.6 * side
            twig, twig_width = root(
                point, (heading + turn, heading + turn * 0.2), 0.36 * length * depth, width * 0.5
            )
            shapes.append(tapered(twig, twig_width, twig_width * 0.1))
    return shapes


def main() -> None:
    font = load_font()
    paths, boxes, cap = letters(font)
    t_left, _, t_right, _ = boxes[TEXT.index("T")]
    stem = 0.19 * cap
    depth = 0.62 * cap
    shapes = roots((t_left + t_right) / 2, cap, stem, depth)
    xs = [x for box in boxes for x in (box[0], box[2])] + [x for o in shapes for x, _ in o]
    ys = [y for box in boxes for y in (box[1], box[3])] + [y for o in shapes for _, y in o]
    left, top = min(xs) - MARGIN, min(ys) - MARGIN
    width, height = max(xs) + MARGIN - left, max(ys) + MARGIN - top
    body = [f'  <path fill="{ROOTS}" d="{path_data(outline)}"/>' for outline in shapes]
    body += [f'  <path fill="{LETTERS}" d="{d}"/>' for d in paths]
    svg = "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{left:.0f} {top:.0f} {width:.0f} '
            f'{height:.0f}" width="{width:.0f}" height="{height:.0f}" role="img" aria-label="ruTS">',
            "  <title>ruTS</title>",
            *body,
            "</svg>",
            "",
        ]
    )
    svg_path = IMG_DIR / "ruts.svg"
    svg_path.write_text(svg, encoding="utf-8")
    png_path = IMG_DIR / "ruts.png"
    subprocess.run(
        ["rsvg-convert", "-w", str(PNG_WIDTH), "-o", str(png_path), str(svg_path)], check=True
    )


if __name__ == "__main__":
    main()
