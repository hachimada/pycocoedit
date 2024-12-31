from abc import ABC, abstractmethod
from enum import Enum


class FilterType(Enum):
    """
    Enum class for filter types.

    Attributes
    ----------
    INCLUSION : int
        The inclusion filter type. Value is 1.
    EXCLUSION : int
        The exclusion filter type. Value is 2.
    """

    INCLUSION = 1
    EXCLUSION = 2


class TargetType(Enum):
    """
    Enum class for filter types.

    Attributes
    ----------
    IMAGE : str
    ANNOTATION : str
    CATEGORY : str
    LICENSE : str
    """

    IMAGE = "image"
    ANNOTATION = "annotation"
    CATEGORY = "category"
    LICENSE = "license"


class BaseFilter(ABC):
    """Base class for filters.

    Attributes
    ----------
    filter_type : FilterType | None
        The type of the filter.
    """

    def __init__(self, filter_type: FilterType, target_type: TargetType):
        if not isinstance(filter_type, FilterType) or filter_type is None:
            raise ValueError("filter_type must be a FilterType and not None.")
        if not isinstance(target_type, TargetType) or target_type is None:
            raise ValueError("target_type must be a TargetType and not None.")
        self.filter_type: FilterType = filter_type
        self.target_type: TargetType = target_type

    @abstractmethod
    def apply(self, data: dict) -> bool:
        """Apply the filter to the data.

        Implement logic within this function to determine what data to include or exclude to your dataset.

        -  when self.filter_type is INCLUSION and this function return True, the data is included
        -  when self.filter_type is INCLUSION and this function return False, the data is excluded
        -  when self.filter_type is EXCLUSION and this function return True, the data is excluded
        -  when self.filter_type is EXCLUSION and this function return False, the data is included

        Parameters:
        -----------
        data : dict
            The data to filter.
            data is expected to be as follows
            - element of the images in the COCO format
            - element of the annotations in the COCO format
            - element of the categories in the COCO format
            - element of the licenses in the COCO format
            - info in the COCO format
            - other dict elements
        """
        raise NotImplementedError


class Filters:

    def __init__(self):
        self.include_filters: list[BaseFilter] = []
        self.exclude_filters: list[BaseFilter] = []

    def add(self, filter: BaseFilter) -> None:
        if filter.filter_type == FilterType.INCLUSION and isinstance(
            filter, BaseFilter
        ):
            self.include_filters.append(filter)
        if filter.filter_type == FilterType.EXCLUSION and isinstance(
            filter, BaseFilter
        ):
            self.exclude_filters.append(filter)


class ImageFileNameFilter(BaseFilter):
    """
    Filter class to filter data by image file name.

    Attributes
    ----------
    filter_type : FilterType
        - The type of the filter.FilterType.INCLUSION or FilterType.EXCLUSION.
        - if FilterType.INCLUSION, the images with the file names in the `file_names` are included.
        - if FilterType.EXCLUSION, the images with the file names in the `file_names` are excluded.
    file_names : list[str]
        The list of image file names to filter.
    """

    def __init__(self, filter_type: FilterType, file_names: list[str]):
        super().__init__(filter_type, TargetType.IMAGE)
        self.file_names = file_names

    def apply(self, data: dict) -> bool:
        return data["file_name"] in self.file_names


class CategoryNameFilter(BaseFilter):
    """
    Filter class to filter data by category name.

    Attributes
    ----------
    filter_type : FilterType
        - The type of the filter.FilterType.INCLUSION or FilterType.EXCLUSION.
        - if FilterType.INCLUSION, the categories with the names in the `category_names` are included.
        - if FilterType.EXCLUSION, the categories with the names in the `category_names` are excluded.
    """

    def __init__(self, filter_type: FilterType, category_names: list[str]):
        super().__init__(filter_type, TargetType.CATEGORY)
        self.category_names = category_names

    def apply(self, data: dict) -> bool:
        return data["name"] in self.category_names


class BoxAreaFilter(BaseFilter):
    """
    Filter class to filter data by box area.

    Attributes
    ----------
    filter_type : FilterType
        - The type of the filter.FilterType.INCLUSION or FilterType.EXCLUSION.
        - if FilterType.INCLUSION, the data with the area of bbox in the range of `min_area` and `max_area` are included.
        - if FilterType.EXCLUSION, the data with the area of bbox in the range of `min_area` and `max_area` are excluded.
    min_area : int | None
        The minimum area of the box.
    max_area : int | None
        The maximum area of the box.
    """

    def __init__(
        self,
        filter_type: FilterType,
        min_area: int | None = None,
        max_area: int | None = None,
    ):
        super().__init__(filter_type, TargetType.ANNOTATION)
        self.min_area = min_area
        self.max_area = max_area

    def apply(self, data: dict) -> bool:
        if self.min_area and self.max_area:
            return self.min_area <= data["area"] <= self.max_area
        elif self.min_area:
            return self.min_area <= data["area"]
        elif self.max_area:
            return data["area"] <= self.max_area
        return True
