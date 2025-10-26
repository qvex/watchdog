import pytest
from src.graph_builder import ASTGraphBuilder
from src.knowledge_graph_domain import NodeType, EdgeType
from src.effects import Success, Failure, is_success, is_failure


@pytest.fixture
def builder():
    return ASTGraphBuilder()


def test_build_from_code_simple_function(builder):
    code = """
def greet(name):
    print(f"Hello, {name}")
"""
    result = builder.build_from_code(code)

    assert is_success(result)
    graph = result.value
    assert len(graph.nodes) > 0

    func_nodes = [n for n in graph.nodes.values() if n.node_type == NodeType.FUNCTION]
    assert len(func_nodes) == 1
    assert func_nodes[0].name == "greet"


def test_build_from_code_with_class(builder):
    code = """
class MyClass:
    def method(self):
        pass
"""
    result = builder.build_from_code(code)

    assert is_success(result)
    graph = result.value

    class_nodes = [n for n in graph.nodes.values() if n.node_type == NodeType.CLASS]
    assert len(class_nodes) == 1
    assert class_nodes[0].name == "MyClass"


def test_build_from_code_with_loop(builder):
    code = """
for i in range(10):
    print(i)
"""
    result = builder.build_from_code(code)

    assert is_success(result)
    graph = result.value

    loop_nodes = [n for n in graph.nodes.values() if n.node_type == NodeType.LOOP]
    assert len(loop_nodes) == 1
    assert loop_nodes[0].name == "for"


def test_build_from_code_with_conditional(builder):
    code = """
if True:
    print("yes")
"""
    result = builder.build_from_code(code)

    assert is_success(result)
    graph = result.value

    cond_nodes = [n for n in graph.nodes.values() if n.node_type == NodeType.CONDITIONAL]
    assert len(cond_nodes) == 1


def test_build_from_code_with_import(builder):
    code = """
import os
from pathlib import Path
"""
    result = builder.build_from_code(code)

    assert is_success(result)
    graph = result.value

    import_nodes = [n for n in graph.nodes.values() if n.node_type == NodeType.IMPORT]
    assert len(import_nodes) == 2


def test_build_from_code_syntax_error(builder):
    code = """
def broken(
    print("missing closing paren")
"""
    result = builder.build_from_code(code)

    assert is_failure(result)


def test_build_from_code_empty(builder):
    code = ""
    result = builder.build_from_code(code)

    assert is_success(result)
    graph = result.value
    assert len(graph.nodes) == 0


def test_add_node(builder):
    from src.knowledge_graph_domain import CodeGraph, GraphNode

    graph = CodeGraph()
    node = GraphNode(
        id="test_1",
        node_type=NodeType.FUNCTION,
        name="test_func",
        line_number=1
    )

    new_graph = builder.add_node(graph, node)

    assert "test_1" in new_graph.nodes
    assert new_graph.nodes["test_1"].name == "test_func"


def test_add_edge(builder):
    from src.knowledge_graph_domain import CodeGraph, GraphEdge

    graph = CodeGraph()
    edge = GraphEdge(
        source_id="node_1",
        target_id="node_2",
        edge_type=EdgeType.CALLS
    )

    new_graph = builder.add_edge(graph, edge)

    assert edge in new_graph.edges


def test_process_function_with_args(builder):
    code = """
def add(a, b):
    return a + b
"""
    result = builder.build_from_code(code)

    assert is_success(result)
    graph = result.value

    func_nodes = [n for n in graph.nodes.values() if n.node_type == NodeType.FUNCTION]
    assert len(func_nodes) == 1
    assert "args" in func_nodes[0].metadata
    assert func_nodes[0].metadata["args"] == ["a", "b"]


def test_process_class_with_bases(builder):
    code = """
class Child(Parent):
    pass
"""
    result = builder.build_from_code(code)

    assert is_success(result)
    graph = result.value

    class_nodes = [n for n in graph.nodes.values() if n.node_type == NodeType.CLASS]
    assert len(class_nodes) == 1
    assert "bases" in class_nodes[0].metadata


def test_process_while_loop(builder):
    code = """
while True:
    break
"""
    result = builder.build_from_code(code)

    assert is_success(result)
    graph = result.value

    loop_nodes = [n for n in graph.nodes.values() if n.node_type == NodeType.LOOP]
    assert len(loop_nodes) == 1
    assert loop_nodes[0].metadata["type"] == "while"


def test_complex_code_structure(builder):
    code = """
import math

class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        result = 0
        for i in range(b):
            result = self.add(result, a)
        return result

def main():
    calc = Calculator()
    if calc.add(2, 3) == 5:
        print("correct")
"""
    result = builder.build_from_code(code)

    assert is_success(result)
    graph = result.value

    assert len(graph.nodes) > 5
    assert any(n.node_type == NodeType.CLASS for n in graph.nodes.values())
    assert any(n.node_type == NodeType.FUNCTION for n in graph.nodes.values())
    assert any(n.node_type == NodeType.LOOP for n in graph.nodes.values())
    assert any(n.node_type == NodeType.CONDITIONAL for n in graph.nodes.values())
    assert any(n.node_type == NodeType.IMPORT for n in graph.nodes.values())
