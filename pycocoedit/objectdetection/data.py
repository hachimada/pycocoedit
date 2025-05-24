"""
COCO dataset editing module.

This module provides functions and classes for managing and editing
COCO format datasets for object detection tasks.
"""

import copy
import json
import random
from typing import Any

from pycocoedit.objectdetection.filter import BaseFilter, Filters, TargetType


def _validate_keys(data: list[dict], required_keys: list[str], target: str) -> None:
    """
    Validate that all dictionaries in a list contain the required keys.

    Parameters
    ----------
    data : list[dict]
        List of dictionaries to validate.
    required_keys : list[str]
        List of keys that must be present in each dictionary.
    target : str
        Name of the data type being validated, used in error messages.

    Raises
    ------
    KeyError
        If any dictionary is missing required keys.
    """
    for d in data:
        missing_keys = [key for key in required_keys if key not in d]
        if missing_keys:
            raise KeyError(f"Missing keys {missing_keys} in {target} with ID: {d.get('id', 'Unknown')}")


def validate_images(images: list[dict]) -> None:
    """
    Validate image entries in a COCO dataset.

    Parameters
    ----------
    images : list[dict]
        List of image dictionaries to validate.

    Raises
    ------
    KeyError
        If any image dictionary is missing required keys "id", "file_name", "width", or "height".
    """
    required_keys = ["id", "file_name", "width", "height"]
    _validate_keys(images, required_keys, "image")


def validate_categories(categories: list[dict]) -> None:
    """
    Validate category entries in a COCO dataset.

    Parameters
    ----------
    categories : list[dict]
        List of category dictionaries to validate.

    Raises
    ------
    KeyError
        If any category dictionary is missing required keys "id", "name" or "supercategory".
    """
    required_keys = ["id", "name", "supercategory"]
    _validate_keys(categories, required_keys, "category")


def validate_annotations(annotations: list[dict]) -> None:
    """
    Validate annotation entries in a COCO dataset.

    Parameters
    ----------
    annotations : list[dict]
        List of annotation dictionaries to validate.

    Raises
    ------
    KeyError
        If any annotation dictionary is missing required keys "id",
        "image_id", "category_id", "bbox", "area" or "segmentation".
    """
    required_keys = ["id", "image_id", "category_id", "bbox", "area", "segmentation"]
    _validate_keys(annotations, required_keys, "annotation")


class CocoData:
    """
    Class for managing and manipulating COCO format datasets.

    This class provides methods to load, filter, correct and save
    COCO format datasets for object detection tasks.

    Parameters
    ----------
    annotation : str or dict[str, Any]
        Either a file path to a JSON COCO dataset file or
        a dictionary containing the dataset.

    Raises
    ------
    KeyError
        If the dataset is missing required keys or entries with required fields.
    """

    def __init__(self, annotation: str | dict[str, Any]):
        """Initialize a CocoData object from a file path or dictionary."""
        if isinstance(annotation, dict):
            dataset = copy.deepcopy(annotation)
        else:
            with open(annotation) as f:
                dataset = json.load(f)
        self.images: list[dict] = dataset["images"]
        self.annotations: list[dict] = dataset["annotations"]
        self.categories: list[dict] = dataset["categories"]
        self.licenses: list[dict] = dataset.get("licenses", [])
        self.info: dict[str, Any] = dataset.get("info", {})

        validate_images(self.images)
        validate_categories(self.categories)
        validate_annotations(self.annotations)

        self.image_filters: Filters = Filters()
        self.category_filters: Filters = Filters()
        self.annotation_filters: Filters = Filters()

        self.filter_applied = False

    def add_filter(self, filter_: BaseFilter) -> "CocoData":
        """
        Add a filter.

        Parameters
        ----------
        filter_ : BaseFilter
            The filter to add.

        Returns
        -------
        CocoData
            Self reference for method chaining.
        """
        if filter_.target_type == TargetType.IMAGE:
            self.image_filters.add(filter_)
        if filter_.target_type == TargetType.CATEGORY:
            self.category_filters.add(filter_)
        if filter_.target_type == TargetType.ANNOTATION:
            self.annotation_filters.add(filter_)

        # a new filter means filters need to be reapplied
        self.filter_applied = False
        return self

    def apply_filter(self) -> "CocoData":
        """
        Apply all added filters to the dataset.

        This method processes all filters, both inclusion and exclusion,
        across all data types (images, categories, annotations).

        Returns
        -------
        CocoData
            Self reference for method chaining.
        """
        targets: list[list[dict]] = [
            self.images,
            self.categories,
            self.annotations,
        ]
        all_filters: list[Filters] = [
            self.image_filters,
            self.category_filters,
            self.annotation_filters,
        ]

        def update(index: int, new_data: list[dict]):
            """
            Update the appropriate data list based on index.

            Parameters
            ----------
            index : int
                Index indicating which data list to update.
            new_data : list[dict]
                New data to replace the current list.
            """
            if index == 0:
                self.images = new_data
            if index == 1:
                self.categories = new_data
            if index == 2:
                self.annotations = new_data

        for i in range(len(targets)):
            filters: Filters = all_filters[i]
            include_filters: list[BaseFilter] = filters.include_filters
            exclude_filters: list[BaseFilter] = filters.exclude_filters
            if len(include_filters) != 0:
                new_dicts = []
                for d in targets[i]:
                    for include_filter in include_filters:
                        if include_filter.apply(d):
                            new_dicts.append(d)
                            break
                update(i, new_dicts)
            if len(exclude_filters) != 0:
                new_dicts = []
                for d in targets[i]:
                    should_exclude = any(ex_f.apply(d) for ex_f in exclude_filters)
                    if not should_exclude:
                        new_dicts.append(d)
                update(i, new_dicts)

        self.filter_applied = True
        return self

    def correct(self, correct_image: bool = True, correct_category: bool = False) -> "CocoData":
        """
        Ensure dataset consistency after filtering.

        This method removes annotations with category IDs not in categories,
        annotations with image IDs not in images, and optionally removes
        images with no annotations and categories with no annotations.

        Parameters
        ----------
        correct_image : bool, optional
            Whether to remove images that have no annotations, default is True.
        correct_category : bool, optional
            Whether to remove categories that have no annotations, default is False.

        Returns
        -------
        CocoData
            Self reference for method chaining.
        """
        if not self.filter_applied:
            self.apply_filter()

        # Remove annotations with category_id not in categories
        cat_ids = [cat["id"] for cat in self.categories]
        _annotations = []
        for i in range(len(self.annotations)):
            ann = self.annotations[i]
            _cat_id = ann["category_id"]
            if ann["category_id"] in cat_ids:
                _annotations.append(ann)
        self.annotations = _annotations

        # Remove annotations with no images
        img_ids = [img["id"] for img in self.images]
        _annotations = []
        for i in range(len(self.annotations)):
            ann = self.annotations[i]
            _img_id = ann["image_id"]
            if ann["image_id"] in img_ids:
                _annotations.append(ann)
        self.annotations = _annotations

        if correct_image:
            # Remove images with no annotations
            img_ids = [ann["image_id"] for ann in self.annotations]
            _images = []
            for img in self.images:
                if img["id"] in img_ids:
                    _images.append(img)
            self.images = _images

        if correct_category:
            # Remove categories with no annotations
            cat_ids = [ann["category_id"] for ann in self.annotations]
            _categories = []
            for cat in self.categories:
                if cat["id"] in cat_ids:
                    _categories.append(cat)
            self.categories = _categories

        return self

    def get_dataset(self) -> dict[str, Any]:
        """
        Get the dataset as a dictionary.

        Returns
        -------
        dict
            Dataset including info, licenses, images, categories and annotations.
        """
        return {
            "info": self.info,
            "licenses": self.licenses,
            "images": self.images,
            "categories": self.categories,
            "annotations": self.annotations,
        }

    def save(self, file_path: str, correct_image: bool = True, correct_category: bool = False) -> None:
        """
        Save the dataset to a JSON file.

        Parameters
        ----------
        file_path : str
            Path where the JSON file will be saved.
        correct_image : bool, optional
            Whether to remove images with no annotations before saving, default is True.
        correct_category : bool, optional
            Whether to remove categories with no annotations before saving, default is False.
        """
        self.correct(correct_image=correct_image, correct_category=correct_category)
        dataset = self.get_dataset()
        with open(file_path, "w") as f:
            json.dump(dataset, f)

    def sample(self, n: int, correct_image: bool = True, correct_category: bool = False) -> dict[str, Any]:
        """
        Create a random sample of the dataset with n images.

        Parameters
        ----------
        n : int
            Number of images to sample.
        correct_image : bool, optional
            Whether to remove images with no annotations, default is True.
        correct_category : bool, optional
            Whether to remove categories with no annotations, default is False.

        Returns
        -------
        dict
            A new sampled dataset as a dictionary.

        Raises
        ------
        ValueError
            If n is greater than the number of images in the dataset.
        """
        if not self.filter_applied:
            self.apply_filter()

        if n > len(self.images):
            raise ValueError(
                f"Number of images to sample is greater than the number of images in the dataset. n: {n}, number of images: {len(self.images)}"
            )

        self.images = random.sample(self.images, n)
        self.correct(correct_image, correct_category)
        return self.get_dataset()
