from typing import Generic, NoReturn
from .interface import E, T, Result

class Ok(Result[T, E], Generic[T, E]):
    """
    Represents a successful operation from a Result returning 
    function containing the value T.

    Error type is NoReturn because an Ok cannot (and should not
    be forced to) contain an error.
    """

    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return f'Ok({self._value!r})'

    def __eq__(self, o: object):
        if isinstance(o, Ok):
            return self._value == o._value
        return False
    
    def __hash__(self):
        return hash(("Ok", self._value))


    def is_ok(self):
        return True

    def is_err(self):
        return False

    def unwrap(self):
        return self._value

    def expect(self, _):
        return self._value

    def unwrap_err(self) -> NoReturn:
        raise RuntimeError(f'Called unwrap_err on an Ok value: {self._value!r}')

    def unwrap_or(self, _): 
        return self._value

    def map(self, f):
        return Ok(f(self._value))
        
    def map_err(self, _):
        return self

    def and_then(self, f):
        return f(self._value)

    def or_else(self, _):
        return self