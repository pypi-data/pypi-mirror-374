from __future__ import annotations

import json
from typing import Any, Optional

from sigmf import SigMFFile


class Annotation:
    """Signal annotations are labels or additional information associated with specific data points or segments within
    a signal. These annotations could be used for tasks like supervised learning, where the goal is to train a model
    to recognize patterns or characteristics in the signal associated with these annotations.

    Annotations can be used to label interesting points in your recording.

    :param sample_start: The index of the starting sample of the annotation.
    :type sample_start: int
    :param sample_count: The index of the ending sample of the annotation, inclusive.
    :type sample_count: int
    :param freq_lower_edge: The lower frequency of the annotation.
    :type freq_lower_edge: float
    :param freq_upper_edge: The upper frequency of the annotation.
    :type freq_upper_edge: float
    :param label: The label that will be displayed with the bounding box in compatible viewers including IQEngine.
     Defaults to an emtpy string.
    :type label: str, optional
    :param comment: A human-readable comment. Defaults to an empty string.
    :type comment: str, optional
    :param detail: A dictionary of user defined annotation-specific metadata. Defaults to None.
    :type detail: dict, optional
    """

    def __init__(
        self,
        sample_start: int,
        sample_count: int,
        freq_lower_edge: float,
        freq_upper_edge: float,
        label: Optional[str] = "",
        comment: Optional[str] = "",
        detail: Optional[dict] = None,
    ):
        """Initialize a new Annotation instance."""
        self.sample_start = int(sample_start)
        self.sample_count = int(sample_count)
        self.freq_lower_edge = float(freq_lower_edge)
        self.freq_upper_edge = float(freq_upper_edge)
        self.label = str(label)
        self.comment = str(comment)

        if detail is None:
            self.detail = {}
        elif not _is_jsonable(detail):
            raise ValueError(f"Detail object is not json serializable: {detail}")
        else:
            self.detail = detail

    def is_valid(self) -> bool:
        """
        Check that the annotation sample count is > 0 and the freq_lower_edge<freq_upper_edge.

        :returns: True if valid, False if not.
        """

        return self.sample_count > 0 and self.freq_lower_edge < self.freq_upper_edge

    def overlap(self, other):
        """
        Quantify how much the bounding box in this annotation overlaps with another annotation.

        :param other: The other annotation.
        :type other: Annotation

        :returns: The area of the overlap in samples*frequency, or 0 if they do not overlap."""

        sample_overlap_start = max(self.sample_start, other.sample_start)
        sample_overlap_end = min(self.sample_start + self.sample_count, other.sample_start + other.sample_count)

        freq_overlap_start = max(self.freq_lower_edge, other.freq_lower_edge)
        freq_overlap_end = min(self.freq_upper_edge, other.freq_upper_edge)

        if freq_overlap_start >= freq_overlap_end or sample_overlap_start >= sample_overlap_end:
            return 0
        else:
            return (sample_overlap_end - sample_overlap_start) * (freq_overlap_end - freq_overlap_start)

    def area(self):
        """
        The 'area' of the bounding box, samples*frequency.
        Useful to quantify annotation size.

        :returns: sample length multiplied by bandwidth."""

        return self.sample_count * (self.freq_upper_edge - self.freq_lower_edge)

    def __eq__(self, other: Annotation) -> bool:
        return self.__dict__ == other.__dict__

    def to_sigmf_format(self):
        """
        Returns a JSON dictionary representing this annotation formatted to be saved in a .sigmf-meta file.
        """

        annotation_dict = {SigMFFile.START_INDEX_KEY: self.sample_start, SigMFFile.LENGTH_INDEX_KEY: self.sample_count}

        annotation_dict["metadata"] = {
            SigMFFile.LABEL_KEY: self.label,
            SigMFFile.COMMENT_KEY: self.comment,
            SigMFFile.FHI_KEY: self.freq_upper_edge,
            SigMFFile.FLO_KEY: self.freq_lower_edge,
            "ria:detail": self.detail,
        }

        if _is_jsonable(annotation_dict):
            return annotation_dict
        else:
            raise ValueError("Annotation dictionary was not json serializable.")


def _is_jsonable(x: Any) -> bool:
    """
    :return: True if x is JSON serializable, False otherwise.
    """
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False
