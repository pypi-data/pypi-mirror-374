from typing import Generic, TypeVar, Callable
from abc import abstractmethod

from ..meta import SealedAccord

T = TypeVar('T')
U = TypeVar('U')

class Option(Generic[T], metaclass=SealedAccord):

    @abstractmethod
    def is_some(self) -> bool:
        """Returns True if the Option is Some"""
        pass

    @abstractmethod
    def is_none(self) -> bool:
        """Returns True if the Option is None"""
        pass

    @abstractmethod
    def unwrap(self) -> T:
        """
        Unwraps the Option, yielding the content of its Some class.
        If called on a Result containing None, it will raise a RuntimeError.
        """
        pass

    @abstractmethod
    def expect(self, e: str) -> T:
        """
        Unwraps the Option, yielding the content of its Some class.
        If called on a Result containing None, it will raise a RuntimeError
        with a custom message.
        """
        pass


    @abstractmethod
    def unwrap_or(self, fallback: T) -> T:
        """
        Yields the contained value of an Some, or the provided fallback
        of the same type if None
        """
        pass

    @abstractmethod
    def map(self, f: Callable[[T], U]) -> "Option[U]":
        """
        Maps an Option[T] into Option[U] by applying a function to a
        Some contained value. Returns None skipping the Callable if the
        value is None.
        """
        pass

    @abstractmethod
    def map_unchecked(self, f: Callable[[T], U]) -> "Option[U]":
        """
        Maps an Option[T] into Option[U] by applying a function to an
        Option without checking if its value is None. Can raise exceptions 
        if the Callable can not handle an operation with None.
        """
        pass

    @abstractmethod
    def and_then(self, f: Callable[[T], "Option[U]"]) -> "Option[U]":
        """
        Makes a call to the Callable parameter if the Option contains a Some
        Otherwise returns None
        """
        pass

    @abstractmethod
    def take(self) -> T:
        """Takes the value out of the Option, leaving a None in its place"""
        pass


