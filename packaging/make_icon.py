"""Derive Windows frames without editing or cropping the locked master."""
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parent.parent
with Image.open(root / "assets/icon/yoink-master.png") as source:
    source.convert("RGBA").save(
        root / "assets/icon/yoink.ico", format="ICO",
        sizes=[(n, n) for n in (16, 20, 24, 32, 40, 48, 64, 128, 256)],
    )
