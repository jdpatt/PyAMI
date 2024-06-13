from _typeshed import Incomplete
from traits.api import HasTraits

DBG: bool

class Component(HasTraits):
    def __init__(self, subDict): ...
    def __call__(self) -> None: ...
    def default_traits_view(self): ...
    @property
    def pin(self): ...
    @property
    def pins(self): ...

class Model(HasTraits):
    plot_iv: Incomplete
    def __init__(self, subDict): ...
    def __call__(self) -> None: ...
    def default_traits_view(self): ...
    @property
    def zout(self): ...
    @property
    def slew(self): ...
    @property
    def zin(self): ...
    @property
    def ccomp(self): ...
    @property
    def mtype(self): ...