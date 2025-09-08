from .exporter import Exporter
from traceforest.nodes import CallNode


class ShellExporter(Exporter):
    adapter = None

    def export(self, main_node: CallNode) -> None:
        def print_tree(node: CallNode, indent: int = 0) -> None:
            if node.time > 0:
                print(" " * indent + f"{node.name}: {node.time:.4f}s")
            for child in node.children.values():
                print_tree(child, indent + 2)

        print_tree(main_node)
