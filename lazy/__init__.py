from collections.abc import Callable, Iterable, Iterator
from typing import Any, Optional

type _Transformation[T, K] = Callable[[T], K]
type _Mutation[T] = Callable[[T], Any]


class TransformQueue:
    """Queue of transformations and mutations

    All mutations get converted into transforms under the hood
    """

    class __Node[T, K]:
        def __init__(self, transform: _Transformation[T, K]) -> None:
            self.transform: _Transformation = transform
            self.next: Optional[TransformQueue.__Node] = None

        def eval(self, previous: T) -> K:
            if not self.next:
                return self.transform(previous)
            return self.next.eval(self.transform(previous))

    def __init__(self) -> None:
        self.__first: Optional[TransformQueue.__Node] = None
        self.__last: Optional[TransformQueue.__Node] = None

    # really wish it was better typed
    def eval(self, obj: object) -> object:
        if not self.__first:
            return obj
        return self.__first.eval(obj)

    def transform(self, transform: _Transformation) -> None:
        if not self.__first:
            self.__first = self.__Node(transform)
            self.__last = self.__first
            return
        new: TransformQueue.__Node = self.__Node(transform)
        self.__last.next = new  # pyright: ignore
        self.__last = new

    def mutate(self, mutation: _Mutation) -> None:
        def wrapper(obj: object) -> object:
            mutation(obj)
            return obj

        self.transform(wrapper)


class LazyObj:
    """Lazily evaluated object"""

    def __init__(self, obj: object) -> None:
        self.__obj: object = obj
        self.__queue: TransformQueue = TransformQueue()

    def transform(self, transformation: _Transformation) -> None:
        """Takes the object as input, and transforms it into the return value"""

        self.__queue.transform(transformation)

    def mutate(self, mutation: _Mutation) -> None:
        """Mutates the object

        Immutable types like strings and integers won't work
        use transform instead
        """
        self.__queue.mutate(mutation)

    def eval(self) -> object:
        """Evaluates and returns the object."""
        self.__obj = self.__queue.eval(self.__obj)
        self.__queue = TransformQueue()
        return self.__obj

    def __invert__(self) -> object:
        """Same as calling .eval()"""
        return self.eval()


class LazyCollection[T](Iterator):
    """Lazily evaluated finite collection"""

    def __init__(self, items: Iterable[T]) -> None:
        self.__it: Iterator = iter(items)
        self.__queue = TransformQueue()

    def map(self, transformation: _Transformation) -> None:
        self.__queue.transform(transformation)

    def foreach(self, mutation: _Mutation) -> None:
        self.__queue.mutate(mutation)

    def take(self, n: int = 1) -> list[object]:
        """Returns the next n items of the collection

        0 or less returns the rest of the collection
        """
        objects: list[object] = []
        try:
            for _ in (
                range(n) if n > 0 else iter(int, 1)
            ):  # really hacky way to do it lmfao
                objects.append(self.__queue.eval(next(self.__it)))
        except StopIteration:
            pass
        return objects

    # def __iter__(self) -> Iterator[object]:
    #     return self

    def __next__(self) -> object:
        l: list[object] = self.take()
        if not l:
            raise StopIteration
        return l[0]


type GenFunc[T] = Callable[[T], T]

class InfGenerator[T](Iterator):
    def __init__(self, first: T, gen_func: GenFunc[T]) -> None:
        self.__last: T = first
        self.__gen: GenFunc[T] = gen_func

    def __next__(self) -> T:
        self.__last = self.__gen(self.__last)
        return self.__last
