from __future__ import annotations

import os
from abc import ABC
from typing import Optional

import h5py
import numpy as np

from ria_toolkit_oss.datatypes.datasets.h5helpers import (
    append_entry_inplace,
    copy_dataset_entry_by_index,
)
from ria_toolkit_oss.datatypes.datasets.radio_dataset import RadioDataset


class IQDataset(RadioDataset, ABC):
    """An ``IQDataset`` is a ``RadioDataset`` tailored for machine learning tasks that involve processing
    radiofrequency (RF) signals represented as In-phase (I) and Quadrature (Q) samples.

    For machine learning tasks that involve processing spectrograms, please use
    ria_toolkit_oss.datatypes.datasets.SpectDataset instead.

    This is an abstract interface defining common properties and behaviour of IQDatasets. Therefore, this class
    should not be instantiated directly. Instead, it is subclassed to define custom interfaces for specific machine
    learning backends.

    :param source: Path to the dataset source file. For more information on dataset source files
        and their format, see :doc:`radio_datasets`.
    :type source: str or os.PathLike
    """

    def __init__(self, source: str | os.PathLike):
        """Create a new IQDataset."""
        super().__init__(source=source)

    @property
    def shape(self) -> tuple[int]:
        """IQ datasets are M x C x N, where M is the number of examples, C is the number of channels, N is the length
         of the signals.

        :return: The shape of the dataset. The elements of the shape tuple give the lengths of the corresponding
            dataset dimensions.
        :type: tuple of ints
        """
        return super().shape

    def trim_examples(
        self, trim_length: int, keep: Optional[str] = "start", inplace: Optional[bool] = False
    ) -> IQDataset | None:
        """Trims all examples in a dataset to a desired length.

        :param trim_length: The desired length of the trimmed examples.
        :type trim_length: int
        :param keep: Specifies the part of the example to keep. Defaults to "start".
            The options are:
            - "start"
            - "end"
            - "middle"
            - "random"
        :type keep: str, optional
        :param inplace: If True, the operation modifies the existing source file directly and returns None.
            If False, the operation creates a new dataset cbject and corresponding source file, leaving the original
            dataset unchanged. Default is False.
        :type inplace: bool

        :raises ValueError: If trim_length is greater than or equal to the length of the examples.
        :raises ValueError: If value of keep is not recognized.
        :raises ValueError: If specified trim length is invalid for middle index.

        :return: The dataset that is composed of shorter examples.
        :rtype: IQDataset

         **Examples:**

        >>> from ria.dataset_manager.builders import AWGN_Builder()
        >>> builder = AWGN_Builder()
        >>> builder.download_and_prepare()
        >>> ds = builder.as_dataset()
        >>> ds.shape
        (5, 1, 3)
        >>> new_ds = ds.trim_examples(2)
        >>> new_ds.shape
        (5, 1, 2)
        """

        keep = keep.lower()

        channels, example_length = np.shape(self[0])

        if trim_length >= example_length:
            raise ValueError(f"Trim length must be less than {example_length}")

        if keep not in {"start", "end", "middle", "random"}:
            raise ValueError('keep must be "start", "end", "middle", or "random"')

        start = None
        if keep == "middle":
            start = int(example_length / 2)
            if start + trim_length > example_length:
                raise ValueError(f"Trim length of {trim_length} is invalid for middle index of: {start} ")

        elif keep == "random":
            start = np.random.randint(0, example_length - trim_length + 1)

        if not inplace:
            ds = self._create_next_dataset(example_length=trim_length)

        with h5py.File(self.source, "a") as f:
            data = f["data"]
            for idx in range(len(self)):

                trimmed_example = generate_trimmed_example(
                    example=data[idx],
                    keep=keep,
                    trim_length=trim_length,
                    start=start,
                )

                if not inplace:
                    append_entry_inplace(source=ds.source, dataset_path="data", entry=trimmed_example)
                    copy_dataset_entry_by_index(
                        source=self.source, destination=ds.source, dataset_path="metadata/metadata", idx=idx
                    )

                else:
                    trimmed_example = np.pad(
                        trimmed_example, ((0, 0), (0, example_length - trim_length)), "constant", constant_values=0
                    )
                    data[idx] = trimmed_example

            if not inplace:
                return ds
            else:
                data.resize(trim_length, axis=2)

    def split_examples(
        self, split_factor: Optional[int] = None, example_length: Optional[int] = None, inplace: Optional[bool] = False
    ) -> IQDataset | None:
        """If the current example length is not evenly divisible by the provided example_length, excess samples are
        discarded. Excess examples are always at the end of the slice. If the split factor results in non-integer
        example lengths for the new example chunks, it rounds down.

            For example:


            Requires either split_factor or example_length to be specified but not both. If both are provided,
            split factor will be used by default, and a warning will be raised.

        :param split_factor: the number of new example chunks produced from each original example, defaults to None.
        :type split_factor: int, optional
        :param example_length: the example length of the new example chunks, defaults to None.
        :type example_length: int, optional
        :param inplace: If True, the operation modifies the existing source file directly and returns None.
            If False, the operation creates a new dataset cbject and corresponding source file, leaving the original
            dataset unchanged. Default is False.
        :type inplace: bool, optional

        :return: A dataset with more examples that are shorter.
        :rtype: IQDataset

        **Examples:**

        If the dataset has 100 examples of length 1024 and the split factor is 2, the resulting dataset
        will have 200 examples of 512. No samples have been discarded.

        If the example dataset has 100 examples of length 1024 and the example length is 100, the resulting dataset
        will have 1000 examples of length 100. The remaining 24 samples from each example have been discarded.
        """

        if split_factor is not None and example_length is not None:
            # Raise warning and use split factor
            raise Warning("split_factor and example_length should not both be specified.")

        if not inplace:
            # ds = self.create_new_dataset(example_length=example_length)
            pass

        raise NotImplementedError


def generate_trimmed_example(
    example: np.ndarray, keep: str, trim_length: int, start: Optional[int] = None
) -> np.ndarray:
    """Takes in an IQ example as input and returns a trimmed example.

    :param example: The example to be trimmed.
    :type example: np.ndarray
    :param keep: The position the trimming occurs from.
    :type keep: str
    :param trim_length: The desired length of the trimmed example:
    :type trim_length: int
    :param start: The starting index if keep = "middle" or "random"
    :type start: int, optional

    :return: The trimmed example
    :rtype: np.ndarray
    """

    if keep == "start":
        return example[:, :trim_length]

    elif keep == "end":
        return example[:, -trim_length:]

    elif keep == "middle":
        return example[:, start : start + trim_length]

    else:
        return example[:, start : start + trim_length]
