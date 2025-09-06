import os

import h5py
import numpy as np


def copy_dataset_entry_by_index(
    source: str | os.PathLike, destination: str | os.PathLike, dataset_path: str, idx: int
) -> None:
    """
    Copies an entry from a dataset based on an index from the source HDF5 file to the destination HDF5 file.

    :param source: The name of the original HDF5 file.
    :type source: str
    :param destination: The name of the new HDF5 file.
    :type destination: str
    :param dataset_path: The path of the dataset from the root of the file.
    :type dataset_path: str
    :param idx: The index of the specified example.
    :type idx: int

    :return: None
    """
    # TODO: Generalize so that source and destination can be file objects or strings
    with h5py.File(source, "r") as original_file, h5py.File(destination, "a") as new_file:
        original_ds = original_file[dataset_path]

        entry = original_ds[idx]
        new_ds = new_file[dataset_path]
        new_ds.resize(new_ds.shape[0] + 1, axis=0)
        new_ds[-1] = entry


def copy_over_example(source: str | os.PathLike, destination: str | os.PathLike, idx: int) -> None:
    """
    Copies over an example and it's corresponding metadata located at the given index to a new file.
        It appends the new example to the end of the new file.

    :param source: The name of the original HDF5 file.
    :type source: str or os.PathLike
    :param destination: The name of the new HDF5 file.
    :type destination: str or os.PathLike
    :param idx: The index of the example within the dataset.
    :type idx: int

    :return: None
    """

    with h5py.File(source, "r") as original_file, h5py.File(destination, "a") as new_file:
        ds, md = original_file["data"], original_file["metadata/metadata"]

        new_ds, new_md = new_file["data"], new_file["metadata/metadata"]

        new_ds.resize(new_ds.shape[0] + 1, axis=0)
        new_md.resize(new_md.shape[0] + 1, axis=0)

        new_ds[-1], new_md[-1] = ds[idx], md[idx]


def append_entry_inplace(source: str | os.PathLike, dataset_path: str, entry: np.ndarray) -> None:
    """
    Appends an entry to the specified dataset of the source HDF5 file. This operation is done inplace.

    :param source: The name of the source HDF5 file.
    :type source: str or os.PathLike
    :param dataset_path: The path of the dataset from the root of the file.
    :type dataset_path: str
    :param entry: The entry that is being copied.
    :type entry: np.ndarray

    :return: None
    """
    # TODO: Generalize so that source can be file object or string
    with h5py.File(source, "a") as new_file:
        new_ds = new_file[dataset_path]
        new_ds.resize(new_ds.shape[0] + 1, axis=0)
        new_ds[-1] = entry


def duplicate_entry_inplace(source: str | os.PathLike, dataset_path: str, idx: int) -> None:
    """
    Appends the entry at index to the end of the dataset. This operation is done inplace.

    :param source: The name of the source HDF5 file.
    :type source: str or os.PathLike
    :param dataset_path: The path of the dataset from the root of the file. This dataset is usually
      'data' or 'metadata/metadata'.
    :type dataset_path: str
    :param idx: The index of the example within the dataset.
    :type idx: int

    :return: None
    """
    # This function appends to dataset, so upon dataset creation, chunks has to = True and max_size has to = None
    with h5py.File(source, "a") as f:
        ds = f[dataset_path]
        entry = ds[idx]
        ds.resize(ds.shape[0] + 1, axis=0)
        ds[-1] = entry


def copy_file(original_source: str | os.PathLike, new_source: str | os.PathLike) -> None:
    """Copies contents of source HDF5 file to a new HDF5 file.

    :param original_source: The name of the original HDF5 source file.
    :type original_source: str or os.PathLike
    :param new_source: The copy of the HDF5 source file.
    :type new_source: str or os.PathLike

    :return: None
    """
    original_file = h5py.File(original_source, "r")

    with h5py.File(new_source, "w") as new_file:
        for key in original_file.keys():
            original_file.copy(key, new_file)

    original_file.close()


def make_empty_clone(original_source: str | os.PathLike, new_source: str | os.PathLike, example_length: int) -> None:
    """Creates a new HDF5 file with the same structure but will leave metadata and dataset empty for operations.

    :param original_source: The name of the original HDF5 source file.
    :type original_source: str or os.PathLike
    :param new_source: The name of the new HDF5 source file.
    :type new_source: str or os.PathLike
    :param example_length: The desired length of an example in the new file.
    :type example_length: int

    :return: None
    """

    with h5py.File(new_source, "w") as new_file, h5py.File(original_source, "r") as original_file:
        for key in original_file.keys():
            if key == "data":
                ds = original_file["data"]
                channels = ds.shape[1]
                new_file.create_dataset(
                    "data",
                    shape=(0, channels, example_length),
                    chunks=True,
                    maxshape=(None, None, None),
                    dtype=original_file["data"].dtype,
                )
            elif key == "metadata":
                new_metadata_group = new_file.create_group("metadata")
                new_metadata_group.create_dataset(
                    "metadata",
                    shape=(0,),
                    chunks=True,
                    maxshape=(None,),
                    dtype=original_file["metadata/metadata"].dtype,
                )
            else:
                original_file.copy(key, new_file)


def delete_example_inplace(source: str | os.PathLike, idx: int) -> None:
    """Deletes an example and it's corresponding metadata located at the given index.
        This deletion is done by creating a temporary dataset and copying all contents
        to the temporary dataset except for the example at idx. This operation is inplace.

    :param source: The name of the source HDF5 file.
    :type source: str or os.PathLike
    :param idx: The index of the example and metadata to be deleted.
    :type idx: int

    :return: None
    """

    with h5py.File(source, "a") as f:
        ds, md = f["data"], f["metadata/metadata"]
        m, c, n = ds.shape
        assert 0 <= idx <= m - 1
        assert len(ds) == len(md)

        new_ds = f.create_dataset(
            "data.temp",
            shape=(m - 1, c, n),
            chunks=True,
            dtype=ds.dtype,
            maxshape=(None, None, None),  # Required to allow future mutations which expand the shape
        )
        new_md = f.create_dataset(
            "metadata/metadata.temp", shape=len(md) - 1, chunks=True, dtype=md.dtype, maxshape=(None,)
        )

        for row in range(idx):
            new_ds[row], new_md[row] = ds[row], md[row]

        for row in range(idx + 1, len(md)):
            new_ds[row - 1], new_md[row - 1] = ds[row], md[row]

        del f["data"]
        del f["metadata/metadata"]

        f.move("data.temp", "data")
        f.move("metadata/metadata.temp", "metadata/metadata")


def overwrite_file(source: str | os.PathLike, new_data: np.ndarray) -> None:
    """
    Overwrites data in an HDF5 file with new data.

    :param source: The copy of the HDF5 source file.
    :type source: str or os.PathLike
    :param new_data: The updated copy of the data that should be stored.
    :type new_data: np.ndarray

    :return: None
    """

    # TODO: Might need to pass in dataset_path instead of datastet_name depending on file structure
    # Update copy to include augmented data

    with h5py.File(source, "r+") as f:
        ds_name = tuple(f.keys())[0]
        del f[ds_name]
        f.create_dataset(ds_name, data=new_data)
        f.close()
