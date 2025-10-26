import pytest
from src.effects import (
    Success,
    Failure,
    ErrorType,
    bind,
    map_result,
    flatten,
    sequence,
    traverse,
    catch,
    unwrap_or,
    is_success,
    is_failure,
    get_error
)


def test_success_creation():
    result = Success(42)
    assert result.value == 42


def test_failure_creation():
    result = Failure(ErrorType.PARSE_ERROR, "test error")
    assert result.error == ErrorType.PARSE_ERROR
    assert result.context == "test error"


def test_bind_with_success():
    result = Success(5)
    bound = bind(result, lambda x: Success(x * 2))
    assert isinstance(bound, Success)
    assert bound.value == 10


def test_bind_with_failure():
    result = Failure(ErrorType.FILE_ERROR, "error")
    bound = bind(result, lambda x: Success(x * 2))
    assert isinstance(bound, Failure)
    assert bound.error == ErrorType.FILE_ERROR


def test_map_result_with_success():
    result = Success(5)
    mapped = map_result(result, lambda x: x * 2)
    assert isinstance(mapped, Success)
    assert mapped.value == 10


def test_map_result_with_failure():
    result = Failure(ErrorType.TEST_ERROR, "error")
    mapped = map_result(result, lambda x: x * 2)
    assert isinstance(mapped, Failure)


def test_flatten_with_success():
    inner = Success(42)
    outer = Success(inner)
    flattened = flatten(outer)
    assert isinstance(flattened, Success)
    assert flattened.value == 42


def test_flatten_with_failure():
    result = Failure(ErrorType.GRAPH_ERROR, "error")
    flattened = flatten(result)
    assert isinstance(flattened, Failure)


def test_sequence_all_success():
    results = [Success(1), Success(2), Success(3)]
    sequenced = sequence(results)
    assert isinstance(sequenced, Success)
    assert sequenced.value == [1, 2, 3]


def test_sequence_with_failure():
    results = [Success(1), Failure(ErrorType.PARSE_ERROR, "err"), Success(3)]
    sequenced = sequence(results)
    assert isinstance(sequenced, Failure)
    assert sequenced.error == ErrorType.PARSE_ERROR


def test_traverse_all_success():
    items = [1, 2, 3]
    result = traverse(items, lambda x: Success(x * 2))
    assert isinstance(result, Success)
    assert result.value == [2, 4, 6]


def test_traverse_with_failure():
    items = [1, 2, 3]

    def f(x):
        if x == 2:
            return Failure(ErrorType.VALIDATION_ERROR, "invalid")
        return Success(x * 2)

    result = traverse(items, f)
    assert isinstance(result, Failure)


def test_catch_with_success():
    result = Success(42)
    caught = catch(result, lambda e, c: Success(0))
    assert isinstance(caught, Success)
    assert caught.value == 42


def test_catch_with_failure():
    result = Failure(ErrorType.FILE_ERROR, "error")
    caught = catch(result, lambda e, c: Success(0))
    assert isinstance(caught, Success)
    assert caught.value == 0


def test_unwrap_or_with_success():
    result = Success(42)
    value = unwrap_or(result, 0)
    assert value == 42


def test_unwrap_or_with_failure():
    result = Failure(ErrorType.TEST_ERROR, "error")
    value = unwrap_or(result, 0)
    assert value == 0


def test_is_success_true():
    result = Success(42)
    assert is_success(result)


def test_is_success_false():
    result = Failure(ErrorType.PARSE_ERROR, "error")
    assert not is_success(result)


def test_is_failure_true():
    result = Failure(ErrorType.FILE_ERROR, "error")
    assert is_failure(result)


def test_is_failure_false():
    result = Success(42)
    assert not is_failure(result)


def test_get_error_with_failure():
    result = Failure(ErrorType.GRAPH_ERROR, "test context")
    error = get_error(result)
    assert error is not None
    assert error[0] == ErrorType.GRAPH_ERROR
    assert error[1] == "test context"


def test_get_error_with_success():
    result = Success(42)
    error = get_error(result)
    assert error is None
