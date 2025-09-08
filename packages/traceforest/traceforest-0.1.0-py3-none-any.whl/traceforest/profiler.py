import sys
import time

from traceforest.nodes import CallNode
from traceforest.exporters import Exporter, WebExporter


class Profiler:

    def __init__(self):
        self._started = False
        self._root = CallNode("root")
        self._call_stack = [self._root]
        self._all = {}

    def _profile(self, frame, event: str, arg):
        code = frame.f_code

        class_name = None

        if "self" in frame.f_locals:
            class_name = frame.f_locals["self"].__class__.__name__
            func_name = f"{class_name}.{code.co_name} ({code.co_filename}:{code.co_firstlineno})"
        else:
            func_name = f"{code.co_name} ({code.co_filename}:{code.co_firstlineno})"

        if event == "call":
            node: CallNode = self._call_stack[-1].get_child(func_name)
            node.start_time = time.perf_counter()
            self._call_stack.append(node)

        elif event == "return":
            if f"{class_name}.{code.co_name}" == "Profiler.start":
                return

            node: CallNode = self._call_stack.pop()
            if node.start_time is not None:
                node.time += time.perf_counter() - node.start_time

    def start(self):
        self._started = True
        sys.setprofile(self._profile)

        self._root.start_time = time.perf_counter()

    def stop(self):
        assert self._started, "The profiler has not been started yet, call the start method first"
        self._started = False

        sys.setprofile(None)

        self._root.time += time.perf_counter() - self._root.start_time

    def export(self, exporter: Exporter = WebExporter()) -> None:
        exporter.export(self._root)
