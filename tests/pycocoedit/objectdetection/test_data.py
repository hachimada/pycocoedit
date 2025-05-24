import json

import pytest

from pycocoedit.objectdetection.data import CocoData, _validate_keys
from pycocoedit.objectdetection.filter import (
    BaseFilter,
    CategoryNameFilter,
    FilterType,
    ImageFileNameFilter,
    TargetType,
)


def test_validate_keys_success():
    data = [
        {"id": 1, "name": "Data 1", "category": "A"},
        {"id": 2, "name": "Data 2", "category": "B"},
    ]
    required_keys = ["id", "name", "category"]
    _validate_keys(data, required_keys, "data item")


def test_validate_keys_failure():
    data = [{"id": 1, "name": "Data 1", "category": "A"}, {"id": 2, "category": "B"}]
    required_keys = ["id", "name", "category"]
    # KeyErrorが発生することを確認
    with pytest.raises(KeyError) as exc_info:
        _validate_keys(data, required_keys, "data item")
    # エラーメッセージの内容も確認
    assert "Missing keys ['name'] in data item with ID: 2" in str(exc_info.value)


def test_init(tmp_path):
    # given
    dataset = {
        "info": {},
        "licenses": [],
        "images": [
            {"file_name": "image0.jpg", "id": 1, "height": 100, "width": 100},
        ],
        "annotations": [
            {"id": 1, "image_id": 1, "category_id": 1, "segmentation": [], "area": 100, "bbox": [0, 0, 10, 10]},
        ],
        "categories": [
            {"id": 1, "name": "category1", "supercategory": "category1"},
        ],
    }

    annotaion_file = tmp_path / "annotations.json"
    with annotaion_file.open("w") as f:
        json.dump(dataset, f)

    # when
    coco_data1 = CocoData(dataset)
    coco_data2 = CocoData(str(annotaion_file))

    # then
    assert coco_data1.get_dataset() == dataset
    assert coco_data2.get_dataset() == dataset


class TestCorrect:
    def test_no_change(self):
        # given
        dataset = {
            "info": {},
            "licenses": [],
            "images": [
                {"file_name": "image0.jpg", "id": 1, "height": 100, "width": 100},
                {"file_name": "image1.jpg", "id": 2, "height": 200, "width": 200},
            ],
            "annotations": [
                {"id": 1, "image_id": 1, "category_id": 1, "segmentation": [], "area": 100, "bbox": [0, 0, 10, 10]},
                {"id": 2, "image_id": 2, "category_id": 2, "segmentation": [], "area": 100, "bbox": [0, 0, 10, 10]},
            ],
            "categories": [
                {"id": 1, "name": "category1", "supercategory": "category1"},
                {"id": 2, "name": "category2", "supercategory": "category2"},
            ],
        }

        # when
        coco_data = CocoData(dataset)
        coco_data.correct()

        # then
        assert coco_data.get_dataset() == dataset

    def test_remove_ann_with_no_category(self):
        # given
        dataset = {
            "info": {},
            "licenses": [],
            "images": [
                {"file_name": "image0.jpg", "id": 1, "height": 100, "width": 100},
                {"file_name": "image1.jpg", "id": 2, "height": 200, "width": 200},
            ],
            "annotations": [
                {"id": 1, "image_id": 1, "category_id": 1, "segmentation": [], "area": 100, "bbox": [0, 0, 10, 10]},
                {"id": 2, "image_id": 2, "category_id": 2, "segmentation": [], "area": 100, "bbox": [0, 0, 10, 10]},
            ],
            "categories": [
                {"id": 1, "name": "category1", "supercategory": "category1"},
            ],
        }

        # when
        coco_data = CocoData(dataset)
        coco_data.correct(correct_image=False)

        # then
        assert coco_data.get_dataset().get("images") == dataset["images"]
        assert coco_data.get_dataset().get("annotations") == [dataset["annotations"][0]]
        assert coco_data.get_dataset().get("categories") == dataset["categories"]

    def test_remove_ann_with_no_image(self):
        # given
        dataset = {
            "info": {},
            "licenses": [],
            "images": [
                {"file_name": "image0.jpg", "id": 1, "height": 100, "width": 100},
            ],
            "annotations": [
                {"id": 1, "image_id": 1, "category_id": 1, "segmentation": [], "area": 100, "bbox": [0, 0, 10, 10]},
                {"id": 2, "image_id": 2, "category_id": 2, "segmentation": [], "area": 100, "bbox": [0, 0, 10, 10]},
            ],
            "categories": [
                {"id": 1, "name": "category1", "supercategory": "category1"},
                {"id": 2, "name": "category2", "supercategory": "category2"},
            ],
        }

        # when
        coco_data = CocoData(dataset)
        coco_data.correct()

        # then
        assert coco_data.get_dataset().get("images") == dataset["images"]
        assert coco_data.get_dataset().get("annotations") == [dataset["annotations"][0]]
        assert coco_data.get_dataset().get("categories") == dataset["categories"]

    def test_remove_image_with_no_annotation(self):
        # given
        dataset = {
            "info": {},
            "licenses": [],
            "images": [
                {"file_name": "image0.jpg", "id": 1, "height": 100, "width": 100},
                {"file_name": "image1.jpg", "id": 2, "height": 200, "width": 200},
            ],
            "annotations": [
                {"id": 1, "image_id": 1, "category_id": 1, "segmentation": [], "area": 100, "bbox": [0, 0, 10, 10]},
            ],
            "categories": [
                {"id": 1, "name": "category1", "supercategory": "category1"},
                {"id": 2, "name": "category2", "supercategory": "category2"},
            ],
        }

        # when
        coco_data = CocoData(dataset)
        coco_data.correct(correct_image=True)

        # then
        assert coco_data.get_dataset().get("images") == [dataset["images"][0]]
        assert coco_data.get_dataset().get("annotations") == dataset["annotations"]
        assert coco_data.get_dataset().get("categories") == dataset["categories"]

        # when
        coco_data = CocoData(dataset)
        coco_data.correct(correct_image=False)

        # then
        assert coco_data.get_dataset() == dataset

    def test_remove_category_with_no_annotation(self):
        # given
        dataset = {
            "info": {},
            "licenses": [],
            "images": [
                {"file_name": "image0.jpg", "id": 1, "height": 100, "width": 100},
                {"file_name": "image1.jpg", "id": 2, "height": 200, "width": 200},
            ],
            "annotations": [
                {"id": 1, "image_id": 1, "category_id": 1, "segmentation": [], "area": 100, "bbox": [0, 0, 10, 10]},
                {"id": 2, "image_id": 2, "category_id": 2, "segmentation": [], "area": 100, "bbox": [0, 0, 10, 10]},
            ],
            "categories": [
                {"id": 1, "name": "category1", "supercategory": "category1"},
                {"id": 2, "name": "category2", "supercategory": "category2"},
                {"id": 3, "name": "category3", "supercategory": "category3"},
            ],
        }

        # when
        coco_data = CocoData(dataset)
        coco_data.correct(correct_category=True)

        # then
        assert coco_data.get_dataset().get("images") == dataset["images"]
        assert coco_data.get_dataset().get("annotations") == dataset["annotations"]
        assert coco_data.get_dataset().get("categories") == [
            dataset["categories"][0],
            dataset["categories"][1],
        ]

        # when
        coco_data = CocoData(dataset)
        coco_data.correct(correct_category=False)

        # then
        assert coco_data.get_dataset() == dataset


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

dataset = {
    "info": info,
    "licenses": licenses,
    "images": images,
    "annotations": annotations,
    "categories": categories,
}


def test_add_file_name_filter():
    # check file_name filter
    coco_data = CocoData(dataset)
    assert len(coco_data.image_filters.include_filters) == 0
    assert len(coco_data.image_filters.exclude_filters) == 0

    include_filter = ImageFileNameFilter(FilterType.INCLUSION, ["image0.jpg", "image1.jpg"])

    coco_data.add_filter(include_filter)
    coco_data.apply_filter()
    assert coco_data.images == [images[0], images[1]]
    assert coco_data.images[0]["file_name"] == "image0.jpg"
    assert coco_data.images[1]["file_name"] == "image1.jpg"
    assert coco_data.info == info
    assert coco_data.licenses == licenses
    assert coco_data.annotations == annotations
    assert coco_data.categories == categories

    exclude_filter = ImageFileNameFilter(FilterType.EXCLUSION, ["image1.jpg"])
    coco_data.add_filter(exclude_filter)
    coco_data.apply_filter()
    assert coco_data.images == [images[0]]
    assert coco_data.images[0]["file_name"] == "image0.jpg"
    assert coco_data.info == info
    assert coco_data.licenses == licenses
    assert coco_data.annotations == annotations
    assert coco_data.categories == categories

    coco_data.correct()
    assert coco_data.info == info
    assert coco_data.licenses == licenses
    assert coco_data.annotations == [annotations[0]]
    assert coco_data.images == [images[0]]
    assert coco_data.categories == categories

    coco_data.correct(correct_category=True)
    assert coco_data.info == info
    assert coco_data.licenses == licenses
    assert coco_data.annotations == [annotations[0]]
    assert coco_data.images == [images[0]]
    assert coco_data.categories == [categories[0]]


def test_add_category_filter():
    coco_data = CocoData(dataset)

    # check include filter
    include_filter = CategoryNameFilter(FilterType.INCLUSION, ["category0", "category1"])
    coco_data.add_filter(include_filter)
    coco_data.apply_filter()
    assert coco_data.info == info
    assert coco_data.licenses == licenses
    assert coco_data.annotations == annotations
    assert coco_data.images == images
    assert coco_data.categories == [categories[0], categories[1]]
    assert coco_data.categories[0]["name"] == "category0"
    assert coco_data.categories[1]["name"] == "category1"

    # check exclude filter
    exclude_filter = CategoryNameFilter(FilterType.EXCLUSION, ["category0"])
    coco_data.add_filter(exclude_filter)
    coco_data.apply_filter()
    assert coco_data.info == info
    assert coco_data.licenses == licenses
    assert coco_data.annotations == annotations
    assert coco_data.images == images
    assert coco_data.categories == [categories[1]]
    assert coco_data.categories[0]["name"] == "category1"

    # check correct
    coco_data.correct(correct_image=False)
    assert coco_data.info == info
    assert coco_data.licenses == licenses
    assert coco_data.annotations == [annotations[1]]
    assert coco_data.images == images
    assert coco_data.categories == [categories[1]]

    # check correct
    coco_data.correct()
    assert coco_data.info == info
    assert coco_data.licenses == licenses
    assert coco_data.annotations == [annotations[1]]
    assert coco_data.images == [images[1]]
    assert coco_data.categories == [categories[1]]


def test_add_custom_filter():
    class AreaInclusionFilter(BaseFilter):
        def __init__(self):
            super().__init__(FilterType.INCLUSION, TargetType.ANNOTATION)

        def apply(self, data: dict) -> bool:
            return data["area"] > 100

    coco_data = CocoData(dataset)
    coco_data.add_filter(AreaInclusionFilter())
    assert len(coco_data.annotation_filters.include_filters) == 1
    assert len(coco_data.annotation_filters.exclude_filters) == 0
    coco_data.apply_filter()
    assert coco_data.info == info
    assert coco_data.licenses == licenses
    assert coco_data.annotations == [annotations[1], annotations[2]]
    assert coco_data.images == images
    assert coco_data.categories == categories

    class AreaExclusionFilter(BaseFilter):
        def __init__(self):
            super().__init__(FilterType.EXCLUSION, TargetType.ANNOTATION)

        def apply(self, data: dict) -> bool:
            return data["area"] > 250

    coco_data.add_filter(AreaExclusionFilter())
    assert len(coco_data.annotation_filters.include_filters) == 1
    assert len(coco_data.annotation_filters.exclude_filters) == 1
    coco_data.apply_filter()
    assert coco_data.info == info
    assert coco_data.licenses == licenses
    assert coco_data.annotations == [annotations[1]]
    assert coco_data.images == images
    assert coco_data.categories == categories

    coco_data.correct()
    assert coco_data.info == info
    assert coco_data.licenses == licenses
    assert coco_data.annotations == [annotations[1]]
    assert coco_data.images == [images[1]]
    assert coco_data.categories == categories


def test_get_dataset():
    coco_data = CocoData(dataset)
    assert coco_data.get_dataset() == dataset


def test_sample():
    # given
    num = 100
    dataset = {
        "info": {},
        "licenses": [],
        "images": [
            {
                "file_name": f"image{i}.jpg",
                "id": i,
                "height": 100,
                "width": 100,
            }
            for i in range(num)
        ],
        "annotations": [
            {
                "id": i,
                "image_id": i,
                "category_id": i,
                "segmentation": [],
                "area": 100,
                "bbox": [0, 0, 10, 10],
            }
            for i in range(num)
        ],
        "categories": [{"id": i, "name": f"category{i}", "supercategory": f"category{i}"} for i in range(num)],
    }

    # when
    coco_data = CocoData(dataset)
    sampled = coco_data.sample(10, correct_category=False)

    # then
    assert len(sampled.get("images")) == 10
    assert len(sampled.get("annotations")) == 10
    assert len(sampled.get("categories")) == 100

    # when
    coco_data = CocoData(dataset)
    sampled = coco_data.sample(10, correct_category=True)

    # then
    assert len(sampled.get("images")) == 10
    assert len(sampled.get("annotations")) == 10
    assert len(sampled.get("categories")) == 10


class TestSave:
    @staticmethod
    def _make_base_dataset() -> dict:
        """
        Return a minimal COCO‑like dataset.

        * two images (id 1, 2)
        * one annotation (for image id 1)
        * two categories (id 1 is used, id 2 is isolated)
        """
        return {
            "info": {},
            "licenses": [],
            "images": [
                {"file_name": "img0.jpg", "id": 1, "height": 100, "width": 100},
                {"file_name": "img1.jpg", "id": 2, "height": 200, "width": 200},
            ],
            "annotations": [
                {
                    "id": 1,
                    "image_id": 1,
                    "category_id": 1,
                    "segmentation": [],
                    "area": 100,
                    "bbox": [0, 0, 10, 10],
                }
            ],
            "categories": [
                {"id": 1, "name": "cat", "supercategory": "cat"},
                {"id": 2, "name": "dog", "supercategory": "dog"},
            ],
        }

    def test_save_basic(self, tmp_path):
        # given
        ds = self._make_base_dataset()
        coco = CocoData(ds)
        out_path = tmp_path / "out.json"

        # when
        coco.save(out_path.as_posix())

        # then
        with out_path.open() as f:
            loaded = json.load(f)
        assert loaded == coco.get_dataset()

    def test_save_correct_image_false(self, tmp_path):
        # given: image id 2 is isolated (no annotation)
        ds = self._make_base_dataset()
        coco = CocoData(ds)
        out_path = tmp_path / "keep_isolated_img.json"

        # when
        coco.save(out_path.as_posix(), correct_image=False)

        # then
        with out_path.open() as f:
            loaded = json.load(f)
        assert len(loaded["images"]) == 2  # isolated image kept
        assert len(loaded["annotations"]) == 1  # annotation count unchanged

    def test_save_correct_category_true(self, tmp_path):
        # given: category id 2 is isolated (unused)
        ds = self._make_base_dataset()
        coco = CocoData(ds)
        out_path = tmp_path / "rm_isolated_cat.json"

        # when
        coco.save(out_path.as_posix(), correct_category=True)

        # then
        with out_path.open() as f:
            loaded = json.load(f)
        assert {c["id"] for c in loaded["categories"]} == {1}  # isolated category removed

    def test_save_to_nonexistent_dir(self, tmp_path):
        # given
        ds = self._make_base_dataset()
        coco = CocoData(ds)
        out_path = tmp_path / "no_dir" / "out.json"

        # when / then
        with pytest.raises(FileNotFoundError):
            coco.save(out_path.as_posix())
