#!/usr/bin/env python3
"""Score composite de naturalité forensique.

Agrège plusieurs indicateurs pour produire un score 0-100 :
    - fourier_score        : spectre FFT (pondération 30%)
    - noise_coherence      : corrélation spatiale du bruit (20%)
    - exif_present         : tags EXIF présents (15%)
    - exif_coherence       : valeurs EXIF cohérentes (15%)
    - texture_variance     : variance locale de texture (20%)

Retourne aussi des suggestions actionnables quand un indicateur est bas.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


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


def compute_noise_coherence(np_mod, arr) -> float:
    """Bruit naturel = corrélation spatiale non-nulle. Bruit gaussien iid = corrélation nulle."""
    gray = 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]
    from scipy.ndimage import gaussian_filter
    smooth = gaussian_filter(gray, sigma=1.2)
    residual = gray - smooth
    shifted = np_mod.roll(residual, 1, axis=0)
    denom = np_mod.sqrt(np_mod.sum(residual**2) * np_mod.sum(shifted**2)) + 1e-9
    corr = float(np_mod.sum(residual * shifted) / denom)
    return max(0.0, min(1.0, (corr + 0.05) * 2.0))


def compute_texture_variance(np_mod, arr) -> float:
    gray = 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]
    h, w = gray.shape
    tile = 32
    variances = []
    for y in range(0, h - tile, tile):
        for x in range(0, w - tile, tile):
            variances.append(float(np_mod.var(gray[y:y+tile, x:x+tile])))
    if not variances:
        return 0.5
    variances = np_mod.asarray(variances)
    coef_var = float(variances.std() / (variances.mean() + 1e-6))
    return max(0.0, min(1.0, coef_var / 1.5))


def read_exif(input_path: Path) -> dict:
    try:
        res = subprocess.run(
            ["exiftool", "-j", "-n", str(input_path)],
            check=True, capture_output=True, text=True,
        )
        data = json.loads(res.stdout or "[]")
        return data[0] if data else {}
    except (FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError):
        return {}


def compute_exif_scores(exif: dict) -> tuple[float, float]:
    expected = ["Make", "Model", "ISO", "FNumber", "ExposureTime",
                "FocalLength", "DateTimeOriginal"]
    present = sum(1 for k in expected if k in exif)
    present_score = present / len(expected)
    coherence = 1.0
    if "Software" in exif:
        sw = str(exif["Software"]).lower()
        if "gemini" in sw or "ai" in sw or "diffusion" in sw:
            coherence -= 0.6
    if "FNumber" in exif:
        try:
            fn = float(exif["FNumber"])
            if fn < 0.7 or fn > 32:
                coherence -= 0.3
        except (TypeError, ValueError):
            coherence -= 0.2
    if "ISO" in exif:
        try:
            iso = int(exif["ISO"])
            if iso < 25 or iso > 25600:
                coherence -= 0.3
        except (TypeError, ValueError):
            coherence -= 0.2
    return round(present_score, 3), round(max(0.0, coherence), 3)


def run_fourier(input_path: Path) -> float:
    fourier_script = SCRIPT_DIR / "fourier_check.py"
    try:
        res = subprocess.run(
            [sys.executable, str(fourier_script), "--input", str(input_path)],
            check=True, capture_output=True, text=True,
        )
        data = json.loads(res.stdout)
        return float(data.get("fourier_score", 0.5))
    except Exception:  # noqa: BLE001
        return 0.5


def score(input_path: Path) -> dict:
    np, Image = _load_deps()
    img = Image.open(input_path).convert("RGB")
    arr = np.asarray(img, dtype=np.float32) / 255.0

    fourier = run_fourier(input_path)
    noise = compute_noise_coherence(np, arr)
    texture = compute_texture_variance(np, arr)
    exif = read_exif(input_path)
    exif_present_score, exif_coherence = compute_exif_scores(exif)

    weighted = (
        fourier * 0.30
        + noise * 0.20
        + exif_present_score * 0.15
        + exif_coherence * 0.15
        + texture * 0.20
    )
    total = int(round(weighted * 100))

    warnings: list[str] = []
    suggestions: list[str] = []

    if fourier < 0.6:
        warnings.append(f"Fourier score bas ({fourier:.2f}) : pattern VAE détecté.")
        suggestions.append("Relancer `scripts/downsample_up.py --passes 2 --intermediate-ratio 0.45`.")
    if noise < 0.35:
        warnings.append(f"Bruit trop uniforme/absent ({noise:.2f}).")
        suggestions.append("Relancer `scripts/sensor_noise.py --intensity high`.")
    if texture < 0.3:
        warnings.append(f"Variance de texture faible ({texture:.2f}) : zones trop lisses.")
        suggestions.append("Re-run grain film avec --intensity plus élevée, ou ajouter un pass sensor_noise.")
    if not exif:
        warnings.append("Aucune métadonnée EXIF détectée.")
        suggestions.append("Relancer `scripts/exif_inject.sh` avec le bon preset caméra.")
    elif exif_coherence < 0.7:
        warnings.append(f"Métadonnées EXIF incohérentes ({exif_coherence:.2f}).")
        suggestions.append("Vérifier le preset EXIF, en particulier ISO/FNumber/Software.")

    return {
        "score_total": total,
        "breakdown": {
            "fourier_score": round(fourier, 3),
            "noise_coherence": round(noise, 3),
            "exif_present": exif_present_score,
            "exif_coherence": exif_coherence,
            "texture_variance": round(texture, 3),
        },
        "warnings": warnings,
        "suggestions": suggestions,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Score composite de naturalité forensique.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", help="Chemin JSON de sortie.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = score(Path(args.input))
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
