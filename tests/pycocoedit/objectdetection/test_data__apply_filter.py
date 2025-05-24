"""
test for ``pycocoedit.objectdetection.data.CocoData.apply_filter``
"""

import pytest

from pycocoedit.objectdetection.data import CocoData
from pycocoedit.objectdetection.filter import BaseFilter, FilterType, ImageFileNameFilter, TargetType


class AnnotationExcludeDummyFilter(BaseFilter):
    """Dummy exclusion filter returning a constant boolean."""

    def __init__(self, is_exclude: bool) -> None:
        super().__init__(FilterType.EXCLUSION, TargetType.ANNOTATION)
        self._is_exclude: bool = is_exclude

    def apply(self, data: dict) -> bool:
        return self._is_exclude


class AnnotationIncludeDummyFilter(BaseFilter):
    """Dummy inclusion filter returning a constant boolean."""

    def __init__(self, is_include: bool) -> None:
        super().__init__(FilterType.INCLUSION, TargetType.ANNOTATION)
        self._is_include: bool = is_include

    def apply(self, data: dict) -> bool:
        return self._is_include


COCO_DATA: dict = {
    "images": [
        {"id": 1, "file_name": "keep.jpg", "width": 640, "height": 480},
    ],
    "annotations": [
        {
            "id": 1,
            "image_id": 1,
            "category_id": 1,
            "segmentation": [],
            "bbox": [0, 0, 10, 10],
            "area": 100,
            "iscrowd": 0,
        },
    ],
    "categories": [
        {"id": 1, "name": "cat", "supercategory": "cat"},
    ],
}


@pytest.mark.parametrize(
    "filter1, filter2, is_keep_data",
    [
        # Any filter returns True → remove annotations
        (
            AnnotationExcludeDummyFilter(is_exclude=True),
            AnnotationExcludeDummyFilter(is_exclude=False),
            False,
        ),
        (
            AnnotationExcludeDummyFilter(is_exclude=False),
            AnnotationExcludeDummyFilter(is_exclude=True),
            False,
        ),
        (
            AnnotationExcludeDummyFilter(is_exclude=True),
            AnnotationExcludeDummyFilter(is_exclude=True),
            False,
        ),
        # All filters return False → keep annotations
        (
            AnnotationExcludeDummyFilter(is_exclude=False),
            AnnotationExcludeDummyFilter(is_exclude=False),
            True,
        ),
    ],
)
def test_exclude_combination(filter1: BaseFilter, filter2: BaseFilter, is_keep_data: bool) -> None:
    """Verify the logic of multiple exclusion filters.

    The sample COCO data contains **one** image / annotation pair.
    If any exclusion filter returns ``True``, the pair must be removed.
    If all exclusion filters return ``False``, the pair must be kept.
    """
    # given
    coco = CocoData(COCO_DATA).add_filter(filter1).add_filter(filter2)

    # when
    filtered = coco.apply_filter().correct()

    # then
    kept = len(filtered.annotations) == 1

    assert kept == is_keep_data


def test_include_exclude_combination() -> None:
    """Verify the logic of inclusion and exclusion filters."""
    # given
    coco = (
        CocoData(COCO_DATA)
        .add_filter(AnnotationExcludeDummyFilter(is_exclude=True))
        .add_filter(AnnotationExcludeDummyFilter(is_exclude=False))
    )

    # when
    filtered = coco.apply_filter().correct()

    # then
    kept = len(filtered.annotations) == 1

    assert not kept


@pytest.mark.parametrize(
    "filter1, filter2, is_keep_data",
    [
        # Any filter returns True → keep annotations
        (
            AnnotationIncludeDummyFilter(is_include=True),
            AnnotationIncludeDummyFilter(is_include=False),
            True,
        ),
        (
            AnnotationIncludeDummyFilter(is_include=False),
            AnnotationIncludeDummyFilter(is_include=True),
            True,
        ),
        (
            AnnotationIncludeDummyFilter(is_include=True),
            AnnotationIncludeDummyFilter(is_include=True),
            True,
        ),
        # All filters return False → remove annotations
        (
            AnnotationIncludeDummyFilter(is_include=False),
            AnnotationIncludeDummyFilter(is_include=False),
            False,
        ),
    ],
)
def test_include_combination(filter1: BaseFilter, filter2: BaseFilter, is_keep_data: bool) -> None:
    """Verify the logic of multiple inclusion filters.

    The sample COCO data contains **one** image / annotation pair.
    If any inclusion filter returns True, the pair must be kept
    """
    # given
    coco = CocoData(COCO_DATA).add_filter(filter1).add_filter(filter2)

    # when
    filtered = coco.apply_filter().correct()

    # then
    kept = len(filtered.annotations) == 1

    assert kept == is_keep_data


def test_correct_readded_filter() -> None:
    """Verify that a re-added filter is also corrected."""

    # given
    dataset = {
        "info": {},
        "licenses": [],
        "images": [
            {"file_name": "image1.jpg", "id": 1, "height": 100, "width": 100},
            {"file_name": "image2.jpg", "id": 2, "height": 200, "width": 200},
        ],
        "annotations": [
            {
                "id": 1,
                "image_id": 1,
                "category_id": 1,
                "segmentation": [],
                "area": 100,
                "bbox": [0, 0, 10, 10],
            },
            {
                "id": 2,
                "image_id": 2,
                "category_id": 2,
                "segmentation": [],
                "area": 100,
                "bbox": [0, 0, 10, 10],
            },
        ],
        "categories": [
            {"id": 1, "name": "cat1", "supercategory": "cat"},
            {"id": 2, "name": "cat2", "supercategory": "cat"},
        ],
    }
    coco = CocoData(dataset)

    # when: Apply first filter
    coco.add_filter(ImageFileNameFilter(FilterType.EXCLUSION, ["image1.jpg"]))
    result1 = coco.apply_filter().correct().get_dataset()

    # then: added filter should be corrected
    assert result1["images"] == dataset["images"][1:]  # type: ignore[index]
    assert result1["annotations"] == dataset["annotations"][1:]  # type: ignore[index]
    assert result1["categories"] == dataset["categories"]

    # when: Add second filter
    coco.add_filter(ImageFileNameFilter(FilterType.EXCLUSION, ["image2.jpg"]))
    result2 = coco.apply_filter().correct().get_dataset()

    # then: added filter should be corrected
    assert result2["images"] == []
    assert result2["annotations"] == []
    assert result2["categories"] == dataset["categories"]
