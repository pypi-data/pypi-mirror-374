"""
A `DatasetBuilder` is a creator class that manages the download, preparation, and creation of radio datasets.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from packaging.version import Version

from ria_toolkit_oss.datatypes.datasets.license.dataset_license import DatasetLicense
from ria_toolkit_oss.datatypes.datasets.radio_dataset import RadioDataset
from ria_toolkit_oss.utils.abstract_attribute import abstract_attribute


class DatasetBuilder(ABC):
    """Abstract interface for radio dataset builders. These builder produce radio datasets for common and project
    datasets related to radio science.

    This class should not be instantiated directly. Instead, subclass it to define specific builders for different
    datasets.
    """

    _url: str = abstract_attribute()
    _SHA256: str  # SHA256 checksum.
    _name: str = abstract_attribute()
    _author: str = abstract_attribute()
    _license: DatasetLicense = abstract_attribute()
    _version: Version = abstract_attribute()
    _latest_version: Version = None

    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        """
        :return: The name of the dataset.
        :type: str
        """
        return self._name

    @property
    def author(self) -> str:
        """
        :return: The author of the dataset.
        :type: str
        """
        return self._author

    @property
    def url(self) -> str:
        """
        :return: The URL where the dataset was accessed.
        :type: str
        """
        return self._url

    @property
    def sha256(self) -> Optional[str]:
        """
        :return: The SHA256 checksum, or None if not set.
        :type: str
        """
        return self._SHA256

    @property
    def md5(self) -> Optional[str]:
        """
        :return: The MD5 checksum, or None if not set.
        :type: str
        """
        return self._MD5

    @property
    def version(self) -> Version:
        """
        :return: The version identifier of the dataset.
        :type: Version Identifier
        """
        return self._version

    @property
    def latest_version(self) -> Optional[Version]:
        """
        :return: The version identifier of the latest available version of the dataset, or None if not set.
        :type: Version Identifier or None
        """
        return self._latest_version

    @property
    def license(self) -> DatasetLicense:
        """
        :return: The dataset license information.
        :type: DatasetLicense
        """
        return self._license

    @property
    def info(self) -> dict[str, Any]:
        """
        :return: Information about the dataset including the name, author, and version of the dataset.
        :rtype: dict
        """
        # TODO: We should increase the amount of information that's included here. See the information included in
        #  tdfs.core.DatasetInfo for more: https://www.tensorflow.org/datasets/api_docs/python/tfds/core/DatasetInfo.
        return {
            "name": self.name,
            "author": self.author,
            "url": self.url,
            "sha256": self.sha256,
            "md5": self.md5,
            "version": self.version,
            "license": self.license,
            "latest_version": self.latest_version,
        }

    @abstractmethod
    def download_and_prepare(self) -> None:
        """Download and prepare the dataset for use as an HDF5 source file.

        Once an HDF5 source file has been prepared, the downloaded files are deleted.
        """
        pass

    @abstractmethod
    def as_dataset(self, backend: str) -> RadioDataset:
        """A factory method to manage the creation of radio datasets.

        :param backend: Backend framework to use ("pytorch" or "tensorflow").
        :type backend: str

        Note: Depending on your installation, not all backends may be available.

        :return: A new RadioDataset based on the signal representation and specified backend.
        :type: RadioDataset
        """
        pass
