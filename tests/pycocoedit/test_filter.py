import pytest

from pycocoedit.filter import (BoxAreaIncludeFilter, CategoryExcludeFilter,
                               CategoryIncludeFilter, ImageNameExcludeFilter,
                               ImageNameIncludeFilter)


# ImageFileIncludeFilterのテスト
@pytest.mark.parametrize(
    "file_names, data, expected",
    [
        (["image1.jpg", "image2.jpg"], {"file_name": "image1.jpg"}, True),
        (["image1.jpg", "image2.jpg"], {"file_name": "image3.jpg"}, False),
        ([], {"file_name": "image1.jpg"}, False),
    ],
)
def test_image_file_include_filter(file_names, data, expected):
    image_filter = ImageNameIncludeFilter(file_names)
    assert image_filter.apply(data) == expected


# ImageFileExcludeFilterのテスト
@pytest.mark.parametrize(
    "file_names, data, expected",
    [
        (["image1.jpg", "image2.jpg"], {"file_name": "image1.jpg"}, True),
        (["image1.jpg", "image2.jpg"], {"file_name": "image3.jpg"}, False),
        ([], {"file_name": "image1.jpg"}, False),
    ],
)
def test_image_file_exclude_filter(file_names, data, expected):
    image_filter = ImageNameExcludeFilter(file_names)
    assert image_filter.apply(data) == expected


# CategoryIncludeFilterのテスト
@pytest.mark.parametrize(
    "category_names, data, expected",
    [
        (["cat", "dog"], {"name": "cat"}, True),
        (["cat", "dog"], {"name": "bird"}, False),
        ([], {"name": "cat"}, False),
    ],
)
def test_category_include_filter(category_names, data, expected):
    category_filter = CategoryIncludeFilter(category_names)
    assert category_filter.apply(data) == expected


# CategoryExcludeFilterのテスト
@pytest.mark.parametrize(
    "category_names, data, expected",
    [
        (["cat", "dog"], {"name": "cat"}, True),
        (["cat", "dog"], {"name": "bird"}, False),
        ([], {"name": "cat"}, False),
    ],
)
def test_category_exclude_filter(category_names, data, expected):
    category_filter = CategoryExcludeFilter(category_names)
    assert category_filter.apply(data) == expected


# BoxAreaIncludeFilterのテスト
@pytest.mark.parametrize(
    "min_area, max_area, data, expected",
    [
        (100, 200, {"area": 99}, False),
        (100, 200, {"area": 100}, True),
        (100, 200, {"area": 101}, True),
        (100, 200, {"area": 199}, True),
        (100, 200, {"area": 200}, True),
        (100, 200, {"area": 201}, False),
        (None, 200, {"area": 199}, True),
        (None, 200, {"area": 200}, True),
        (None, 200, {"area": 201}, False),
        (100, None, {"area": 99}, False),
        (100, None, {"area": 100}, True),
        (100, None, {"area": 101}, True),
    ],
)
def test_box_area_include_filter(min_area, max_area, data, expected):
    area_filter = BoxAreaIncludeFilter(min_area=min_area, max_area=max_area)
    assert area_filter.apply(data) == expected
