#!/usr/bin/env python3
"""Aberration chromatique radiale.

Les vrais objectifs produisent une aberration chromatique qui sépare
légèrement les canaux R et B sur les bords de l'image. Ce script applique
un shift radial subtil : R s'éloigne du centre, B se rapproche, G reste fixe.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def _load_deps():
    try:
        import numpy as np
        from PIL import Image
        from scipy.ndimage import map_coordinates
    except ImportError as exc:
        _eprint("Erreur : dépendances manquantes. pip install -r requirements.txt")
        raise SystemExit(2) from exc
    return np, Image, map_coordinates


INTENSITY_PIXELS = {
    "subtle": 1.5,
    "moderate": 3.0,
    "strong": 5.0,
}


def _shift_channel(np_mod, map_coords_fn, channel, max_shift: float, sign: int):
    """Shift radial : chaque pixel est déplacé d'une fraction de sa distance au centre."""
    h, w = channel.shape
    cy, cx = h / 2.0, w / 2.0
    max_r = np_mod.hypot(cx, cy)
    yy, xx = np_mod.indices((h, w), dtype=np_mod.float32)
    dy = yy - cy
    dx = xx - cx
    r = np_mod.hypot(dx, dy)
    r_norm = r / max_r
    shift_y = sign * max_shift * r_norm * (dy / (r + 1e-6))
    shift_x = sign * max_shift * r_norm * (dx / (r + 1e-6))
    coords = np_mod.stack([yy - shift_y, xx - shift_x])
    return map_coords_fn(channel, coords, order=1, mode="reflect")


def apply_chromatic_aberration(
    input_path: Path,
    output_path: Path,
    intensity: str = "subtle",
    pattern: str = "radial",
) -> None:
    np, Image, map_coords = _load_deps()
    if intensity not in INTENSITY_PIXELS:
        raise SystemExit(f"Erreur : intensity inconnue : {intensity}")
    if pattern != "radial":
        raise SystemExit("Seul le pattern radial est implémenté.")

    max_shift = INTENSITY_PIXELS[intensity]
    img = Image.open(input_path).convert("RGB")
    arr = np.asarray(img, dtype=np.float32)

    r = _shift_channel(np, map_coords, arr[:, :, 0], max_shift=max_shift, sign=+1)
    b = _shift_channel(np, map_coords, arr[:, :, 2], max_shift=max_shift, sign=-1)
    g = arr[:, :, 1]

    out = np.stack([r, g, b], axis=-1)
    out = np.clip(out, 0, 255).astype(np.uint8)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(out).save(output_path)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Aberration chromatique radiale subtile.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--intensity", choices=list(INTENSITY_PIXELS.keys()), default="subtle")
    p.add_argument("--pattern", choices=["radial"], default="radial")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    apply_chromatic_aberration(
        Path(args.input),
        Path(args.output),
        intensity=args.intensity,
        pattern=args.pattern,
    )
    print(f"Aberration chromatique appliquée (intensity={args.intensity}) : {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
