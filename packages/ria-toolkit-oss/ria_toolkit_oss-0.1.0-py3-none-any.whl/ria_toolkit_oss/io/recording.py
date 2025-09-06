"""
Utilities for input/output operations on the ria_toolkit_oss.datatypes.Recording object.
"""

import datetime as dt
import os
from datetime import timezone
from typing import Optional

import numpy as np
import sigmf
from sigmf import SigMFFile, sigmffile
from sigmf.utils import get_data_type_str

from ria_toolkit_oss.datatypes import Annotation
from ria_toolkit_oss.datatypes.recording import Recording


def load_rec(file: os.PathLike) -> Recording:
    """Load a recording from file.

    :param file: The directory path to the file(s) to load, **with** the file extension.
        To loading from SigMF, the file extension must be one of *sigmf*, *sigmf-data*, or *sigmf-meta*,
        either way both the SigMF data and meta files must be present for a successful read.
    :type file: os.PathLike

    :raises IOError: If there is an issue encountered during the file reading process.

    :raises ValueError: If the inferred file extension is not supported.

    :return: The recording, as initialized from file(s).
    :rtype: ria_toolkit_oss.datatypes.Recording
    """
    _, extension = os.path.splitext(file)
    extension = extension.lstrip(".")

    if extension.lower() in ["sigmf", "sigmf-data", "sigmf-meta"]:
        return from_sigmf(file=file)

    elif extension.lower() == "npy":
        return from_npy(file=file)

    else:
        raise ValueError(f"File extension {extension} not supported.")


SIGMF_KEY_CONVERSION = {
    SigMFFile.AUTHOR_KEY: "author",
    SigMFFile.COLLECTION_KEY: "sigmf:collection",
    SigMFFile.DATASET_KEY: "sigmf:dataset",
    SigMFFile.DATATYPE_KEY: "datatype",
    SigMFFile.DATA_DOI_KEY: "data_doi",
    SigMFFile.DESCRIPTION_KEY: "description",
    SigMFFile.EXTENSIONS_KEY: "sigmf:extensions",
    SigMFFile.GEOLOCATION_KEY: "geolocation",
    SigMFFile.HASH_KEY: "sigmf:hash",
    SigMFFile.HW_KEY: "sdr",
    SigMFFile.LICENSE_KEY: "license",
    SigMFFile.META_DOI_KEY: "metadata",
    SigMFFile.METADATA_ONLY_KEY: "sigmf:metadata_only",
    SigMFFile.NUM_CHANNELS_KEY: "sigmf:num_channels",
    SigMFFile.RECORDER_KEY: "source_software",
    SigMFFile.SAMPLE_RATE_KEY: "sample_rate",
    SigMFFile.START_OFFSET_KEY: "sigmf:start_offset",
    SigMFFile.TRAILING_BYTES_KEY: "sigmf:trailing_bytes",
    SigMFFile.VERSION_KEY: "sigmf:version",
}


def convert_to_serializable(obj):
    """
    Recursively convert a JSON-compatible structure into a fully JSON-serializable one.
    Handles cases like NumPy data types, nested dicts, lists, and sets.
    """
    if isinstance(obj, np.integer):
        return int(obj)  # Convert NumPy int to Python int
    elif isinstance(obj, np.floating):
        return float(obj)  # Convert NumPy float to Python float
    elif isinstance(obj, np.ndarray):
        return obj.tolist()  # Convert NumPy array to list
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]  # Process list or tuple
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}  # Process dict
    elif isinstance(obj, set):
        return list(obj)  # Convert set to list
    elif obj in [float("inf"), float("-inf"), None]:  # Handle infinity or None
        return None
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj  # Base case: already serializable
    else:
        raise TypeError(f"Value of type {type(obj)} is not JSON serializable: {obj}")


def to_sigmf(recording: Recording, filename: Optional[str] = None, path: Optional[os.PathLike | str] = None) -> None:
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

    >>> from ria_toolkit_oss.sdr import Synth
    >>> from ria_toolkit_oss.data import Recording
    >>> from ria_toolkit_oss.io import to_sigmf
    >>> sdr = Synth()
    >>> rec = sdr.record(center_frequency=2.4e9, sample_rate=20e6)
    >>> to_sigmf(recording=rec, file="sample_recording")
    """

    if filename is not None:
        filename, _ = os.path.splitext(filename)
    else:
        filename = recording.generate_filename()

    if path is None:
        path = "recordings"

    if not os.path.exists(path):
        os.makedirs(path)

    multichannel_samples = recording.data
    metadata = recording.metadata
    annotations = recording.annotations

    if multichannel_samples.shape[0] > 1:
        raise NotImplementedError("SigMF File Saving Not Implemented for Multichannel Recordings")
    else:
        # extract single channel
        samples = multichannel_samples[0]

    data_file_path = os.path.join(path, f"{filename}.sigmf-data")

    samples.tofile(data_file_path)
    global_info = {
        SigMFFile.DATATYPE_KEY: get_data_type_str(samples),
        SigMFFile.VERSION_KEY: sigmf.__version__,
        SigMFFile.RECORDER_KEY: "RIA",
    }

    converted_metadata = {
        sigmf_key: metadata[metadata_key]
        for sigmf_key, metadata_key in SIGMF_KEY_CONVERSION.items()
        if metadata_key in metadata
    }

    # Merge dictionaries, giving priority to sigmf_meta
    global_info = {**converted_metadata, **global_info}

    ria_metadata = {f"ria:{key}": value for key, value in metadata.items()}
    ria_metadata = convert_to_serializable(ria_metadata)
    global_info.update(ria_metadata)

    sigMF_metafile = SigMFFile(
        data_file=data_file_path,
        global_info=global_info,
    )

    for annotation_object in annotations:
        annotation_dict = annotation_object.to_sigmf_format()
        annotation_dict = convert_to_serializable(annotation_dict)
        sigMF_metafile.add_annotation(
            start_index=annotation_dict[SigMFFile.START_INDEX_KEY],
            length=annotation_dict[SigMFFile.LENGTH_INDEX_KEY],
            metadata=annotation_dict["metadata"],
        )

    sigMF_metafile.add_capture(
        0,
        metadata={
            SigMFFile.FREQUENCY_KEY: metadata.get("center_frequency", 0),
            SigMFFile.DATETIME_KEY: dt.datetime.fromtimestamp(float(metadata.get("timestamp", 0)), tz=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        },
    )

    meta_dict = sigMF_metafile.ordered_metadata()
    meta_dict["ria"] = metadata

    sigMF_metafile.tofile(f"{os.path.join(path, filename)}.sigmf-meta")


def from_sigmf(file: os.PathLike | str) -> Recording:
    """Load a recording from a set of SigMF files.

    :param file: The directory path to the SigMF recording files, without any file extension.
        The recording will be initialized from ``file_name.sigmf-data`` and ``file_name.sigmf-meta``.
        Both the data and meta files must be present for a successful read.
    :type file: str or os.PathLike

    :raises IOError: If there is an issue encountered during the file reading process.

    :return: The recording, as initialized from the SigMF files.
    :rtype: ria_toolkit_oss.datatypes.Recording
    """

    file = str(file)
    if len(file) > 11:
        if file[-11:-5] != ".sigmf":
            file = file + ".sigmf-data"

    sigmf_file = sigmffile.fromfile(file)

    data = sigmf_file.read_samples()
    global_metadata = sigmf_file.get_global_info()
    dict_annotations = sigmf_file.get_annotations()

    processed_metadata = {}
    for key, value in global_metadata.items():
        # Process core keys
        if key.startswith("core:"):
            base_key = key[5:]  # Remove 'core:' prefix
            converted_key = SIGMF_KEY_CONVERSION.get(base_key, base_key)
        # Process ria keys
        elif key.startswith("ria:"):
            converted_key = key[4:]  # Remove 'ria:' prefix
        else:
            # Load non-core/ria keys as is
            converted_key = key

        processed_metadata[converted_key] = value

    annotations = []

    for dict in dict_annotations:
        annotations.append(
            Annotation(
                sample_start=dict[SigMFFile.START_INDEX_KEY],
                sample_count=dict[SigMFFile.LENGTH_INDEX_KEY],
                freq_lower_edge=dict.get(SigMFFile.FLO_KEY, None),
                freq_upper_edge=dict.get(SigMFFile.FHI_KEY, None),
                label=dict.get(SigMFFile.LABEL_KEY, None),
                comment=dict.get(SigMFFile.COMMENT_KEY, None),
                detail=dict.get("ria:detail", None),
            )
        )

    output_recording = Recording(data=data, metadata=processed_metadata, annotations=annotations)
    return output_recording


def to_npy(recording: Recording, filename: Optional[str] = None, path: Optional[os.PathLike | str] = None) -> str:
    """Write recording to ``.npy`` binary file.

    :param recording: The recording to be written to file.
    :type recording: ria_toolkit_oss.datatypes.Recording
    :param filename: The name of the file where the recording is to be saved. Defaults to auto generated filename.
    :type filename: os.PathLike or str, optional
    :param path: The directory path to where the recording is to be saved. Defaults to recordings/.
    :type path: os.PathLike or str, optional

    :raises IOError: If there is an issue encountered during the file writing process.

    :return: Path where the file was saved.
    :rtype: str

    **Examples:**

    >>> from ria_toolkit_oss.sdr import Synth
    >>> from ria_toolkit_oss.data import Recording
    >>> from ria_toolkit_oss.io import to_npy
    >>> sdr = Synth()
    >>> rec = sdr.record(center_frequency=2.4e9, sample_rate=20e6)
    >>> to_npy(recording=rec, file="sample_recording.npy")
    """
    if filename is not None:
        filename, _ = os.path.splitext(filename)
    else:
        filename = recording.generate_filename()
    filename = filename + ".npy"

    if path is None:
        path = "recordings"

    if not os.path.exists(path):
        os.makedirs(path)
    fullpath = os.path.join(path, filename)

    data = np.array(recording.data)
    metadata = recording.metadata
    annotations = recording.annotations

    with open(file=fullpath, mode="wb") as f:
        np.save(f, data)
        np.save(f, metadata)
        np.save(f, annotations)

    # print(f"Saved recording to {os.getcwd()}/{fullpath}")
    return str(fullpath)


def from_npy(file: os.PathLike | str) -> Recording:
    """Load a recording from a ``.npy`` binary file.

    :param file: The directory path to the recording file, with or without the ``.npy`` file extension.
    :type file: str or os.PathLike

    :raises IOError: If there is an issue encountered during the file reading process.

    :return: The recording, as initialized from the ``.npy`` file.
    :rtype: ria_toolkit_oss.datatypes.Recording
    """

    filename, extension = os.path.splitext(file)
    if extension != ".npy" and extension != "":
        raise ValueError("Cannot use from_npy if file extension is not .npy")

    # Rebuild with .npy extension.
    filename = str(filename) + ".npy"

    with open(file=filename, mode="rb") as f:
        data = np.load(f, allow_pickle=True)
        metadata = np.load(f, allow_pickle=True)
        metadata = metadata.tolist()
        try:
            annotations = list(np.load(f, allow_pickle=True))
        except EOFError:
            annotations = []

    recording = Recording(data=data, metadata=metadata, annotations=annotations)
    return recording
