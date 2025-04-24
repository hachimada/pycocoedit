# pycocoedit

[![ci](https://github.com/hachimada/pycocoedit/actions/workflows/ci.yml/badge.svg)](https://github.com/hachimada/pycocoedit/actions)
[![codecov](https://codecov.io/gh/hachimada/pycocoedit/branch/main/graph/badge.svg)](https://codecov.io/gh/hachimada/pycocoedit)


**pycocoedit** is a Python package for editing and analyzing COCO datasets.

It is particularly useful for specifying which images, annotations, categories, or licenses to include or exclude from your dataset.

With **pycocoedit**, you can apply custom filters to your dataset. These filters allow you to control inclusion or exclusion based on custom conditions for images, categories, annotations, and licenses.

For example, you can filter out specific images that have a certain number of annotations or exclude annotations with bounding boxes of a certain aspect ratio.


## Usage

Example of filtering images and categories.

```python
from pycocoedit.objectdetection.data import CocoData
from objectdetection.filter import FilterType, ImageFileNameFilter, CategoryNameFilter

annotation = "path/to/annotation.json"
new_annotation = "path/to/new_annotation.json"

# only include images with file name "image1.jpg" and "image2.jpg"
file_filter = ImageFileNameFilter(FilterType.INCLUSION, ["image1.jpg", "image2.jpg"])
# only include categories with category name "cat" and "dog"
category_filter = CategoryNameFilter(FilterType.INCLUSION, ["cat", "dog"])

coco_data = CocoData(annotation)
# apply filters and export new annotation
coco_data.add_filter(file_filter).add_filter(category_filter).apply_filter().save(new_annotation)
```

Example of custom filter for annotations:
In this example, we create a custom filter that only includes annotations with bounding boxes of area less than 100.

```python
from pycocoedit.objectdetection.data import CocoData
from objectdetection.filter import BaseFilter, FilterType, TargetType


# only include annotations with area less than 100
class SmallBboxIncludeFilter(BaseFilter):
    def __init__(self):
        super().__init__(FilterType.INCLUSION, TargetType.ANNOTATION)

    def apply(self, data: dict) -> bool:
        return data["area"] < 100


annotation = "path/to/annotation.json"
new_annotation = "path/to/new_annotation.json"

coco_data = CocoData(annotation)
# apply custom filter and export new annotation
coco_data.add_filter(SmallBboxIncludeFilter()).apply_filter().save(new_annotation)
```

## Installation

```
git clone https://github.com/hachimada/pycocoedit.git
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


