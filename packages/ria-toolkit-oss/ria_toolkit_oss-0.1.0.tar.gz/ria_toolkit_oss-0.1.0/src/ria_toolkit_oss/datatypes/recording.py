from __future__ import annotations

import copy
import datetime
import hashlib
import json
import os
import re
import time
import warnings
from typing import Any, Iterator, Optional

import numpy as np
from numpy.typing import ArrayLike
from quantiphy import Quantity

from ria_toolkit_oss.datatypes.annotation import Annotation

PROTECTED_KEYS = ["rec_id", "timestamp"]


class Recording:
    """Tape of complex IQ (in-phase and quadrature) samples with associated metadata and annotations.

    Recording data is a complex array of shape C x N, where C is the number of channels
    and N is the number of samples in each channel.

    Metadata is stored in a dictionary of key value pairs,
    to include information such as sample_rate and center_frequency.

    Annotations are a list of :ref:`Annotation <ria_toolkit_oss.datatypes.Annotation>`,
    defining bounding boxes in time and frequency with labels and metadata.

    Here, signal data is represented as a NumPy array. This class is then extended in the RIA Backends to provide
    support for different data structures, such as Tensors.

    Recordings are long-form tapes can be obtained either from a software-defined radio (SDR) or generated
    synthetically. Then, machine learning datasets are curated from collection of recordings by segmenting these
    longer-form tapes into shorter units called slices.

    All recordings are assigned a unique 64-character recording ID, ``rec_id``. If this field is missing from the
    provided metadata, a new ID will be generated upon object instantiation.

    :param data: Signal data as a tape IQ samples, either C x N complex, where C is the number of
        channels and N is number of samples in the signal. If data is a one-dimensional array of complex samples with
        length N, it will be reshaped to a two-dimensional array with dimensions 1 x N.
    :type data: array_like

    :param metadata: Additional information associated with the recording.
    :type metadata: dict, optional
    :param annotations: A collection of ``Annotation`` objects defining bounding boxes.
    :type annotations: list of Annotations, optional

    :param dtype: Explicitly specify the data-type of the complex samples. Must be a complex NumPy type, such as
        ``np.complex64`` or ``np.complex128``. Default is None, in which case the type is determined implicitly. If
        ``data`` is a NumPy array, the Recording will use the dtype of ``data`` directly without any conversion.
    :type dtype: numpy dtype object, optional
    :param timestamp: The timestamp when the recording data was generated. If provided, it should be a float or integer
        representing the time in seconds since epoch (e.g., ``time.time()``). Only used if the `timestamp` field is not
        present in the provided metadata.
    :type dtype: float or int, optional

    :raises ValueError: If data is not complex 1xN or CxN.
    :raises ValueError: If metadata is not a python dict.
    :raises ValueError: If metadata is not json serializable.
    :raises ValueError: If annotations is not a list of valid annotation objects.

    **Examples:**

    >>> import numpy
    >>> from ria_toolkit_oss.datatypes import Recording, Annotation

    >>> # Create an array of complex samples, just 1s in this case.
    >>> samples = numpy.ones(10000, dtype=numpy.complex64)

    >>> # Create a dictionary of relevant metadata.
    >>> sample_rate = 1e6
    >>> center_frequency = 2.44e9
    >>> metadata = {
    ...     "sample_rate": sample_rate,
    ...     "center_frequency": center_frequency,
    ...     "author": "me",
    ... }

    >>> # Create an annotation for the annotations list.
    >>> annotations = [
    ...     Annotation(
    ...         sample_start=0,
    ...         sample_count=1000,
    ...         freq_lower_edge=center_frequency - (sample_rate / 2),
    ...         freq_upper_edge=center_frequency + (sample_rate / 2),
    ...         label="example",
    ...     )
    ... ]

    >>> # Store samples, metadata, and annotations together in a convenient object.
    >>> recording = Recording(data=samples, metadata=metadata, annotations=annotations)
    >>> print(recording.metadata)
    {'sample_rate': 1000000.0, 'center_frequency': 2440000000.0, 'author': 'me'}
    >>> print(recording.annotations[0].label)
    'example'
    """

    def __init__(  # noqa C901
        self,
        data: ArrayLike | list[list],
        metadata: Optional[dict[str, any]] = None,
        dtype: Optional[np.dtype] = None,
        timestamp: Optional[float | int] = None,
        annotations: Optional[list[Annotation]] = None,
    ):

        data_arr = np.asarray(data)

        if np.iscomplexobj(data_arr):
            # Expect C x N
            if data_arr.ndim == 1:
                self._data = np.expand_dims(data_arr, axis=0)  # N -> 1 x N
            elif data_arr.ndim == 2:
                self._data = data_arr
            else:
                raise ValueError("Complex data must be C x N.")

        else:
            raise ValueError("Input data must be complex.")

        if dtype is not None:
            self._data = self._data.astype(dtype)

        assert np.iscomplexobj(self._data)

        if metadata is None:
            self._metadata = {}
        elif isinstance(metadata, dict):
            self._metadata = metadata
        else:
            raise ValueError(f"Metadata must be a python dict, but was {type(metadata)}.")

        if not _is_jsonable(metadata):
            raise ValueError("Value must be JSON serializable.")

        if "timestamp" not in self.metadata:
            if timestamp is not None:
                if not isinstance(timestamp, (int, float)):
                    raise ValueError(f"timestamp must be int or float, not {type(timestamp)}")
                self._metadata["timestamp"] = timestamp
            else:
                self._metadata["timestamp"] = time.time()
        else:
            if not isinstance(self._metadata["timestamp"], (int, float)):
                raise ValueError("timestamp must be int or float, not ", type(self._metadata["timestamp"]))

        if "rec_id" not in self.metadata:
            self._metadata["rec_id"] = generate_recording_id(data=self.data, timestamp=self._metadata["timestamp"])

        if annotations is None:
            self._annotations = []
        elif isinstance(annotations, list):
            self._annotations = annotations
        else:
            raise ValueError("Annotations must be a list or None.")

        if not all(isinstance(annotation, Annotation) for annotation in self._annotations):
            raise ValueError("All elements in self._annotations must be of type Annotation.")

        self._index = 0

    @property
    def data(self) -> np.ndarray:
        """
        :return: Recording data, as a complex array.
        :type: np.ndarray

        .. note::

           For recordings with more than 1,024 samples, this property returns a read-only view of the data.

        .. note::

           To access specific samples, consider indexing the object directly with ``rec[c, n]``.
        """
        if self._data.size > 1024:
            # Returning a read-only view prevents mutation at a distance while maintaining performance.
            v = self._data.view()
            v.setflags(write=False)
            return v
        else:
            return self._data.copy()

    @property
    def metadata(self) -> dict:
        """
        :return: Dictionary of recording metadata.
        :type: dict
        """
        return self._metadata.copy()

    @property
    def annotations(self) -> list[Annotation]:
        """
        :return: List of recording annotations
        :type: list of Annotation objects
        """
        return self._annotations.copy()

    @property
    def shape(self) -> tuple[int]:
        """
        :return: The shape of the data array.
        :type: tuple of ints
        """
        return np.shape(self.data)

    @property
    def n_chan(self) -> int:
        """
        :return: The number of channels in the recording.
        :type: int
        """
        return self.shape[0]

    @property
    def rec_id(self) -> str:
        """
        :return: Recording ID.
        :type: str
        """
        return self.metadata["rec_id"]

    @property
    def dtype(self) -> str:
        """
        :return: Data-type of the data array's elements.
        :type: numpy dtype object
        """
        return self.data.dtype

    @property
    def timestamp(self) -> float | int:
        """
        :return: Recording timestamp (time in seconds since epoch).
        :type: float or int
        """
        return self.metadata["timestamp"]

    @property
    def sample_rate(self) -> float | None:
        """
        :return: Sample rate of the recording, or None is 'sample_rate' is not in metadata.
        :type: str
        """
        return self.metadata.get("sample_rate")

    @sample_rate.setter
    def sample_rate(self, sample_rate: float | int) -> None:
        """Set the sample rate of the recording.

        :param sample_rate: The sample rate of the recording.
        :type sample_rate: float or int

        :return: None
        """
        self.add_to_metadata(key="sample_rate", value=sample_rate)

    def astype(self, dtype: np.dtype) -> Recording:
        """Copy of the recording, data cast to a specified type.

        .. todo: This method is not yet implemented.

        :param dtype: Data-type to which the array is cast. Must be a complex scalar type, such as ``np.complex64`` or
            ``np.complex128``.
        :type dtype: NumPy data type, optional

        .. note: Casting to a data type with less precision can risk losing data by truncating or rounding values,
          potentially resulting in a loss of accuracy and significant information.

        :return: A new recording with the same metadata and data, with dtype.

        TODO: Add example usage.
        """
        # Rather than check for a valid datatype, let's cast and check the result. This makes it easier to provide
        # cross-platform support where the types are aliased across platforms.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Casting may generate user warnings. E.g., complex -> real
            data = self.data.astype(dtype)

        if np.iscomplexobj(data):
            return Recording(data=data, metadata=self.metadata, annotations=self.annotations)
        else:
            raise ValueError("dtype must be a complex number scalar type.")

    def add_to_metadata(self, key: str, value: Any) -> None:
        """Add a new key-value pair to the recording metadata.

        :param key: New metadata key, must be snake_case.
        :type key: str
        :param value: Corresponding metadata value.
        :type value: any

        :raises ValueError: If key is already in metadata or if key is not a valid metadata key.
        :raises ValueError: If value is not JSON serializable.

        :return: None.

        **Examples:**

        Create a recording and add metadata:

        >>> import numpy
        >>> from ria_toolkit_oss.datatypes import Recording
        >>>
        >>> samples = numpy.ones(10000, dtype=numpy.complex64)
        >>> metadata = {
        >>>     "sample_rate": 1e6,
        >>>     "center_frequency": 2.44e9,
        >>> }
        >>>
        >>> recording = Recording(data=samples, metadata=metadata)
        >>> print(recording.metadata)
        {'sample_rate': 1000000.0,
        'center_frequency': 2440000000.0,
        'timestamp': 17369...,
        'rec_id': 'fda0f41...'}
        >>>
        >>> recording.add_to_metadata(key="author", value="me")
        >>> print(recording.metadata)
        {'sample_rate': 1000000.0,
        'center_frequency': 2440000000.0,
        'author': 'me',
        'timestamp': 17369...,
        'rec_id': 'fda0f41...'}
        """
        if key in self.metadata:
            raise ValueError(
                f"Key {key} already in metadata. Use Recording.update_metadata() to modify existing fields."
            )

        if not _is_valid_metadata_key(key):
            raise ValueError(f"Invalid metadata key: {key}.")

        if not _is_jsonable(value):
            raise ValueError("Value must be JSON serializable.")

        self._metadata[key] = value

    def update_metadata(self, key: str, value: Any) -> None:
        """Update the value of an existing metadata key,
        or add the key value pair if it does not already exist.

        :param key: Existing metadata key.
        :type key: str
        :param value: New value to enter at key.
        :type value: any

        :raises ValueError: If value is not JSON serializable
        :raises ValueError: If key is protected.

        :return: None.

        **Examples:**

        Create a recording and update metadata:

        >>> import numpy
        >>> from ria_toolkit_oss.datatypes import Recording

        >>> samples = numpy.ones(10000, dtype=numpy.complex64)
        >>> metadata = {
        >>>     "sample_rate": 1e6,
        >>>     "center_frequency": 2.44e9,
        >>>     "author": "me"
        >>> }

        >>> recording = Recording(data=samples, metadata=metadata)
        >>> print(recording.metadata)
        {'sample_rate': 1000000.0,
        'center_frequency': 2440000000.0,
        'author': "me",
        'timestamp': 17369...
        'rec_id': 'fda0f41...'}

        >>> recording.update_metadata(key="author", value=you")
        >>> print(recording.metadata)
        {'sample_rate': 1000000.0,
        'center_frequency': 2440000000.0,
        'author': "you",
        'timestamp': 17369...
        'rec_id': 'fda0f41...'}
        """
        if key not in self.metadata:
            self.add_to_metadata(key=key, value=value)

        if not _is_jsonable(value):
            raise ValueError("Value must be JSON serializable.")

        if key in PROTECTED_KEYS:  # Check protected keys.
            raise ValueError(f"Key {key} is protected and cannot be modified or removed.")

        else:
            self._metadata[key] = value

    def remove_from_metadata(self, key: str):
        """
        Remove a key from the recording metadata.
        Does not remove key if it is protected.

        :param key: The key to remove.
        :type key: str

        :raises ValueError: If key is protected.

        :return: None.

        **Examples:**

        Create a recording and add metadata:

        >>> import numpy
        >>> from ria_toolkit_oss.datatypes import Recording

        >>> samples = numpy.ones(10000, dtype=numpy.complex64)
        >>> metadata = {
        ...     "sample_rate": 1e6,
        ...     "center_frequency": 2.44e9,
        ... }

        >>> recording = Recording(data=samples, metadata=metadata)
        >>> print(recording.metadata)
        {'sample_rate': 1000000.0,
        'center_frequency': 2440000000.0,
        'timestamp': 17369...,  # Example value
        'rec_id': 'fda0f41...'}  # Example value

        >>> recording.add_to_metadata(key="author", value="me")
        >>> print(recording.metadata)
        {'sample_rate': 1000000.0,
        'center_frequency': 2440000000.0,
        'author': 'me',
        'timestamp': 17369...,  # Example value
        'rec_id': 'fda0f41...'}  # Example value
        """
        if key not in PROTECTED_KEYS:
            self._metadata.pop(key)
        else:
            raise ValueError(f"Key {key} is protected and cannot be modified or removed.")

    def view(self, output_path: Optional[str] = "images/signal.png", **kwargs) -> None:
        """Create a plot of various signal visualizations as a PNG image.

        :param output_path: The output image path. Defaults to "images/signal.png".
        :type output_path: str, optional
        :param kwargs: Keyword arguments passed on to ria_toolkit_oss.view.view_sig.
        :type: dict of keyword arguments

        **Examples:**

        Create a recording and view it as a plot in a .png image:

        >>> import numpy
        >>> from ria_toolkit_oss.datatypes import Recording

        >>> samples = numpy.ones(10000, dtype=numpy.complex64)
        >>> metadata = {
        >>>     "sample_rate": 1e6,
        >>>     "center_frequency": 2.44e9,
        >>> }

        >>> recording = Recording(data=samples, metadata=metadata)
        >>> recording.view()
        """
        from ria_toolkit_oss.view import view_sig

        view_sig(recording=self, output_path=output_path, **kwargs)

    def to_sigmf(self, filename: Optional[str] = None, path: Optional[os.PathLike | str] = None) -> None:
        """Write recording to a set of SigMF files.

        The SigMF io format is defined by the `SigMF Specification Project <https://github.com/sigmf/SigMF>`_

        :param recording: The recording to be written to file.
        :type recording: ria_toolkit_oss.datatypes.Recording
        :param filename: The name of the file where the recording is to be saved. Defaults to auto generated filename.
        :type filename: os.PathLike or str, optional
        :param path: The directory path to where the recording is to be saved. Defaults to recordings/.
        :type path: os.PathLike or str, optional

        :raises IOError: If there is an issue encountered during the file writing process.

        :return: None

        **Examples:**

        Create a recording and view it as a plot in a `.png` image:

        >>> import numpy
        >>> from ria_toolkit_oss.datatypes import Recording

        >>> samples = numpy.ones(10000, dtype=numpy.complex64)
        >>> metadata = {
        ...     "sample_rate": 1e6,
        ...     "center_frequency": 2.44e9,
        ... }

        >>> recording = Recording(data=samples, metadata=metadata)
        >>> recording.view()
        """
        from ria_toolkit_oss.io.recording import to_sigmf

        to_sigmf(filename=filename, path=path, recording=self)

    def to_npy(self, filename: Optional[str] = None, path: Optional[os.PathLike | str] = None) -> str:
        """Write recording to ``.npy`` binary file.

        :param filename: The name of the file where the recording is to be saved. Defaults to auto generated filename.
        :type filename: os.PathLike or str, optional
        :param path: The directory path to where the recording is to be saved. Defaults to recordings/.
        :type path: os.PathLike or str, optional

        :raises IOError: If there is an issue encountered during the file writing process.

        :return: Path where the file was saved.
        :rtype: str

        **Examples:**

        Create a recording and save it to a .npy file:

        >>> import numpy
        >>> from ria_toolkit_oss.datatypes import Recording

        >>> samples = numpy.ones(10000, dtype=numpy.complex64)
        >>> metadata = {
        >>>     "sample_rate": 1e6,
        >>>     "center_frequency": 2.44e9,
        >>> }

        >>> recording = Recording(data=samples, metadata=metadata)
        >>> recording.to_npy()
        """
        from ria_toolkit_oss.io.recording import to_npy

        to_npy(recording=self, filename=filename, path=path)

    def trim(self, num_samples: int, start_sample: Optional[int] = 0) -> Recording:
        """Trim Recording samples to a desired length, shifting annotations to maintain alignment.

        :param start_sample: The start index of the desired trimmed recording. Defaults to 0.
        :type start_sample: int, optional
        :param num_samples: The number of samples that the output trimmed recording will have.
        :type num_samples: int
        :raises IndexError: If start_sample + num_samples is greater than the length of the recording.
        :raises IndexError: If sample_start < 0 or num_samples < 0.

        :return: The trimmed Recording.
        :rtype: Recording

        **Examples:**

        Create a recording and trim it:

        >>> import numpy
        >>> from ria_toolkit_oss.datatypes import Recording

        >>> samples = numpy.ones(10000, dtype=numpy.complex64)
        >>> metadata = {
        ...     "sample_rate": 1e6,
        ...     "center_frequency": 2.44e9,
        ... }

        >>> recording = Recording(data=samples, metadata=metadata)
        >>> print(len(recording))
        10000

        >>> trimmed_recording = recording.trim(start_sample=1000, num_samples=1000)
        >>> print(len(trimmed_recording))
        1000
        """

        if start_sample < 0:
            raise IndexError("start_sample cannot be < 0.")
        elif start_sample + num_samples > len(self):
            raise IndexError(
                f"start_sample {start_sample} + num_samples {num_samples} > recording length {len(self)}."
            )

        end_sample = start_sample + num_samples

        data = self.data[:, start_sample:end_sample]

        new_annotations = copy.deepcopy(self.annotations)
        for annotation in new_annotations:
            # trim annotation if it goes outside the trim boundaries
            if annotation.sample_start < start_sample:
                annotation.sample_count = annotation.sample_count - (start_sample - annotation.sample_start)
                annotation.sample_start = start_sample

            if annotation.sample_start + annotation.sample_count > end_sample:
                annotation.sample_count = end_sample - annotation.sample_start

            # shift annotation to align with the new start point
            annotation.sample_start = annotation.sample_start - start_sample

        return Recording(data=data, metadata=self.metadata, annotations=new_annotations)

    def normalize(self) -> Recording:
        """Scale the recording data, relative to its maximum value, so that the magnitude of the maximum sample is 1.

        :return: Recording where the maximum sample amplitude is 1.
        :rtype: Recording

        **Examples:**

        Create a recording with maximum amplitude 0.5 and normalize to a maximum amplitude of 1:

        >>> import numpy
        >>> from ria_toolkit_oss.datatypes import Recording

        >>> samples = numpy.ones(10000, dtype=numpy.complex64) * 0.5
        >>> metadata = {
        ...     "sample_rate": 1e6,
        ...     "center_frequency": 2.44e9,
        ... }

        >>> recording = Recording(data=samples, metadata=metadata)
        >>> print(numpy.max(numpy.abs(recording.data)))
        0.5

        >>> normalized_recording = recording.normalize()
        >>> print(numpy.max(numpy.abs(normalized_recording.data)))
        1
        """
        scaled_data = self.data / np.max(abs(self.data))
        return Recording(data=scaled_data, metadata=self.metadata, annotations=self.annotations)

    def generate_filename(self, tag: Optional[str] = "rec"):
        """Generate a filename from metadata.

        :param tag: The string at the beginning of the generated filename. Default is "rec".
        :type tag: str, optional

        :return: A filename without an extension.
        :rtype: str
        """
        # TODO: This method should be refactored to use the first 7 characters of the 'rec_id' field.

        tag = tag + "_"
        source = self.metadata.get("source", "")
        if source != "":
            source = source + "_"

        # converts 1000 to 1k for example
        center_frequency = str(Quantity(self.metadata.get("center_frequency", 0)))
        if center_frequency != "0":
            num = center_frequency[:-1]
            suffix = center_frequency[-1]
            num = int(np.round(float(num)))
        else:
            num = 0
            suffix = ""
        center_frequency = str(num) + suffix + "Hz_"

        timestamp = int(self.timestamp)
        timestamp = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d_%H-%M-%S") + "_"

        # Add first seven characters of rec_id for uniqueness
        rec_id = self.rec_id[0:7]
        return tag + source + center_frequency + timestamp + rec_id

    def __len__(self) -> int:
        """The length of a recording is defined by the number of complex samples in each channel of the recording."""
        return self.shape[1]

    def __eq__(self, other: Recording) -> bool:
        """Two Recordings are equal if all data, metadata, and annotations are the same."""

        # counter used to allow for differently ordered annotation lists
        return (
            np.array_equal(self.data, other.data)
            and self.metadata == other.metadata
            and self.annotations == other.annotations
        )

    def __ne__(self, other: Recording) -> bool:
        """Two Recordings are equal if all data, and metadata, and annotations are the same."""
        return not self.__eq__(other=other)

    def __iter__(self) -> Iterator:
        self._index = 0
        return self

    def __next__(self) -> np.ndarray:
        if self._index < self.n_chan:
            to_ret = self.data[self._index]
            self._index += 1
            return to_ret
        else:
            raise StopIteration

    def __getitem__(self, key: int | tuple[int] | slice) -> np.ndarray | np.complexfloating:
        """If key is an integer, tuple of integers, or a slice, return the corresponding samples.

        For arrays with 1,024 or fewer samples, return a copy of the recording data. For larger arrays, return a
        read-only view. This prevents mutation at a distance while maintaining performance.
        """
        if isinstance(key, (int, tuple, slice)):
            v = self._data[key]
            if isinstance(v, np.complexfloating):
                return v
            elif v.size > 1024:
                v.setflags(write=False)  # Make view read-only.
                return v
            else:
                return v.copy()

        else:
            raise ValueError(f"Key must be an integer, tuple, or slice but was {type(key)}.")

    def __setitem__(self, *args, **kwargs) -> None:
        """Raise an error if an attempt is made to assign to the recording."""
        raise ValueError("Assignment to Recording is not allowed.")


def generate_recording_id(data: np.ndarray, timestamp: Optional[float | int] = None) -> str:
    """Generate unique 64-character recording ID. The recording ID is generated by hashing the recording data with
    the datetime that the recording data was generated. If no datatime is provided, the current datatime is used.

    :param data: Tape of IQ samples, as a NumPy array.
    :type data: np.ndarray
    :param timestamp: Unix timestamp in seconds. Defaults to None.
    :type timestamp: float or int, optional

    :return: 256-character hash, to be used as the recording ID.
    :rtype: str
    """
    if timestamp is None:
        timestamp = time.time()

    byte_sequence = data.tobytes() + str(timestamp).encode("utf-8")
    sha256_hash = hashlib.sha256(byte_sequence)

    return sha256_hash.hexdigest()


def _is_jsonable(x: Any) -> bool:
    """
    :return: True if x is JSON serializable, False otherwise.
    """
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


def _is_valid_metadata_key(key: Any) -> bool:
    """
    :return: True if key is a valid metadata key, False otherwise.
    """
    if isinstance(key, str) and key.islower() and re.match(pattern=r"^[a-z_]+$", string=key) is not None:
        return True

    else:
        return False
