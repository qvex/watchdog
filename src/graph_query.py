from typing import List
from src.knowledge_graph_domain import (
    GraphNode,
    CodeGraph,
    EdgeType,
    NodeType
)


class SimpleGraphQuery:
    def get_node(
        self,
        graph: CodeGraph,
        node_id: str
    ) -> GraphNode | None:
        return graph.nodes.get(node_id)

    def get_neighbors(
        self,
        graph: CodeGraph,
        node_id: str
    ) -> List[GraphNode]:
        neighbor_ids = [
            edge.target_id
            for edge in graph.edges
            if edge.source_id == node_id
        ]
        return [
            graph.nodes[nid]
            for nid in neighbor_ids
            if nid in graph.nodes
        ]

    def get_dependencies(
        self,
        graph: CodeGraph,
        node_id: str
    ) -> List[GraphNode]:
        dep_ids = [
            edge.target_id
            for edge in graph.edges
            if edge.source_id == node_id and edge.edge_type == EdgeType.DEPENDS_ON
        ]
        return [
            graph.nodes[did]
            for did in dep_ids
            if did in graph.nodes
        ]

    def get_related_patterns(
        self,
        graph: CodeGraph,
        pattern_type: str
    ) -> List[GraphNode]:
        node_type_map = {
            'loops': NodeType.LOOP,
            'functions': NodeType.FUNCTION,
            'conditionals': NodeType.CONDITIONAL,
            'classes': NodeType.CLASS
        }

        target_type = node_type_map.get(pattern_type)
        if not target_type:
            return []

        return [
            node
            for node in graph.nodes.values()
            if node.node_type == target_type
        ]

    def get_function_calls(
        self,
        graph: CodeGraph,
        function_id: str
    ) -> List[GraphNode]:
        call_ids = [
            edge.target_id
            for edge in graph.edges
            if edge.source_id == function_id and edge.edge_type == EdgeType.CALLS
        ]
        return [
            graph.nodes[cid]
            for cid in call_ids
            if cid in graph.nodes
        ]

    def get_callers(
        self,
        graph: CodeGraph,
        function_id: str
    ) -> List[GraphNode]:
        caller_ids = [
            edge.source_id
            for edge in graph.edges
            if edge.target_id == function_id and edge.edge_type == EdgeType.CALLS
        ]
        return [
            graph.nodes[cid]
            for cid in caller_ids
            if cid in graph.nodes
        ]
