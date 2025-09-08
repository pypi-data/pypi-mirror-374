from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from traceforest.nodes import CallNode


class Exporter(metaclass=ABCMeta):

    @property
    @abstractmethod
    def adapter(self):
        pass

    @abstractmethod
    def export(self, main_node: "CallNode") -> None:
        pass
