import pytest
from src.graph_query import SimpleGraphQuery
from src.knowledge_graph_domain import (
    CodeGraph,
    GraphNode,
    GraphEdge,
    NodeType,
    EdgeType
)


@pytest.fixture
def query_engine():
    return SimpleGraphQuery()


@pytest.fixture
def sample_graph():
    node1 = GraphNode(
        id="node_1",
        node_type=NodeType.FUNCTION,
        name="main",
        line_number=1
    )
    node2 = GraphNode(
        id="node_2",
        node_type=NodeType.FUNCTION,
        name="helper",
        line_number=5
    )
    node3 = GraphNode(
        id="node_3",
        node_type=NodeType.LOOP,
        name="for",
        line_number=10
    )

    edge1 = GraphEdge(
        source_id="node_1",
        target_id="node_2",
        edge_type=EdgeType.CALLS
    )
    edge2 = GraphEdge(
        source_id="node_1",
        target_id="node_3",
        edge_type=EdgeType.CONTAINS
    )

    return CodeGraph(
        nodes={"node_1": node1, "node_2": node2, "node_3": node3},
        edges={edge1, edge2}
    )


def test_get_node_exists(query_engine, sample_graph):
    node = query_engine.get_node(sample_graph, "node_1")
    assert node is not None
    assert node.name == "main"


def test_get_node_not_exists(query_engine, sample_graph):
    node = query_engine.get_node(sample_graph, "node_999")
    assert node is None


def test_get_neighbors(query_engine, sample_graph):
    neighbors = query_engine.get_neighbors(sample_graph, "node_1")
    assert len(neighbors) == 2
    neighbor_names = {n.name for n in neighbors}
    assert "helper" in neighbor_names
    assert "for" in neighbor_names


def test_get_neighbors_no_edges(query_engine, sample_graph):
    neighbors = query_engine.get_neighbors(sample_graph, "node_2")
    assert len(neighbors) == 0


def test_get_dependencies(query_engine):
    node1 = GraphNode(
        id="node_1",
        node_type=NodeType.FUNCTION,
        name="main",
        line_number=1
    )
    node2 = GraphNode(
        id="node_2",
        node_type=NodeType.IMPORT,
        name="math",
        line_number=0
    )

    edge = GraphEdge(
        source_id="node_1",
        target_id="node_2",
        edge_type=EdgeType.DEPENDS_ON
    )

    graph = CodeGraph(
        nodes={"node_1": node1, "node_2": node2},
        edges={edge}
    )

    deps = query_engine.get_dependencies(graph, "node_1")
    assert len(deps) == 1
    assert deps[0].name == "math"


def test_get_related_patterns_loops(query_engine, sample_graph):
    loops = query_engine.get_related_patterns(sample_graph, "loops")
    assert len(loops) == 1
    assert loops[0].node_type == NodeType.LOOP


def test_get_related_patterns_functions(query_engine, sample_graph):
    functions = query_engine.get_related_patterns(sample_graph, "functions")
    assert len(functions) == 2
    assert all(n.node_type == NodeType.FUNCTION for n in functions)


def test_get_related_patterns_unknown(query_engine, sample_graph):
    result = query_engine.get_related_patterns(sample_graph, "unknown_pattern")
    assert len(result) == 0


def test_get_function_calls(query_engine, sample_graph):
    calls = query_engine.get_function_calls(sample_graph, "node_1")
    assert len(calls) == 1
    assert calls[0].name == "helper"


def test_get_callers(query_engine, sample_graph):
    callers = query_engine.get_callers(sample_graph, "node_2")
    assert len(callers) == 1
    assert callers[0].name == "main"


def test_get_callers_no_callers(query_engine, sample_graph):
    callers = query_engine.get_callers(sample_graph, "node_1")
    assert len(callers) == 0


def test_empty_graph(query_engine):
    empty_graph = CodeGraph()

    assert query_engine.get_node(empty_graph, "node_1") is None
    assert query_engine.get_neighbors(empty_graph, "node_1") == []
    assert query_engine.get_dependencies(empty_graph, "node_1") == []
    assert query_engine.get_related_patterns(empty_graph, "functions") == []
