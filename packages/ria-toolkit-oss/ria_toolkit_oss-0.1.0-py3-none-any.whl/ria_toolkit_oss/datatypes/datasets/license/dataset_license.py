from dataclasses import dataclass


@dataclass
class DatasetLicense:
    """
    Represents a dataset license.
    """

    name: str  #: The name or title of the license.
    identifier: str | None  #: SPDX short identifier, or None if one does not exist.
    description: str  #: A description of the license.
    license: str  #: Full license text or URL if the license is available online.
