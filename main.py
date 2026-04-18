#!/usr/bin/env python3
"""Daily Minimal English Quote Wallpaper — entry point."""

import argparse
import io
import logging
import sys
import traceback
from pathlib import Path

# Fix Windows console encoding for Unicode output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent


def _setup_logging(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stream_handler = logging.StreamHandler(
        io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(str(log_path), encoding="utf-8"),
            stream_handler,
        ],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a minimal English quote wallpaper and set it as desktop background."
    )
    parser.add_argument("--mood", type=str, default=None,
                        help="Mood adjustment (tired, motivated, stressed, uncertain, brave)")
    parser.add_argument("--preview", action="store_true",
                        help="Generate image only, do not set wallpaper")
    parser.add_argument("--quote-id", type=str, default=None,
                        help="Force a specific quote by ID (e.g. q001)")
    parser.add_argument("--no-set-wallpaper", action="store_true",
                        help="Generate image file only, do not change wallpaper")
    parser.add_argument("--variants", action="store_true",
                        help="Generate v1/v2/v3 style variants for comparison")
    parser.add_argument("--compare-author", action="store_true",
                        help="Generate author size comparison (0.24/0.26/0.28)")
    parser.add_argument("--compare-bg", action="store_true",
                        help="Generate background style comparison")
    parser.add_argument("--compare-font", action="store_true",
                        help="Generate font comparison (Georgia/Garamond/Palatino/BookAntiqua)")
    parser.add_argument("--demo", action="store_true",
                        help="Generate demo wallpapers for each routing rule")
    parser.add_argument("--explain-style", action="store_true",
                        help="Show style routing decision without generating image")
    parser.add_argument("--validate-quotes", action="store_true",
                        help="Validate quotes.json structure and data quality")
    parser.add_argument("--validate-calendar", action="store_true",
                        help="Validate calendar_assignments.json constraints and distribution")
    parser.add_argument("--force", action="store_true",
                        help="Force regeneration even if today's wallpaper is already set")
    parser.add_argument("--mode", type=str, default="calendar",
                        choices=["calendar", "random"],
                        help="Selection mode: 'calendar' (MM-DD fixed) or 'random' (weighted random). Default: calendar")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    from src.config_loader import load_config, load_quotes, validate_quotes
    from src.history_manager import load_history, save_history, add_entry
    from src.quote_selector import select_quote, select_quote_by_calendar
    from src.wallpaper_generator import (
        generate_wallpaper, generate_variants, generate_author_comparison,
        generate_bg_comparison, generate_font_comparison, generate_demo,
        select_best_style,
    )
    from src.wallpaper_setter import set_wallpaper
    from src.utils import get_current_season

    config = load_config(BASE_DIR)
    log_path = BASE_DIR / config.get("log_path", "logs/app.log")
    _setup_logging(log_path)

    logger = logging.getLogger("main")
    logger.info("=== Daily Wallpaper starting ===")

    try:
        # Validate-only mode
        if args.validate_quotes:
            results = validate_quotes(BASE_DIR, config)
            stats_prefixes = ("---", "Total", "Enabled", "Category", "Language", "Warning")
            errors = [r for r in results if r and not r.startswith(stats_prefixes)]
            print(f"Validation: {len(errors)} issue(s) found.\n")
            for line in results:
                print(f"  {line}")
            sys.exit(1 if errors else 0)

        if args.validate_calendar:
            from scripts.generate_calendar import (
                validate_calendar, print_distribution, ALL_DAYS,
            )
            cal_path = BASE_DIR / "calendar_assignments.json"
            if not cal_path.exists():
                print("calendar_assignments.json not found. Run scripts/generate_calendar.py first.")
                sys.exit(1)
            import json as _json
            cal = _json.loads(cal_path.read_text(encoding="utf-8"))
            all_qs = _json.loads((BASE_DIR / "quotes.json").read_text(encoding="utf-8"))
            by_id = {q["id"]: q for q in all_qs}
            issues = validate_calendar(cal, by_id)
            if issues:
                print(f"Calendar violations: {len(issues)}")
                for issue in issues:
                    print(f"  {issue}")
            else:
                print("All calendar constraints satisfied.")
            print(f"Days assigned: {len(cal)}/366")
            res_path = BASE_DIR / "calendar_reserve.json"
            if res_path.exists():
                reserve = _json.loads(res_path.read_text(encoding="utf-8"))
                print(f"Reserve quotes: {len(reserve)}")
            print_distribution(cal, by_id)
            sys.exit(1 if issues else 0)

        quotes = load_quotes(BASE_DIR)
        if not quotes:
            logger.error("No quotes available. Exiting.")
            print("Error: No quotes found in quotes.json.")
            sys.exit(1)

        # Demo mode: generate representative samples
        if args.demo:
            demo_paths = generate_demo(quotes, config, BASE_DIR)
            for dp in demo_paths:
                print(f"Demo: {dp}")
            print(f"Generated {len(demo_paths)} demo wallpapers.")
            logger.info("=== Done (demo) ===")
            return

        history_path = BASE_DIR / config.get("history_path", "output/history.json")
        history = load_history(history_path)
        mood = args.mood or config.get("default_mood")

        # Idempotency guard: skip if today's wallpaper was already generated.
        # Bypassed by --force, --preview, --quote-id, and visual comparison
        # modes (which are explicit testing flows).
        is_standard_run = not (
            args.force or args.preview or args.quote_id
            or args.variants or args.compare_author or args.compare_bg
            or args.compare_font or args.explain_style
        )
        if is_standard_run:
            from datetime import date
            today_iso = date.today().isoformat()
            if any(entry.get("date") == today_iso for entry in history):
                logger.info("Wallpaper already updated today (%s). Skipping.", today_iso)
                print(f"Wallpaper already updated today ({today_iso}). Use --force to override.")
                logger.info("=== Done (skipped) ===")
                return

        if args.mode == "calendar":
            quote = select_quote_by_calendar(quotes, BASE_DIR, force_id=args.quote_id)
            if quote is None:
                # Fallback to random if calendar not available
                logger.info("Calendar mode unavailable, falling back to random.")
                quote = select_quote(quotes, config, history, mood=mood, force_id=args.quote_id)
        else:
            quote = select_quote(quotes, config, history, mood=mood, force_id=args.quote_id)
        if quote is None:
            logger.error("Failed to select a quote.")
            print("Error: Could not select a quote.")
            sys.exit(1)

        logger.info("Quote: [%s] %s - %s", quote["id"], quote["text"], quote.get("author", ""))
        print(f'Selected: "{quote["text"]}"')
        if quote.get("author"):
            print(f"  - {quote['author']}")

        # Explain style mode
        if args.explain_style:
            info = select_best_style(quote, config)
            print(f"\n--- Style Routing ---")
            print(f"  quote_id:   {quote['id']}")
            print(f"  category:   {', '.join(info['categories'])}")
            print(f"  length:     {info['quote_length']} chars, {info['line_count']} lines")
            print(f"  rule:       {info['rule']}")
            print(f"  font:       {info['font_preset']}")
            print(f"  background: {info['bg_style']}")
            print(f"  reason:     {info['reason']}")
            return

        # Generate wallpaper
        if args.variants:
            variant_paths = generate_variants(quote, config, BASE_DIR)
            for vp in variant_paths:
                print(f"Variant: {vp}")
            output_path = variant_paths[0]
        elif args.compare_font:
            variant_paths = generate_font_comparison(quote, config, BASE_DIR)
            for vp in variant_paths:
                print(f"Font compare: {vp}")
            output_path = variant_paths[0]
        elif args.compare_bg:
            variant_paths = generate_bg_comparison(quote, config, BASE_DIR)
            for vp in variant_paths:
                print(f"BG compare: {vp}")
            output_path = variant_paths[0]
        elif args.compare_author:
            variant_paths = generate_author_comparison(quote, config, BASE_DIR)
            for vp in variant_paths:
                print(f"Author compare: {vp}")
            output_path = variant_paths[1]
        else:
            info = select_best_style(quote, config)
            output_path = generate_wallpaper(quote, config, BASE_DIR)
            print(f"Style: {info['font_preset']} + {info['bg_style']} ({info['rule']})")
        print(f"Wallpaper: {output_path}")

        # Set wallpaper
        should_set = not args.preview and not args.no_set_wallpaper
        if should_set:
            success = set_wallpaper(output_path)
            if success:
                print("Desktop wallpaper updated.")
            else:
                print("Warning: Failed to set wallpaper (image was saved).")
        else:
            logger.info("Wallpaper setting skipped.")
            print("Wallpaper setting skipped.")

        # Save history
        season = get_current_season()
        history = add_entry(history, quote, mood, season, str(output_path))
        save_history(history_path, history)

        logger.info("=== Done ===")

    except Exception as e:
        logger.error("Unexpected error: %s", e, exc_info=True)
        print(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
