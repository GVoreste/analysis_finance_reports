"""Module that detect the locale and implement the translation of the messages"""

import locale
import tempfile
from pathlib import Path
import gettext
from importlib_resources import files


LOC = locale.getlocale()[0]
if LOC is None:
    LOC = "en_US.UFT-8"
lang = LOC.split("_")[0]
TRANSLATION = None
with tempfile.TemporaryDirectory() as tmp_dir:
    for f in (files("freeports_analysis.locales") / lang / "LC_MESSAGES").iterdir():
        translation_dir = Path(tmp_dir) / lang / "LC_MESSAGES"
        translation_dir.mkdir(parents=True, exist_ok=True)
        tmp_file = translation_dir / f.name
        tmp_file.write_bytes(f.read_bytes())
    TRANSLATION = gettext.translation("messages", tmp_dir, [lang])
    TRANSLATION.install()
_ = TRANSLATION.gettext
