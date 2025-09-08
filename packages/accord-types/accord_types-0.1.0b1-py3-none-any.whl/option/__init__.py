from .interface import Option
from .some import Some

Option = Option.seal(Some)

__all__ = ["Option", "Some"]