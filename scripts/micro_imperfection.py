#!/usr/bin/env python3
"""Ajoute 1-3 micro-taches sensor/poussière invisibles mais statistiquement présentes.

Une vraie photo de capteur contient quasi toujours 1 à 3 dust spots de l'ordre
de 3 à 8 pixels, avec une opacité très faible (0.05 à 0.15). Ces taches sont
imperceptibles à l'œil mais détectables par analyse forensique et ancrent
l'image dans le réel.
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
        from PIL import Image, ImageDraw
    except ImportError as exc:
        _eprint("Erreur : Pillow + numpy requis.")
        raise SystemExit(2) from exc
    return np, Image, ImageDraw


def apply_micro_imperfection(
    input_path: Path,
    output_path: Path,
    count: int = 2,
    max_opacity: float = 0.15,
    min_size: int = 3,
    max_size: int = 8,
    seed: int | None = None,
) -> None:
    np, Image, ImageDraw = _load_deps()
    rng = np.random.default_rng(seed)

    img = Image.open(input_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = img.size

    for _ in range(max(0, count)):
        cx = int(rng.uniform(w * 0.15, w * 0.85))
        cy = int(rng.uniform(h * 0.15, h * 0.85))
        size = int(rng.integers(min_size, max_size + 1))
        opacity = float(rng.uniform(max_opacity * 0.5, max_opacity))
        alpha = int(opacity * 255)
        bbox = (cx - size, cy - size, cx + size, cy + size)
        draw.ellipse(bbox, fill=(0, 0, 0, alpha))

    composed = Image.alpha_composite(img, overlay).convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    composed.save(output_path)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Ajoute 1-3 micro-taches sensor invisibles.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--count", type=int, default=2, help="Nombre de taches (1-5).")
    p.add_argument("--max-opacity", type=float, default=0.15,
                   help="Opacité maximum de chaque tache (0.05-0.25 conseillé).")
    p.add_argument("--min-size", type=int, default=3)
    p.add_argument("--max-size", type=int, default=8)
    p.add_argument("--seed", type=int, default=None)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    apply_micro_imperfection(
        Path(args.input),
        Path(args.output),
        count=args.count,
        max_opacity=args.max_opacity,
        min_size=args.min_size,
        max_size=args.max_size,
        seed=args.seed,
    )
    print(f"Micro-taches ajoutées ({args.count} max opacity={args.max_opacity}) : {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
