# Production blue CRT shutdown

The owner chose this CRT as the default shutdown presentation. Source integration
and local verification are complete; independent TPM review and final owner visual
confirmation remain pending. Nothing has been committed, packaged or released.

Production uses gui/shutdown_screen.py and reusable gui/shutdown_crt.py.
It never imports tools. To inspect the same production screen standalone:

    C:\Users\User\Desktop\Projects\YOINK\.venv\Scripts\python.exe -B tools/preview_shutdown_crt.py

The screen remains 220 × 140 logical pixels. SYSTEM / SHUTDOWN use procedural
block glyphs with blue faces, dark depth and narrow bevels; no title font file is
needed. Exactly one runtime random.choice(EXIT_MESSAGES) quip appears inside the
CRT. All 22 existing strings are preserved. No extra status lines or floating
message capsule. The quip uses Windows-installed Consolas; no font is redistributed.

The historical filename assets/shutdown_system_optional.gif now denotes the
production text-free CRT surface. It retains the accepted raster, grain, vignette
and perimeter, with a broader soft moving band at the same peak brightness and
cadence. assets/shutdown.gif is byte-identical, retained as an inactive legacy asset.

The existing author-only generator tools/generate_shutdown_crt.py requires Pillow.
Runtime remains PySide6-only. YOINK.spec includes both GIFs; no EXE was built.
Do not alter caller timing, overlay or worker completion logic for previews.

Final native production evidence and audit:
C:\Users\User\Desktop\artifacts-yoink\new\YOINK_Task-B_Final-Production-CRT_2026-11-02_212136
