from __future__ import annotations

import os
from abc import ABC

from ria_toolkit_oss.datatypes.datasets.radio_dataset import RadioDataset


class SpectDataset(RadioDataset, ABC):
    """A ``SpectDataset`` is a ``RadioDataset`` tailored for machine learning tasks that involve processing
    radiofrequency (RF) signals represented as spectrograms. This class is integrated with vision frameworks,
    allowing you to leverage models and techniques from the field of computer vision for analyzing and processing
    radio signal spectrograms.

    For machine learning tasks that involve processing on IQ samples, please use
    ria_toolkit_oss.datatypes.datasets.IQDataset instead.

    This is an abstract interface defining common properties and behaviour of IQDatasets. Therefore, this class
    should not be instantiated directly. Instead, it is subclassed to define custom interfaces for specific machine
    learning backends.

    :param source: Path to the dataset source file. For more information on dataset source files
        and their format, see :doc:`radio_datasets`.
    :type source: str or os.PathLike
    """

    def __init__(self, source: str | os.PathLike):
        """Create a new SpectDataset."""
        super().__init__(source=source)

    @property
    def shape(self) -> tuple[int]:
        """Spectrogram datasets are M x C x H x W, where M is the number of examples, C is the number of image
        channels, H is the height of the spectrogram, and W is the width of the spectrogram.

        :return: The shape of the dataset. The elements of the shape tuple give the lengths of the corresponding
            dataset dimensions.
        :type: tuple of ints
        """
        return super().shape

    def default_augmentations(self) -> list[callable]:
        """Returns the list of default augmentations for spectrogram datasets.

        .. todo:: This method is not yet implemented.

        :return: A list of default augmentations.
        :rtype: list[callable]
        """
        # Consider the following list of default augmentations:
        # #. horizontal_flip
        # #. vertical_flip
        # #. sharpen
        # #. darken
        # #. lighten
        # #. linear_rotate
        raise NotImplementedError
