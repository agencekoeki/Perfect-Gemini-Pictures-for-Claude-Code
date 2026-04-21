#!/usr/bin/env python3
"""Orchestrateur Python de la cascade de post-processing.

Lit un shot-plan JSON, enchaîne les scripts dans l'ordre strict :

    downsample_up → chromatic_ab → film_grain → sensor_noise
    → micro_imperfection → color_grade → vignette → jpeg_cycle → exif_inject

Chaque étape produit un fichier intermédiaire dans .pgp-session/stages/.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def _eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def _run(cmd: list[str]) -> None:
    print(f"→ {' '.join(str(c) for c in cmd)}")
    res = subprocess.run(cmd, check=False)
    if res.returncode != 0:
        _eprint(f"Erreur : étape échouée avec code {res.returncode}. Commande : {cmd}")
        raise SystemExit(res.returncode)


def _resolve_script(name: str) -> str:
    """Retourne le chemin absolu du script (py ou sh)."""
    path = SCRIPT_DIR / name
    if not path.exists():
        raise SystemExit(f"Script introuvable : {path}")
    return str(path)


def _python(name: str) -> list[str]:
    return [sys.executable, _resolve_script(name)]


def _bash(name: str) -> list[str]:
    if os.name == "nt":
        return ["bash", _resolve_script(name)]
    return [_resolve_script(name)]


def load_shot_plan(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Erreur : shot-plan introuvable : {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def run_pipeline(
    shot_plan_path: Path,
    input_image: Path,
    output_image: Path,
    stages_dir: Path | None = None,
) -> None:
    plan = load_shot_plan(shot_plan_path)
    stages_dir = stages_dir or input_image.parent / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)

    pp = plan.get("post_processing_intent", {})
    grain = pp.get("grain_intensity", "medium")
    vignette_strength = pp.get("vignette_strength", "low")
    ca_intensity = pp.get("chromatic_aberration", "subtle")
    mood = pp.get("color_grade_mood", "neutral-editorial")
    iso = int(plan.get("iso", 400))
    camera = plan.get("camera_simulation", "iphone_15_pro")
    film_stock = plan.get("film_stock", "kodak_portra_400")
    aperture = str(plan.get("aperture", "1.8")).replace("f/", "").strip()
    focal = plan.get("focal_length_mm", 24)
    shutter = plan.get("shutter", "1/120")

    stage1 = stages_dir / "01-downsample-up.png"
    stage2 = stages_dir / "02-chromatic-ab.png"
    stage3 = stages_dir / "03-film-grain.png"
    stage4 = stages_dir / "04-sensor-noise.png"
    stage5 = stages_dir / "05-imperfection.png"
    stage6 = stages_dir / "06-color-grade.png"
    stage7 = stages_dir / "07-vignette.png"
    stage8 = stages_dir / "08-jpeg-cycle.jpg"

    grain_intensity_float = {"low": "0.4", "medium": "0.7", "high": "1.0"}.get(grain, "0.7")

    _run([*_python("downsample_up.py"),
          "--input", str(input_image), "--output", str(stage1),
          "--intermediate-ratio", "0.5", "--passes", "1"])

    _run([*_python("chromatic_ab.py"),
          "--input", str(stage1), "--output", str(stage2),
          "--intensity", ca_intensity])

    _run([*_bash("film_grain.sh"),
          "--input", str(stage2), "--output", str(stage3),
          "--film", film_stock, "--intensity", grain_intensity_float])

    _run([*_python("sensor_noise.py"),
          "--input", str(stage3), "--output", str(stage4),
          "--iso", str(iso), "--intensity", grain])

    _run([*_python("micro_imperfection.py"),
          "--input", str(stage4), "--output", str(stage5),
          "--count", "2", "--max-opacity", "0.15"])

    _run([*_bash("color_grade.sh"),
          "--input", str(stage5), "--output", str(stage6),
          "--mood", mood, "--intensity", "0.8"])

    _run([*_bash("vignette.sh"),
          "--input", str(stage6), "--output", str(stage7),
          "--strength", vignette_strength])

    _run([*_python("jpeg_cycle.py"),
          "--input", str(stage7), "--output", str(stage8)])

    output_image.parent.mkdir(parents=True, exist_ok=True)
    if output_image.suffix.lower() in {".jpg", ".jpeg"}:
        shutil.copy(stage8, output_image)
    else:
        _run([*_python("jpeg_cycle.py"),
              "--input", str(stage8), "--output", str(output_image)])

    _run([*_bash("exif_inject.sh"),
          "--input", str(output_image), "--output", str(output_image),
          "--camera", camera,
          "--iso", str(iso),
          "--aperture", aperture,
          "--focal", str(focal),
          "--shutter", shutter])

    print(f"\n✓ Pipeline complet. Image finale : {output_image}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Orchestrateur cascade post-processing.")
    p.add_argument("--shot-plan", required=True, help="Chemin du shot-plan.json.")
    p.add_argument("--input", required=True, help="Image brute Gemini.")
    p.add_argument("--output", required=True, help="Image finale.")
    p.add_argument("--stages-dir", help="Dossier des fichiers intermédiaires.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_pipeline(
        Path(args.shot_plan),
        Path(args.input),
        Path(args.output),
        Path(args.stages_dir) if args.stages_dir else None,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
