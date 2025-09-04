"""Interface for Sample objects."""

from __future__ import annotations

from typing import Any, Generic, Protocol, TypeVar

from sqlalchemy.orm import object_session

from lightly_studio.models.sample import SampleTable

T = TypeVar("T")


class _HasInner(Protocol):
    _inner: Any


class DBField(Generic[T]):
    """Descriptor for a database-backed field.

    Provides interface to a SQLAlchemy model field. Setting the field
    immediately commits to the database. The owner class must implement
    the _inner attribute.
    """

    __slots__ = ("_sqla_descriptor",)
    """Store the SQLAlchemy descriptor for accessing the field."""

    def __init__(self, sqla_descriptor: T) -> None:
        """Initialize the DBField with a SQLAlchemy descriptor.

        Note: Mypy thinks that the descriptor has type T. In reality, during
        runtime, it will be InstrumentedAttribute[T].
        """
        self._sqla_descriptor = sqla_descriptor

    def __get__(self, obj: _HasInner | None, owner: type | None = None) -> T:
        """Get the value of the field from the database."""
        assert obj is not None, "DBField must be accessed via an instance, not the class"
        # Delegate to SQLAlchemy's descriptor.
        # Note: Mypy incorrectly thinks that the descriptor has type T. It complains
        # about the lack of a __get__ method.
        value: T = self._sqla_descriptor.__get__(obj._inner, type(obj._inner))  # type: ignore[attr-defined]  # noqa: SLF001
        return value

    def __set__(self, obj: _HasInner, value: T) -> None:
        """Set the value of the field in the database. Commits the session."""
        # Delegate to SQLAlchemy's descriptor.
        # Note: Mypy incorrectly thinks that the descriptor has type T. It complains
        # about the lack of a __set__ method.
        self._sqla_descriptor.__set__(obj._inner, value)  # type: ignore[attr-defined]  # noqa: SLF001
        sess = object_session(obj._inner)  # noqa: SLF001
        if sess is None:
            raise RuntimeError("No active session found for the DBField object")
        sess.commit()


class Sample:
    """Interface to a dataset sample."""

    file_name = DBField(SampleTable.file_name)
    width = DBField(SampleTable.width)
    height = DBField(SampleTable.height)
    dataset_id = DBField(SampleTable.dataset_id)
    file_path_abs = DBField(SampleTable.file_path_abs)

    sample_id = DBField(SampleTable.sample_id)
    created_at = DBField(SampleTable.created_at)
    updated_at = DBField(SampleTable.updated_at)

    def __init__(self, inner: SampleTable) -> None:
        """Initialize the Sample.

        Args:
            inner: The SampleTable SQLAlchemy model instance.
        """
        self._inner = inner
