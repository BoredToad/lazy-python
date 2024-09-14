import unittest

from lib import InfCollection


class BasicTest(unittest.TestCase):
    def simple_int(self) -> None:
        # def func(collection: InfCollection, x: int) -> int:
        #     collection.__last =
        collection: InfCollection = InfCollection(0)
        collection.func(lambda x: x + 1)

        for i in range(1, 11):
            self.assertEqual(i, collection.take()[0])


if __name__ == "__main__":
    unittest.main()
