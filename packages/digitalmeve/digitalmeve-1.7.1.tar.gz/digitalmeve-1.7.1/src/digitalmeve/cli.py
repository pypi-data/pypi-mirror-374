from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import click

from .embedding_pdf import embed_proof_pdf, extract_proof_pdf
from .embedding_png import embed_proof_png, extract_proof_png
from .generator import generate_meve
from .verifier import verify_meve

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #

logger = logging.getLogger("digitalmeve.cli")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _read_json_file(path: Path) -> Optional[Dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        logger.debug("Failed to read %s: %s", path, e)
        return None
    if not text.strip():
        return None
    try:
        return json.loads(text)
    except Exception as e:
        logger.debug("Invalid JSON in %s: %s", path, e)
        return None


def _sidecar_candidates(path: Path) -> list[Path]:
    """
    Conventions testées, dans l'ordre :
      A) file.ext.meve.json
      B) file.meve.json
      C) <str(path)>.meve.json
      D) path.parent / (path.name + ".meve.json")
      E) path.parent / (path.stem + ".meve.json")
    """
    cands: list[Path] = []
    try:
        cands.append(path.with_suffix(path.suffix + ".meve.json"))
    except Exception as e:
        logger.debug(
            "with_suffix(%s + .meve.json) failed for %s: %s", path.suffix, path, e
        )
    try:
        cands.append(path.with_suffix(".meve.json"))
    except Exception as e:
        logger.debug("with_suffix(.meve.json) failed for %s: %s", path, e)
    cands.append(Path(str(path) + ".meve.json"))
    cands.append(path.parent / (path.name + ".meve.json"))
    cands.append(path.parent / (path.stem + ".meve.json"))

    seen: set[str] = set()
    uniq: list[Path] = []
    for p in cands:
        key = str(p)
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    return uniq


def _find_sidecar_for(path: Path) -> Optional[Path]:
    for cand in _sidecar_candidates(path):
        if cand.exists():
            return cand
    return None


def _maybe_extract_embedded(path: Path) -> Optional[Dict[str, Any]]:
    sfx = path.suffix.lower()
    if sfx == ".pdf":
        return extract_proof_pdf(path)
    if sfx == ".png":
        return extract_proof_png(path)
    return None


def _write_sidecars(
    path: Path,
    proof: Dict[str, Any],
    outdir: Optional[Path],
) -> list[Path]:
    """
    Écrit des sidecars robustes, y compris pour les fichiers SANS extension.

    On tente :
      - file.ext.meve.json (si extension présente)
      - file.meve.json (remplacement extension)
      - file.name + ".meve.json" (toujours)
      - file.stem + ".meve.json" (souvent identique au précédent)
    """
    base = outdir or path.parent
    base.mkdir(parents=True, exist_ok=True)

    outs: list[Path] = []

    # Variante "conserve l'extension"
    try:
        outs.append((base / path.name).with_suffix(path.suffix + ".meve.json"))
    except Exception as e:
        logger.debug("sidecar keep-ext failed for %s: %s", path, e)

    # Variante "remplace l'extension par .meve.json"
    try:
        outs.append((base / path.name).with_suffix(".meve.json"))
    except Exception as e:
        logger.debug("sidecar replace-ext failed for %s: %s", path, e)

    # Variantes robustes (fonctionnent même sans extension)
    outs.append(base / (path.name + ".meve.json"))
    outs.append(base / (path.stem + ".meve.json"))

    # Déduplication
    uniq: list[Path] = []
    seen: set[str] = set()
    for o in outs:
        k = str(o)
        if k not in seen:
            seen.add(k)
            uniq.append(o)

    payload = json.dumps(proof, ensure_ascii=False, separators=(",", ":"))
    for o in uniq:
        o.write_text(payload, encoding="utf-8")
    return uniq


def _summarize_proof(proof: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforme une preuve MEVE complète en résumé lisible, attendu par les tests.
    Champs minimaux requis par les tests : level, issuer, hash_prefix.
    """
    h = proof.get("hash")
    if not isinstance(h, str):
        h = ""
    subject = proof.get("subject") or {}
    if not isinstance(subject, dict):
        subject = {}

    return {
        "level": "info",
        "issuer": proof.get("issuer"),
        "hash_prefix": h[:8],
        "filename": subject.get("filename"),
        "size": subject.get("size"),
    }


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """DigitalMeve command-line interface."""


@cli.command("generate")
@click.argument(
    "file",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
)
@click.option(
    "--issuer",
    type=str,
    required=False,
    help="Issuer name to embed in the proof.",
)
@click.option(
    "--also-json",
    "also_json",
    is_flag=True,
    default=False,
    help="Also write a .meve.json sidecar (kept for backwards-compat).",
)
@click.option(
    "--outdir",
    type=click.Path(path_type=Path, file_okay=False, dir_okay=True),
    required=False,
    help="Directory for outputs (sidecar and/or embedded copy).",
)
def cmd_generate(
    file: Path,
    issuer: Optional[str],
    also_json: bool,
    outdir: Optional[Path],
) -> None:
    """
    Generate a MEVE proof for FILE.

    Comportement:
      - PDF/PNG: embed la preuve dans un .meve.pdf/.meve.png (dans --outdir si fourni).
      - Toujours écrire un sidecar à côté du fichier source.
      - Si --outdir est fourni: écrire aussi un sidecar dans --outdir.
      - Et AFFICHER la preuve en JSON sur stdout (attendu par les tests).
    """
    proof = generate_meve(file, issuer=issuer)

    # 1) Embedding si supporté
    suffix = file.suffix.lower()
    if suffix == ".pdf":
        dst = None if outdir is None else (outdir / (file.stem + ".meve.pdf"))
        embed_proof_pdf(file, proof, out_path=dst)
    elif suffix == ".png":
        dst = None if outdir is None else (outdir / (file.stem + ".meve.png"))
        embed_proof_png(file, proof, out_path=dst)

    # 2) Sidecar TOUJOURS à côté du fichier source
    _write_sidecars(file, proof, outdir=None)

    # 3) Sidecar AUSSI dans --outdir si fourni (ou si --also-json demandé)
    if outdir is not None or also_json:
        _write_sidecars(file, proof, outdir=outdir)

    # 4) Sortie attendue par les tests : JSON pur sur stdout
    click.echo(json.dumps(proof, ensure_ascii=False, separators=(",", ":")), nl=False)


@cli.command("verify")
@click.argument(
    "file",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
)
@click.option(
    "--expected-issuer",
    type=str,
    required=False,
    help="Expected issuer.",
)
def cmd_verify(file: Path, expected_issuer: Optional[str]) -> None:
    """
    Verify FILE (embedded first, then sidecar).
    Exit code 0 on success, 1 on failure.
    """
    proof: Optional[Dict[str, Any]]

    # Cas 1 : on inspecte directement un *.meve.json
    if file.name.endswith(".meve.json"):
        proof = _read_json_file(file)
    else:
        # Cas 2 : embedded (PDF/PNG)
        proof = _maybe_extract_embedded(file)
        # Cas 3 : sidecar à partir d’un fichier “source”
        if proof is None:
            sc = _find_sidecar_for(file)
            if sc is not None:
                proof = _read_json_file(sc)

    if proof is None:
        click.echo(
            "Error: No proof found (neither embedded nor sidecar).",
            err=True,
        )
        sys.exit(1)

    ok, info = verify_meve(proof, expected_issuer=expected_issuer)
    if ok:
        sys.exit(0)

    click.echo(f"Error: {info.get('error', 'Invalid proof')}", err=True)
    sys.exit(1)


@cli.command("inspect")
@click.argument(
    "file",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
)
def cmd_inspect(file: Path) -> None:
    """
    Print a compact JSON summary of the MEVE proof.
      1) Si FILE est un *.meve.json → lire directement
      2) Sinon, embedded (PDF/PNG)
      3) Sinon, sidecar (plusieurs conventions)
    """
    proof: Optional[Dict[str, Any]]

    # 1) *.meve.json donné directement
    if file.name.endswith(".meve.json"):
        proof = _read_json_file(file)
    else:
        # 2) embedded
        proof = _maybe_extract_embedded(file)
        # 3) sidecars
        if proof is None:
            for cand in _sidecar_candidates(file):
                proof = _read_json_file(cand)
                if proof is not None:
                    break

    if proof is None:
        click.echo(
            "Error: No proof found (neither embedded nor sidecar).",
            err=True,
        )
        sys.exit(1)

    summary = _summarize_proof(proof)
    click.echo(json.dumps(summary, ensure_ascii=False, separators=(",", ":")), nl=False)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
