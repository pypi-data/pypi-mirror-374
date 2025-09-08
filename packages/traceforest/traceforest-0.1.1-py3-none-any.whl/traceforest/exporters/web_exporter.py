import requests

from traceforest.exporters import Exporter
from traceforest.nodes import CallNode
from traceforest.constants import DEFAULT_WEB_EXPORTER_URL


class WebExporter(Exporter):
    adapter = None

    def __init__(self, repository_url=DEFAULT_WEB_EXPORTER_URL) -> None:
        self._repository_url = repository_url

    def _upload_profile(self, profile: dict):
        response = requests.post(self._repository_url, json=profile)
        print(response.json())

    def export(self, main_node: CallNode) -> None:
        profile = {
            "name": main_node.name,
            "time": main_node.time,
            "children": []
        }

        def add_node(node: CallNode, data: dict):
            for child in node.children.values():
                child_data = {
                    "name": child.name,
                    "time": child.time,
                    "children": []
                }
                add_node(child, child_data)
                data["children"].append(child_data)

        add_node(main_node, profile)

        self._upload_profile(profile)
