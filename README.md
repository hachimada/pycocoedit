# pycocoedit

**pycocoedit** is a Python package for editing and analyzing COCO datasets.

It is particularly useful for specifying which images, annotations, categories, or licenses to include or exclude from your dataset.

With **pycocoedit**, you can apply custom filters to your dataset. These filters allow you to control inclusion or exclusion based on custom conditions for images, categories, annotations, and licenses.

For example, you can filter out specific images that have a certain number of annotations or exclude annotations with bounding boxes of a certain aspect ratio.


## Usage

Example of filtering images and categories.
```python
from pycocoedit.cocodata import CocoEditor
annotation = "path/to/annotation.json"

editor = CocoEditor(annotation)
editor.add_file_name_filter(
        exclude_files=["image1.jpg", "image2.jpg"]  # exclude images with names "image1.jpg" or "image2.jpg"
    ) \
    .add_category_filter(
        include_names=["cat", "dog"]  # only include categories with names "cat" or "dog"
    ) \
    .apply_filter().correct()
```

Example of custom filter for annotations:
In this example, we create a custom filter that only includes annotations with bounding boxes of area less than 100.
```python
from pycocoedit.cocodata import CocoEditor
from pycocoedit.filter import BaseInclusionFilter

class SmallBboxIncludeFilter(BaseInclusionFilter):
    def __init__(self):
        super().__init__()

    def apply(self, data: dict) -> bool:
        return data["area"] < 100
    
annotation = "path/to/annotation.json"

editor = CocoEditor(annotation)
editor.add_custom_filter(
        SmallBboxIncludeFilter(), target_type="annotation"  # only include annotations with area less than 100
    ).apply_filter().correct()
```

## Installation

```
git clone https://github.com/Nao-Y1996/pycocoedit.git
cd pycocoedit
poetry install
```

## Features

- Filter images by file name
- Filter categories by category name
- Filter images by custom conditions
- Filter categories by custom conditions
- Filter annotations by custom conditions
- Fix inconsistencies after applying filters

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.


