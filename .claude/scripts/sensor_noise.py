#!/usr/bin/env python3
"""Ajoute un bruit sensor cohérent (PRNU-like) à une image.

Un vrai capteur produit un bruit spatialement corrélé (Photo Response Non
Uniformity + read noise), pas un bruit gaussien indépendant pixel à pixel.
Ce script approxime ce comportement en combinant du bruit basse fréquence
(pattern capteur) et du bruit gaussien modulé par la luminance (shot noise).

L'intensité est corrélée à l'ISO simulé :
    - ISO <= 200  → low
    - ISO 200-800 → medium
    - ISO > 800   → high
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
        from scipy.ndimage import gaussian_filter
    except ImportError as exc:
        _eprint("Erreur : dépendances manquantes. pip install -r requirements.txt")
        raise SystemExit(2) from exc
    return np, Image, gaussian_filter


INTENSITY_PARAMS = {
    "low": {"prnu_std": 0.008, "shot_std": 0.010, "prnu_sigma": 2.0},
    "medium": {"prnu_std": 0.016, "shot_std": 0.020, "prnu_sigma": 1.8},
    "high": {"prnu_std": 0.030, "shot_std": 0.040, "prnu_sigma": 1.5},
}


def iso_to_intensity(iso: int) -> str:
    if iso <= 200:
        return "low"
    if iso <= 800:
        return "medium"
    return "high"


def apply_sensor_noise(
    input_path: Path,
    output_path: Path,
    iso: int,
    intensity: str | None = None,
    seed: int | None = None,
) -> None:
    np, Image, gaussian_filter = _load_deps()
    if intensity is None:
        intensity = iso_to_intensity(iso)
    if intensity not in INTENSITY_PARAMS:
        raise SystemExit(f"Erreur : intensity inconnue : {intensity}")

    params = INTENSITY_PARAMS[intensity]
    rng = np.random.default_rng(seed)

    img = Image.open(input_path).convert("RGB")
    arr = np.asarray(img, dtype=np.float32) / 255.0

    prnu = rng.normal(0.0, params["prnu_std"], size=arr.shape[:2]).astype(np.float32)
    prnu = gaussian_filter(prnu, sigma=params["prnu_sigma"])
    prnu_3c = prnu[:, :, None]

    luminance = 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]
    shot = rng.normal(0.0, params["shot_std"], size=arr.shape).astype(np.float32)
    shot *= np.sqrt(np.clip(luminance, 0.01, 1.0))[:, :, None]

    noisy = arr * (1.0 + prnu_3c) + shot
    noisy = np.clip(noisy, 0.0, 1.0)
    out = (noisy * 255.0 + 0.5).astype(np.uint8)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(out).save(output_path)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Ajoute un bruit sensor PRNU-like calibré sur l'ISO.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--iso", type=int, default=400, help="ISO simulé (influence l'intensité).")
    p.add_argument("--intensity", choices=["low", "medium", "high"], default=None,
                   help="Force une intensité. Par défaut dérivée de --iso.")
    p.add_argument("--seed", type=int, default=None, help="Seed aléatoire pour reproductibilité.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    apply_sensor_noise(
        Path(args.input),
        Path(args.output),
        iso=args.iso,
        intensity=args.intensity,
        seed=args.seed,
    )
    eff = args.intensity or iso_to_intensity(args.iso)
    print(f"Bruit sensor appliqué (ISO {args.iso}, intensity={eff}) : {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
