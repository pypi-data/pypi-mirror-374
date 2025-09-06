from __future__ import annotations

import os
import pathlib
import re
from abc import ABC, abstractmethod
from collections import Counter
from typing import Iterator, Optional

import h5py
import numpy as np
import pandas as pd
from numpy.typing import ArrayLike

from ria_toolkit_oss.datatypes.datasets.h5helpers import (
    append_entry_inplace,
    copy_file,
    copy_over_example,
    delete_example_inplace,
    duplicate_entry_inplace,
    make_empty_clone,
)


class RadioDataset(ABC):
    """A radio dataset is an iterable dataset designed for machine learning applications in radio signal
    processing and analysis. They are a structured collections of examples in a machine learning-ready format,
    with associated metadata.

    This is an abstract interface defining common properties and behavior of radio datasets. Therefore, this class
    should not be instantiated directly. Instead, it should be subclassed to define specific interfaces for different
    types of radio datasets. For example, see ria_toolkit_oss.datatypes.datasets.IQDataset, which is a radio dataset
    subclass tailored for tasks involving the processing of radio signals represented as IQ (In-phase and Quadrature)
    samples.

    :param source: Path to the dataset source file. For more information on dataset source files
        and their format, see :doc:`radio_datasets`.
    :type source: str or os.PathLike
    """

    def __init__(self, source: str | os.PathLike):
        """Create a new RadioDataset."""
        if not h5py.is_hdf5(source):
            raise ValueError(f"Dataset source must be HDF5, {source} is not.")

        # TODO: Check to see if source is RIA dataset, and let them know otherwise they should use dataset builder
        #  utilities to generate a dataset compatible with the RIA framework.

        self._source = pathlib.Path(source)
        self._index = 0

    @property
    def source(self) -> pathlib.Path:
        """
        :return: Path to the dataset source file.
        :type: pathlib.Path
        """
        return self._source

    @property
    def shape(self) -> tuple[int]:
        """
        :return: The shape of the dataset. The elements of the shape tuple give the lengths of the corresponding
            dataset dimensions.
        :type: tuple of ints
        """
        with h5py.File(self.source, "r") as f:
            return f["data"].shape

    @property
    def data(self) -> np.ndarray:
        """Retrieve the data from the source file.

        .. note::

           Accessing this property reads all the data from the source file into memory as a NumPy array, which can
           consume significant amounts of memory and potentially degrade performance. Instead, use the
           ``RadioDataset`` class methods to process and manipulate the dataset source file. You can read individual
           examples into memory as NumPy arrays by indexing the dataset: ``RadioDataset[idx]``.

        :return: The dataset examples as a single NumPy array.
        :type: np.ndarray
        """
        with h5py.File(self.source, "r") as f:
            return f["data"][:]

    @property
    def metadata(self) -> pd.DataFrame:
        """Retrieve the metadata from the source file.

        .. note::

           Accessing this property reads all the metadata from the source file into memory as a Pandas DataFrame.

        :return: The dataset metadata as a Pandas DataFrame.
        :type: pd.DataFrame
        """
        with h5py.File(self.source, "r") as f:
            return pd.DataFrame(f["metadata/metadata"][:]).map(decode_bytes)

    @property
    def labels(self) -> list[str]:
        """Retrieves the metadata labels from the dataset file.

        :return: A list of metadata column headers.
        :rtype: list of strings

        **Examples:**

        >>> awgn_builder = AWGN_Builder()
        >>> awgn_builder.download_and_prepare()
        >>> ds = awgn_builder.as_dataset(backend="pytorch")
        >>> print(ds.labels)
        ['rec_id', 'modulation', 'snr']
        """
        with h5py.File(self.source, "r") as f:
            return [name for name, _ in f["metadata/metadata"].dtype.fields.items()]

    @abstractmethod
    def inspect(self):
        """
        .. todo:: This method is not yet fully conceptualized. Likely, it will wrap some of the functionality in the
                Dataset Inspector package (dataset_manager.inspector) to produce an image or visualization. However,
                the Dataset Inspector package is not yet implemented.
        """
        # TODO: Implement in subclass based on https://github.com/qoherent/QDM/blob/main/inspection_utils/inspector.py
        #       Consider removing moving into the dataset builder.
        pass

    @abstractmethod
    def default_augmentations(self) -> list[callable]:
        """Returns a list of default augmentations.

        :return: A list of default augmentations.
        :rtype: list of callable
        """
        pass

    def augment(  # noqa: C901  # TODO: Simplify function
        self,
        class_key: str,
        augmentations: Optional[callable | list[callable]] = None,
        level: Optional[float | list[float]] = 1.0,
        target_size: Optional[int | list[int]] = None,
        classes_to_augment: Optional[str | list[str]] = None,
        inplace: Optional[bool] = False,
    ) -> RadioDataset | None:
        """Supplement the dataset with new examples by applying various transformations to the pre-existing examples
        in the dataset.

        .. todo::

           This method is currently under construction, and may produce unexpected results.

        The process of supplementing a dataset to artificially increases the diversity of the examples is called
        augmentation. In many cases, training on augmented data can enhance the generalization and robustness of
        deep machine learning models. For more information on the benefits and limitations of data
        augmentation, please refer to this tutorial by Abid Ali Awan: `A Complete Guide to Data Augmentation
        <https://www.datacamp.com/tutorial/complete-guide-data-augmentation>`_.

        The metadata for each new example will be identical to the metadata of the pre-existing example from
        which it was generated. However, the metadata will be extended to include a 'augmentation' column, which will
        be populated for each new example with the string representation of the transform used to generate it, and left
        empty for all the pre-existing examples.

        Please note that augmented data should only be utilized for model training, not for testing or validation.

        Unless specified, augmentations are applied equally across classes, maintaining the original class
        distribution.

        In the case where target_size is not equal to the sum of the original class sizes scaled by an integer
        multiple, it is not possible to maintain the original class distribution, so the distribution gets slightly
        skewed to satisfy target_size. To do this, each class size gets divided by the total size and then
        multiplied by target_size, then these values all get rounded to the nearest integers. If the target_size is
        not equal to the sum of the rounded sizes, the sizes get sorted based on their decimal portions and then
        values are adjusted one by one until the target_size is reached.

        :param class_key: Class name that is used to augment from and calculate class distribution.
        :type class_key: str

        :param augmentations: A function or a list of functions that take as input an example from the
            dataset and return a transformed version of that example. If no augmentations are specified, the default
            augmentations returned by the ``default_augmentations()`` method will be applied.
        :type augmentations: callable or list of callables, optional

        :param level: The level or extent of data augmentation to apply, ranging from 0.0 (no augmentation) to
            1.0 (full augmentation, where each augmentation is applied to each pre-existing example).
            |br| |br| If ``classes_to_augment`` is specified, this can be either:
                * A single float:
                    All classes are augmented evenly to this level, maintaining the original class distribution.
                * A list of floats:
                    Each element corresponds to the augmentation level target for the corresponding class.
            The default is 1.0.
        :type level: float or list of floats, optional

        :param target_size: Target size of the augmented dataset. If specified, ``level`` is ignored, and augmentations
            are applied to expand the dataset to contain the specified number of examples.
            If ``classes_to_augment`` is specified, this can be either:
                * A single float:
                    All classes are augmented proportional to their relative frequency until the dataset reaches the
                    target size, maintaining the original class distribution.
                * A list of floats:
                    Each element in the list corresponds to the target size for the corresponding class.
            Defaults to None.
        :type target_size: int or list of ints, optional

        :param classes_to_augment: List of the metadata keys of the classes to augment. If specified, only these
            classes will be augmented. Defaults to None.
        :type classes_to_augment: string or list of strings, optional

        :param inplace: If True, the augmentation is performed inplace and ``None`` is returned. Defaults to False.
        :type inplace: bool, optional

        :raises ValueError: If level has any values that are not in the range (0,1].
        :raises ValueError: If target_size of dataset is already sufficed.
        :raises ValueError: If a class name in classes_to_augment does not exist in the specified class_key.

        :return: The augmented dataset or None if ``inplace=True``.
        :rtype: RadioDataset or None

        **Examples:**

        >>> from ria.dataset_manager.builders import AWGN_Builder()
        >>> builder = AWGN_Builder()
        >>> builder.download_and_prepare()
        >>> ds = builder.as_dataset()
        >>> ds.get_class_sizes(class_key='col')
        {a:100, b:500, c:300}
        >>> new_ds = ds.augment(class_key='col', classes_to_augment=['a', 'b'], target_size=1200)
        >>> new_ds.get_class_sizes(class_key='col')
        {a:150 b:750, c:300}

        >>> from ria.dataset_manager.builders import AWGN_Builder()
        >>> builder = AWGN_Builder()
        >>> builder.download_and_prepare()
        >>> ds = builder.as_dataset()
        >>> ds.get_class_sizes(class_key='col')
        {a:50, b:20, c:130}
        >>> new_ds = ds.augment(class_key='col', level=0.5)
        >>> new_ds.get_class_sizes(class_key='col')
        {a:75 b:30, c:195}
        """

        if augmentations is None:
            augmentations = self.default_augmentations()

        if not isinstance(augmentations, list):
            augmentations = [augmentations]

        if isinstance(level, list):
            for i in level:
                if i <= 0 or i > 1:
                    raise ValueError("level must be in this range: (0,1]")
        else:
            if level <= 0 or level > 1:
                raise ValueError("level must be in this range: (0,1]")

        class_sizes = self.get_class_sizes(class_key=class_key)

        if isinstance(target_size, int) and target_size <= sum(class_sizes.values()):
            raise ValueError("target_size must be greater than the total sum of the current class sizes.")

        # Encode class names to byte strings and check if all class names exist in class key
        if classes_to_augment is not None:
            if isinstance(classes_to_augment, list):
                classes_to_augment = [cls_name.encode("utf-8") for cls_name in classes_to_augment]
                for i in classes_to_augment:
                    if i not in class_sizes:
                        raise ValueError(f"class name of {i} does not belong to the class key of {class_key}")
            else:
                classes_to_augment = classes_to_augment.encode("utf-8")
                if classes_to_augment not in class_sizes:
                    raise ValueError(f"class name of {i} does not belong to the class key of {class_key}")

        result_sizes = get_result_sizes(
            level=level, target_size=target_size, classes_to_augment=classes_to_augment, class_sizes=class_sizes
        )

        if "augmentations" not in self.metadata.columns:
            # Add metadata column to metadata
            raise NotImplementedError

        # Create new dataset object in not inplace
        if not inplace:
            new_source = self._get_next_file_name()
            copy_file(original_source=self.source, new_source=new_source)
            ds = self.__class__(source=new_source)
        else:
            ds = self

        # Create a dict where each pair is the class name and a list of all indices of the examples of that class
        indices_to_add = dict()
        with h5py.File(ds.source, "a") as f:
            class_labels = f["metadata/metadata"][class_key]

            for i in range(len(class_labels)):
                current_class = class_labels[i]
                if class_sizes[current_class] < result_sizes[current_class] and current_class not in indices_to_add:
                    indices_to_add[current_class] = []

                if class_sizes[current_class] < result_sizes[current_class] and current_class in indices_to_add:
                    indices_to_add[current_class].append(i)

        for key in class_sizes:
            if class_sizes[key] < result_sizes[key]:
                # Generate a sublist which holds the indices of examples to be augmented
                rand_idxs = np.random.choice(indices_to_add[key], result_sizes[key] - class_sizes[key], replace=True)

                aug_idx = 0

                with h5py.File(ds.source, "a") as f:
                    data = f["data"]
                    metadata = f["metadata/metadata"]
                    for idx in rand_idxs:
                        rand_example = data[idx]
                        augmented_example = augmentations[aug_idx](rand_example)

                        # Update corresponding metadata entry to contain the augmentation that was applied
                        original_metadata_entry = metadata[idx]
                        augmented_metadata_entry = original_metadata_entry.copy()
                        augmented_metadata_entry["augmentations"] = augmentations[aug_idx].__name__

                        # Update augmentation index after adding name of augmentation to metadata column
                        if aug_idx < len(augmentations) - 1:
                            aug_idx += 1
                        else:
                            aug_idx = 0

                        append_entry_inplace(source=ds.source, dataset_path="data", entry=augmented_example)
                        append_entry_inplace(
                            source=ds.source, dataset_path="metadata/metadata", entry=augmented_metadata_entry
                        )

        if not inplace:
            return ds

    def subsample(self, class_key: str, percentage: float, inplace: Optional[bool] = False) -> RadioDataset | None:
        """Reduces the number of examples in all classes of a dataset by randomly subsampling each class according
        to a specified percentage. This function reduces the number of examples per class to the specified
        percentage without affecting the overall class distribution.

        :param class_key: The name of the class to subsample.
        :type class_key: str
        :param percentage: The percentage of the original class sizes to keep.
        :type percentage: float
        :param inplace: If True, the operation modifies the existing source file directly and returns None.
            If False, the operation creates a new dataset object and corresponding source file, leaving the original
            dataset unchanged. Default is False.
        :type inplace: bool, optional

        :raises ValueError: If the target size of the class with the lowest frequency goes to 0.

        :return: The subsampled dataset.
        :rtype: RadioDataset or None

        **Examples:**

        >>> from ria.dataset_manager.builders import AWGN_Builder()
        >>> builder = AWGN_Builder()
        >>> builder.download_and_prepare()
        >>> ds = builder.as_dataset()
        >>> ds.get_class_sizes(class_key="col")
        {a:100, b:200, c:300}
        >>> new_ds = ds.subsample(percentage=0.80, class_key="col")
        >>> new_ds.get_class_sizes(class_key="col")
        {a:80, b:160, c:240}
        """
        class_sizes = self.get_class_sizes(class_key=class_key)

        channels, example_length = np.shape(self[0])
        target_sizes = dict()
        for key in class_sizes:
            target_sizes[key] = target_sizes.get(key, int(class_sizes[key] * percentage))

        if min(target_sizes.values()) <= 0:
            raise ValueError("Subsampling can not be performed on dataset because class size will equal 0")

        if not inplace:
            ds = self._create_next_dataset(example_length=example_length)

        masks = dict()
        for key in class_sizes:
            masks[key] = masks.get(
                key, np.array([1] * target_sizes[key] + [0] * (class_sizes[key] - target_sizes[key]))
            )
            np.random.shuffle(masks[key])

        counters = dict()
        for key in class_sizes:
            counters[key] = counters.get(key, 0)

        idx = 0
        with h5py.File(self.source, "a") as f:
            while idx < len(self):
                labels = f["metadata/metadata"][class_key]
                current_class = labels[idx]
                current_mask = masks[current_class]
                current_mask_value = current_mask[counters[current_class]]

                counters[current_class] += 1

                if not inplace and current_mask_value == 1:
                    copy_over_example(self.source, ds.source, idx)

                elif inplace and current_mask_value == 0:
                    delete_example_inplace(self.source, idx)
                    continue

                idx += 1

        if not inplace:
            return ds

    def resample(self, quantity_target: int, class_key: str, inplace: Optional[bool] = False) -> RadioDataset | None:
        """Adjusts an unsampled dataset by changing the number of examples per class to a user-specified quantity.

            For each class:
             - If there are excess examples, it randomly subsamples the class to the quantity target.
             - If there are less examples, it randomly duplicates examples to reach the quantity target.

        :param quantity_target: The number of examples each class should have.
        :type quantity_target: int
        :param class_key: The label of the class to resample.
        :type class_key: str
        :param inplace: If True, the operation modifies the existing source file directly and returns None.
            If False, the operation creates a new dataset object and corresponding source file, leaving the original
            dataset unchanged. Default is False.
        :type inplace: bool, optional

        :return: The resampled dataset.
        :rtype: RadioDataset or None

        **Examples:**

        >>> from ria.dataset_manager.builders import AWGN_Builder()
        >>> builder = AWGN_Builder()
        >>> builder.download_and_prepare()
        >>> ds = builder.as_dataset()
        >>> ds.get_class_sizes(class_key="col")
        {a:100, b:200, c:300}
        >>> new_ds = ds.resample(quantity_target=250, class_key="col")
        >>> new_ds.get_class_sizes(class_key="col")
        {a:250, b:250, c:250}
        """

        if not inplace:
            ds = self.homogenize(class_key=class_key, example_limit=quantity_target)
        else:
            self.homogenize(class_key=class_key, example_limit=quantity_target, inplace=True)
            ds = self

        class_sizes = ds.get_class_sizes(class_key=class_key)

        indices_to_add = dict()
        with h5py.File(ds.source, "a") as f:
            labels = f["metadata/metadata"][class_key]

            for i in range(len(labels)):
                current_class = labels[i]
                if class_sizes[current_class] < quantity_target and current_class not in indices_to_add:
                    indices_to_add[current_class] = []

                if class_sizes[current_class] < quantity_target and current_class in indices_to_add:
                    indices_to_add[current_class].append(i)

        for key in indices_to_add.keys():
            rand_idxs = np.random.choice(indices_to_add[key], quantity_target - class_sizes[key], replace=True)
            for idx in rand_idxs:
                duplicate_entry_inplace(ds.source, "data", idx)
                duplicate_entry_inplace(ds.source, "metadata/metadata", idx)

        if not inplace:
            return ds

    def homogenize(
        self, class_key: str, example_limit: Optional[int] = None, inplace: Optional[bool] = False
    ) -> RadioDataset | None:
        """Discards excess samples by randomly subsampling all classes within a dataset that have more than a
            user-specified limit of examples. If the user doesn't specify a limit, the class the with the
            fewest examples is selected as the limit.

        :param class_key: The label of the class to homogenize.
        :type class_key: str
        :param example_limit: The class size limit to which all classes are subsampled. If not specified,
            the class with the fewest examples is used as the limit. Default is None.
        :type example_limit: int, optional
        :param inplace: If True, the operation modifies the existing source file directly and returns None.
            If False, the operation creates a new dataset cbject and corresponding source file, leaving the original
            dataset unchanged. Default is False.
        :type inplace: bool, optional

        :return: The homogenized dataset.
        :rtype: RadioDataset or None

        **Examples:**

        >>> from ria.dataset_manager.builders import AWGN_Builder()
        >>> builder = AWGN_Builder()
        >>> builder.download_and_prepare()
        >>> ds = builder.as_dataset()
        >>> ds.get_class_sizes(class_key="col")
        {a:1000, b:5000, c:1500, d:900}
        >>> new_ds = ds.homogenize(example_limit=1000, class_key="col")
        >>> new_ds.get_class_sizes(class_key="col")
        {a:1000, b:1000, c:1000, d:900}

        >>> from ria.dataset_manager.builders import AWGN_Builder()
        >>> builder = AWGN_Builder()
        >>> builder.download_and_prepare()
        >>> ds = builder.as_dataset()
        >>> ds.get_class_sizes(class_key="col")
        {a:1000, b:5000, c:1500, d:900}
        >>> new_ds = ds.homogenize(class_key="col")
        >>> new_ds.get_class_sizes(class_key="col")
        {a:900, b:900, c:900, d:900}
        """

        class_sizes = self.get_class_sizes(class_key=class_key)

        if example_limit is None:
            example_limit = min(class_sizes.values())

        channels, example_length = np.shape(self[0])

        if not inplace:
            ds = self._create_next_dataset(example_length=example_length)

        masks, counters = get_masks_and_counters(class_sizes, example_limit)

        idx = 0

        with h5py.File(self.source, "a") as f:
            while idx < len(self):
                labels = f["metadata/metadata"][class_key]
                current_class = labels[idx]
                current_mask = masks[current_class]
                if current_mask is None and not inplace:
                    copy_over_example(self.source, ds.source, idx)

                if current_mask is not None:
                    current_mask_value = current_mask[counters[current_class]]
                    counters[current_class] += 1

                    if not inplace and current_mask_value == 1:
                        copy_over_example(self.source, ds.source, idx)

                    elif inplace and current_mask_value == 0:
                        delete_example_inplace(self.source, idx)
                        continue

                idx += 1

        if not inplace:
            return ds

    def drop_class(self, class_key: str, class_value: str, inplace: Optional[bool] = False) -> RadioDataset | None:
        """Removes an entire class from the dataset.

        :param class_key: Class that will have a value dropped from it. Example: 'signal_type'
        :type class_key: str
        :param class_value: Value of the class to be dropped. Example: 'LTE', 'NR'
        :type class_value: str
        :param inplace: If True, the operation modifies the existing source file directly and returns None.
            If False, the operation creates a new dataset cbject and corresponding source file, leaving the original
            dataset unchanged. Defaults to False.
        :type inplace: bool, optional

        :raises ValueError: If the entered class name does not exist in the dataset.

        :return: The dataset without the removed class.
        :rtype: RadioDataset or None

        **Examples:**

        >>> from ria.dataset_manager.builders import AWGN_Builder()
        >>> builder = AWGN_Builder()
        >>> builder.download_and_prepare()
        >>> ds = builder.as_dataset()
        >>> ds.get_class_sizes()
        {a:100, b:500, c:300}
        >>> new_ds = ds.drop_class('a')
        >>> new_ds.get_class_sizes()
        {b:500, c:300}
        """
        class_sizes = self.get_class_sizes(class_key=class_key)

        if class_value.encode("utf-8") not in class_sizes.keys():
            raise ValueError(f"{class_value} is not a class of this dataset.")

        channels, example_length = np.shape(self[0])

        if not inplace:
            ds = self._create_next_dataset(example_length=example_length)

        idx = 0
        with h5py.File(self.source, "a") as f:
            while idx < len(self):
                labels = f["metadata/metadata"][class_key]
                current_label = labels[idx].decode("utf-8")
                if current_label == class_value and inplace:
                    delete_example_inplace(self.source, idx)
                    continue

                elif current_label != class_value and not inplace:
                    copy_over_example(self.source, ds.source, idx)

                idx += 1

        if not inplace:
            return ds

    def add_label(self, column_name: str, data: ArrayLike, inplace: Optional[bool] = False) -> RadioDataset | None:
        """Add a new metadata label to the dataset.

        .. todo:: This method is not yet implemented.

        :param column_name: Name of the new metadata column header.
        :type inplace: str
        :param data: The contents of the new metadata column.
        :type inplace: np.typing.ArrayLike
        :param inplace: If True, the label is added inplace and ``None`` is returned. Defaults to False.
        :type inplace: bool, optional

        :raises ValueError: If the length of ``data`` is not equal to the length of the dataset.

        :return: The augmented dataset or None if ``inplace=True``.
        :rtype: RadioDataset or None

        **Examples:**

        .. todo:: Usage examples coming soon.
        """
        raise NotImplementedError

    def get_class_sizes(self, class_key: str) -> dict[str, int]:
        """Returns a dictionary containing the sizes of each class in the dataset at the provided key.

        :param class_key: The class label.
        :type class_key: str

        :raises ValueError: If the specified key is not found in the dataset labels.

        :return: A dictionary where each key is a distinct class label, and it's value is the class size.
        :rtype: A dictionary where the keys are strings and the values are integers

        **Examples:**

        >>> from ria.dataset_manager.builders import AWGN_Builder()
        >>> spectrogram_sensing_builder = AWGN_Builder()
        >>> spectrogram_sensing_builder.download_and_prepare()
        >>> ds = spectrogram_sensing_builder.as_dataset(backend="pytorch")
        >>> ds.get_class_sizes(class_key='signal_type')
        {'LTE': 900, 'NR': 900, 'LTE_NR': 900}
        """
        with h5py.File(self.source, "r") as f:
            labels = f["metadata/metadata"][class_key]
            return dict(Counter(labels))

    def delete_example(self, idx: int, inplace: Optional[bool] = False) -> RadioDataset | None:
        """Deletes an example and it's corresponding metadata from the dataset.

        :param idx: The index of the example to be deleted.
        :type idx: int

        :param inplace: If True, the deletion is performed inplace and ``None`` is returned. Defaults to False.
        :type inplace: bool, optional

        :return: The new dataset or None if ``inplace=True``.
        :rtype: RadioDataset or None

        **Examples:**

        >>> from ria.dataset_manager.builders import AWGN_Builder()
        >>> spectrogram_sensing_builder = AWGN_Builder()
        >>> spectrogram_sensing_builder.download_and_prepare()
        >>> ds = spectrogram_sensing_builder.as_dataset(backend="pytorch")
        >>> len(ds)
        2700
        >>> ds = ds.delete_example(idx=34)
        >>> len(ds)
        2699
        """

        if inplace:
            delete_example_inplace(source=self.source, idx=idx)
            return None

        else:
            # The deletion is performed by 1. creating a new source file, 2. copying all contents to the new source
            # file, and 3. deleting the example at idx inplace.
            new_source = self._get_next_file_name()
            copy_file(original_source=self.source, new_source=new_source)
            delete_example_inplace(source=new_source, idx=idx)
            return self.__class__(source=new_source)

    def append(self, example: ArrayLike, metadata: dict) -> None:
        """Append a single example to the end of the dataset. This operation is performed inplace.

        .. todo:: This method is not yet implemented.

        :param example: The example to append.
        :type example: np.typing.ArrayLike
        :param metadata: The corresponding metadata dictionary.
        :type metadata: dict

        :raises ValueError: If example does not the same shape and type as rest of the examples in the dataset.

        :return: None.

        **Examples:**

        .. todo:: Usage examples coming soon.
        """
        raise NotImplementedError

    def join(self, ds: RadioDataset) -> RadioDataset:
        """Join or merge together two radio datasets.

        .. todo:: This method is not yet implemented.

        - Duplicate entries are not removed; they are included.
        - The examples are not shuffled; examples from ``ds`` are appended at the end.
        - Metadata will be expanded to contain all columns.

        :param ds: The dataset to merge together with self. Examples from both datasets must have the same shape.
        :type ds: bool

        :return: The combined dataset.
        :rtype: RadioDataset

        **Examples:**

        .. todo:: Usage examples coming soon.
        """
        raise NotImplementedError

    def filter(self, mask: ArrayLike, inplace: Optional[bool] = False) -> RadioDataset:
        """Filter the dataset using the provided mask.

        .. todo:: This method is not yet implemented.

        :param mask: A boolean mask. Where True, keep the corresponding examples. Where False, discard keep the
            corresponding examples. The filtering mask is often the result of applying a condition across the elements
            of the dataset.
        :type mask: array_like

        :param inplace: If True, the filter operation is performed inplace and ``None`` is returned. Defaults to False.
        :type inplace: bool, optional

        :return: The filtered dataset or None if ``inplace=True``.
        :rtype: RadioDataset or None

        Examples:

        .. todo:: Usage examples coming soon!

        """
        raise NotImplementedError

    def _get_next_file_name(self) -> str:
        """As we manipulate a dataset, we create new source files. That is, unless inplace==True. Each new source
        file needs a new name, and so we count up. This function computes and returns the next file name.

        If the file has not been manipulated before, it will add `.001` to the end of the file name before the
        extension. If there is already a number at the end of the file name, it will update the current number to the
        next consecutive number.

        For example:

        >>> from ria.dataset_manager.builders import AWGN_Builder()
        >>> builder = AWGN_Builder()
        >>> builder.download_and_prepare()
        >>> ds = builder.as_dataset()  # my_dataset.hdf5
        >>> ds = ds.subsample()  # my_dataset.001.hdf5
        >>> ds = ds.augment()  # my_dataset.002.hdf5

        :raises ValueError: If the number at the end of the file name exceeds 999.

        :return: The name of the next file, including the file extension
        :rtype: str
        """

        name, ext = os.path.splitext(str(self.source))
        end_of_name = name[-3:]

        if re.match(r"^\d+$", end_of_name):
            operation_number = int(end_of_name)
            operation_number += 1

            if operation_number < 10:
                operation_number_as_string = f"00{operation_number}"  # 1 digits

            elif operation_number < 100:
                operation_number_as_string = f"0{operation_number}"  # 2 digits

            elif operation_number < 1000:
                operation_number_as_string = f"{operation_number}"  # 3 digits

            else:
                # We assume the maximum number of dataset manipulations will not exceed 999.
                raise ValueError("The maximum allowed number of dataset manipulations is 999.")

            return f"{name[:-3]}{operation_number_as_string}{ext}"

        else:
            return f"{name}.001{ext}"

    def _create_next_dataset(self, example_length: int) -> RadioDataset:
        """Creates a new empty dataset with a new source file, but with the same file structure as self.source.

        :param example_length: The length of the examples in the new dataset.
        :type example_length: int

        :return: A new dataset with empty data and labels.
        :rtype: RadioDataset
        """
        new_source = self._get_next_file_name()
        make_empty_clone(self.source, new_source, example_length=example_length)
        return self.__class__(source=new_source)

    def __iter__(self) -> Iterator:
        self._index = 0
        return self

    def __next__(self) -> np.ndarray:
        if self._index < len(self):
            with h5py.File(self.source, "r") as f:
                dataset = f["data"]
                result = dataset[self._index]
                self._index += 1
                return result
        else:
            raise StopIteration

    def __eq__(self, other: RadioDataset) -> bool:
        """Two RadioDatasets are equal iff they share the same source file."""
        return self._source == other._source

    def __len__(self) -> int:
        """
        :return: The number of examples in a dataset.
        :rtype: int
        """
        return self.shape[0]

    def __getitem__(self, key: int | slice | ArrayLike) -> np.ndarray | RadioDataset:
        """If key is an integer read in and return the example at key.

        If key is a slice, a new dataset instance is returned, initialized with the data and metadata corresponding
         to that slice. However, if key is `[:]`, the data is read and returned as a NumPy array.

        If key is array_like, it is interpreted as a boolean mask and used to filter the dataset. In this case, we
         return a new instance of the dataset, initialized from a new source file with the filtered data/metadata.
        """
        if isinstance(key, int):
            with h5py.File(self.source, "r") as file:
                return file["data"][key]

        elif isinstance(key, slice):
            if key == slice(None):
                return self.data
            else:
                # Create and return a new dataset, initialized from a new source file, with the data/metadata at slice.
                raise NotImplementedError("Dataset slicing not yet implemented.")

        else:
            try:
                key = np.asarray(key)
                if key.dtype == bool:
                    return self.filter(mask=key)
                else:
                    raise ValueError("Array-like mask must be of boolean type.")

            except (TypeError, ValueError):
                raise ValueError(f"Indexing with key of type {key} is not supported.")

    def __setitem__(self, *args, **kwargs) -> None:
        """Raise an error if an attempt is made to assign to the dataset."""
        raise ValueError("Assignment to dataset is not allowed.")


def decode_bytes(cell: any) -> any:
    """If cell is of type bytes, returns the decoded UTF-8 string. Otherwise, returns the input value unchanged."""
    if isinstance(cell, bytes):
        return cell.decode("utf-8")

    return cell


def get_result_sizes(  # noqa: C901  # TODO: Simplify function
    level: float | list[float],
    target_size: int | list[int] | None,
    classes_to_augment: str | list[str] | None,
    class_sizes: dict,
) -> dict:
    """Returns the desired sizes of each class in the metadata. This is a helper function specifically
    used by the augment method.

    :param level: The level or extent of data augmentation to apply, ranging from 0.0 (no augmentation) to
        1.0 (full augmentation, where each augmentation is applied to each pre-existing example).
    :type level: float or list of floats

    :param target_size: Target size of the augmented dataset. If specified, ``level`` is ignored, and augmentations
        are applied to expand the dataset to contain the specified number of examples.
    :type target_size: int or list of ints or None

    :param classes_to_augment: List of the classes to augment.
    :type classes_to_augment: string or list of strings or None

    :param class_sizes: A dictionary where each key-value pair is the class label and the class size.
    :type class_sizes: dict

    :raises ValueError: If level is a list when classes_to_augment is None.
    :raises ValueError: If classes_to_augment and level are lists, but they have different sizes.
    :raises ValueError: If target_size is a list when classes_to_augment is None.
    :raises ValueError: If classes_to_augment and target_size are lists, but they have different sizes.
    :raises ValueError: If classes_to_augment and target_size are lists, but the target_size of a class is already met.

    :return: A dictionary where each key is a distinct class label, and it's value is the desired class size.
    :rtype: A dictionary where the keys are strings and the values are integers
    """
    result_sizes = dict(class_sizes)

    if target_size is None:
        # Calculate off of level
        if classes_to_augment is None:
            # Apply to entire dataset, if classes_to_augment is None
            if isinstance(level, list):
                raise ValueError("Since classes_to_augment is None, level must be a single float value.")

            for key in result_sizes:
                result_sizes[key] = round(result_sizes[key] + class_sizes[key] * level)
        else:
            if not isinstance(classes_to_augment, list):
                classes_to_augment = [classes_to_augment]

            if isinstance(level, list):
                if len(level) != len(classes_to_augment):
                    raise ValueError("If level is a list, there must be one value for each class you wish to augment.")

                for index, class_name in enumerate(classes_to_augment):
                    result_sizes[class_name] = round(result_sizes[class_name] + class_sizes[class_name] * level[index])

            else:
                for class_name in classes_to_augment:
                    result_sizes[class_name] = round(result_sizes[class_name] + class_sizes[class_name] * level)
    else:
        # Calculate off of target_size
        if classes_to_augment is None:
            # apply to entire dataset, if classes_to_augment is None
            if isinstance(target_size, list):
                raise ValueError("Since classes_to_augment is None, target_size must be a single int value.")

            result_sizes = calculate_size_with_original_distribution(
                class_sizes=class_sizes, target_size=target_size, classes_to_augment=classes_to_augment
            )

        else:
            # user specified classes to augment

            # if user provides only 1 class convert it to a list
            if not isinstance(classes_to_augment, list):
                classes_to_augment = [classes_to_augment]

            if isinstance(target_size, list):
                if len(target_size) != len(classes_to_augment):
                    raise ValueError(
                        "If target_size is a list, there must be one value for each class you wish to augment."
                    )

                # Check that each class that will be augmented does not already suffice target_size
                for cls_name, target_size_value in zip(classes_to_augment, target_size):
                    if class_sizes[cls_name] >= target_size_value:
                        raise ValueError(
                            f"""target_size of {target_size_value} is already sufficed for current size of
                            {class_sizes[cls_name]} for class: {cls_name}"""
                        )

                for index, class_name in enumerate(classes_to_augment):
                    result_sizes[class_name] = target_size[index]
            else:
                result_sizes = calculate_size_with_original_distribution(
                    class_sizes=class_sizes, target_size=target_size, classes_to_augment=classes_to_augment
                )

    return result_sizes


def calculate_size_with_original_distribution(  # noqa: C901  # TODO: Simplify function
    class_sizes: dict, target_size: int, classes_to_augment: list[str] | None
) -> dict:
    """Returns the desired sizes of each class when target_size is used to calculate the resultant class sizes.
        Specifically used as a helper by the get result sizes method.

    :param class_sizes: A dictionary where each key-value pair is the class label and the class size.
    :type class_sizes: dict

    :param target_size: Target size of the augmented dataset.
    :type target_size: int

    :param classes_to_augment: List of the classes to augment.
    :type classes_to_augment: list of strings or None

    :return: A dictionary where each key is a distinct class label, and it's value is the desired class size.
    :rtype: dict
    """

    total_size = sum(class_sizes.values())

    if classes_to_augment is None:
        scaled_sizes = {cls: (size / total_size) * target_size for cls, size in class_sizes.items()}
        rounded_sizes = {cls: round(size) for cls, size in scaled_sizes.items()}
        difference = target_size - sum(rounded_sizes.values())

    else:
        partial_class_size_total = sum(size for cls, size in class_sizes.items() if cls in classes_to_augment)
        partial_target_size = target_size - sum(
            size for cls, size in class_sizes.items() if cls not in classes_to_augment
        )
        scaled_sizes = {
            cls: (size / partial_class_size_total) * partial_target_size
            for cls, size in class_sizes.items()
            if cls in classes_to_augment
        }
        rounded_sizes = {cls: round(size) for cls, size in scaled_sizes.items()}
        difference = partial_target_size - sum(rounded_sizes.values())

    if difference != 0:
        decimals = {cls: scaled_sizes[cls] % 1 for cls in scaled_sizes}

        if difference > 0:
            sorted_classes = sorted(rounded_sizes, key=decimals.get, reverse=True)
            for cls in sorted_classes:
                rounded_sizes[cls] += 1
                difference -= 1

                if difference == 0:
                    break
        else:
            sorted_classes = sorted(rounded_sizes, key=decimals.get)
            for cls in sorted_classes:
                rounded_sizes[cls] -= 1
                difference += 1

                if difference == 0:
                    break

    # Put back classes that were not chosen to be augmented back into resultant size dictionary
    if classes_to_augment is not None:
        for cls, count in class_sizes.items():
            if cls not in rounded_sizes:
                rounded_sizes[cls] = count

    return rounded_sizes


def get_masks_and_counters(class_sizes: dict, example_limit: int) -> tuple:
    """
    Returns the masks and counters based on the class sizes and example limit of a dataset.
        Specifically used for the homogenize method.

    :param class_sizes: Dictionary containing the sizes of each class in the dataset.
    :type class_sizes: dict
    :param example_limit: The class size limit to which all classes are subsampled. If not specified,
        the class with the fewest examples is used as the limit.
    :type example_limit: int

    :return: The mask and counter dictionaries.
    :rtype: tuple

    """
    masks, counters = dict(), dict()

    for key in class_sizes:
        if class_sizes[key] <= example_limit:
            masks[key] = None

        else:
            masks[key] = np.array([1] * example_limit + [0] * (class_sizes[key] - example_limit))
            np.random.shuffle(masks[key])
            counters[key] = 0

    return masks, counters
