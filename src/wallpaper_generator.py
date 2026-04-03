"""Generate a minimal quote wallpaper image using Pillow.

Design philosophy: dark, minimal, elegant — Apple keynote-style quiet sophistication.
"""

import logging
import math
import random
import re
import textwrap
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logger = logging.getLogger(__name__)

# Font tiers: light/thin preferred for quote, regular for author
FONTS_LIGHT = [
    "C:/Windows/Fonts/segoeuil.ttf",     # Segoe UI Light
    "C:/Windows/Fonts/segoeuisl.ttf",     # Segoe UI Semilight
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/calibril.ttf",
    "C:/Windows/Fonts/arial.ttf",
]

FONTS_SERIF = [
    "C:/Windows/Fonts/georgia.ttf",
    "C:/Windows/Fonts/cambria.ttc",
    "C:/Windows/Fonts/times.ttf",
]

# Premium serif fonts available on Windows — more character than Georgia
FONTS_GARAMOND = [
    "C:/Windows/Fonts/GARA.TTF",          # Garamond — elegant, classic
    "C:/Windows/Fonts/georgia.ttf",
]
FONTS_PALATINO = [
    "C:/Windows/Fonts/pala.ttf",           # Palatino Linotype — warm, refined
    "C:/Windows/Fonts/georgia.ttf",
]
FONTS_BOOKANTIQUA = [
    "C:/Windows/Fonts/BOOKOS.TTF",         # Book Antiqua — literary, clean
    "C:/Windows/Fonts/georgia.ttf",
]

FONTS_REGULAR = [
    "C:/Windows/Fonts/segoeuisl.ttf",    # Semilight for author
    "C:/Windows/Fonts/segoeuil.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
]

FONTS_JP = [
    "C:/Windows/Fonts/YuGothL.ttc",      # Yu Gothic Light
    "C:/Windows/Fonts/YuGothM.ttc",
    "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
]

# Categories considered philosophical / reflective for serif auto-selection
REFLECTIVE_CATEGORIES = {"reflection", "gratitude", "rest"}

# Style presets for variant generation
STYLE_PRESETS: dict[str, dict[str, Any]] = {
    "refined": {
        "font_candidates": FONTS_LIGHT,
        "font_author_candidates": FONTS_REGULAR,
        "size_scale": 1.0,
        "author_color": (145, 145, 150),
        "description": "Clean sans-serif light",
    },
    "larger": {
        "font_candidates": FONTS_LIGHT,
        "font_author_candidates": FONTS_REGULAR,
        "size_scale": 1.15,
        "author_color": (140, 140, 145),
        "description": "Larger sans-serif light",
    },
    "serif": {
        "font_candidates": FONTS_SERIF,
        "font_author_candidates": FONTS_SERIF,
        "size_scale": 0.85,
        "author_color": (140, 140, 145),
        "description": "Georgia serif",
    },
    "garamond": {
        "font_candidates": FONTS_GARAMOND,
        "font_author_candidates": FONTS_GARAMOND,
        "size_scale": 0.90,
        "author_color": (140, 140, 145),
        "description": "Garamond — elegant classic",
    },
    "palatino": {
        "font_candidates": FONTS_PALATINO,
        "font_author_candidates": FONTS_PALATINO,
        "size_scale": 0.85,
        "author_color": (140, 140, 145),
        "description": "Palatino — warm refined",
    },
    "bookantiqua": {
        "font_candidates": FONTS_BOOKANTIQUA,
        "font_author_candidates": FONTS_BOOKANTIQUA,
        "size_scale": 0.85,
        "author_color": (140, 140, 145),
        "description": "Book Antiqua — literary clean",
    },
}


def _resolve_font(
    specified: str | None,
    size: int,
    need_jp: bool = False,
    candidates: list[str] | None = None,
) -> ImageFont.FreeTypeFont:
    """Resolve a font path to a Pillow font object with fallbacks."""
    search: list[str] = []
    if specified:
        search.append(specified)
    if need_jp:
        search.extend(FONTS_JP)
    if candidates:
        search.extend(candidates)
    search.extend(FONTS_LIGHT)

    for path in search:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue

    logger.warning("No TrueType font found, using default bitmap font.")
    return ImageFont.load_default()


def _has_cjk(text: str) -> bool:
    """Check if text contains CJK characters."""
    for ch in text:
        cp = ord(ch)
        if (0x4E00 <= cp <= 0x9FFF or 0x3040 <= cp <= 0x309F or
                0x30A0 <= cp <= 0x30FF or 0xFF00 <= cp <= 0xFFEF):
            return True
    return False


# ---------------------------------------------------------------------------
# Auto style selection
# ---------------------------------------------------------------------------

def select_best_style(quote: dict[str, Any]) -> str:
    """Auto-select the best style preset based on quote characteristics.

    Rules:
    - Short quotes (1-2 semantic lines, <=50 chars): "larger"
    - Philosophical/reflective categories: "serif"
    - Everything else: "refined"
    """
    text = quote["text"]
    categories = set(quote.get("category", []))
    length = len(text)
    semantic_lines = _semantic_split(text)
    line_count = len(semantic_lines)

    # Short quotes: use larger for more impact
    if line_count <= 2 and length <= 50:
        logger.info("Auto-style: 'larger' (short quote, %d chars, %d lines)", length, line_count)
        return "larger"

    # Philosophical / reflective: serif gives gravitas
    if categories & REFLECTIVE_CATEGORIES:
        logger.info("Auto-style: 'serif' (reflective categories: %s)", categories & REFLECTIVE_CATEGORIES)
        return "serif"

    logger.info("Auto-style: 'refined' (default)")
    return "refined"


# ---------------------------------------------------------------------------
# Background generation
# ---------------------------------------------------------------------------

def _generate_bg(width: int, height: int, bg_style: str = "default") -> Image.Image:
    """Dispatch to the correct background generator."""
    generators = {
        "default": _generate_gradient,
        "spotlight": _generate_spotlight,
        "deep_gradient": _generate_deep_gradient,
        "textured_dark": _generate_textured_dark,
    }
    gen = generators.get(bg_style, _generate_gradient)
    return gen(width, height)


def _generate_gradient(width: int, height: int) -> Image.Image:
    """Generate a refined dark background with depth.

    Design: dark, elegant, quiet — flat ではなく deep.
    - Directional light from upper-center, fading toward lower-right
    - Subtle color tint in the lower region (navy / teal / indigo)
    - Moderate radial glow at center for text readability
    - Fine grain noise for texture without visible grain
    """
    # Each palette: (top_color, bottom_color, bottom_tint_rgb)
    # bottom_tint adds a barely-visible hue to the lower third
    palettes = [
        ((10, 10, 18), (24, 22, 38), (12, 18, 32)),   # deep navy tint
        ((8, 8, 12),   (20, 20, 30), (10, 16, 26)),    # smoky indigo tint
        ((12, 10, 16), (8, 16, 28),  (8, 20, 28)),     # muted teal tint
        ((6, 8, 14),   (18, 18, 28), (14, 14, 26)),    # charcoal-navy tint
        ((10, 8, 14),  (14, 20, 24), (10, 18, 22)),    # dark teal tint
    ]
    top_color, bottom_color, bottom_tint = random.choice(palettes)

    # Use numpy for fast pixel operations
    ys = np.linspace(0, 1, height, dtype=np.float32).reshape(-1, 1)
    xs = np.linspace(0, 1, width, dtype=np.float32).reshape(1, -1)

    # Linear vertical gradient
    r = top_color[0] + (bottom_color[0] - top_color[0]) * ys
    g = top_color[1] + (bottom_color[1] - top_color[1]) * ys
    b = top_color[2] + (bottom_color[2] - top_color[2]) * ys

    # Directional light: upper-center is slightly brighter, fading toward lower-right
    # Creates a very gentle sense of direction without being a visible light source
    light_cx, light_cy = 0.48, 0.3   # light origin: slightly left of center, upper third
    light_dist = np.sqrt((xs - light_cx) ** 2 * 0.8 + (ys - light_cy) ** 2 * 1.2)
    light_dist = light_dist / light_dist.max()
    directional = np.clip(1.0 - light_dist, 0, 1) ** 2.5 * 6  # very gentle wash
    r = r + directional * 0.9
    g = g + directional * 0.9
    b = b + directional * 0.7  # slightly cooler at edges

    # Radial glow at center: 10-15% stronger than before for text presence
    cx, cy = 0.5, 0.44
    dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    dist = dist / dist.max()
    radial_boost = np.clip(1.0 - dist, 0, 1) ** 2 * 14  # was 12, now 14

    r = r + radial_boost
    g = g + radial_boost
    b = b + radial_boost * 0.85

    # Bottom tint: add barely-visible color to lower 40% of the image
    # Smoothly fades in — not a band, just atmospheric depth
    tint_fade = np.clip((ys - 0.6) / 0.4, 0, 1) ** 1.5  # gentle ease-in from 60% down
    r = r + tint_fade * (bottom_tint[0] - bottom_color[0]) * 0.4
    g = g + tint_fade * (bottom_tint[1] - bottom_color[1]) * 0.4
    b = b + tint_fade * (bottom_tint[2] - bottom_color[2]) * 0.4

    # Vignette: darken edges
    vignette = 1.0 - (dist ** 1.5 * 0.38)
    r = r * vignette
    g = g * vignette
    b = b * vignette

    # Fine grain noise: slightly increased for texture (was 1.8, now 2.2)
    noise = np.random.normal(0, 2.2, (height, width)).astype(np.float32)
    r = np.clip(r + noise, 0, 255)
    g = np.clip(g + noise, 0, 255)
    b = np.clip(b + noise, 0, 255)

    # Assemble RGB array
    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
    return Image.fromarray(rgb, "RGB")


def _generate_spotlight(width: int, height: int) -> Image.Image:
    """Spotlight: visible light pool at center, deep indigo-black edges.

    Quote floats in a soft blue-tinted light. Clearly not flat black.
    """
    ys = np.linspace(0, 1, height, dtype=np.float32).reshape(-1, 1)
    xs = np.linspace(0, 1, width, dtype=np.float32).reshape(1, -1)

    # Base: deep indigo-black (not pure black — has color)
    r = np.full((height, width), 6.0, dtype=np.float32)
    g = np.full((height, width), 6.0, dtype=np.float32)
    b = np.full((height, width), 16.0, dtype=np.float32)   # visible blue-black

    # Primary spotlight: center, oval, strong — the defining feature
    spot_cx, spot_cy = 0.50, 0.38
    spot_dist = np.sqrt((xs - spot_cx) ** 2 / 0.16 + (ys - spot_cy) ** 2 / 0.10)
    spot = np.clip(1.0 - spot_dist, 0, 1) ** 1.8 * 55  # strong pool of light

    r = r + spot * 0.65
    g = g + spot * 0.70
    b = b + spot * 1.0   # distinctly cool/blue light

    # Fill glow: softer, broader — gives depth to mid-zones
    fill_dist = np.sqrt((xs - 0.5) ** 2 + (ys - 0.48) ** 2)
    fill_dist = fill_dist / fill_dist.max()
    fill = np.clip(1.0 - fill_dist, 0, 1) ** 2.0 * 15
    r = r + fill * 0.5
    g = g + fill * 0.5
    b = b + fill * 0.9

    # Vignette: strong edge darkening
    vignette = 1.0 - (fill_dist ** 1.2 * 0.55)
    r = r * vignette
    g = g * vignette
    b = b * vignette

    noise = np.random.normal(0, 2.0, (height, width)).astype(np.float32)
    r = np.clip(r + noise, 0, 255)
    g = np.clip(g + noise, 0, 255)
    b = np.clip(b + noise, 0, 255)

    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
    return Image.fromarray(rgb, "RGB")


def _generate_deep_gradient(width: int, height: int) -> Image.Image:
    """Deep gradient: black top → clearly visible deep navy/indigo at bottom.

    You can SEE the color — dark but unmistakably not just black.
    """
    palettes = [
        ((4, 4, 8),   (22, 32, 72)),     # black → deep navy (strong)
        ((4, 4, 8),   (14, 36, 56)),     # black → deep teal-blue
        ((4, 4, 10),  (30, 20, 62)),     # black → blue-violet
        ((4, 4, 8),   (20, 28, 65)),     # black → midnight indigo
    ]
    top_color, bottom_color = random.choice(palettes)

    ys = np.linspace(0, 1, height, dtype=np.float32).reshape(-1, 1)
    xs = np.linspace(0, 1, width, dtype=np.float32).reshape(1, -1)

    # Ease-in: top stays black, color builds from ~40% down
    t = ys ** 1.2

    r = top_color[0] + (bottom_color[0] - top_color[0]) * t
    g = top_color[1] + (bottom_color[1] - top_color[1]) * t
    b = top_color[2] + (bottom_color[2] - top_color[2]) * t

    # Center glow — keeps text readable against the darker upper half
    cx, cy = 0.5, 0.44
    dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    dist = dist / dist.max()
    glow = np.clip(1.0 - dist, 0, 1) ** 2 * 14
    r = r + glow * 0.5
    g = g + glow * 0.5
    b = b + glow * 0.9  # blue-toned glow

    # Mild vignette
    vignette = 1.0 - (dist ** 1.5 * 0.25)
    r = r * vignette
    g = g * vignette
    b = b * vignette

    noise = np.random.normal(0, 2.0, (height, width)).astype(np.float32)
    r = np.clip(r + noise, 0, 255)
    g = np.clip(g + noise, 0, 255)
    b = np.clip(b + noise, 0, 255)

    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
    return Image.fromarray(rgb, "RGB")


def _generate_textured_dark(width: int, height: int) -> Image.Image:
    """Textured dark: deep indigo base with visible texture.

    Color is subtle but present. Vertical streaks + noise = not flat.
    """
    ys = np.linspace(0, 1, height, dtype=np.float32).reshape(-1, 1)
    xs = np.linspace(0, 1, width, dtype=np.float32).reshape(1, -1)

    # Dark base with visible indigo tint + slight gradient
    r = np.full((height, width), 10.0, dtype=np.float32) + ys * 5
    g = np.full((height, width), 10.0, dtype=np.float32) + ys * 6
    b = np.full((height, width), 20.0, dtype=np.float32) + ys * 12  # indigo presence

    # Vertical streaks: column-wise brightness variation
    col_variation = np.random.normal(0, 1.2, (1, width)).astype(np.float32)
    kernel_size = 61
    kernel = np.ones(kernel_size, dtype=np.float32) / kernel_size
    col_variation = np.convolve(col_variation.ravel(), kernel, mode="same").reshape(1, -1)
    col_variation = col_variation * 5.0

    r = r + col_variation * 0.6
    g = g + col_variation * 0.6
    b = b + col_variation * 1.0  # streaks carry the blue tone

    # Slow horizontal undulation: broad brightness bands
    row_variation = np.sin(ys * np.pi * 3.5) * 2.5
    r = r + row_variation
    g = g + row_variation
    b = b + row_variation

    # Center glow for text
    cx, cy = 0.5, 0.44
    dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    dist = dist / dist.max()
    glow = np.clip(1.0 - dist, 0, 1) ** 2 * 10
    r = r + glow
    g = g + glow
    b = b + glow * 0.85

    # Vignette
    vignette = 1.0 - (dist ** 1.5 * 0.35)
    r = r * vignette
    g = g * vignette
    b = b * vignette

    # Stronger fine noise: the defining texture of this style
    noise = np.random.normal(0, 3.5, (height, width)).astype(np.float32)
    r = np.clip(r + noise, 0, 255)
    g = np.clip(g + noise, 0, 255)
    b = np.clip(b + noise, 0, 255)

    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
    return Image.fromarray(rgb, "RGB")


def _load_background_image(bg_dir: Path, width: int, height: int) -> Image.Image | None:
    """Load a random background image from directory, resized to fit."""
    if not bg_dir.exists():
        return None
    images = [
        f for f in bg_dir.iterdir()
        if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp", ".webp")
    ]
    if not images:
        return None

    chosen = random.choice(images)
    logger.info("Using background image: %s", chosen.name)
    try:
        img = Image.open(chosen).convert("RGB")
        img = img.resize((width, height), Image.LANCZOS)
        return img
    except Exception as e:
        logger.warning("Failed to load background image %s: %s", chosen, e)
        return None


# ---------------------------------------------------------------------------
# Semantic line breaking
# ---------------------------------------------------------------------------

def _semantic_split(text: str) -> list[str]:
    """Split text at semantic boundaries (sentence ends, semicolons, em-dashes).

    Returns candidate line groups. Falls back to the full text if no split found.
    """
    parts = re.split(r'(?<=[.!?;])\s+|(?<=\.\")\s+', text)
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) >= 2:
        return parts
    return [text]


def _smart_wrap(
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    """Wrap text with semantic-aware line breaks.

    Priority: sentence/clause boundaries > word wrap.
    Target: 1-3 lines, balanced width.
    """
    # Try semantic split first
    semantic_lines = _semantic_split(text)

    # Check if semantic lines all fit
    if len(semantic_lines) >= 2:
        all_fit = all(font.getlength(line) <= max_width for line in semantic_lines)
        if all_fit and len(semantic_lines) <= 4:
            return semantic_lines

    # If semantic split produces lines that are too long, wrap each
    if len(semantic_lines) >= 2:
        result = []
        for seg in semantic_lines:
            if font.getlength(seg) <= max_width:
                result.append(seg)
            else:
                result.extend(_pixel_wrap(seg, font, max_width))
        if len(result) <= 5:
            return result

    # Fall back to pixel-based word wrap
    return _pixel_wrap(text, font, max_width)


def _pixel_wrap(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Word-wrap text to fit within max_width pixels, balancing line widths."""
    avg_char_width = font.getlength("M")
    chars_per_line = max(int(max_width / avg_char_width), 10)

    lines = textwrap.wrap(text, width=chars_per_line)

    for _ in range(8):
        too_wide = any(font.getlength(line) > max_width for line in lines)
        if not too_wide:
            break
        chars_per_line = max(chars_per_line - 2, 5)
        lines = textwrap.wrap(text, width=chars_per_line)

    return lines


# ---------------------------------------------------------------------------
# Font sizing
# ---------------------------------------------------------------------------

def _compute_font_size(
    text: str,
    width: int,
    height: int,
    config: dict[str, Any],
    style_scale: float = 1.0,
) -> int:
    """Compute font size with short-quote boost.

    Short quotes (<=30 chars) get an extra 10-15% boost on top of the base size.
    """
    length = len(text)
    if length <= 25:
        base = 88
    elif length <= 40:
        base = 78
    elif length <= 60:
        base = 68
    elif length <= 90:
        base = 58
    elif length <= 120:
        base = 50
    else:
        base = 44

    # Short quote boost: extra 10-15% for very short text
    if length <= 20:
        base = int(base * 1.15)
    elif length <= 30:
        base = int(base * 1.10)

    # Config override
    override = config.get("quote_font_size")
    if override:
        base = override

    scale = min(width / 1920, height / 1080) * style_scale
    return max(int(base * scale), 24)


# ---------------------------------------------------------------------------
# Vertical offset by quote type
# ---------------------------------------------------------------------------

def _compute_vertical_offset(
    text: str,
    line_count: int,
    config: dict[str, Any],
) -> float:
    """Compute vertical offset based on quote length and line count.

    - Short quotes (1-2 lines): slightly above center (-0.03)
    - Medium quotes (3 lines): near center (-0.01)
    - Long quotes (4+ lines): true center (0.0)
    """
    config_offset = config.get("vertical_offset")
    if config_offset is not None:
        return config_offset

    length = len(text)
    if line_count <= 2 and length <= 50:
        return -0.03
    elif line_count <= 3:
        return -0.015
    else:
        return 0.0


# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------

def generate_wallpaper(
    quote: dict[str, Any],
    config: dict[str, Any],
    base_dir: Path,
    output_suffix: str = "",
    style_preset: str | None = None,
    author_size_ratio_override: float | None = None,
    bg_style: str = "default",
) -> Path:
    """Generate wallpaper image and return the output path.

    Args:
        output_suffix: appended before extension (e.g. "_v2" -> wallpaper_today_v2.jpg)
        style_preset: one of "refined", "larger", "serif" for variant generation.
                      If None, auto-selects based on quote characteristics.
        author_size_ratio_override: override author size ratio for comparison.
        bg_style: background style — "default", "spotlight", "deep_gradient", "textured_dark".
    """
    width = config.get("wallpaper_width", 1920)
    height = config.get("wallpaper_height", 1080)
    output_rel = config.get("output_path", "output/wallpaper_today.jpg")

    # Apply suffix for variants
    if output_suffix:
        p = Path(output_rel)
        output_rel = str(p.with_stem(p.stem + output_suffix))

    output_path = base_dir / output_rel
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Resolve style preset — auto-select if not specified
    if style_preset is None:
        style_preset = select_best_style(quote)
    preset = STYLE_PRESETS.get(style_preset, STYLE_PRESETS["refined"])
    size_scale = preset["size_scale"]

    # Background
    bg: Image.Image | None = None
    if config.get("use_background_images", False):
        bg_dir = base_dir / config.get("background_image_dir", "assets/backgrounds")
        bg = _load_background_image(bg_dir, width, height)

    if bg is None:
        bg = _generate_bg(width, height, bg_style)

    img = bg.copy()

    # Apply overlay if using background image
    if config.get("use_background_images", False):
        opacity = config.get("overlay_opacity", 0.55)
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, int(255 * opacity)))
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        img = img.convert("RGB")

    draw = ImageDraw.Draw(img)

    text = quote["text"]
    author = quote.get("author", "")
    show_author = config.get("show_author", True) and bool(author)
    need_jp = _has_cjk(text) or _has_cjk(author)

    # Font sizing
    quote_font_size = _compute_font_size(text, width, height, config, size_scale)
    author_ratio = author_size_ratio_override or config.get("author_size_ratio", 0.26)
    author_font_size = max(int(quote_font_size * author_ratio), 14)

    font_quote_path = config.get("font_quote")
    font_author_path = config.get("font_author")

    quote_font = _resolve_font(
        font_quote_path, quote_font_size, need_jp,
        candidates=preset["font_candidates"],
    )
    author_font = _resolve_font(
        font_author_path, author_font_size, need_jp,
        candidates=preset["font_author_candidates"],
    )

    # Layout
    margin_x = int(width * 0.14)
    max_text_width = width - 2 * margin_x

    # Smart wrap
    lines = _smart_wrap(text, quote_font, max_text_width)

    # Line heights
    line_spacing_ratio = config.get("line_spacing_ratio", 0.50)
    line_spacing = int(quote_font_size * line_spacing_ratio)
    line_heights: list[int] = []
    for line in lines:
        bbox = quote_font.getbbox(line)
        line_heights.append(bbox[3] - bbox[1])

    total_quote_height = sum(line_heights) + line_spacing * max(len(lines) - 1, 0)

    # Author spacing
    author_gap_ratio = config.get("author_gap_ratio", 1.0)
    author_gap = int(quote_font_size * author_gap_ratio)
    author_block_height = 0
    if show_author:
        author_text = f"— {author}"
        a_bbox = author_font.getbbox(author_text)
        author_block_height = author_gap + (a_bbox[3] - a_bbox[1])

    total_height = total_quote_height + author_block_height

    # Translated label
    show_translated = (
        config.get("show_translated_label", False)
        and quote.get("translated", False)
    )
    if show_translated:
        total_height += int(author_font_size * 1.8)

    # Vertical offset — adaptive by quote type
    vertical_offset = _compute_vertical_offset(text, len(lines), config)
    start_y = int((height - total_height) / 2 + height * vertical_offset)
    start_y = max(start_y, int(height * 0.05))

    # Draw quote lines — centered
    text_color = (240, 240, 240)
    author_color = preset.get("author_color", (145, 145, 150))
    y = start_y

    for i, line in enumerate(lines):
        line_width = quote_font.getlength(line)
        x = (width - line_width) / 2
        draw.text((x, y), line, font=quote_font, fill=text_color)
        y += line_heights[i] + line_spacing

    # Draw author — subtle, offset from text
    if show_author:
        y += author_gap - line_spacing  # replace last line_spacing with author_gap
        author_text = f"— {author}"
        author_width = author_font.getlength(author_text)
        # Right of center, elegant positioning
        ax = (width + author_width) / 2 - author_width + int(width * 0.02)
        ax = max(margin_x, min(ax, width - margin_x - author_width))
        draw.text((ax, y), author_text, font=author_font, fill=author_color)
        y += int(author_block_height - author_gap)

    # Translated label (very subtle)
    if show_translated:
        y += int(author_font_size * 0.8)
        label = "(translated)"
        label_font = _resolve_font(
            font_author_path, max(int(author_font_size * 0.75), 11), False,
        )
        label_color = (100, 100, 105)
        lw = label_font.getlength(label)
        draw.text(((width - lw) / 2, y), label, font=label_font, fill=label_color)

    # Save
    img.save(str(output_path), "JPEG", quality=95)
    logger.info("Wallpaper saved to %s (style=%s)", output_path, style_preset)
    return output_path


def generate_variants(
    quote: dict[str, Any],
    config: dict[str, Any],
    base_dir: Path,
) -> list[Path]:
    """Generate multiple style variants for preview comparison.

    Output filenames include quote ID: {quote_id}_v1_refined.jpg etc.
    """
    quote_id = quote.get("id", "unknown")
    variants = [
        (f"_{quote_id}_v1_refined", "refined"),
        (f"_{quote_id}_v2_larger", "larger"),
        (f"_{quote_id}_v3_serif", "serif"),
    ]
    paths: list[Path] = []
    for suffix, preset in variants:
        path = generate_wallpaper(
            quote, config, base_dir,
            output_suffix=suffix, style_preset=preset,
        )
        paths.append(path)
        logger.info("Variant '%s' saved: %s", preset, path)
    return paths


def generate_author_comparison(
    quote: dict[str, Any],
    config: dict[str, Any],
    base_dir: Path,
) -> list[Path]:
    """Generate author size comparison variants (0.24 / 0.26 / 0.28)."""
    quote_id = quote.get("id", "unknown")
    ratios = [0.24, 0.26, 0.28]
    paths: list[Path] = []
    for ratio in ratios:
        suffix = f"_{quote_id}_author{int(ratio * 100)}"
        path = generate_wallpaper(
            quote, config, base_dir,
            output_suffix=suffix,
            author_size_ratio_override=ratio,
        )
        paths.append(path)
        logger.info("Author ratio %.2f saved: %s", ratio, path)
    return paths


def generate_bg_comparison(
    quote: dict[str, Any],
    config: dict[str, Any],
    base_dir: Path,
) -> list[Path]:
    """Generate background style comparison: spotlight / deep_gradient / textured_dark.

    All use serif font preset. Output: wallpaper_{quote_id}_{bg_style}.jpg
    """
    quote_id = quote.get("id", "unknown")
    bg_styles = ["spotlight", "deep_gradient", "textured_dark"]
    paths: list[Path] = []
    for bg in bg_styles:
        suffix = f"_{quote_id}_{bg}"
        path = generate_wallpaper(
            quote, config, base_dir,
            output_suffix=suffix,
            style_preset="serif",
            bg_style=bg,
        )
        paths.append(path)
        logger.info("BG style '%s' saved: %s", bg, path)
    return paths


def generate_font_comparison(
    quote: dict[str, Any],
    config: dict[str, Any],
    base_dir: Path,
    bg_style: str = "deep_gradient",
) -> list[Path]:
    """Generate font comparison: Georgia / Garamond / Palatino / Book Antiqua."""
    quote_id = quote.get("id", "unknown")
    fonts = [
        ("serif", "georgia"),
        ("garamond", "garamond"),
        ("palatino", "palatino"),
        ("bookantiqua", "bookantiqua"),
    ]
    paths: list[Path] = []
    for preset_name, label in fonts:
        suffix = f"_{quote_id}_font_{label}"
        path = generate_wallpaper(
            quote, config, base_dir,
            output_suffix=suffix,
            style_preset=preset_name,
            bg_style=bg_style,
        )
        paths.append(path)
        logger.info("Font '%s' saved: %s", label, path)
    return paths
