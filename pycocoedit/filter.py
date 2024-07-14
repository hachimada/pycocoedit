from abc import ABC, abstractmethod
from enum import Enum


class FilterType(Enum):
    INCLUSION = 1
    EXCLUSION = 2


class BaseFilter(ABC):
    def __init__(self):
        self.filter_type: FilterType | None = None

    @abstractmethod
    def apply(self, data: dict) -> bool:
        raise NotImplementedError


class BaseInclusionFilter(BaseFilter, ABC):
    def __init__(self):
        super().__init__()
        self.filter_type: FilterType = FilterType.INCLUSION


class BaseExclusionFilter(BaseFilter, ABC):
    def __init__(self):
        super().__init__()
        self.filter_type: FilterType = FilterType.EXCLUSION


class Filters:

    def __init__(self):
        self.include_filters: list[BaseInclusionFilter] = []
        self.exclude_filters: list[BaseExclusionFilter] = []

    def add(self, filter: BaseFilter):
        if filter.filter_type == FilterType.INCLUSION and isinstance(
            filter, BaseInclusionFilter
        ):
            self.include_filters.append(filter)
        if filter.filter_type == FilterType.EXCLUSION and isinstance(
            filter, BaseExclusionFilter
        ):
            self.exclude_filters.append(filter)


class ImageNameIncludeFilter(BaseInclusionFilter):
    def __init__(self, file_names: list[str]):
        super().__init__()
        self.file_names = file_names

    def apply(self, data: dict) -> bool:
        return data["file_name"] in self.file_names


class ImageNameExcludeFilter(BaseExclusionFilter):
    def __init__(self, file_names: list[str]):
        super().__init__()
        self.file_names = file_names

    def apply(self, data: dict) -> bool:
        return data["file_name"] in self.file_names


class CategoryIncludeFilter(BaseInclusionFilter):
    def __init__(self, category_names: list[str]):
        super().__init__()
        self.category_names = category_names

    def apply(self, data: dict) -> bool:
        return data["name"] in self.category_names


class CategoryExcludeFilter(BaseExclusionFilter):
    def __init__(self, category_names: list[str]):
        super().__init__()
        self.category_names = category_names

    def apply(self, data: dict) -> bool:
        return data["name"] in self.category_names


class BoxAreaIncludeFilter(BaseInclusionFilter):
    def __init__(self, min_area: int | None = None, max_area: int | None = None):
        super().__init__()
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
