import unittest

import lazy


class LazyObjTest(unittest.TestCase):
    def test_basic_obj(self):
        lazyint: lazy.LazyObj = lazy.LazyObj(5)
        lazyint.transform(lambda x: x * 2)

        @lazyint.transform
        def _(x: int):
            return x + 5

        self.assertEqual(15, ~lazyint)

    def test_complex_obj(self):
        lazylist: lazy.LazyObj = lazy.LazyObj([43])

        @lazylist.transform
        def _(x: list[int]):
            x.append(5)
            return x

        lazylist.mutate(lambda x: x.append(55))

        @lazylist.mutate
        def _(x: list[int]):
            x[1] -= 3

        lazylist.transform(lambda x: sum(x))

        self.assertEqual(100, ~lazylist)


class LazyCollectionTest(unittest.TestCase):
    def test_simple(self):
        lazylist: lazy.LazyCollection = lazy.LazyCollection(range(11))
        lazylist.map(lambda x: x * x)
        self.assertEqual([0, 1, 4, 9, 16, 25, 36, 49, 64, 81], lazylist.take(10))

        lazylist.map(lambda x: str(x))

        @lazylist.map
        def _(x: str) -> str:
            x = f"the num is {x}"
            return x

        self.assertEqual("the num is 100", lazylist.take()[0])

    def test_out_of_bounds(self):
        lazylist: lazy.LazyCollection = lazy.LazyCollection([])
        self.assertEqual(lazylist.take(), [])

    def test_takes_rest(self):
        lazylist: lazy.LazyCollection = lazy.LazyCollection([1, 2, 3, 4, 5])
        lazylist.take(2)
        self.assertEqual([3, 4, 5], lazylist.take(0))

    def test_mutation(self):
        lazylist: lazy.LazyCollection = lazy.LazyCollection([[1, 2], [3, 4]])

        @lazylist.foreach
        def _(l: list[int]) -> None:
            l[0] = l[1]

        lazylist.map(lambda l: sum(l))

        self.assertEqual([4, 8], lazylist.take(0))

    def test_iteration(self):
        lazylist: lazy.LazyCollection = lazy.LazyCollection(range(10))
        lazylist.map(lambda i: i * 2)
        x: int = 0
        for i in lazylist:
            self.assertEqual(i, x * 2)
            x += 1


class InfiniteTest(unittest.TestCase):
    def test_basic(self):
        l: lazy.LazyCollection = lazy.LazyCollection(lazy.InfGenerator(0, lambda a: a + 1))
        l.map(lambda x: x * 2)
        self.assertEqual([2, 4, 6, 8, 10], l.take(5))

    def test_cycle(self):
        l: lazy.LazyCollection = lazy.LazyCollection(lazy.InfGenerator.cycle(range(1, 4)))
        self.assertEqual([1, 2, 3, 1, 2], l.take(5))

class FilterTest(unittest.TestCase):
    def test_filter(self):
        l: lazy.LazyCollection = lazy.LazyCollection(lazy.InfGenerator.cycle(range(1, 4)))
        l.map(lambda x: x * 2)
        l.filter(lambda x: x != 4)
        self.assertEqual([2, 6, 2, 6, 2], l.take(5))


if __name__ == "__main__":
    unittest.main()
