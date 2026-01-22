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
# FILE: runtime_manager.py
# CREATION DATE: 22-11-2025
# LAST Modified: 14:43:14 19-12-2025
# DESCRIPTION:
# This is the backend server in charge of making the actual website work.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Provide an ECS-like lookup dictionary with lazy singleton creation.
# // AR
# +==== END CatFeeder =================+
"""
from __future__ import annotations
from typing import Type, TypeVar, Dict, Any, Union, overload, Optional
import asyncio
import threading

from display_tty import Disp, initialise_logger

from .final_singleton_class import FinalSingleton

T = TypeVar("T")  # legacy / compatibility if external code refers
S = TypeVar("S")  # precise service type for overloads


class RuntimeManager:
    """Flexible runtime service container.

    Summary:
        Lazy, thread-safe instantiation and retrieval of service classes.
        Supports plain classes or ``FinalSingleton`` subclasses. First access
        may supply constructor args; later accesses ignore them.

    Raises:
        RuntimeError: Named lookup with no registration.
        TypeError: Constructor argument mismatch (propagated).
        Exception: Any user exception from constructor or ``async_init``.

    Notes:
        Failed constructions are not cached; later calls retry.
    """

    _instances: Dict[str, Any] = {}
    _classes: Dict[str, Type[Any]] = {}
    _thread_locks: Dict[str, threading.Lock] = {}

    _disp: Disp = initialise_logger(__qualname__, False)

    @classmethod
    def update_debug(cls, debug: bool = False) -> None:
        cls._disp.update_disp_debug(debug)

    # ------------------------------------------------------
    # SETTER
    # ------------------------------------------------------
    @classmethod
    def set(cls, service: Type[T], *args, **kwargs) -> None:
        """Register and construct eagerly.

        No-op if already present.
        Raises any exception from constructor / async_init.
        """
        key = service.__name__
        tlock = cls._thread_locks.setdefault(key, threading.Lock())

        with tlock:
            if key in cls._instances:
                # Already initialized
                return

            cls._classes[key] = service

            # Handle FinalSingleton enforcement
            if issubclass(service, FinalSingleton):
                setattr(service, "_allow_create", True)
                instance = service(*args, **kwargs)
                setattr(service, "_allow_create", False)
            else:
                instance = service(*args, **kwargs)

            # Async initializer
            async_init = getattr(instance, "async_init", None)
            if callable(async_init):
                maybe_coro = async_init()
                if asyncio.iscoroutine(maybe_coro):
                    asyncio.run(maybe_coro)

            cls._instances[key] = instance

    # ------------------------------------------------------
    # GETTER
    # ------------------------------------------------------
    @overload
    @classmethod
    def get(cls, service: Type[S], *args,
            auto_register: bool = False, **kwargs) -> S: ...

    @overload
    @classmethod
    def get(cls, service: str, *args,
            auto_register: bool = False, **kwargs) -> Any: ...

    @classmethod
    def get(cls, service: Union[str, Type[S]], *args, auto_register: bool = False, **kwargs) -> Any:
        """Retrieve (and lazily initialize) a service instance.

        Overloads:
            - ``get(Type[Service]) -> Service``
            - ``get("ServiceName") -> Any`` (returns registered instance when the concrete type is not statically known)

        First call may pass constructor args/kwargs; they are ignored on later calls.
        Async initialization via optional ``async_init`` coroutine is supported.

        Args:
            service: Class type or string name of the service.
            *args: Constructor arguments for first initialization.
            auto_register: If True, automatically register unregistered classes. If False, raise RuntimeError. Defaults to True.
            **kwargs: Constructor keyword arguments for first initialization.

        Raises
            RuntimeError if named lookup missing or auto_register=False with unregistered class; propagates constructor / async_init exceptions.
        """
        if isinstance(service, str):
            key = service
            klass = cls._classes.get(key)
            if klass is None:
                raise RuntimeError(
                    f"Class {key} not registered in RuntimeManager."
                )
        else:
            key = service.__name__
            klass = service
            if key not in cls._classes:
                if not auto_register:
                    raise RuntimeError(
                        f"Class {key} not registered in RuntimeManager. Use set() first or pass auto_register=True."
                    )
                cls._classes[key] = klass

        existing = cls._instances.get(key)
        if existing is not None:
            return existing

        tlock = cls._thread_locks.setdefault(key, threading.Lock())
        with tlock:
            existing = cls._instances.get(key)
            if existing is not None:
                return existing

            # FinalSingleton enforcement
            if issubclass(klass, FinalSingleton):
                setattr(klass, "_allow_create", True)
                instance = klass(*args, **kwargs)
                setattr(klass, "_allow_create", False)
            else:
                instance = klass(*args, **kwargs)

            async_init = getattr(instance, "async_init", None)
            if callable(async_init):
                maybe_coro = async_init()
                if asyncio.iscoroutine(maybe_coro):
                    asyncio.run(maybe_coro)

            cls._instances[key] = instance
            return instance

    # ------------------------------------------------------
    # GET IF EXISTS
    # ------------------------------------------------------

    @overload
    @classmethod
    def get_if_exists(cls, service: Type[S],
                      target: Optional[object] = None) -> Optional[S]: ...

    @overload
    @classmethod
    def get_if_exists(cls, service: str,
                      target: Optional[object] = None) -> Optional[Any]: ...

    @classmethod
    def get_if_exists(cls, service: Union[str, Type[S]], target: Optional[object] = None) -> Optional[Any]:
        class_name = getattr(service, "__qualname__", None) or getattr(
            service, "__name__", "")
        cls._disp.log_debug(f"Attempting to retrieve the {class_name} class")
        if target:
            cls._disp.log_debug(
                f"{class_name} class exists and is stored in class, returning"
            )
            return target
        if cls.exists(service):
            cls._disp.log_debug(f"{class_name} class exists, retrieving")
            return cls.get(service)

        cls._disp.log_debug(
            f"{class_name} class does not exist, returning None"
        )
        return None

    # ------------------------------------------------------
    # CHECK IF INITIALIZED
    # ------------------------------------------------------

    @classmethod
    def exists(cls, service: Union[str, Type[T]]) -> bool:
        """Return True if service instance is already initialized."""
        if isinstance(service, str):
            key = service
        else:
            if hasattr(service, "__name__"):
                key = service.__name__
            elif hasattr(service, "__qualname__"):
                key = service.__qualname__
            else:
                return False
        return key in cls._instances


# Singleton instance to make sure a shared instance exists
RI: RuntimeManager = RuntimeManager()
