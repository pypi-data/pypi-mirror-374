"""
This module defines the tools required to mark class attributes as abstract.

Credit to krassowski: https://stackoverflow.com/questions/23831510/abstract-attribute-not-property.
"""

from abc import ABCMeta


class DummyAttribute:
    pass


def abstract_attribute(obj=None):
    """
    A utility function used to mark class attributes (not properties, attributes) as abstract. Use with ABCMeta2.

    Usage example:
    .. code-block:: python

        class AbstractFoo(metaclass=ABCMeta2):
            bar = abstract_attribute()
    """
    if obj is None:
        obj = DummyAttribute()

    # Mark as abstract.
    obj.__is_abstract_attribute__ = True
    return obj


class ABCMeta2(ABCMeta):

    def __call__(cls, *args, **kwargs):
        # Create an instance of the base class and identify abstract attributes based on the presence of the
        #  __is_abstract_attribute__ attribute being set to True.
        instance = ABCMeta.__call__(cls, *args, **kwargs)
        abstract_attributes = {
            name for name in dir(instance) if getattr(getattr(instance, name), "__is_abstract_attribute__", False)
        }
        if abstract_attributes:
            raise NotImplementedError(
                "Cannot instantiate abstract class {} with missing attributes: {}".format(
                    cls.__name__, ", ".join(abstract_attributes)
                )
            )
        return instance
