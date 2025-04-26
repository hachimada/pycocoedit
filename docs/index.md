---
hide:
  - toc
---

<div style="text-align: center;">
  <div class="centered-logo-text-group">
    <img src="assets/pycocoedit.png" alt="pycocoedit Logo" width="120">
    <h1>pycocoedit</h1>
  </div>
</div>

## What is pycocoedit?

pycocoedit is a lightweight, dependency-free Python library for **querying**, **filtering**, and **rewriting**
COCO-format
annotation files.

Need to pull only 10 % of each class for a quick experiment?  
Need to keep only chosen categories—or trim out a few you don’t need?  
Maybe you just need the images whose filenames begin with night_?

With pycocoedit you write those rules in two-or-three short, readable lines—no manual JSON surgery, no error-prone
for-loops.

<div class="install-command-container">
  <p style="text-align:center;">
    Get started:
    <br/>
    <code>pip install pycocoedit</code>
  </p>
</div>

## Why pycocoedit?

- **Complex filtering in short, readable code**  
  Quickly create subsets such as "limit to 200 images per category, then exclude bboxes smaller than 32²."

- **Automatic data cleanup**  
  Removes annotations with invalid category or image IDs, and optionally cleans out images or categories without
  annotations.

- **Zero external dependencies**  
  Runs anywhere Python does—install with just `pip install pycocoedit`, perfect for Colab or CI environments.

## Quick Start

```python
from pycocoedit.objectdetection.data import CocoData
from pycocoedit.objectdetection.filter import BoxAreaFilter, CategoryNameFilter, FilterType

# 1. Load COCO JSON
coco = CocoData("annotations/train.json")

# 2. Keep only annotation with area between 10 and 100
file_filter = BoxAreaFilter(filter_type=FilterType.INCLUSION, min_area=10, max_area=100)

# 3. Drop annotations with category names "car" and "truck"
cat_filter = CategoryNameFilter(
    filter_type=FilterType.EXCLUSION,
    category_names=["car", "truck"]
)

# 4. Apply filters and save
coco.add_filter(file_filter).add_filter(cat_filter).apply_filter().save("annotations.json")
```

## Installation

```terminal
pip install pycocoedit
```

**No external dependencies required.**

## Key Features

| Feature                          | What it gives you                                                                                     |
|----------------------------------|-------------------------------------------------------------------------------------------------------|
| **LEGO-style chainable filters** | One-liner `include` / `exclude` rules for images, annotations, categories, etc.                       |
| **Custom rules**                 | simply inherit `BaseFilter`, implement a short apply() method, and your custom logic is ready to use. |
| **Built-in data cleanup**        | `CocoData.correct()` - Built-in data cleanup that removes orphaned annotations & empty categories.    |
| **Pure Python ≥ 3.10**           | Zero external deps; runs anywhere CPython runs—no C build hassle.                                     |
| **Typed & unit-tested**          | IDE auto-completion and high confidence when refactoring.                                             |

## Task Support

| Task                  | Supported                            | version |
|-----------------------|--------------------------------------|---------|
| Object Detection      | ✅ (`pycocoedit.objectdetection`)     | 0.1.0   |
| Image Segmentation    | ✅ (use `pycocoedit.objectdetection`) | 0.1.0   |
| Keypoint Detection    | ❌ (future release)                   |         |
| Panoptic Segmentation | ❌ (future release)                   |         |
| Image Captioning      | ❌ (future release)                   |         |

## Roadmap

1. Image Captioning
2. key-point support
3. Panoptic Segmentation

Contributions and ideas are welcome—feel free to open an issue or pull request on GitHub!  
© 2025 Nao Yamada · Licensed under the Apache License 2.0
