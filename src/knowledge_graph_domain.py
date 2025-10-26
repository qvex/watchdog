from typing import Protocol, Set, List
from dataclasses import dataclass, field
from enum import Enum, auto
from src.effects import Result, ErrorType


class NodeType(Enum):
    FUNCTION = auto()
    VARIABLE = auto()
    CLASS = auto()
    IMPORT = auto()
    MODULE = auto()
    LOOP = auto()
    CONDITIONAL = auto()


class EdgeType(Enum):
    CALLS = auto()
    USES = auto()
    DEFINES = auto()
    IMPORTS_FROM = auto()
    CONTAINS = auto()
    DEPENDS_ON = auto()


@dataclass(frozen=True, slots=True)
class GraphNode:
    id: str
    node_type: NodeType
    name: str
    line_number: int
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GraphEdge:
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0


@dataclass(frozen=True, slots=True)
class CodeGraph:
    nodes: dict[str, GraphNode] = field(default_factory=dict)
    edges: Set[GraphEdge] = field(default_factory=set)


class GraphBuilder(Protocol):
    def build_from_code(
        self,
        code: str
    ) -> Result[CodeGraph, ErrorType]:
        ...

    def add_node(
        self,
        graph: CodeGraph,
        node: GraphNode
    ) -> CodeGraph:
        ...

    def add_edge(
        self,
        graph: CodeGraph,
        edge: GraphEdge
    ) -> CodeGraph:
        ...


class GraphQuery(Protocol):
    def get_node(
        self,
        graph: CodeGraph,
        node_id: str
    ) -> GraphNode | None:
        ...

    def get_neighbors(
        self,
        graph: CodeGraph,
        node_id: str
    ) -> List[GraphNode]:
        ...

    def get_dependencies(
        self,
        graph: CodeGraph,
        node_id: str
    ) -> List[GraphNode]:
        ...

    def get_related_patterns(
        self,
        graph: CodeGraph,
        pattern_type: str
    ) -> List[GraphNode]:
        ...
