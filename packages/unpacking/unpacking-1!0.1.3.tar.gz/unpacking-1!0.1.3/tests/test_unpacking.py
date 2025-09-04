import unittest
from concurrent.futures import ProcessPoolExecutor

from src.unpacking import (
    doublestarred,
    doublestarredpart,
    starred,
    starredpart,
    unpacking,
    unpackingpart,
)


def add(x, y):
    return x + y


class TestUnpacking(unittest.TestCase):
    def test_basic(self):

        args = [1, 2]
        kwargs = {"x": 1, "y": 2}
        self.assertEqual(starred(add)(args), 3)
        self.assertEqual(doublestarred(add)(kwargs), 3)
        self.assertEqual(unpacking(add)(args), 3)
        self.assertEqual(unpacking(add)(kwargs), 3)

    def test_multiprocessing(self):

        args_list = [[1, 2], [3, 4]]
        kwargs_list = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
        with ProcessPoolExecutor(2) as executor:
            result_args = tuple(executor.map(unpacking(add), args_list))
            self.assertEqual(result_args, (3, 7))
            result_kwargs = tuple(executor.map(unpacking(add), kwargs_list))
            self.assertEqual(result_kwargs, (3, 7))

    def test_excess_args(self):

        args_excess = [1, 2, 3]
        kwargs_excess = {"x": 1, "y": 2, "z": 3}
        self.assertEqual(starredpart(add)(args_excess), 3)
        self.assertEqual(doublestarredpart(add)(kwargs_excess), 3)
        args_excess_m = [[1, 2, 3], [3, 4, 5]]
        kwargs_excess_m = [{"x": 1, "y": 2, "z": 3}, {"x": 3, "y": 4, "z": 5}]
        with ProcessPoolExecutor(2) as executor:
            result_args = tuple(executor.map(unpackingpart(add), args_excess_m))
            self.assertEqual(result_args, (3, 7))
            result_kwargs = tuple(executor.map(unpackingpart(add), kwargs_excess_m))
            self.assertEqual(result_kwargs, (3, 7))


if __name__ == "__main__":
    unittest.main()
