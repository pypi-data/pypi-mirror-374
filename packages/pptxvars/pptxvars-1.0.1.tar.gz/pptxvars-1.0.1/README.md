# pptxvars

- **Replace {{KEY}} tokens in PPTX while preserving styling**
- **Swap a Frame for an image in PPTX while preserving size**
- Execute both in sequence from CLI or through import

---

#### Install [pptxvars](https://pypi.org/project/pptxvars/)

```
pip install pptxvars
```

---

## Replace Variables

1. Create a custom powerpoint presentation
2. Define your variables in powerpoint textboxes by {{VARIABLE_NAME}}
3. Define in a YAML file what values must replace the {{KEYS}}. YAML format: `KEY: "value"`
4. Execute replacement (from CLI):

```powershell
pptxvars --template templates/example_prs.pptx `
         --vars templates/example.yml `
         --out 'output/{STEM}_{DATE}.pptx'
```

---

## Swap Frame for Image

1. Create a custom powerpoint presentation
2. Insert frames as placeholder for an image. In powerpoint you can find a frame shape under: `Insert>Shapes>Basic Shapes>Frame`
3. Define in a YAML file what Frames must be swaped. The Frames are swaped per slide in order (Top>Right). YAML format:

```yml
slides:
  - index: 1
    images:
      - example_img.png
```

4. Execute image swap (from CLI):

```powershell
pptxvars --template templates/example_prs.pptx `
         --imgs templates/image_swap.yml `
         --out "output/{STEM}_swapped.pptx"

```

## Both in sequence: replace variables and swap frames for images

From powershell CLI:

```powershell
pptxvars --template templates/input_prs.pptx `
          --vars templates/replace.yml `
          --imgs templates/img_swap.yml `
          --out "output/{STEM}_{DATE}.pptx"
```

From notebook by import:

```python
from pptxvars import render_presentation

output_prs = render_presentation(
    template="templates/input_prs.pptx",
    vars_yml="templates/replace.yml",
    imgs_yml="templates/img_swap.yml",
    out_pattern="output/{STEM}_{DATE}.pptx",
)
```
