"""MVP: 名言壁紙に解説テキストを重ねた 1 枚を試作する。

既存の wallpaper_today.jpg を base にして、下部に解説を追加描画して
output/preview_commentary_<lang>.jpg として保存する。

Usage:
    python scripts/preview_with_commentary.py --lang ja   # 日本語版（default）
    python scripts/preview_with_commentary.py --lang en   # 英語版

既存の generate_wallpaper() には影響しない。
"""

import argparse
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Windows console: UTF-8 で出力（em-dash など非 cp932 文字対応）
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
BASE_IMAGE = BASE_DIR / "output" / "wallpaper_today.jpg"

# 日本語解説（Yu Gothic Light）
# 80字版（独立解説）はコメントアウトで保存。意訳版を一時的に有効化中
# COMMENTARY_JA = (
#     "単なる根性論ではない。Nietzsche が説いたのは、苦難を運命として引き受け、"
#     "自分の養分に変える姿勢である。耐えるのではなく、組み替えるのだ。"
# )
COMMENTARY_JA = "我々を殺さぬものは、ただ強くするのではない。我々を作り変える。"
FONT_CANDIDATES_JA = [
    "C:/Windows/Fonts/YuGothL.ttc",
    "C:/Windows/Fonts/YuGothM.ttc",
    "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
]

# 英語解説（Segoe UI Light、名言本文と同系統）
COMMENTARY_EN = (
    "Not a creed of endurance. Nietzsche set this maxim inside "
    "\"the school of war\" — a discipline, not a consolation. "
    "The strong do not merely outlast what wounds them; "
    "they take it on as fate and convert it into substance. "
    "To suffer well is to compose."
)
FONT_CANDIDATES_EN = [
    "C:/Windows/Fonts/segoeuil.ttf",   # Segoe UI Light
    "C:/Windows/Fonts/segoeuisl.ttf",  # Segoe UI Semilight
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/calibril.ttf",
    "C:/Windows/Fonts/arial.ttf",
]

# 言語別設定
LANG_CONFIG = {
    "ja": {
        "commentary": COMMENTARY_JA,
        "fonts": FONT_CANDIDATES_JA,
        "font_size": 28,
        "output_name": "preview_commentary_ja.jpg",
    },
    "en": {
        "commentary": COMMENTARY_EN,
        "fonts": FONT_CANDIDATES_EN,
        "font_size": 26,  # 英語は文字幅が広いので少し小さめ
        "output_name": "preview_commentary_en.jpg",
    },
}

# 共通レイアウト
LINE_SPACING = 12
TEXT_COLOR = (160, 160, 165)
MARGIN_BOTTOM = 90
MAX_WIDTH_RATIO = 0.70


def _resolve_font(candidates: list[str], size: int) -> ImageFont.FreeTypeFont:
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _wrap_japanese(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """句読点優先 → 文字単位の改行（日本語向け）"""
    segments = [s for s in re.split(r'(?<=[。、])', text) if s]
    lines: list[str] = []
    current = ""

    def _width(s: str) -> int:
        bbox = draw.textbbox((0, 0), s, font=font)
        return bbox[2] - bbox[0]

    for seg in segments:
        candidate = current + seg
        if _width(candidate) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
                current = ""
            for ch in seg:
                test = current + ch
                if _width(test) <= max_width:
                    current = test
                else:
                    if current:
                        lines.append(current)
                    current = ch

    if current:
        lines.append(current)
    return lines


def _wrap_english(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """単語境界で改行（英語向け）"""
    words = text.split()
    lines: list[str] = []
    current = ""

    def _width(s: str) -> int:
        bbox = draw.textbbox((0, 0), s, font=font)
        return bbox[2] - bbox[0]

    for word in words:
        candidate = (current + " " + word).strip()
        if _width(candidate) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)
    return lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate commentary overlay preview")
    parser.add_argument("--lang", choices=["ja", "en"], default="ja",
                        help="Commentary language (default: ja)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = LANG_CONFIG[args.lang]
    output_path = BASE_DIR / "output" / cfg["output_name"]

    if not BASE_IMAGE.exists():
        print(f"Error: base image not found: {BASE_IMAGE}")
        sys.exit(1)

    img = Image.open(BASE_IMAGE).convert("RGB")
    width, height = img.size
    draw = ImageDraw.Draw(img)

    font = _resolve_font(cfg["fonts"], cfg["font_size"])
    max_width = int(width * MAX_WIDTH_RATIO)

    if args.lang == "ja":
        lines = _wrap_japanese(cfg["commentary"], font, max_width, draw)
    else:
        lines = _wrap_english(cfg["commentary"], font, max_width, draw)

    line_height = cfg["font_size"] + LINE_SPACING
    total_height = len(lines) * line_height
    start_y = height - MARGIN_BOTTOM - total_height

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = start_y + i * line_height
        draw.text((x, y), line, font=font, fill=TEXT_COLOR)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=95)

    print(f"Saved: {output_path}")
    print(f"Lang: {args.lang}")
    print(f"Image size: {width}x{height}")
    print(f"Max text width: {max_width}px")
    print(f"Lines: {len(lines)}")
    for i, line in enumerate(lines):
        print(f"  {i + 1}: {line}")


if __name__ == "__main__":
    main()
