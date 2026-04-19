"""Fusionne fr_partial + fr_extra puis applique en_patch pour locale/en.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

fr = json.loads((ROOT / "fr_partial.json").read_text(encoding="utf-8"))
extra = json.loads((ROOT / "locale" / "fr_extra.json").read_text(encoding="utf-8"))
overlap = set(fr) & set(extra)
if overlap:
    raise SystemExit(f"Clés en double fr_partial / fr_extra : {overlap}")
fr.update(extra)

locale_dir = ROOT / "locale"
locale_dir.mkdir(exist_ok=True)
(locale_dir / "fr.json").write_text(json.dumps(fr, ensure_ascii=False, indent=2), encoding="utf-8")

patch_path = locale_dir / "en_patch.json"
if patch_path.exists():
    patch = json.loads(patch_path.read_text(encoding="utf-8"))
    unknown = set(patch) - set(fr)
    if unknown:
        raise SystemExit(f"en_patch contient des clés inconnues : {unknown}")
    en = {**fr, **patch}
else:
    en = dict(fr)

(locale_dir / "en.json").write_text(json.dumps(en, ensure_ascii=False, indent=2), encoding="utf-8")
print("OK locale/fr.json + locale/en.json", len(fr), "clés")
