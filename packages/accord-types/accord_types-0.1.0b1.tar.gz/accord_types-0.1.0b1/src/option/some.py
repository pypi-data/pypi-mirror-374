from typing import Generic, cast
from .interface import T, Option

class Some(Option[T], Generic[T]):

    def __init__(self, value):
        self._value = value
    
    def __repr__(self):
        return f'Some({self._value!r})' if self._value is not None else 'None'

    def __eq__(self, o: object):
        if isinstance(o, Some):
            return self._value == o._value
        return False

    def __hash__(self):
        return hash(("Some", self._value))


    def is_some(self):
        return self._value is not None

    def is_none(self):
        return self._value is None

    def unwrap(self):
        if self._value is None:
            raise RuntimeError(f'Called unwrap in a None Option value: {self._value!r}')
        return self._value

    def expect(self, e):
        if self._value is None:
            raise RuntimeError(f'{e}.\n{self._value!r}')
        return self._value

    def unwrap_or(self, fallback):
        return fallback if self._value is None else self._value

    def map(self, f):
        return cast(Option[T], Some(f(self._value))) if self._value is not None else None

    def map_unchecked(self, f):
        return cast(Option[T], Some(f(self._value)))

    def and_then(self, f):
        return f(self._value)

    def take(self):
        v = self._value
        self._value = None
        return v
    