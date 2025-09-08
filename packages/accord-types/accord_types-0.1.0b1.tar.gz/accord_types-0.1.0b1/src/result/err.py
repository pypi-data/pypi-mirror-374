from typing import Any, Generic, overload
from .interface import E, T, Result

class _Err(Result[Any, E], Generic[T, E]):
    """
    Represents a failed operation from a Result returning 
    function containing the value E.

    Success type is NoReturn because an Err cannot (and should not
    be forced to) contain a non-error type.
    """

    def __init__(self, error):
        self._error = error

    def __repr__(self):
        return f'Err({self._error!r})'

    def __eq__(self, o: object):
        if not isinstance(o, _Err):
            return False
        if isinstance(self._error, BaseException) and isinstance(o._error, BaseException):
            return self._error.args == o._error.args
        return self._error == o._error

    def __hash__(self):
        return hash(("Err", self._error))


    def is_ok(self):
        return False

    def is_err(self):
        return True

    def unwrap(self):
        raise self._error

    def expect(self, e):
        raise RuntimeError(f'{e}.\n{self._error!r}')

    def unwrap_err(self):
        return self._error

    def unwrap_or(self, fallback): 
        return fallback

    def map(self, f):
        return self
        
    def map_err(self, f):
        return _Err(f(self._error))

    def and_then(self, f):
        return self

    def or_else(self, f):
        return f(self._error)

@overload
def Err(error: E) -> Result[T, E]: ...
@overload
def Err(error: E) -> _Err[T, E]: ...

def Err(error: E):
    return _Err(error)


err_result: Result[int, str] = Err("test")
