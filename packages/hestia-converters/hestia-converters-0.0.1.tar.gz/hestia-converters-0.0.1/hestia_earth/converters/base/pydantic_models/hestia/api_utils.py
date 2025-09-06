from functools import cache
from hestia_earth.utils.api import download_hestia as api_download_hestia

from . import Node

download_hestia = cache(api_download_hestia)


def update_hestia_node(node: Node) -> Node:
    downloaded_node_d = download_hestia(node.id, node_type=str(node.type))

    original_node_d = node.model_dump(by_alias=True, exclude_none=True)
    updated_node_d = downloaded_node_d | original_node_d | {"flow_metadata": node.flow_metadata}

    node_type = type(node)
    return node_type(**updated_node_d)
