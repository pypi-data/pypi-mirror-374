from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import date
from .replacer import apply_vars, load_vars, format_outpath
from .image_swap import swap_frames_from_imgs

__all__ = ["render_presentation"]


def render_presentation(
    template: Path | str,
    vars_yml: Path | str | None,
    imgs_yml: Path | str | None,
    out_pattern: str = "{STEM}_{DATE}.pptx",
    default_dir: Path | None = None,
) -> Path:
    """
    Run replacer and/or image swap. Returns final output path.
    - template: input .pptx
    - vars_yml: YAML with {{KEY}} values; if None, skip replacer
    - imgs_yml: YAML with slides[].images[]; if None, skip image swap
    - out_pattern: supports {STEM} and keys from vars_yml; {DATE} auto-fills if missing
    """
    tpl = Path(template).resolve()
    if not tpl.exists():
        raise FileNotFoundError(f"Missing template: {tpl}")

    # load variables if present
    vars_map = {}
    if vars_yml:
        yml = Path(vars_yml).resolve()
        if not yml.exists():
            raise FileNotFoundError(f"Missing vars: {yml}")
        vars_map = load_vars(yml)

    # defaults for filename templating
    vars_map.setdefault("STEM", tpl.stem)
    vars_map.setdefault("DATE", date.today().isoformat())

    base_dir = default_dir or tpl.parent
    out_final = format_outpath(out_pattern, vars_map, default_dir=base_dir)
    out_final.parent.mkdir(parents=True, exist_ok=True)

    # nothing to do
    if not vars_yml and not imgs_yml:
        return out_final

    # decide execution graph
    if vars_yml and imgs_yml:
        with TemporaryDirectory() as td:
            mid = Path(td) / f"{tpl.stem}_replaced.pptx"
            apply_vars(tpl, Path(vars_yml), mid)
            swap_frames_from_imgs(mid, Path(imgs_yml), out_final)
    elif vars_yml:
        apply_vars(tpl, Path(vars_yml), out_final)
    else:  # imgs only
        swap_frames_from_imgs(tpl, Path(imgs_yml), out_final)

    return out_final
