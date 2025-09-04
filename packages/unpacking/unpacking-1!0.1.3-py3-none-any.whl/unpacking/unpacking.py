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
        return apply_packed_part(self.fnct, x)  # type: ignore[return]
