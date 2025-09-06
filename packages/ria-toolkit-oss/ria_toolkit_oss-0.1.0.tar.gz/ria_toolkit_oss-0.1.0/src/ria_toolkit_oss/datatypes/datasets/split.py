import math
import os
from collections import Counter
from typing import Optional

import numpy as np
from numpy.random import Generator

from ria_toolkit_oss.datatypes.datasets import RadioDataset
from ria_toolkit_oss.datatypes.datasets.h5helpers import (
    copy_over_example,
    make_empty_clone,
)


def split(dataset: RadioDataset, lengths: list[int | float]) -> list[RadioDataset]:
    """Split a radio dataset into non-overlapping new datasets of given lengths.

    Recordings are long-form tapes, which can be obtained either from a software-defined radio (SDR) or generated
    synthetically. Then, radio datasets are curated from collections of recordings by segmenting these
    longer-form tapes into shorter units called slices.

    For each slice in the dataset, the metadata should include the unique ID of the recording from which the example
    was cut ('rec_id'). To avoid leakage, all examples with the same 'rec_id' are assigned only to one of the new
    datasets. This ensures, for example, that slices cut from the same recording do not appear in both the training
    and test datasets.

    This restriction makes it challenging to generate datasets with the exact lengths specified. To get as close as
    possible, this method uses a greedy algorithm, which assigns the recordings with the most slices first, working
    down to those with the fewest. This may not always provide a perfect split, but it works well in most practical
    cases.

    This function is deterministic, meaning it will always produce the same split. For a random split, see
    ria_toolkit_oss.datatypes.datasets.random_split.

    :param dataset: Dataset to be split.
    :type dataset: RadioDataset
    :param: lengths: Lengths or fractions of splits to be produced. If given a list of fractions, the list should
     sum up to 1. The lengths will be computed automatically as ``floor(frac * len(dataset))`` for each fraction
     provided, and any remainders will be distributed in round-robin fashion.
    :type lengths: list of ints (lengths) or floats (fractions)

    :return: List of radio datasets. The number of returned datasets will correspond to the length of the provided
     'lengths' list.
    :rtype: list of RadioDataset

    **Examples:**

    >>> import random
    >>> import string
    >>> import numpy as np
    >>> import pandas as pd
    >>> from ria_toolkit_oss.datatypes.datasets import split

    First, let's generate some random data:

    >>> shape = (24, 1, 1024)  # 24 examples, each of length 1024
    >>> real_part, imag_part = np.random.randint(0, 12, size=shape), np.random.randint(0, 79, size=shape)
    >>> data = real_part + 1j * imag_part

    Then, a list of recording IDs. Let's pretend this data was cut from 4 separate recordings:

    >>> rec_id_options = [''.join(random.choices(string.ascii_lowercase + string.digits, k=256)) for _ in range(4)]
    >>> rec_id = [np.random.choice(rec_id_options) for _ in range(shape[0])]

    Using this data and metadata, let's initialize a dataset:

    >>> metadata = pd.DataFrame(data={"rec_id": rec_id}).to_records(index=False)
    >>> fid = os.path.join(os.getcwd(), "source_file.hdf5")
    >>> ds = RadioDataset(source=fid)

    Finally, let's do an 80/20 train-test split:

    >>> train_ds, test_ds = split(ds, lengths=[0.8, 0.2])
    """
    if not isinstance(dataset, RadioDataset):
        raise ValueError(f"'dataset' must be RadioDataset or one of its subclasses, got {type(dataset)}.")

    lengths_ = _validate_lengths(dataset=dataset, lengths=lengths)

    if "rec_id" not in dataset.metadata or not isinstance(dataset.metadata["rec_id"][0], str):
        raise ValueError("Dataset missing string field 'rec_id'.")

    rec_ids = dict(Counter(dataset.metadata["rec_id"]))

    if len(rec_ids) < len(lengths_):
        raise ValueError(f"Not enough Recordings IDs in the dataset for a {len(lengths_)}-way split.")

    # Sort the rec_ids in descending order by frequency.
    ids, freqs = list(rec_ids.keys()), list(rec_ids.values())
    sorted_indices = np.flip(np.argsort(freqs))
    sorted_rec_ids = [ids[x] for x in sorted_indices]
    sorted_freqs = [freqs[x] for x in sorted_indices]

    # Preallocate keys, which we'll use to track which recordings are assigned to which subsets.
    split_key_ids = [[] for _ in range(len(lengths_))]
    split_key_freqs = [[] for _ in range(len(lengths_))]

    for i in range(len(rec_ids)):
        # Find the subset whose current length is farthest from its target length.
        current_lengths = [sum(subkey) for subkey in split_key_freqs]
        diffs = [lengths_[j] - current_lengths[j] for j in range(len(lengths_))]
        index = np.argmax(diffs)

        # Add the 'rec_id' with the highest frequency to the subset farthest from its target.
        split_key_freqs[index].append(sorted_freqs[i])
        split_key_ids[index].append(sorted_rec_ids[i])

    _validate_sublists(list_of_lists=split_key_ids, ids=ids)

    return _split_datasets(dataset=dataset, key=split_key_ids)


def random_split(
    dataset: RadioDataset, lengths: list[int | float], generator: Optional[Generator] = None
) -> list[RadioDataset]:
    """Randomly split a radio dataset into non-overlapping new datasets of given lengths.

    Recordings are long-form tapes, which can be obtained either from a software-defined radio (SDR) or generated
    synthetically. Then, radio datasets are curated from collections of recordings by segmenting these
    longer-form tapes into shorter units called slices.

    For each slice in the dataset, the metadata should include the unique recording ID ('rec_id') of the recording
    from which the example was cut. To avoid leakage, all examples with the same 'rec_id' are assigned only to one of
    the new datasets. This ensures, for example, that slices cut from the same recording do not appear in both the
    training and test datasets.

    This restriction makes it unlikely that a random split will produce datasets with the exact lengths specified.
    If it is important to ensure the closest possible split, consider using ria_toolkit_oss.datatypes.datasets.split
     instead.

    :param dataset: Dataset to be split.
    :type dataset: RadioDataset
    :param: lengths: Lengths or fractions of splits to be produced. If given a list of fractions, the list should
     sum up to 1. The lengths will be computed automatically as ``floor(frac * len(dataset))`` for each fraction
     provided, and any remainders will be distributed in round-robin fashion.
    :type lengths: list of ints (lengths) or floats (fractions)

    :param generator: Random generator. Defaults to None.
    :type generator: NumPy Generator Object, optional.

    :return: List of radio datasets. The number of returned datasets will correspond to the length of the provided
     'lengths' list.
    :rtype: list of RadioDataset

    See Also:
        ria_toolkit_oss.datatypes.datasets.split: Usage is the same as for ``random_split()``.
    """
    if not isinstance(dataset, RadioDataset):
        raise ValueError(f"'dataset' must be RadioDataset or one of its subclasses, got {type(dataset)}.")

    lengths_ = _validate_lengths(dataset=dataset, lengths=lengths)

    if generator is None:
        rng = np.random.default_rng(np.random.randint(0, np.iinfo(np.int32).max))
    else:
        rng = generator

    if "rec_id" not in dataset.metadata or not isinstance(dataset.metadata["rec_id"][0], str):
        raise ValueError("Dataset missing string field 'rec_id'.")

    rec_ids = dict(Counter(dataset.metadata["rec_id"]))

    if len(rec_ids) < len(lengths_):
        raise ValueError(f"Not enough Recordings IDs in the dataset for a {len(lengths_)}-way split.")

    ids, freqs = list(rec_ids.keys()), list(rec_ids.values())
    sorted_indices = np.flip(np.argsort(freqs))
    sorted_rec_ids = [ids[x] for x in sorted_indices]
    sorted_freqs = [freqs[x] for x in sorted_indices]

    # Preallocate keys, which we'll use to track which recordings are assigned to which subsets.
    n = len(lengths_)
    split_key_ids = [[] for _ in range(n)]
    split_key_freqs = [[] for _ in range(n)]

    # Taking from the bottom (least frequent), assign one recording to each subset. This is important to ensure we
    # don't end up with any empty subsets, and serves to help randomize the results.
    top_rec_ids, bottom_rec_ids = sorted_rec_ids[:-n], sorted_rec_ids[-n:]
    top_freqs, bottom_freqs = sorted_freqs[:-n], sorted_freqs[-n:]
    bottom_indices = rng.permutation(x=np.asarray(range(n)))

    for i in range(n):
        split_key_freqs[i].append(bottom_freqs[bottom_indices[i]])
        split_key_ids[i].append(bottom_rec_ids[bottom_indices[i]])

    for i in range(len(top_rec_ids)):
        # Find the subset whose current length is farthest from its target length.
        current_lengths = np.array([sum(subkey) for subkey in split_key_freqs])
        diffs = np.array([lengths_[j] - current_lengths[j] for j in range(n)])

        # Use the normalized diffs as probabilities. This results in a higher probability for larger diffs.
        diffs = np.asarray([0 if d < 0 else d for d in diffs])  # Don't add to full or overfull subsets.
        probabilities = diffs / sum(diffs)

        index = rng.choice(range(n), p=probabilities)

        # Add the 'rec_id' with the highest frequency to the chosen subset.
        split_key_freqs[index].append(top_freqs[i])
        split_key_ids[index].append(top_rec_ids[i])

    _validate_sublists(list_of_lists=split_key_ids, ids=ids)

    return _split_datasets(dataset=dataset, key=split_key_ids, generator=rng)


def _validate_lengths(dataset: RadioDataset, lengths: list[int | float]) -> list[int]:
    """Validate lengths. If lengths are fractions of splits, lengths will be computed automatically.

    :param dataset: Dataset to be split.
    :type dataset: RadioDataset
    :param: lengths: Lengths or fractions of splits to be produced.
    :type lengths: list of ints (lengths) or floats (fractions)

    :return: List of lengths to be produced.
    :rtype: list of ints
    """
    if not isinstance(lengths, list):
        raise ValueError(f"'lengths' must be a list of ints or a list of floats, got {type(lengths)}.")

    if len(lengths) < 2:
        raise ValueError("'lengths' list must contain at least 2 elements.")

    if not all(isinstance(sub, type(lengths[0])) for sub in lengths[1:]):
        raise ValueError("All elements of 'lengths' must be of the same type.")

    if sum(lengths) == len(dataset):
        return [int(i) for i in lengths]

    elif math.isclose(sum(lengths), 1, abs_tol=1e-9):
        # Fractions of splits, which add to 1.
        lengths_ = [math.floor(f * len(dataset)) for f in lengths]

        # Distribute remainders in round-robin fashion to the lengths until there are no remainders left.
        i = 0
        while len(dataset) > sum(lengths_):
            lengths_[i] = lengths_[i] + 1
            i = i + 1

        return lengths_

    else:
        raise ValueError("'lengths' must sum to either the length of 'dataset' or 1.")


def _validate_sublists(list_of_lists: list[list[str]], ids: list[str]) -> None:
    """Ensure that each ID is present in one and only one sublist."""
    all_elements = [item for sublist in list_of_lists for item in sublist]

    assert len(all_elements) == len(set(all_elements)) and list(set(ids)).sort() == list(set(all_elements)).sort()


def _generate_split_source_filenames(
    parent_dataset: RadioDataset, n_new_datasets: int, generator: Generator
) -> list[str]:
    """Generate source filenames for each new dataset.

    Examples:

    .../file_name.hdf5 -> [
        .../file_name.split66ce07f-0.hdf5,
        .../file_name.split66ce07f-1.hdf5,
        .../file_name.split66ce07f-2.hdf5
    ]

    .../file_name.002.hdf5 -> [
        .../file_name.002.split156afd7-0.hdf5,
        .../file_name.002.split156afd7-1.hdf5,
        .../file_name.002.split156afd7-2.hdf5
    ]
    """
    parent_file_name = str(parent_dataset.source)
    parent_base_name = os.path.splitext(parent_file_name)[0]

    random_tag = generator.bytes(length=4).hex()[:7]

    return [f"{parent_base_name}.split{random_tag}-{i}.hdf5" for i in range(n_new_datasets)]


def _split_datasets(
    dataset: RadioDataset, key: list[list[str]], generator: Optional[Generator] = None
) -> list[RadioDataset]:
    """Once we know how we'd like to split up the dataset (i.e., which slices are to be included in which new
    dataset), this helper function does the actual split.

    :param dataset: Dataset to be split.
    :type dataset: RadioDataset
    :param key: A key indicating which slices are to be included in which dataset. This is a list of lists, where
     each sublist contains the recordings IDs of the slices to be included in the corresponding subset.
    :type key: A list of lists

    :param generator: Random generator. Defaults to None.
    :type generator: NumPy Generator Object, optional.

    :return: Non-overlapping datasets
    :rtype: list of RadioDataset
    """
    if generator is None:
        rng = np.random.default_rng(np.random.randint(0, np.iinfo(np.int32).max))
    else:
        rng = generator

    new_source_filenames = _generate_split_source_filenames(
        parent_dataset=dataset, n_new_datasets=len(key), generator=rng
    )

    for new_source in new_source_filenames:
        make_empty_clone(original_source=dataset.source, new_source=new_source, example_length=len(dataset.data[0, 0]))

    new_datasets = [dataset.__class__(source=new_source) for new_source in new_source_filenames]

    rec_ids = list(dataset.metadata["rec_id"])

    for i, sublist in enumerate(key):
        for rec_id in sublist:
            # The examples at these indices are part of the corresponding new dataset.
            indices = [index for index, value in enumerate(rec_ids) if value == rec_id]
            for idx in indices:
                copy_over_example(source=dataset.source, destination=new_datasets[i].source, idx=idx)

    return new_datasets
