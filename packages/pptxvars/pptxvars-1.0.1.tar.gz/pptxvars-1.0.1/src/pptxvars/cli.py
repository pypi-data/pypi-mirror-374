import argparse
import tempfile
import sys
from pathlib import Path
from .replacer import apply_vars, load_vars, format_outpath
from .image_swap import swap_frames_from_imgs


def main():
    ap = argparse.ArgumentParser(
        prog="pptxvars",
        description="Replace {{KEY}} in PPTX from YAML, swap 'Frame*' shapes with images from YAML, or both."
    )
    ap.add_argument("--template", required=True, help="Input PPTX path")
    ap.add_argument("--out", default="{STEM}_{DATE}.pptx",
                    help="Final output path or pattern. Supports {KEY} (from --vars) and {STEM}.")
    ap.add_argument("--vars", help="YAML with variables for {{KEY}} replacement (optional)")
    ap.add_argument("--imgs", help="YAML with slide->images mapping (image_swap.yml) (optional)")
    args = ap.parse_args()

    tpl = Path(args.template).resolve()
    if not tpl.exists(): sys.exit(f"Missing template: {tpl}")

    vars_map = {}
    if args.vars:
        yml = Path(args.vars).resolve()
        if not yml.exists(): sys.exit(f"Missing vars: {yml}")
        vars_map = load_vars(yml)

    vars_map.setdefault("STEM", tpl.stem)
    out_final = format_outpath(args.out, vars_map, default_dir=tpl.parent)

    if args.vars and args.imgs:
        with tempfile.TemporaryDirectory() as td:
            mid = Path(td) / (tpl.stem + "_replaced.pptx")
            apply_vars(tpl, Path(args.vars), mid)
            swap_frames_from_imgs(mid, Path(args.imgs), out_final)
        print(f"Pipeline done: replacer -> image-swap -> {out_final}")
    elif args.vars:
        apply_vars(tpl, Path(args.vars), out_final)
        print(f"Variables applied: {tpl.name} -> {out_final}")
    elif args.imgs:
        swap_frames_from_imgs(tpl, Path(args.imgs), out_final)
        print(f"Images swapped: {tpl.name} -> {out_final}")
    else:
        sys.exit("Nothing to do. Provide --vars, --imgs, or both.")


if __name__ == "__main__":
    main()

# Example usage:
# pptxvars --template templates/input_prs.pptx `
#          --vars templates/replace.yml `
#          --imgs templates/img_swap.yml `
#          --out "output/{STEM}_{DATE}.pptx"
