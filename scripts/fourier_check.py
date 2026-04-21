#!/usr/bin/env python3
"""Analyse du spectre de Fourier pour détecter les patterns VAE.

Les modèles de diffusion (Nano Banana inclus) laissent une signature
périodique moyenne-haute fréquence dans le spectre. Ce script calcule la
FFT 2D de la luminance, cherche les pics réguliers, retourne un score :

    1.0  = spectre naturel (pas de périodicité suspecte)
    0.0  = forte périodicité (très suspect)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def _load_deps():
    try:
        import numpy as np
        from PIL import Image
    except ImportError as exc:
        _eprint("Erreur : numpy + Pillow requis.")
        raise SystemExit(2) from exc
    return np, Image


def compute_fourier_score(input_path: Path) -> dict:
    np, Image = _load_deps()
    img = Image.open(input_path).convert("L")
    arr = np.asarray(img, dtype=np.float32) / 255.0

    h, w = arr.shape
    hann_y = np.hanning(h)[:, None]
    hann_x = np.hanning(w)[None, :]
    windowed = arr * hann_y * hann_x

    fft = np.fft.fftshift(np.fft.fft2(windowed))
    magnitude = np.log1p(np.abs(fft))

    cy, cx = h // 2, w // 2
    y, x = np.indices(magnitude.shape)
    r = np.hypot(y - cy, x - cx)
    r_max = min(cy, cx)

    inner = (r > r_max * 0.2) & (r < r_max * 0.7)
    band = magnitude[inner]

    mean = float(band.mean())
    std = float(band.std())
    pct_99 = float(np.percentile(band, 99))
    peak_ratio = (pct_99 - mean) / (std + 1e-6)

    score = max(0.0, min(1.0, 1.0 - max(0.0, (peak_ratio - 2.5) / 4.0)))

    return {
        "fourier_score": round(score, 3),
        "peak_ratio": round(peak_ratio, 3),
        "band_mean": round(mean, 3),
        "band_std": round(std, 3),
        "comment": "Score 1.0 = naturel. Sous 0.6 = pattern VAE suspect, refaire un downsample_up.",
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Score de naturalité du spectre FFT 2D.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", help="Fichier JSON de sortie (optionnel).")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = compute_fourier_score(Path(args.input))
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
