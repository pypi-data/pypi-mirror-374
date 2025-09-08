from .interface import Result
from .err import Err, _Err
from .ok import Ok

Result = Result.seal(Ok, _Err)

__all__ = ["Result", "Ok", "Err"]