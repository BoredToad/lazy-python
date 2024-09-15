import unittest

from lazy import InfCollection, TempQueueTypeForTesting


class LazyQueueTest(unittest.TestCase):
    def test_queue(self):
        queue: TempQueueTypeForTesting = TempQueueTypeForTesting()
        queue.transform(lambda x: x * 2)
        queue.transform(lambda x: x + 1)

        for i in range(10):
            self.assertEqual(i * 2 + 1, queue.eval(i))

    def test_complex_obj(self):
        queue: TempQueueTypeForTesting = TempQueueTypeForTesting()

        @queue.transform
        def _(x: list[int]):
            x.append(5)
            return x

        queue.mutate(lambda x: x.append(55))

        @queue.mutate
        def _(x: list[int]):
            x[1] -= 3

        queue.transform(lambda x: sum(x))

        self.assertEqual(100, queue.eval([43]))


if __name__ == "__main__":
    unittest.main()
