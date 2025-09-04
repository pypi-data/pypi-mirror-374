from collections.abc import Callable, Iterable, Mapping
from functools import partial as prt
from inspect import signature
from itertools import islice
from operator import contains
from typing import Any

from cytoolz import keyfilter  # type: ignore[import]
from plum import dispatch, overload

# the module uses plum's mypy integration (https://beartype.github.io/plum/integration.html)


class starred[T]:
    def __init__(self, fnct: Callable[..., T]):
        self.fnct = fnct

    def __call__(self, x: Iterable[Any]) -> T:
        return self.fnct(*x)


class doublestarred[T]:
    def __init__(self, fnct: Callable[..., T]):
        self.fnct = fnct

    def __call__(self, x: Mapping[str, Any]) -> T:
        return self.fnct(**x)


@overload
def apply_packed[T](fnct: Callable[..., T], x: Iterable[Any]) -> T:
    return fnct(*x)


@overload
def apply_packed[T](fnct: Callable[..., T], x: Mapping[str, Any]) -> T:
    return fnct(**x)


@dispatch
def apply_packed[T](fnct: Callable[..., T], x: Iterable[Any] | Mapping[str, Any]) -> T:  # type: ignore[empty-body]
    pass


class unpacking[T]:
    def __init__(self, fnct: Callable[..., T]):
        self.fnct = fnct

    def __call__(self, x: Iterable[Any] | Mapping[str, Any]) -> T:
        return apply_packed(self.fnct, x)


class starredpart[T]:
    def __init__(self, fnct: Callable[..., T]):
        self.fnct = fnct

    def __call__(self, x: Iterable[Any]) -> T:
        return self.fnct(*islice(x, len(signature(self.fnct).parameters)))


class doublestarredpart[T]:
    def __init__(self, fnct: Callable[..., T]):
        self.fnct = fnct

    def __call__(self, x: Mapping[str, Any]) -> T:
        return self.fnct(**keyfilter(prt(contains, signature(self.fnct).parameters.keys()), x))


@overload
def apply_packed_part[T](fnct: Callable[..., T], x: Iterable[Any]) -> T:
    return fnct(*islice(x, len(signature(fnct).parameters)))


@overload
def apply_packed_part[T](fnct: Callable[..., T], x: Mapping[str, Any]) -> T:
    return fnct(**keyfilter(prt(contains, signature(fnct).parameters.keys()), x))


@dispatch
def apply_packed_part[T](fnct: Callable[..., T], x: Iterable[Any] | Mapping[str, Any]) -> T:  # type: ignore[empty-body]
    pass


class unpackingpart[T]:
    def __init__(self, fnct: Callable[..., T]):
        self.fnct = fnct

    def __call__(self, x: Iterable[Any] | Mapping[str, Any]) -> T:
        return apply_packed_part(self.fnct, x)
