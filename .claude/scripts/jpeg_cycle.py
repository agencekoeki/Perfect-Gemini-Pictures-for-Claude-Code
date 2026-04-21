#!/usr/bin/env python3
"""Cycle de re-compression JPEG → PNG → JPEG.

Les images Gemini sortent en PNG sans historique de compression. Ce cycle
simule le parcours typique d'une vraie photo (export caméra JPEG, import
éditeur, export JPEG final) et introduit les micro-artefacts JPEG naturels.
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path


def _eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def _load_pil():
    try:
        from PIL import Image
    except ImportError as exc:
        _eprint("Erreur : Pillow non installé. pip install Pillow")
        raise SystemExit(2) from exc
    return Image


def jpeg_cycle(input_path: Path, output_path: Path,
               q1: int = 92, q2: int = 95) -> None:
    Image = _load_pil()
    img = Image.open(input_path).convert("RGB")

    buf1 = io.BytesIO()
    img.save(buf1, format="JPEG", quality=q1, subsampling=2)
    buf1.seek(0)
    img = Image.open(buf1).convert("RGB")

    buf_png = io.BytesIO()
    img.save(buf_png, format="PNG")
    buf_png.seek(0)
    img = Image.open(buf_png).convert("RGB")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = output_path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        img.save(output_path, format="JPEG", quality=q2, subsampling=2, optimize=True)
    else:
        tmp_buf = io.BytesIO()
        img.save(tmp_buf, format="JPEG", quality=q2, subsampling=2)
        tmp_buf.seek(0)
        Image.open(tmp_buf).convert("RGB").save(output_path)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Cycle JPEG-PNG-JPEG pour naturalite compression.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--q1", type=int, default=92)
    p.add_argument("--q2", type=int, default=95)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    jpeg_cycle(Path(args.input), Path(args.output), q1=args.q1, q2=args.q2)
    print(f"Cycle JPEG appliqué (q1={args.q1}, q2={args.q2}) : {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
