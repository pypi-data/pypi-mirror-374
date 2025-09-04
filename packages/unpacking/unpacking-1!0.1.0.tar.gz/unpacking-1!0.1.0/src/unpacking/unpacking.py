from collections.abc import Callable, Iterable, Mapping
from functools import partial as prt
from inspect import signature
from itertools import islice
from operator import contains

from cytoolz import keyfilter  # from toolz import keyfilter  # type: ignore[import]
from plum import dispatch


@dispatch
def apply_packed[T](fnct: Callable[..., T], itrb: Iterable) -> T:  # type: ignore[return]
    return fnct(*itrb)


@dispatch
def apply_packed[T](fnct: Callable[..., T], assctbl: Mapping) -> T:
    return fnct(**assctbl)


@dispatch
def apply_packed_part[T](fnct: Callable[..., T], itrb: Iterable) -> T:  # type: ignore[return]
    return fnct(*islice(itrb, len(signature(fnct).parameters)))


@dispatch
def apply_packed_part[T](fnct: Callable[..., T], assctbl: Mapping) -> T:
    return fnct(**keyfilter(prt(contains, signature(fnct).parameters.keys()), assctbl))


class starred[T]:
    def __init__(self, fnct: Callable[..., T]):
        self.fnct = fnct

    def __call__(self, itrb: Iterable) -> T:
        return self.fnct(*itrb)


class doublestarred[T]:
    def __init__(self, fnct: Callable[..., T]):
        self.fnct = fnct

    def __call__(self, assctbl: Mapping) -> T:
        return self.fnct(**assctbl)


class unpacking[T]:
    def __init__(self, fnct: Callable[..., T]):
        self.fnct = fnct

    def __call__(self, x: Iterable | Mapping) -> T:
        return apply_packed(self.fnct, x)  # type: ignore[return]


class starredpart[T]:
    def __init__(self, fnct: Callable[..., T]):
        self.fnct = fnct

    def __call__(self, itrb: Iterable) -> T:
        return self.fnct(*islice(itrb, len(signature(self.fnct).parameters)))


class doublestarredpart[T]:
    def __init__(self, fnct: Callable[..., T]):
        self.fnct = fnct

    def __call__(self, assctbl: Mapping) -> T:
        return self.fnct(
            **keyfilter(prt(contains, signature(self.fnct).parameters.keys()), assctbl)
        )


class unpackingpart[T]:
    def __init__(self, fnct: Callable[..., T]):
        self.fnct = fnct

    def __call__(self, x: Iterable | Mapping) -> T:
        return apply_packed_part(self.fnct, x)


if __name__ == "__main__":

    from concurrent.futures import ProcessPoolExecutor

    def test_fnct_add(x: int, y: int) -> int:
        added = x + y
        print(f"{x} added to {y} produces {added}")
        return added

    data_args = [1, 2]
    data_kwargs = {"x": 1, "y": 2}

    assert starred(test_fnct_add)(data_args) == 3
    assert doublestarred(test_fnct_add)(data_kwargs) == 3
    assert unpacking(test_fnct_add)(data_args) == 3
    assert unpacking(test_fnct_add)(data_kwargs) == 3

    data_args_m = [[1, 2], [3, 4]]
    data_kwargs_m = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
    with ProcessPoolExecutor(2) as executor:
        result_args = tuple(executor.map(unpacking(test_fnct_add), data_args_m))
        assert result_args == (3, 7)
        result_kwargs = tuple(executor.map(unpacking(test_fnct_add), data_kwargs_m))
        assert result_kwargs == (3, 7)

    data_args_excess = [1, 2, 3]
    data_kwargs_excess = {"x": 1, "y": 2, "z": 3}
    assert apply_packed_part(test_fnct_add, data_args_excess) == 3
    assert apply_packed_part(test_fnct_add, data_kwargs_excess) == 3

    assert starredpart(test_fnct_add)(data_args_excess) == 3
    assert doublestarredpart(test_fnct_add)(data_kwargs_excess) == 3

    data_args_excess_m = [[1, 2, 3], [3, 4, 5]]
    data_kwargs_excess_m = [{"x": 1, "y": 2, "z": 3}, {"x": 3, "y": 4, "z": 5}]
    with ProcessPoolExecutor(2) as executor:
        result_args = tuple(executor.map(unpackingpart(test_fnct_add), data_args_excess_m))
        assert result_args == (3, 7)
        result_kwargs = tuple(executor.map(unpackingpart(test_fnct_add), data_kwargs_excess_m))
        assert result_kwargs == (3, 7)
