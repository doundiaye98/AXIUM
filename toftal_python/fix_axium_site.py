# -*- coding: utf-8 -*-
"""
Réparation rapide AXIUM : gabarits (images services) + synchro img_service + version cache.

Lancer depuis le dossier toftal_python :
    python fix_axium_site.py
    python fix_axium_site.py --bump-cache   # force aussi la mise a jour de _SERVICE_ASSETS_VER (cache navigateur)

Ou double-clic si .py est associé à Python (mieux : cmd puis commande ci-dessus).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_TEMPLATES = _ROOT / "templates"
_APP = _ROOT / "app.py"

# Remplacements connus (anciennes versions cassées).
_TEMPLATE_SNIPPETS: list[tuple[str, str]] = [
    (
        "{% set svc_thumb_src = service_image_url(offer.slug) %}",
        "{% set svc_thumb_src = '/i/service/' ~ offer.slug ~ '?v=' ~ (service_thumb_ver|default('1')) %}",
    ),
    (
        "{% set svc_detail_src = service_image_url(service.slug) %}",
        "{% set svc_detail_src = '/i/service/' ~ service.slug ~ '?v=' ~ (service_thumb_ver|default('1')) %}",
    ),
    (
        "{{ service_image_url(offer.slug) }}",
        "/i/service/{{ offer.slug }}?v={{ service_thumb_ver|default('1') }}",
    ),
    (
        "{% set svc_thumb_src = url_for('axium_service_image', slug=offer.slug) ~ '?v=' ~ (service_thumb_ver|default('1')) %}",
        "{% set svc_thumb_src = '/i/service/' ~ offer.slug ~ '?v=' ~ (service_thumb_ver|default('1')) %}",
    ),
    (
        "{% set svc_detail_src = url_for('axium_service_image', slug=service.slug) ~ '?v=' ~ (service_thumb_ver|default('1')) %}",
        "{% set svc_detail_src = '/i/service/' ~ service.slug ~ '?v=' ~ (service_thumb_ver|default('1')) %}",
    ),
    (
        "{% set svc_thumb_src = url_for('service_offer_image', slug=offer.slug) ~ '?v=' ~ (service_thumb_ver|default('1')) %}",
        "{% set svc_thumb_src = '/i/service/' ~ offer.slug ~ '?v=' ~ (service_thumb_ver|default('1')) %}",
    ),
    (
        "{% set svc_detail_src = url_for('service_offer_image', slug=service.slug) ~ '?v=' ~ (service_thumb_ver|default('1')) %}",
        "{% set svc_detail_src = '/i/service/' ~ service.slug ~ '?v=' ~ (service_thumb_ver|default('1')) %}",
    ),
]

# url_for('axium_service_image', slug=offer.slug) dans src d'attribut
_RE_URLFOR_AXIUM = re.compile(
    r"\{\{\s*url_for\(\s*['\"]axium_service_image['\"]\s*,\s*slug\s*=\s*offer\.slug\s*\)\s*\}\}\s*\?\s*v\s*=\s*\{\{\s*service_thumb_ver\|default\(['\"]1['\"]\)\s*\}\}",
    re.MULTILINE,
)
_REPLACEMENT_FLIP_SRC = '/i/service/{{ offer.slug }}?v={{ service_thumb_ver|default(\'1\') }}'


def _patch_file(path: Path) -> int:
    raw = path.read_text(encoding="utf-8")
    orig = raw
    for old, new in _TEMPLATE_SNIPPETS:
        if old in raw:
            raw = raw.replace(old, new)
    raw = _RE_URLFOR_AXIUM.sub(_REPLACEMENT_FLIP_SRC, raw)
    # Ligne résiduelle générique
    raw = re.sub(
        r"url_for\(\s*['\"]axium_service_image['\"]\s*,\s*slug\s*=\s*offer\.slug\s*\)",
        "'/i/service/' ~ offer.slug ~ '?v=' ~ (service_thumb_ver|default('1'))",
        raw,
    )
    raw = re.sub(
        r"url_for\(\s*['\"]service_offer_image['\"]\s*,\s*slug\s*=\s*offer\.slug\s*\)",
        "'/i/service/' ~ offer.slug ~ '?v=' ~ (service_thumb_ver|default('1'))",
        raw,
    )
    if raw != orig:
        path.write_text(raw, encoding="utf-8", newline="\n")
        return 1
    return 0


def _bump_assets_ver() -> str | None:
    if not _APP.is_file():
        return None
    text = _APP.read_text(encoding="utf-8")
    m = re.search(r'^(_SERVICE_ASSETS_VER\s*=\s*["\'])([^"\']+)(["\'])', text, re.MULTILINE)
    if not m:
        return None
    old = m.group(2)
    if re.match(r"^\d{8}[a-z]?$", old):
        base, suf = old[:8], old[8:] or "a"
        if suf and suf[-1] < "z":
            new = base + chr(ord(suf[-1]) + 1)
        else:
            new = base + "fix"
    else:
        new = old + "fix"
    new_text = text[: m.start(2)] + new + text[m.end(2) :]
    _APP.write_text(new_text, encoding="utf-8", newline="\n")
    return new


def _check_app_route() -> list[str]:
    warnings: list[str] = []
    if not _APP.is_file():
        warnings.append("app.py introuvable")
        return warnings
    t = _APP.read_text(encoding="utf-8")
    if "/i/service/" not in t and "axium_service_image" not in t:
        warnings.append("app.py : route /i/service/ ou axium_service_image absente — ajoutez la vue des visuels.")
    if "def service_detail" in t:
        idx = t.find("def service_detail")
        chunk = t[idx : idx + 1200]
        if "OPENAI_BASE_URL" in chunk or "complete_chat" in chunk:
            warnings.append(
                "app.py : le code du chat semble melange dans service_detail() — restaurez la vue "
                "(return render_template service_detail seulement)."
            )
    return warnings


def main() -> int:
    print("AXIUM — reparation site (templates + sync + version)")
    changed = 0
    for name in ("services.html", "service_detail.html", "index.html"):
        p = _TEMPLATES / name
        if p.is_file():
            n = _patch_file(p)
            if n:
                print(f"  OK  patche {name}")
                changed += n
            else:
                print(f"  --  {name} (rien a remplacer)")
        else:
            print(f"  !!  manquant : {p}")

    force_bump = "--bump-cache" in sys.argv
    if changed or force_bump:
        nv = _bump_assets_ver()
        if nv:
            print(f"  OK  _SERVICE_ASSETS_VER -> {nv}")
        else:
            print("  !!  impossible de modifier _SERVICE_ASSETS_VER dans app.py")
    else:
        print("  --  version cache inchangee (utilisez --bump-cache si besoin)")

    try:
        from sync_service_images import sync_service_thumbnails_to_static

        n = sync_service_thumbnails_to_static(verbose=True)
        print(f"  OK  sync img_service -> static/img/services/ ({n} copie(s))")
    except Exception as exc:
        print(f"  !!  sync : {exc}", file=sys.stderr)

    for w in _check_app_route():
        print(f"  !!  {w}")

    if changed or nv:
        print("\nTermine : redemarrez Flask (run.bat) puis Ctrl+F5 dans le navigateur.")
    else:
        print("\nTermine : si les images sont encore cassees, redemarrez Flask et videz le cache (Ctrl+F5).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
