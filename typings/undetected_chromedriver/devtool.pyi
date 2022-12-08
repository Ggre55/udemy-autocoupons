"""
This type stub file was generated by pyright.
"""

from typing import Any, Callable, Optional

class Structure(dict):
    """
    This is a dict-like object structure, which you should subclass
    Only properties defined in the class context are used on initialization.

    See example
    """
    _store = ...
    def __init__(self, *a, **kw) -> None:
        """
        Instantiate a new instance.

        :param a:
        :param kw:
        """
        ...
    
    def __getattr__(self, item): # -> Any:
        ...
    
    def __getitem__(self, item):
        ...
    
    def __setattr__(self, key, value): # -> None:
        ...
    
    def __setitem__(self, key, value): # -> None:
        ...
    
    def update(self, *a, **kw): # -> None:
        ...
    
    def __eq__(self, other) -> bool:
        ...
    
    def __hash__(self) -> int:
        ...
    
    @classmethod
    def __init_subclass__(cls, **kwargs): # -> None:
        ...
    


def timeout(seconds=..., on_timeout: Optional[Callable[[callable], Any]] = ...): # -> (func: Unknown) -> ((*args: Unknown, **kwargs: Unknown) -> Unknown):
    ...

def test(): # -> None:
    ...

