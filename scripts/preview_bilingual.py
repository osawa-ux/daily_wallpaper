"""Preview bilingual mode for a few sample quotes."""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.config_loader import load_config, load_quotes
from src.wallpaper_generator import generate_wallpaper

config = load_config(BASE)
quotes = {q["id"]: q for q in load_quotes(BASE)}

targets = ["q001", "q002", "q003"]
for qid in targets:
    q = quotes[qid]
    out_rel = f"output/previews/bilingual/{qid}_bilingual.jpg"
    cfg = {**config, "output_path": out_rel}
    path = generate_wallpaper(q, cfg, BASE, bilingual=True)
    print(f"Saved: {path}")

    # Also save English-only for side-by-side comparison
    out_rel_en = f"output/previews/bilingual/{qid}_en_only.jpg"
    cfg_en = {**config, "output_path": out_rel_en}
    path_en = generate_wallpaper(q, cfg_en, BASE, bilingual=False)
    print(f"Saved: {path_en}")
