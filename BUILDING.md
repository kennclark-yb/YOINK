# YOINK — local Windows build

Your Oversized Interactions, Nicely Kept.

This is an internal build/handoff guide, not a public release README.
Windows x64; tested with Python 3.13.15. The application is a portable **folder**,
not a single-file executable or installer. Internet access is still required to
read ChatGPT shared conversations. No Python/browser installation is required
on the destination computer.

## Rebuild

From the project directory in PowerShell:

```powershell
.\build_windows.ps1
```

The default interpreter is `.venv\Scripts\python.exe`. For a fresh build environment:

```powershell
py -3.13 -m venv .venv-build
.\build_windows.ps1 -Python .\.venv-build\Scripts\python.exe
```

The script installs the pinned `requirements-build.txt`, installs the matching
Chromium with `PLAYWRIGHT_BROWSERS_PATH=0`, and runs:

```powershell
python -m PyInstaller --noconfirm --clean YOINK.spec
```

Use the script, not that last command alone: it also isolates PATH to Python and
Windows directories. Otherwise unrelated development-tool DLLs (observed with
Poppler ICU) can be collected and prevent QtGui from loading. Environment values
are restored afterward. Builds replace only generated `build/` and `dist/` output.
Close any running packaged YOINK before rebuilding it.

Open **`dist\YOINK\YOINK.exe`** normally. Distribute the entire `dist\YOINK` folder,
including `_internal`, preferably zipped. Do not distribute the QA folder.
Keep executable and `_internal` together. No shortcut/installer is generated.
Windows executable version metadata is `1.0.0.0`; this does not publish a release.
The running app/update checker version is `VERSION` in `gui/updates.py` (currently
`1.0.0`). Keep it aligned with `packaging/version_info.txt` when changing versions;
GitHub release tags should use semantic versions such as `v1.0.0`.
The executable is unsigned; clean-machine distribution testing and signing are
separate release decisions. Do not bypass Windows security prompts.

## Runtime contents

- PyInstaller folder build contains Python, Qt plugins/DLLs, Markdown and Playwright.
- Playwright's upstream hook includes its Node driver and package-local browser
  directory. Its existing frozen runtime selects that directory by default.
- Chromium 1243 / Chrome for Testing 153.0.8010.12, matching Playwright 1.63.0,
  plus headless shell, FFmpeg and Winldd are included. No external Chrome is used.
- Do not set `PLAYWRIGHT_BROWSERS_PATH` or `PLAYWRIGHT_NODEJS_PATH` to a machine-specific
  location when distributing/running the app; these upstream overrides remain supported.
- No extraction data is written into the application folder. Playwright uses the
  user's temporary directory for its transient browser profile.
- `assets/shutdown.gif`, Inter font/license files and `assets/icon/yoink.ico` are
  collected under `_internal/assets`. Module-relative paths work from any launch cwd.
- Dependency metadata/licenses are retained with their distributions; Playwright
  and Chromium's bundled notices remain with their runtime files.

Inter 4.1 Regular/SemiBold/Bold static TTF files came from the official release.
`assets/fonts/SOURCE.md` records provenance and the archive hash; `LICENSE.txt` is
the upstream SIL OFL. `gui/application.py` registers the bytes in Qt at startup
and changes only the global font family. QTextBrowser uses that same font database;
Preview prefers Inter, Segoe UI, then sans-serif. Code blocks retain their existing
monospace styling. No font is installed into Windows.

The locked PNG is preserved. To regenerate its derived nine-frame ICO only:

```powershell
.venv\Scripts\python.exe packaging\make_icon.py
```

The ICO supplies Qt's inherited window icon, Windows application/taskbar identity,
the executable resource, and the 18-pixel icon before the custom title-bar text.
The title bar retains its 28-pixel height, controls and dragging behavior.

## Tests

```powershell
.venv\Scripts\python.exe -B -m unittest discover -s tests -p 'test_*.py' -v
```

Optional live test uses a shared conversation supplied explicitly for testing:

```powershell
$env:YOINK_LIVE_TEST_URL = 'https://chatgpt.com/share/YOUR-SHARED-CONVERSATION-ID'
.venv\Scripts\python.exe -B -m unittest discover -s tests -p 'test_*.py' -v
.\build_windows.ps1 -QA
.\dist\YOINK-QA\YOINK-QA.exe
Remove-Item Env:YOINK_LIVE_TEST_URL
```

The optional console QA executable freezes the same application modules, assets,
and dependency configuration with a separate test entry point. It runs real Qt
event loops, controlled lifecycle tests, browser-backed filtering tests and the
opt-in live GUI-worker test. It is **not** a product mode or shipped feature.
Always also open and test the actual `YOINK.exe`; QA success alone is insufficient.

Development still launches with `.venv\Scripts\python.exe -m gui` (or `python -m gui`
inside an activated venv). Development browser setup remains `python -m playwright
install chromium`; the build's package-local browser setup does not change it.

See `history/release-verification.md` for actual results and remaining limits.

Upstream references: [Playwright bundling](https://playwright.dev/python/docs/library#pyinstaller),
[PyInstaller runtime paths](https://pyinstaller.org/en/stable/runtime-information.html),
[Inter 4.1](https://github.com/rsms/inter/releases/tag/v4.1).
