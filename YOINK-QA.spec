# Optional separate frozen regression runner. Not part of the shipped folder.
from pathlib import Path
release_qa = True
exec(compile((Path(SPECPATH) / "YOINK.spec").read_text(encoding="utf-8"), "YOINK.spec", "exec"))
