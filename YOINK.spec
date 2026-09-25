# Folder-based build: Chromium remains unpacked beside the Qt/Python runtime.
from pathlib import Path
import playwright
from PyInstaller.utils.hooks import collect_submodules, copy_metadata

root = Path(SPECPATH)
qa = globals().get("release_qa", False)
name = "YOINK-QA" if qa else "YOINK"
licenses = []
for distribution in ("playwright", "PySide6", "PySide6_Essentials", "PySide6_Addons",
                     "shiboken6", "Markdown", "greenlet", "pyee", "typing_extensions"):
    licenses += copy_metadata(distribution)
browser_root = Path(playwright.__file__).parent / "driver/package/.local-browsers"
if not list(browser_root.glob("chromium_headless_shell-*/chrome-headless-shell-win*/chrome-headless-shell.exe")):
    raise RuntimeError("Run build_windows.ps1 first: bundled Chromium headless shell is missing")

a = Analysis(
    [str(root / ("packaging/check_release.py" if qa else "packaging/entry.py"))],
    pathex=[str(root), str(root / "tests")] if qa else [str(root)],
    binaries=[],
    datas=[(str(root / "assets/fonts"), "assets/fonts"),
           (str(root / "assets/icon/yoink.ico"), "assets/icon"),
           (str(root / "assets/shutdown.gif"), "assets")] + licenses,
    hiddenimports=collect_submodules("markdown.extensions"),
    hookspath=[], runtime_hooks=[], excludes=[], noarchive=False,
)
# The upstream hook collects every installed browser, including full Chromium
# left by earlier builds. Filter destinations in both TOCs without deleting the
# developer's browser installation. Keep the headless shell and all other files.
def is_full_chromium(destination):
    parts = destination.replace("\\", "/").split("/")
    return (parts[:4] == ["playwright", "driver", "package", ".local-browsers"]
            and len(parts) > 4 and parts[4].startswith("chromium-"))

a.datas = [entry for entry in a.datas if not is_full_chromium(entry[0])]
a.binaries = [entry for entry in a.binaries if not is_full_chromium(entry[0])]
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name=name,
          debug=False, strip=False, upx=False, console=qa,
          icon=str(root / "assets/icon/yoink.ico"),
          version=str(root / "packaging/version_info.txt"))
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name=name)
