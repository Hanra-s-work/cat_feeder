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
# FILE: final_singleton_class.py
# CREATION DATE: 22-11-2025
# LAST Modified: 20:25:10 22-11-2025
# DESCRIPTION: 
# This is the project in charge of making the connected cat feeder project work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: The file containing the class in charge of acting as a shared instance that cannot contain other instanciated versions of the inheritor class.
# // AR
# +==== END CatFeeder =================+
"""

from __future__ import annotations

import threading
from typing import TypeVar, Self

T = TypeVar("T", bound="FinalSingleton")


class FinalSingleton:
    """Protected-construction singleton base class.

    Summary:
        Subclass this to create a lazily-instantiated singleton whose *only*
        instance must be created by a coordinating manager (e.g. ``RuntimeManager``).
        Direct calls like ``MyService()`` raise ``RuntimeError``. This separates
        lifecycle control from business logic while avoiding accidental multiple
        instantiations under concurrency.

    Construction Guard:
        ``__new__`` checks the class-level flag ``_allow_create`` which the
        manager toggles briefly. If the flag is not set, construction is refused.
        This is lighter than a metaclass approach and keeps normal inheritance
        semantics intact for subclasses.

    Thread Safety:
        A per-class ``_creation_lock`` is provided for managers wishing to guard
        creation paths. The base itself does not acquire the lock; coordination
        logic belongs in the manager to avoid hidden blocking inside ``__new__``.

    Async Initialization:
        Subclasses may define an ``async_init`` coroutine method. A manager can
        detect and ``await`` it after creating the instance to perform async
        setup (e.g. opening connections) without requiring an async ``__init__``.

    Usage Example:
        >>> class Config(FinalSingleton):
        ...     def __init__(self):
        ...         self.value = 42
        >>> # WRONG (direct):
        ... Config()  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            RuntimeError: Config must be instantiated through RuntimeManager.get()
        >>> # Manager (pseudo-code):
        ... # RuntimeManager.get(Config) -> returns single instance

    Design Notes:
        - Keeps public API simple: subclass + retrieve via manager.
        - Avoids global variables; instance access is centralized.
        - Supports both sync and async init flows without coupling to event loop.

    Limitations:
        - Does not prevent manual flag flipping or reflection abuse; treat this
          as a cooperative contract, not a security boundary.
        - State reset/replacement must be explicitly handled by the manager if
          ever required (e.g. test isolation).
    """

    # per-class lock to ensure only one instance is created, even under concurrency
    _creation_lock = threading.Lock()

    # flag preventing user-constructed instances
    _allow_create: bool = False

    def __new__(cls: type[Self], *_args, **_kwargs) -> Self:
        if not cls._allow_create:
            raise RuntimeError(
                f"{cls.__name__} must be instantiated through RuntimeManager.get()"
            )
        return super().__new__(cls)
