import unittest

from lazy import InfCollection


class BasicTest(unittest.TestCase):
    def test_same(self):
        collection: InfCollection = InfCollection("SAME")
        for _ in range(10):
            self.assertEqual("SAME", collection.take()[0])

    def test_simple_int(self):
        collection: InfCollection = InfCollection(0)
        collection.func(lambda x: x + 1)

        for i in range(1, 11):
            self.assertEqual(i, collection.take()[0])

    def test_takes_multiple(self):
        collection: InfCollection = InfCollection(1)

        @collection.func
        def _(x: int) -> int:
            return x * 2

        self.assertEqual([2, 4, 8, 16, 32], collection.take(5))


if __name__ == "__main__":
    unittest.main()
