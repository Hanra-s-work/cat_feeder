""" 
# +==== BEGIN CatFeeder =================+
# LOGO: 
# ..............(..../\\
# ...............)..(.')
# ..............(../..)
# ...............\\(__)|
# Inspired by Joan Stark
# source https://www.asciiart.eu/
# animals/cats
# /STOP
# PROJECT: CatFeeder
# FILE: final_class.py
# CREATION DATE: 22-11-2025
# LAST Modified: 20:24:19 22-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The class in charge of reproducing the method `final` from cpp but for python.
# // AR
# +==== END CatFeeder =================+
"""


class FinalClass(type):
    """Final (non-subclassable) metaclass.

    Summary:
        When a class is declared with ``metaclass=FinalClass`` it becomes *final*:
        any attempt to subclass it will immediately raise ``TypeError`` at class
        creation time. This mimics the C++ ``final`` keyword semantics.

    How it works:
        During metaclass ``__init__`` we inspect each direct base. If one of the
        bases itself was created with ``FinalClass`` we reject the new class.

    Usage Example:
        >>> class Service(metaclass=FinalClass):
        ...     pass
        >>> # This will fail:
        ... class Derived(Service):  # doctest: +IGNORE_EXCEPTION_DETAIL
        ...     pass
        Traceback (most recent call last):
            TypeError: Class 'Service' is final and cannot be subclassed.

    Rationale:
        Preventing inheritance can guard invariants (e.g. security-sensitive
        logic, lifecycle guarantees) and simplify reasoning about extension
        points. Prefer composition or explicitly documented interfaces instead.

    Notes:
        - Only direct subclassing is blocked; mixins inheriting transitively
          still trigger the same check because the original base appears in
          ``bases``.
        - Does not prevent monkey-patching of attributes; Python cannot fully
          emulate C++ immutability semantics.
    """

    def __init__(cls, name, bases, namespace):
        for base in bases:
            if isinstance(base, FinalClass):
                raise TypeError(
                    f"Class '{base.__name__}' is final and cannot be subclassed."
                )
        super().__init__(name, bases, namespace)
