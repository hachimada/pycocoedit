import pytest

from pycocoedit.objectdetection.filter import (
    BaseFilter,
    BoxAreaFilter,
    CategoryNameFilter,
    Filters,
    FilterType,
    ImageFileNameFilter,
    TargetType,
)


class TestBaseFilterGeneral:
    """General unit tests for BaseFilter."""

    def test_cannot_instantiate(self) -> None:
        """Ensure BaseFilter cannot be instantiated while abstract methods remain."""
        with pytest.raises(TypeError):
            BaseFilter(FilterType.INCLUSION, TargetType.IMAGE)  # type: ignore[abstract]

    def test_invalid_types(self) -> None:
        """Passing invalid filter_type or target_type should raise TypeError."""

        class DummyFilter(BaseFilter):
            def __init__(self, filter_type, target_type) -> None:
                super().__init__(filter_type, target_type)

            def apply(self, data: dict) -> bool:
                return True  # pragma: no cover

        # filter_type is not an instance of FilterType
        with pytest.raises(TypeError):
            DummyFilter(object, TargetType.IMAGE)

        # target_type is not an instance of TargetType
        with pytest.raises(TypeError):
            DummyFilter(FilterType.INCLUSION, object)

    def test_apply_override(self) -> None:
        """A subclass that overrides apply should return the value provided by the override."""

        class AlwaysTrueFilter(BaseFilter):
            def __init__(self) -> None:
                super().__init__(FilterType.INCLUSION, TargetType.IMAGE)

            def apply(self, data: dict) -> bool:
                return True

        filt = AlwaysTrueFilter()
        assert filt.apply({}) is True


@pytest.mark.parametrize(
    "file_names, data, expected",
    [
        (["image1.jpg", "image2.jpg"], {"file_name": "image1.jpg"}, True),
        (["image1.jpg", "image2.jpg"], {"file_name": "image3.jpg"}, False),
        ([], {"file_name": "image1.jpg"}, False),
    ],
)
def test_image_file_include_filter(file_names, data, expected):
    image_filter = ImageFileNameFilter(FilterType.INCLUSION, file_names)
    assert image_filter.apply(data) == expected


# ImageFileNameFilter(exclude)のテスト
@pytest.mark.parametrize(
    "file_names, data, expected",
    [
        (["image1.jpg", "image2.jpg"], {"file_name": "image1.jpg"}, True),
        (["image1.jpg", "image2.jpg"], {"file_name": "image3.jpg"}, False),
        ([], {"file_name": "image1.jpg"}, False),
    ],
)
def test_image_file_exclude_filter(file_names, data, expected):
    image_filter = ImageFileNameFilter(FilterType.EXCLUSION, file_names)
    assert image_filter.apply(data) == expected


# CategoryNameFilter(include)のテスト
@pytest.mark.parametrize(
    "category_names, data, expected",
    [
        (["cat", "dog"], {"name": "cat"}, True),
        (["cat", "dog"], {"name": "bird"}, False),
        ([], {"name": "cat"}, False),
    ],
)
def test_category_include_filter(category_names, data, expected):
    category_filter = CategoryNameFilter(FilterType.INCLUSION, category_names)
    assert category_filter.apply(data) == expected


# CategoryNameFilter(exclude)のテスト
@pytest.mark.parametrize(
    "category_names, data, expected",
    [
        (["cat", "dog"], {"name": "cat"}, True),
        (["cat", "dog"], {"name": "bird"}, False),
        ([], {"name": "cat"}, False),
    ],
)
def test_category_exclude_filter(category_names, data, expected):
    category_filter = CategoryNameFilter(FilterType.EXCLUSION, category_names)
    assert category_filter.apply(data) == expected


# BoxAreaFilterのテスト
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
    include_filter = BoxAreaFilter(FilterType.INCLUSION, min_area=min_area, max_area=max_area)
    assert include_filter.apply(data) == expected


def test_filters_add():
    filters = Filters()
    assert len(filters.include_filters) == 0
    assert len(filters.exclude_filters) == 0

    class MockInclusionFilter(BaseFilter):
        def __init__(self):
            super().__init__(FilterType.INCLUSION, TargetType.IMAGE)

        def apply(self, data: dict) -> bool:
            return True  # pragma: no cover

    filters.add(MockInclusionFilter())
    assert len(filters.include_filters) == 1
    assert len(filters.exclude_filters) == 0

    filters.add(MockInclusionFilter())
    assert len(filters.include_filters) == 2
    assert len(filters.exclude_filters) == 0

    class MockExclusionFilter(BaseFilter):
        def __init__(self):
            super().__init__(FilterType.EXCLUSION, TargetType.IMAGE)

        def apply(self, data: dict) -> bool:
            return True  # pragma: no cover

    filters.add(MockExclusionFilter())
    assert len(filters.include_filters) == 2
    assert len(filters.exclude_filters) == 1
