import ast
from dataclasses import replace
from src.knowledge_graph_domain import (
    GraphNode,
    GraphEdge,
    CodeGraph,
    NodeType,
    EdgeType
)
from src.effects import Result, Success, Failure, ErrorType


class ASTGraphBuilder:
    def __init__(self):
        self.node_counter = 0

    def build_from_code(
        self,
        code: str
    ) -> Result[CodeGraph, ErrorType]:
        parse_result = self._safe_parse(code)

        match parse_result:
            case Success(tree):
                graph = CodeGraph()
                return Success(self._build_graph(tree, graph))
            case Failure(error, context):
                return Failure(error, context)

    def add_node(
        self,
        graph: CodeGraph,
        node: GraphNode
    ) -> CodeGraph:
        new_nodes = dict(graph.nodes)
        new_nodes[node.id] = node
        return replace(graph, nodes=new_nodes)

    def add_edge(
        self,
        graph: CodeGraph,
        edge: GraphEdge
    ) -> CodeGraph:
        new_edges = set(graph.edges)
        new_edges.add(edge)
        return replace(graph, edges=new_edges)

    def _safe_parse(
        self,
        code: str
    ) -> Result[ast.Module, ErrorType]:
        try:
            tree = ast.parse(code)
            return Success(tree)
        except SyntaxError as e:
            return Failure(ErrorType.PARSE_ERROR, str(e))

    def _build_graph(
        self,
        tree: ast.Module,
        graph: CodeGraph
    ) -> CodeGraph:
        for node in ast.walk(tree):
            graph = self._process_node(node, graph)
        return graph

    def _process_node(
        self,
        node: ast.AST,
        graph: CodeGraph
    ) -> CodeGraph:
        match node:
            case ast.FunctionDef():
                return self._process_function(node, graph)
            case ast.ClassDef():
                return self._process_class(node, graph)
            case ast.For() | ast.While():
                return self._process_loop(node, graph)
            case ast.If():
                return self._process_conditional(node, graph)
            case ast.Import() | ast.ImportFrom():
                return self._process_import(node, graph)
            case _:
                return graph

    def _process_function(
        self,
        node: ast.FunctionDef,
        graph: CodeGraph
    ) -> CodeGraph:
        func_id = self._generate_id()
        func_node = GraphNode(
            id=func_id,
            node_type=NodeType.FUNCTION,
            name=node.name,
            line_number=node.lineno,
            metadata={'args': [arg.arg for arg in node.args.args]}
        )
        graph = self.add_node(graph, func_node)
        return self._process_function_calls(node, func_id, graph)

    def _process_class(
        self,
        node: ast.ClassDef,
        graph: CodeGraph
    ) -> CodeGraph:
        class_id = self._generate_id()
        class_node = GraphNode(
            id=class_id,
            node_type=NodeType.CLASS,
            name=node.name,
            line_number=node.lineno,
            metadata={'bases': [self._get_name(base) for base in node.bases]}
        )
        return self.add_node(graph, class_node)

    def _process_loop(
        self,
        node: ast.For | ast.While,
        graph: CodeGraph
    ) -> CodeGraph:
        loop_id = self._generate_id()
        loop_type = "for" if isinstance(node, ast.For) else "while"
        loop_node = GraphNode(
            id=loop_id,
            node_type=NodeType.LOOP,
            name=loop_type,
            line_number=node.lineno,
            metadata={'type': loop_type}
        )
        return self.add_node(graph, loop_node)

    def _process_conditional(
        self,
        node: ast.If,
        graph: CodeGraph
    ) -> CodeGraph:
        cond_id = self._generate_id()
        cond_node = GraphNode(
            id=cond_id,
            node_type=NodeType.CONDITIONAL,
            name="if",
            line_number=node.lineno,
            metadata={}
        )
        return self.add_node(graph, cond_node)

    def _process_import(
        self,
        node: ast.Import | ast.ImportFrom,
        graph: CodeGraph
    ) -> CodeGraph:
        import_id = self._generate_id()
        module_name = self._get_import_name(node)
        import_node = GraphNode(
            id=import_id,
            node_type=NodeType.IMPORT,
            name=module_name,
            line_number=node.lineno,
            metadata={}
        )
        return self.add_node(graph, import_node)

    def _process_function_calls(
        self,
        node: ast.FunctionDef,
        func_id: str,
        graph: CodeGraph
    ) -> CodeGraph:
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                graph = self._add_call_edge(child, func_id, graph)
        return graph

    def _add_call_edge(
        self,
        call: ast.Call,
        caller_id: str,
        graph: CodeGraph
    ) -> CodeGraph:
        callee_name = self._get_name(call.func)
        callee_node = self._find_node_by_name(graph, callee_name)

        if callee_node:
            edge = GraphEdge(
                source_id=caller_id,
                target_id=callee_node.id,
                edge_type=EdgeType.CALLS
            )
            return self.add_edge(graph, edge)
        return graph

    def _generate_id(self) -> str:
        self.node_counter += 1
        return f"node_{self.node_counter}"

    def _get_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return "unknown"

    def _get_import_name(
        self,
        node: ast.Import | ast.ImportFrom
    ) -> str:
        if isinstance(node, ast.Import):
            return node.names[0].name if node.names else "unknown"
        return node.module or "unknown"

    def _find_node_by_name(
        self,
        graph: CodeGraph,
        name: str
    ) -> GraphNode | None:
        for node in graph.nodes.values():
            if node.name == name:
                return node
        return None
