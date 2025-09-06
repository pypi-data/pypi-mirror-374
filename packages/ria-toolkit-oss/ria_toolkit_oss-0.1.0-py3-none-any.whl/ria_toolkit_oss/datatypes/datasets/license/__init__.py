"""
This package contains the ``DatasetLicense`` class and a bunch of off-the-shelf implementations for several common
license types.

Common license types for datasets courtesy of the University of Calgary:
`Common license types for datasets and what they mean <https://libanswers.ucalgary.ca/faq/200582>`_

.. note::

   License descriptions are provided for informational purposes only and should not be construed as legal advice.
   For legal guidance, please refer to official license documentation and consult with legal professionals specializing
   in software and dataset licensing.

.. note::

    When licensing datasets, it's recommended to use licenses specifically designed for data, rather than using
    software licenses such as MIT, Apache, or GPL.

"""

__all__ = [
    "DatasetLicense",
    "PUBLIC_DOMAIN",
    "CC_0",
    "CC_BY",
    "CC_BY_NC",
    "CC_BY_NC_ND",
    "CC_BY_NC_SA",
    "CC_BY_ND",
    "CC_BY_SA",
    "ODC_BY",
    "ODC_PDDL",
    "ODC_ODbL",
    "RESTRICTED",
]

from .dataset_license import DatasetLicense

PUBLIC_DOMAIN = DatasetLicense(
    name="Public Domain (No License)",
    identifier=None,
    description="Technically not a license, the public domain mark relinquishes all rights to a dataset and "
    "dedicates the dataset to the public domain.",
    license="https://creativecommons.org/public-domain/pdm/",
)
"""
`Public Domain <https://creativecommons.org/public-domain/pdm/>`_: Technically not a license, the public domain mark
relinquishes all rights to a dataset and dedicates the dataset to the public domain.
"""


CC_0 = DatasetLicense(
    name="Creative Commons Public Domain Dedication",
    identifier="CC0-1.0",
    description="A  Creative Commons license and is like a public domain dedication. The copyright holder "
    "surrenders rights in a dataset using this license.",
    license="https://creativecommons.org/publicdomain/zero/1.0/",
)
"""
`Creative Commons Public Domain Dedication <https://creativecommons.org/public-domain/pdm/>`_: A Creative Commons
license and is like a public domain dedication. The copyright holder surrenders rights in a dataset using this license.
"""


ODC_PDDL = DatasetLicense(
    name="Open Data Commons Public Domain Dedication and License",
    identifier="PDDL-1.0",
    description="This license is one of the Open Data Commons licenses and is like a public domain dedication. "
    "The copyright holder surrenders rights in a dataset using this license.",
    license="https://opendatacommons.org/licenses/pddl/",
)
"""
`Open Data Commons Public Domain Dedication and License <https://opendatacommons.org/licenses/pddl/>`_: This license
is one of the Open Data Commons licenses and is like a public domain dedication. The copyright holder surrenders rights
in a dataset using this license.
"""


CC_BY = DatasetLicense(
    name="Creative Commons Attribution 4.0 International",
    identifier="CC-BY-4.0",
    description="This license is one of the open Creative Commons licenses and allows users to share and adapt "
    "the dataset so long as they give credit to the copyright holder.",
    license="https://creativecommons.org/licenses/by/4.0/",
)
"""
`Creative Commons Attribution 4.0 International <https://creativecommons.org/licenses/by/4.0/>`_: This license is one
of the open Creative Commons licenses and allows users to share and adapt the dataset so long as they give credit to
the copyright holder.
"""


ODC_BY = DatasetLicense(
    name="Open Data Commons Attribution License",
    identifier="ODC-By-1.0",
    description="This license is one of the Open Data Commons licenses and allows users to share and adapt the "
    "dataset as long as they give credit to the copyright holder.",
    license="https://opendatacommons.org/licenses/by/",
)
"""
`Open Data Commons Attribution License <https://opendatacommons.org/licenses/by/>`_: This license is one of the Open
Data Commons licenses and allows users to share and adapt the dataset as long as they give credit to the copyright
holder.
"""


CC_BY_SA = DatasetLicense(
    name="Creative Commons Attribution-ShareAlike 4.0 International",
    identifier="CC-BY-SA-4.0",
    description="This license is one of the open Creative Commons licenses and allows users to share and adapt "
    "the dataset as long as they give credit to the copyright holder and distribute any additions, "
    "transformations or changes to the dataset under this same license.",
    license="https://creativecommons.org/licenses/by-sa/4.0/",
)
"""
`Creative Commons Attribution-ShareAlike 4.0 International <https://creativecommons.org/licenses/by-sa/4.0/>`_: This
license is one of the open Creative Commons licenses and allows users to share and adapt the dataset as long as they
give credit to the copyright holder and distribute any additions, transformations or changes to the dataset under
this same license.
"""


ODC_ODbL = DatasetLicense(
    name="Open Data Commons Open Database License",
    identifier="ODbL-1.0",
    description="This license is one of the Open Data Commons licenses and allows users to share and adapt the "
    "dataset as long as they give credit to the copyright holder and distribute any additions, "
    "transformation or changes to the dataset.",
    license="https://opendatacommons.org/licenses/odbl/",
)
"""
`Open Data Commons Open Database License <https://opendatacommons.org/licenses/odbl/>`_: This license is one of the
Open Data Commons licenses and allows users to share and adapt the dataset as long as they give credit to the copyright
holder and distribute any additions, transformation or changes to the dataset.
"""


CC_BY_NC = DatasetLicense(
    name="Creative Commons Attribution-NonCommercial 4.0 International",
    identifier="CC-BY-NC-4.0",
    description="This license is one of the Creative Commons licenses and allows users to share and adapt the "
    "dataset if they give credit to the copyright holder and do not use the dataset for any "
    "commercial purposes.",
    license="https://creativecommons.org/licenses/by-nc/4.0/",
)
"""
`Creative Commons Attribution-NonCommercial 4.0 International <https://creativecommons.org/licenses/by-nc/4.0/>`_: This
license is one of the Creative Commons licenses and allows users to share and adapt the dataset if they give credit to
the copyright holder and do not use the dataset for any commercial purposes.
"""


CC_BY_ND = DatasetLicense(
    name="Creative Commons Attribution-NoDerivatives 4.0 International",
    identifier="CC-BY-ND-4.0",
    description="This license is one of the Creative Commons licenses and allows users to share the dataset if "
    "they give credit to copyright holder, but they cannot make any additions, transformations or "
    "changes to the dataset under this license.",
    license="https://creativecommons.org/licenses/by-nd/4.0/",
)
"""
`Creative Commons Attribution-NoDerivatives 4.0 International <https://creativecommons.org/licenses/by-nd/4.0/>`_: This
license is one of the Creative Commons licenses and allows users to share the dataset if they give credit to copyright
holder, but they cannot make any additions, transformations or changes to the dataset under this license.
"""


CC_BY_NC_SA = DatasetLicense(
    name="Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International",
    identifier="CC-BY-NC-SA-4.0",
    description="This license is one of the Creative Commons licenses and allows users to share the dataset only "
    "if they (1) give credit to the copyright holder, (2) do not use the dataset for any commercial "
    "purposes, and (3) distribute any additions, transformations or changes to the dataset under this "
    "same license.",
    license="https://creativecommons.org/licenses/by-nc-sa/4.0/",
)
"""
`Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
<https://creativecommons.org/licenses/by-nc-sa/4.0/>`_: This license is one of the Creative Commons licenses and allows
users to share the dataset only if they (1) give credit to the copyright holder, (2) do not use the dataset for any
commercial purposes, and (3) distribute any additions, transformations or changes to the dataset under this same
license.
"""


CC_BY_NC_ND = DatasetLicense(
    name="Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International",
    identifier="CC-BY-NC-ND-4.0",
    description="This license is one of the Creative Commons licenses and allows users to use only your "
    "unmodified dataset if they give credit to the copyright holder and do not share it for "
    "commercial purposes. Users cannot make any additions, transformations or changes to the dataset"
    "under this license.",
    license="https://creativecommons.org/licenses/by-nc-nd/4.0/",
)
"""
`Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International
<https://creativecommons.org/licenses/by-nc-nd/4.0/>`_: This license is one of the Creative Commons licenses and allows
users to use only your unmodified dataset if they give credit to the copyright holder and do not share it for
commercial purposes. Users cannot make any additions, transformations or changes to the dataset under this license.
"""


RESTRICTED = DatasetLicense(
    name="Restricted (All Rights Reserved)",
    identifier="Restricted",
    description="All rights reserved. No permissions granted for use, modification, or distribution of the dataset.",
    license="Restricted (All Rights Reserved)",
)
"""
Restricted (All Rights Reserved): No permissions granted for use, modification, or distribution of the dataset.
"""
