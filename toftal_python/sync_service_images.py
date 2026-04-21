# -*- coding: utf-8 -*-
"""Copie les visuels sources (img_service/, img/, secours __pycache__/img_service/) vers static/img/services/.

Lancer depuis toftal_python :  python sync_service_images.py
Puis redémarrer Flask ; incrémenter _SERVICE_ASSETS_VER dans app.py si besoin (cache navigateur).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from services_catalog import SERVICE_IMAGE_SYNC_RULES

_ROOT = Path(__file__).resolve().parent
_DST = _ROOT / "static" / "img" / "services"


def service_thumbnail_roots() -> tuple[Path, ...]:
    roots: list[Path] = []
    for name in ("img_service", "img"):
        p = _ROOT / name
        if p.is_dir():
            roots.append(p)
    stray = _ROOT / "__pycache__" / "img_service"
    if stray.is_dir():
        roots.append(stray)
    return tuple(roots)


def find_service_image_source(candidates: tuple[str, ...]) -> Path | None:
    for root in service_thumbnail_roots():
        for name in candidates:
            p = root / name
            if p.is_file() and p.stat().st_size > 32:
                return p
    return None


def _needs_copy(src: Path, dest: Path) -> bool:
    """True si la cible est absente, trop petite, ou différente de la source (évite visuels figés / corrompus)."""
    if not dest.is_file():
        return True
    ds = dest.stat()
    ss = src.stat()
    if ds.st_size < 64:
        return True
    if ss.st_size != ds.st_size:
        return True
    if ss.st_mtime > ds.st_mtime:
        return True
    return False


def sync_service_thumbnails_to_static(*, verbose: bool = False) -> int:
    """Copie img_service/ → static/img/services/ lorsque la cible manque ou n’est pas à jour."""
    _DST.mkdir(parents=True, exist_ok=True)
    copied = 0
    for dest_name, candidates in SERVICE_IMAGE_SYNC_RULES:
        src = find_service_image_source(candidates)
        if not src:
            if verbose:
                print(f"SKIP {dest_name} - aucune source parmi : {', '.join(candidates)}", file=sys.stderr)
            continue
        dest = _DST / dest_name
        if not _needs_copy(src, dest):
            if verbose:
                print(f"OK (a jour) {dest_name} <- {src.relative_to(_ROOT)}")
            continue
        shutil.copy2(src, dest)
        copied += 1
        if verbose:
            print(f"OK  {src.relative_to(_ROOT)}  ->  static/img/services/{dest_name}", flush=True)
    return copied


def main() -> int:
    roots = service_thumbnail_roots()
    if not roots:
        print("ERREUR : aucun dossier source (img_service/, img/).", file=sys.stderr)
        return 1
    print("Racines :", ", ".join(str(r.relative_to(_ROOT)) for r in roots))
    n = sync_service_thumbnails_to_static(verbose=True)
    if n == 0:
        print("Aucune copie (deja a jour ou sources introuvables).")
    else:
        print(f"Termine : {n} fichier(s) copie(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
