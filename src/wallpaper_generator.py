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

# Style presets for variant generation
STYLE_PRESETS: dict[str, dict[str, Any]] = {
    "refined": {
        "font_candidates": FONTS_LIGHT,
        "font_author_candidates": FONTS_REGULAR,
        "size_scale": 1.0,
        "description": "Clean sans-serif light",
    },
    "larger": {
        "font_candidates": FONTS_LIGHT,
        "font_author_candidates": FONTS_REGULAR,
        "size_scale": 1.15,
        "description": "Larger sans-serif light",
    },
    "serif": {
        "font_candidates": FONTS_SERIF,
        "font_author_candidates": FONTS_SERIF,
        "size_scale": 0.85,
        "description": "Classic serif",
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
# Background generation
# ---------------------------------------------------------------------------

def _generate_gradient(width: int, height: int) -> Image.Image:
    """Generate a refined dark background with radial gradient, vignette, and subtle noise."""
    palettes = [
        ((12, 12, 20), (28, 25, 42)),     # deep navy to dark purple
        ((8, 8, 12),   (22, 22, 32)),      # near black to dark slate
        ((14, 10, 18), (8, 18, 30)),       # dark plum to dark blue
        ((6, 8, 14),   (20, 20, 30)),      # charcoal to slate
        ((10, 8, 14),  (16, 22, 26)),      # dark wine to dark teal
    ]
    top_color, bottom_color = random.choice(palettes)

    # Use numpy for fast pixel operations
    ys = np.linspace(0, 1, height, dtype=np.float32).reshape(-1, 1)
    xs = np.linspace(0, 1, width, dtype=np.float32).reshape(1, -1)

    # Linear vertical gradient
    r = top_color[0] + (bottom_color[0] - top_color[0]) * ys
    g = top_color[1] + (bottom_color[1] - top_color[1]) * ys
    b = top_color[2] + (bottom_color[2] - top_color[2]) * ys

    # Radial gradient: subtle lighter center
    cx, cy = 0.5, 0.45  # slightly above center
    dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    dist = dist / dist.max()
    radial_boost = np.clip(1.0 - dist, 0, 1) ** 2 * 12  # soft center glow

    r = r + radial_boost
    g = g + radial_boost
    b = b + radial_boost * 0.8  # slightly warm center

    # Vignette: darken edges
    vignette = 1.0 - (dist ** 1.5 * 0.35)
    r = r * vignette
    g = g * vignette
    b = b * vignette

    # Subtle noise for texture
    noise = np.random.normal(0, 1.8, (height, width)).astype(np.float32)
    r = np.clip(r + noise, 0, 255)
    g = np.clip(g + noise, 0, 255)
    b = np.clip(b + noise, 0, 255)

    # Assemble RGB array
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
    # Pattern: split at ". " or "; " or " — " or " – " or " - " (when used as separator)
    # but keep the delimiter with the preceding segment
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
    """Compute font size — 15-30% larger than v1, config-overridable."""
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

    # Config override
    override = config.get("quote_font_size")
    if override:
        base = override

    scale = min(width / 1920, height / 1080) * style_scale
    return max(int(base * scale), 24)


# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------

def generate_wallpaper(
    quote: dict[str, Any],
    config: dict[str, Any],
    base_dir: Path,
    output_suffix: str = "",
    style_preset: str | None = None,
) -> Path:
    """Generate wallpaper image and return the output path.

    Args:
        output_suffix: appended before extension (e.g. "_v2" -> wallpaper_today_v2.jpg)
        style_preset: one of "refined", "larger", "serif" for variant generation
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

    # Resolve style preset
    preset = STYLE_PRESETS.get(style_preset or "refined", STYLE_PRESETS["refined"])
    size_scale = preset["size_scale"]

    # Background
    bg: Image.Image | None = None
    if config.get("use_background_images", False):
        bg_dir = base_dir / config.get("background_image_dir", "assets/backgrounds")
        bg = _load_background_image(bg_dir, width, height)

    if bg is None:
        bg = _generate_gradient(width, height)

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
    author_ratio = config.get("author_size_ratio", 0.28)
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

    # Vertical centering with configurable offset
    # Shift slightly above center for large text blocks, center for smaller ones
    vertical_offset = config.get("vertical_offset", -0.02)
    fill_ratio = total_height / height
    if fill_ratio < 0.15:
        # Small text block: keep closer to true center
        vertical_offset = min(vertical_offset + 0.01, 0.0)
    start_y = int((height - total_height) / 2 + height * vertical_offset)
    start_y = max(start_y, int(height * 0.05))

    # Draw quote lines — centered
    text_color = (240, 240, 240)
    author_color = (155, 155, 160)
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
    logger.info("Wallpaper saved to %s (%s)", output_path, preset.get("description", ""))
    return output_path


def generate_variants(
    quote: dict[str, Any],
    config: dict[str, Any],
    base_dir: Path,
) -> list[Path]:
    """Generate multiple style variants for preview comparison."""
    variants = [
        ("_v1_refined", "refined"),
        ("_v2_larger", "larger"),
        ("_v3_serif", "serif"),
    ]
    paths: list[Path] = []
    for suffix, preset in variants:
        path = generate_wallpaper(quote, config, base_dir, output_suffix=suffix, style_preset=preset)
        paths.append(path)
        logger.info("Variant '%s' saved: %s", preset, path)
    return paths
