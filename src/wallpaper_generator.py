"""Generate a minimal quote wallpaper image using Pillow."""

import logging
import random
import textwrap
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageFilter

logger = logging.getLogger(__name__)

# Windows fallback fonts (tried in order)
FALLBACK_FONTS = [
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/calibri.ttf",
]

# Japanese-capable fallback fonts
FALLBACK_FONTS_JP = [
    "C:/Windows/Fonts/YuGothM.ttc",
    "C:/Windows/Fonts/yugothic.ttf",
    "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
]


def _resolve_font(specified: str | None, size: int, need_jp: bool = False) -> ImageFont.FreeTypeFont:
    """Resolve a font path to a Pillow font object with fallbacks."""
    candidates: list[str] = []
    if specified:
        candidates.append(specified)
    if need_jp:
        candidates.extend(FALLBACK_FONTS_JP)
    candidates.extend(FALLBACK_FONTS)

    for path in candidates:
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


def _generate_gradient(width: int, height: int) -> Image.Image:
    """Generate a dark gradient background."""
    # Pick a subtle color palette
    palettes = [
        ((15, 15, 25), (35, 30, 50)),      # deep navy to dark purple
        ((10, 10, 10), (30, 30, 40)),       # near black to dark gray
        ((20, 15, 25), (10, 20, 35)),       # dark plum to dark blue
        ((5, 10, 15), (25, 25, 35)),        # charcoal to slate
        ((15, 10, 20), (20, 30, 30)),       # dark wine to dark teal
    ]
    top_color, bottom_color = random.choice(palettes)

    img = Image.new("RGB", (width, height))
    pixels = img.load()
    for y in range(height):
        ratio = y / max(height - 1, 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        for x in range(width):
            pixels[x, y] = (r, g, b)
    return img


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


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Word-wrap text to fit within max_width pixels."""
    # Start with a rough char estimate then refine
    avg_char_width = font.getlength("M")
    chars_per_line = max(int(max_width / avg_char_width), 10)

    lines = textwrap.wrap(text, width=chars_per_line)

    # Refine: if any line is too wide, reduce wrap width
    for _ in range(5):
        too_wide = False
        for line in lines:
            if font.getlength(line) > max_width:
                too_wide = True
                break
        if not too_wide:
            break
        chars_per_line = max(chars_per_line - 3, 5)
        lines = textwrap.wrap(text, width=chars_per_line)

    return lines


def _compute_font_size(text: str, width: int, height: int) -> int:
    """Compute an appropriate font size for the quote text."""
    length = len(text)
    if length <= 30:
        base = 72
    elif length <= 60:
        base = 60
    elif length <= 100:
        base = 48
    else:
        base = 40

    # Scale relative to 1920x1080
    scale = min(width / 1920, height / 1080)
    return max(int(base * scale), 20)


def generate_wallpaper(
    quote: dict[str, Any],
    config: dict[str, Any],
    base_dir: Path,
) -> Path:
    """Generate wallpaper image and return the output path."""
    width = config.get("wallpaper_width", 1920)
    height = config.get("wallpaper_height", 1080)
    output_rel = config.get("output_path", "output/wallpaper_today.jpg")
    output_path = base_dir / output_rel
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Background
    bg: Image.Image | None = None
    if config.get("use_background_images", False):
        bg_dir = base_dir / config.get("background_image_dir", "assets/backgrounds")
        bg = _load_background_image(bg_dir, width, height)

    if bg is None:
        bg = _generate_gradient(width, height)

    img = bg.copy()
    draw = ImageDraw.Draw(img)

    # Apply overlay if using background image
    if config.get("use_background_images", False) and bg is not None:
        opacity = config.get("overlay_opacity", 0.55)
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, int(255 * opacity)))
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        img = img.convert("RGB")
        draw = ImageDraw.Draw(img)

    text = quote["text"]
    author = quote.get("author", "")
    show_author = config.get("show_author", True) and author
    need_jp = _has_cjk(text) or _has_cjk(author)

    # Font sizing
    quote_font_size = _compute_font_size(text, width, height)
    author_font_size = max(int(quote_font_size * 0.35), 14)

    font_quote_path = config.get("font_quote")
    font_author_path = config.get("font_author")

    quote_font = _resolve_font(font_quote_path, quote_font_size, need_jp)
    author_font = _resolve_font(font_author_path, author_font_size, need_jp)

    # Layout constants
    margin_x = int(width * 0.12)
    max_text_width = width - 2 * margin_x

    # Wrap quote text
    lines = _wrap_text(text, quote_font, max_text_width)

    # Calculate total text block height
    line_spacing = int(quote_font_size * 0.4)
    line_heights = []
    for line in lines:
        bbox = quote_font.getbbox(line)
        line_heights.append(bbox[3] - bbox[1])

    total_quote_height = sum(line_heights) + line_spacing * (len(lines) - 1)
    author_height = 0
    if show_author:
        author_text = f"— {author}"
        a_bbox = author_font.getbbox(author_text)
        author_height = (a_bbox[3] - a_bbox[1]) + int(quote_font_size * 0.8)

    total_height = total_quote_height + author_height

    # Translated label
    show_translated = (
        config.get("show_translated_label", False)
        and quote.get("translated", False)
    )
    translated_height = 0
    if show_translated:
        translated_height = int(author_font_size * 1.5)
        total_height += translated_height

    # Center vertically (slightly above center)
    start_y = int((height - total_height) / 2) - int(height * 0.03)
    start_y = max(start_y, int(height * 0.1))

    # Draw quote lines (centered)
    text_color = (235, 235, 235)
    author_color = (180, 180, 180)
    y = start_y

    for i, line in enumerate(lines):
        line_width = quote_font.getlength(line)
        x = (width - line_width) / 2
        draw.text((x, y), line, font=quote_font, fill=text_color)
        y += line_heights[i] + line_spacing

    # Draw author
    if show_author:
        y += int(quote_font_size * 0.4)
        author_text = f"— {author}"
        author_width = author_font.getlength(author_text)
        # Position: right-aligned within text area, or centered for short quotes
        if len(lines) <= 2:
            ax = (width - author_width) / 2 + int(width * 0.05)
        else:
            ax = width - margin_x - author_width
        ax = max(margin_x, min(ax, width - margin_x - author_width))
        draw.text((ax, y), author_text, font=author_font, fill=author_color)
        y += author_height

    # Translated label (small, subtle)
    if show_translated:
        label = "(translated)"
        label_font = _resolve_font(font_author_path, max(int(author_font_size * 0.8), 12), False)
        label_color = (120, 120, 120)
        lw = label_font.getlength(label)
        draw.text(((width - lw) / 2, y + 5), label, font=label_font, fill=label_color)

    # Save
    img.save(str(output_path), "JPEG", quality=95)
    logger.info("Wallpaper saved to %s", output_path)
    return output_path
