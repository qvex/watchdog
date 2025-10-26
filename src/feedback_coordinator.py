from dataclasses import dataclass
from typing import Optional
from src.code_analyzer import CodeContext
from src.knowledge_graph_domain import CodeGraph
from src.test_domain import RunResult
from src.proficiency_domain import StudentProfile
from src.effects import Result, Success, Failure, ErrorType, bind, map_result


@dataclass(frozen=True, slots=True)
class EnhancedContext:
    code_context: CodeContext
    knowledge_graph: Optional[CodeGraph]
    test_result: Optional[RunResult]
    student_profile: Optional[StudentProfile]


class FeedbackCoordinator:
    def __init__(
        self,
        graph_builder,
        test_runner,
        profile_calculator
    ):
        self.graph_builder = graph_builder
        self.test_runner = test_runner
        self.profile_calculator = profile_calculator

    def build_enhanced_context(
        self,
        code: str,
        code_context: CodeContext,
        profile: Optional[StudentProfile]
    ) -> Result[EnhancedContext, ErrorType]:
        graph_result = self.graph_builder.build_from_code(code)

        match graph_result:
            case Success(graph):
                return Success(EnhancedContext(
                    code_context=code_context,
                    knowledge_graph=graph,
                    test_result=None,
                    student_profile=profile
                ))
            case Failure(error, context):
                return Success(EnhancedContext(
                    code_context=code_context,
                    knowledge_graph=None,
                    test_result=None,
                    student_profile=profile
                ))

    def enrich_with_tests(
        self,
        context: EnhancedContext,
        test_file: str
    ) -> Result[EnhancedContext, ErrorType]:
        test_result = self.test_runner.run_tests(test_file)

        match test_result:
            case Success(result):
                return Success(self._add_test_result(context, result))
            case Failure(error, msg):
                return Success(context)

    def calculate_adaptive_hint_level(
        self,
        context: EnhancedContext,
        base_level: int
    ) -> int:
        if not context.student_profile:
            return base_level

        pattern_type = context.code_context.missing_element
        pattern_stats = context.student_profile.pattern_stats.get(pattern_type)

        if not pattern_stats:
            return base_level

        mastery = self.profile_calculator.get_pattern_mastery(pattern_stats)

        return self._adjust_for_mastery(base_level, mastery)

    def should_show_test_feedback(
        self,
        context: EnhancedContext
    ) -> bool:
        if not context.test_result:
            return False

        return context.test_result.failed > 0

    def _add_test_result(
        self,
        context: EnhancedContext,
        test_result: RunResult
    ) -> EnhancedContext:
        return EnhancedContext(
            code_context=context.code_context,
            knowledge_graph=context.knowledge_graph,
            test_result=test_result,
            student_profile=context.student_profile
        )

    def _adjust_for_mastery(
        self,
        base_level: int,
        mastery: int
    ) -> int:
        if mastery == 3:
            return max(1, base_level - 1)
        if mastery == 1:
            return min(4, base_level + 1)
        return base_level
