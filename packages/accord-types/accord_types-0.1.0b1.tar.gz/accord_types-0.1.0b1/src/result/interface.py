from typing import Generic, TypeVar, Callable
from abc import abstractmethod

from ..meta import SealedAccord

T = TypeVar('T')
U = TypeVar('U')

E = TypeVar('E')
F = TypeVar('F')

class Result(Generic[T, E], metaclass=SealedAccord):
    """
    Abstract class for Result.

    Wraps the result of an operation, containing either an Ok object
    for success, or an Err object for failure.

    This class will not contain the mentioned classes as the Result 
    enum does in Rust, rather it will define the interface that
    both Ok and Err must implement.
    """

    @abstractmethod
    def is_ok(self) -> bool:
        """Returns True if the result is Ok"""
        pass

    @abstractmethod
    def is_err(self) -> bool:
        """Returns True if the result is Err"""
        pass

    @abstractmethod
    def unwrap(self) -> T:
        """
        Unwraps the Result, yielding the content of its Ok class.
        If called on a Result containing Err, it will raise the containing
        error on the Err class.
        """
        pass

    @abstractmethod
    def expect(self, e: str) -> T:
        """
        Unwraps the Result, yielding the content of its Ok class.
        If called on a Result containing Err, it will raise a RuntimeError
        with a custom message and the representation of the Err.
        """
        pass

    @abstractmethod
    def unwrap_err(self) -> E:
        """
        Unwraps the Result, yielding the content of its Err class.
        If called on a Result containing Ok, it will raise a RuntimeError
        """
        pass

    @abstractmethod
    def unwrap_or(self, fallback: T) -> T:
        """
        Yields the contained value of an Ok, or the provided fallback
        of the same type
        """
        pass

    @abstractmethod
    def map(self, f: Callable[[T], U]) -> "Result[U, E]":
        """
        Maps a Result[T, E] into Result[U, E] by applying a function to an
        Ok contained value.
        """
        pass

    @abstractmethod
    def map_err(self, f: Callable[[E], F]) -> "Result[T, F]":
        """
        Maps a Result[T, E] into Result[T, F] by applying a function to an
        Err contained value.
        """
        pass

    @abstractmethod
    def and_then(self, f: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        """
        Makes a call to the Callable parameter if the Result contains an Ok
        Otherwise returns the Err contained value.
        """
        pass

    @abstractmethod
    def or_else(self, f: Callable[[E], "Result[T, F]"]) -> "Result[U, E]":
        """
        Makes a call to the Callable parameter if the Result contains an Err
        Otherwise returns the Ok contained value.
        """
        pass
    
    #TODO: Implement ok(), err(), is_ok_and(), is_err_and(), map_or(), unwrap_unchecked(), unwrap_err_unchecked()

