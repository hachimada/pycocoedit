import pytest

from pycocoedit.cocodata import CocoEditor, Filters, validate_keys
from pycocoedit.filter import BaseExclusionFilter, BaseInclusionFilter


def test_validate_keys_success():
    data = [
        {"id": 1, "name": "Data 1", "category": "A"},
        {"id": 2, "name": "Data 2", "category": "B"},
    ]
    required_keys = ["id", "name", "category"]
    validate_keys(data, required_keys, "data item")


def test_validate_keys_failure():
    data = [{"id": 1, "name": "Data 1", "category": "A"}, {"id": 2, "category": "B"}]
    required_keys = ["id", "name", "category"]
    # KeyErrorが発生することを確認
    with pytest.raises(KeyError) as exc_info:
        validate_keys(data, required_keys, "data item")
    # エラーメッセージの内容も確認
    assert "Missing keys ['name'] in data item with ID: 2" in str(exc_info.value)


def test_filters_add():
    filters = Filters()
    assert len(filters.include_filters) == 0
    assert len(filters.exclude_filters) == 0

    class MockFilter(BaseInclusionFilter):
        def apply(self, data: dict) -> bool:
            return True

    filters.add(MockFilter())
    assert len(filters.include_filters) == 1
    assert len(filters.exclude_filters) == 0

    filters.add(MockFilter())
    assert len(filters.include_filters) == 2
    assert len(filters.exclude_filters) == 0

    class MockFilter(BaseExclusionFilter):
        def apply(self, data: dict) -> bool:
            return True

    filters.add(MockFilter())
    assert len(filters.include_filters) == 2
    assert len(filters.exclude_filters) == 1


info = {
    "description": "COCO 2020 Dataset",
    "url": "http://cocodataset.org",
    "version": "1.0",
    "year": 2020,
    "contributor": "COCO Consortium",
    "date_created": "2020/12/10",
}
licenses = [{"id": 1, "name": "License", "url": ""}]
images = [
    {
        "date_captured": "2020",
        "file_name": "image0.jpg",
        "id": 1,
        "height": 100,
        "width": 100,
    },
    {
        "date_captured": "2020",
        "file_name": "image1.jpg",
        "id": 2,
        "height": 200,
        "width": 200,
    },
    {
        "date_captured": "2021",
        "file_name": "image2.jpg",
        "id": 3,
        "height": 300,
        "width": 300,
    },
]
annotations = [
    {
        "id": 1,
        "image_id": 1,
        "category_id": 1,
        "segmentation": [],
        "area": 100,
        "bbox": [0, 0, 100, 100],
        "iscrowd": 0,
    },
    {
        "id": 2,
        "image_id": 2,
        "category_id": 2,
        "segmentation": [],
        "area": 200,
        "bbox": [0, 0, 200, 200],
        "iscrowd": 0,
    },
    {
        "id": 3,
        "image_id": 3,
        "category_id": 3,
        "segmentation": [],
        "area": 300,
        "bbox": [0, 0, 300, 300],
        "iscrowd": 0,
    },
]
categories = [
    {"id": 1, "name": "category0", "supercategory": "category"},
    {"id": 2, "name": "category1", "supercategory": "category"},
    {"id": 3, "name": "category2", "supercategory": "category"},
]

annotation = {
    "info": info,
    "licenses": licenses,
    "images": images,
    "annotations": annotations,
    "categories": categories,
}


def test_add_file_name_filter():
    # check file_name filter
    editor = CocoEditor(annotation)
    assert len(editor.image_filters.include_filters) == 0
    assert len(editor.image_filters.exclude_filters) == 0

    editor.add_file_name_filter(include_files=["image0.jpg", "image1.jpg"])
    assert len(editor.image_filters.include_filters) == 1
    assert len(editor.image_filters.exclude_filters) == 0
    editor.apply_filter()
    assert editor.images == [images[0], images[1]]
    assert editor.images[0]["file_name"] == "image0.jpg"
    assert editor.images[1]["file_name"] == "image1.jpg"
    assert editor.info == info
    assert editor.licenses == licenses
    assert editor.annotations == annotations
    assert editor.categories == categories

    editor.add_file_name_filter(exclude_files=["image1.jpg"])
    assert len(editor.image_filters.include_filters) == 1
    assert len(editor.image_filters.exclude_filters) == 1
    editor.apply_filter()
    assert editor.images == [images[0]]
    assert editor.images[0]["file_name"] == "image0.jpg"
    assert editor.info == info
    assert editor.licenses == licenses
    assert editor.annotations == annotations
    assert editor.categories == categories

    editor.correct()
    assert editor.info == info
    assert editor.licenses == licenses
    assert editor.annotations == [annotations[0]]
    assert editor.images == [images[0]]
    assert editor.categories == categories

    editor.correct(correct_category=True)
    assert editor.info == info
    assert editor.licenses == licenses
    assert editor.annotations == [annotations[0]]
    assert editor.images == [images[0]]
    assert editor.categories == [categories[0]]


def test_add_category_filter():
    # check include filter
    editor = CocoEditor(annotation)
    editor.add_category_filter(include_names=["category0", "category1"])
    assert len(editor.category_filters.include_filters) == 1
    assert len(editor.category_filters.exclude_filters) == 0
    editor.apply_filter()
    assert editor.info == info
    assert editor.licenses == licenses
    assert editor.annotations == annotations
    assert editor.images == images
    assert editor.categories == [categories[0], categories[1]]
    assert editor.categories[0]["name"] == "category0"
    assert editor.categories[1]["name"] == "category1"

    # check exclude filter
    editor.add_category_filter(exclude_names=["category0"])
    assert len(editor.category_filters.include_filters) == 1
    assert len(editor.category_filters.exclude_filters) == 1
    editor.apply_filter()
    assert editor.info == info
    assert editor.licenses == licenses
    assert editor.annotations == annotations
    assert editor.images == images
    assert editor.categories == [categories[1]]
    assert editor.categories[0]["name"] == "category1"

    # check correct
    editor.correct(correct_image=False)
    assert editor.info == info
    assert editor.licenses == licenses
    assert editor.annotations == [annotations[1]]
    assert editor.images == images
    assert editor.categories == [categories[1]]

    # check correct
    editor.correct()
    assert editor.info == info
    assert editor.licenses == licenses
    assert editor.annotations == [annotations[1]]
    assert editor.images == [images[1]]
    assert editor.categories == [categories[1]]


def test_add_custom_filter():
    class AreaInclusionFilter(BaseInclusionFilter):
        def apply(self, data: dict) -> bool:
            return data["area"] > 100

    editor = CocoEditor(annotation)
    editor.add_custom_filter(AreaInclusionFilter(), "annotation")
    assert len(editor.annotation_filters.include_filters) == 1
    assert len(editor.annotation_filters.exclude_filters) == 0
    editor.apply_filter()
    assert editor.info == info
    assert editor.licenses == licenses
    assert editor.annotations == [annotations[1], annotations[2]]
    assert editor.images == images
    assert editor.categories == categories

    class AreaExclusionFilter(BaseExclusionFilter):
        def apply(self, data: dict) -> bool:
            return data["area"] > 250

    editor.add_custom_filter(AreaExclusionFilter(), "annotation")
    assert len(editor.annotation_filters.include_filters) == 1
    assert len(editor.annotation_filters.exclude_filters) == 1
    editor.apply_filter()
    assert editor.info == info
    assert editor.licenses == licenses
    assert editor.annotations == [annotations[1]]
    assert editor.images == images
    assert editor.categories == categories

    editor.correct()
    assert editor.info == info
    assert editor.licenses == licenses
    assert editor.annotations == [annotations[1]]
    assert editor.images == [images[1]]
    assert editor.categories == categories


def test_reset():
    class SimpleInclusionFilter(BaseExclusionFilter):
        def apply(self, data: dict) -> bool:
            return True

    editor = CocoEditor(annotation)
    editor.add_file_name_filter(
        include_files=["image0.jpg", "image1.jpg"], exclude_files=["image1.jpg"]
    )
    editor.add_category_filter(
        include_names=["category0", "category1"], exclude_names=["category0"]
    )
    editor.add_custom_filter(SimpleInclusionFilter(), "annotation")
    editor.apply_filter().correct()

    editor.reset(annotation)

    assert editor.info == info
    assert editor.licenses == licenses
    assert editor.images == images
    assert editor.annotations == annotations
    assert editor.categories == categories
    assert len(editor.image_filters.include_filters) == 0
    assert len(editor.image_filters.exclude_filters) == 0
    assert len(editor.category_filters.include_filters) == 0
    assert len(editor.category_filters.exclude_filters) == 0
    assert len(editor.annotation_filters.include_filters) == 0
    assert len(editor.annotation_filters.exclude_filters) == 0
    assert len(editor.licenses_filters.include_filters) == 0
    assert len(editor.licenses_filters.exclude_filters) == 0
