from typing import TypeVar, Generic, Union, Callable
from dataclasses import dataclass
from enum import Enum, auto

A = TypeVar('A')
B = TypeVar('B')
E = TypeVar('E')


class ErrorType(Enum):
    PARSE_ERROR = auto()
    FILE_ERROR = auto()
    TEST_ERROR = auto()
    PROFILE_ERROR = auto()
    GRAPH_ERROR = auto()
    VALIDATION_ERROR = auto()


@dataclass(frozen=True, slots=True)
class Success(Generic[A]):
    value: A


@dataclass(frozen=True, slots=True)
class Failure(Generic[E]):
    error: E
    context: str = ""


Result = Union[Success[A], Failure[E]]


def bind(
    result: Result[A, E],
    f: Callable[[A], Result[B, E]]
) -> Result[B, E]:
    match result:
        case Success(value):
            return f(value)
        case Failure(error, context):
            return Failure(error, context)


def map_result(
    result: Result[A, E],
    f: Callable[[A], B]
) -> Result[B, E]:
    match result:
        case Success(value):
            return Success(f(value))
        case Failure(error, context):
            return Failure(error, context)


def flatten(
    result: Result[Result[A, E], E]
) -> Result[A, E]:
    match result:
        case Success(inner):
            return inner
        case Failure(error, context):
            return Failure(error, context)


def sequence(
    results: list[Result[A, E]]
) -> Result[list[A], E]:
    accumulated = []
    for result in results:
        match result:
            case Success(value):
                accumulated.append(value)
            case Failure(error, context):
                return Failure(error, context)
    return Success(accumulated)


def traverse(
    items: list[A],
    f: Callable[[A], Result[B, E]]
) -> Result[list[B], E]:
    return sequence([f(item) for item in items])


def catch(
    result: Result[A, E],
    handler: Callable[[E, str], Result[A, E]]
) -> Result[A, E]:
    match result:
        case Success(value):
            return Success(value)
        case Failure(error, context):
            return handler(error, context)


def unwrap_or(
    result: Result[A, E],
    default: A
) -> A:
    match result:
        case Success(value):
            return value
        case Failure(_, _):
            return default


def is_success(result: Result[A, E]) -> bool:
    return isinstance(result, Success)


def is_failure(result: Result[A, E]) -> bool:
    return isinstance(result, Failure)


def get_error(result: Result[A, E]) -> tuple[E, str] | None:
    match result:
        case Failure(error, context):
            return (error, context)
        case _:
            return None
