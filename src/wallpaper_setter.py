"""Set Windows desktop wallpaper."""

import logging
import platform
from pathlib import Path

logger = logging.getLogger(__name__)

SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02


def set_wallpaper(image_path: Path) -> bool:
    """Set the desktop wallpaper. Windows only — no-op with warning on other platforms."""
    if platform.system() != "Windows":
        logger.warning(
            "set_wallpaper: not on Windows (platform=%s). Skipping wallpaper update.",
            platform.system(),
        )
        return False

    import ctypes
    abs_path = str(image_path.resolve())
    try:
        result = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER,
            0,
            abs_path,
            SPIF_UPDATEINIFILE | SPIF_SENDCHANGE,
        )
        if result:
            logger.info("Wallpaper set to %s", abs_path)
            return True
        else:
            logger.error("SystemParametersInfoW returned 0.")
            return False
    except Exception as e:
        logger.error("Failed to set wallpaper: %s", e, exc_info=True)
        return False
