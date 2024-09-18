from collections.abc import Callable, Iterable, Iterator
from copy import deepcopy
from typing import Any, Optional, Self

type _Transformation[T, K] = Callable[[T], K]
type _Mutation[T] = Callable[[T], Any]
type _Filter[T] = Callable[[T], bool]


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
    """Lazily evaluated collection"""

    def __init__(self, items: Iterable[T]) -> None:
        self.__it: Iterator = iter(items)
        self.__queue = TransformQueue()

    def map(self, transformation: _Transformation) -> None:
        """Transforms the Collection"""
        self.__queue.transform(transformation)

    def foreach(self, mutation: _Mutation) -> None:
        """Mutates the collection

        Beware when mutating immutable types
        use map instead
        """
        self.__queue.mutate(mutation)

    class Filtered(Exception): ...

    def filter(self, filter: _Filter) -> None:
        """Filters out items

        keeps items that return True
        """
        def wrapper(obj: T) -> T:
            if not filter(obj):
                raise LazyCollection.Filtered
            return obj
        self.map(wrapper)

    def take(self, n: int = 1) -> list[object]:
        """Returns the next n items of the collection

        0 or less returns the rest of the collection
        """
        objects: list[object] = []
        try:
            for _ in (
                range(n) if n > 0 else iter(int, 1)
            ):  # really hacky way to do it lmfao
                try:
                    objects.append(self.__queue.eval(next(self.__it)))
                except LazyCollection.Filtered:
                    objects.append(self.__queue.eval(next(self.__it))) # lmfao
        except StopIteration:
            pass
        return objects

    def __next__(self) -> object:
        l: list[object] = self.take()
        if not l:
            raise StopIteration
        return l[0]


type GenFunc[T] = Callable[[T], T]

class InfGenerator[T](Iterator):
    """Generates an infinite Iterator

    Be careful when iterating over
    """
    def __init__(self, first: T, gen_func: GenFunc[T]) -> None:
        """Basic constructor

        works for basic usecases
        """
        self.__last: T = first
        self.__gen: GenFunc[T] = gen_func

    def __next__(self) -> T:
        self.__last = self.__gen(self.__last)
        return self.__last

    class __Cycler(Iterator[T]):
        # I really dislike this implementation,
        # but I'm too dumb to do something better
        def __init__(self, origin: Iterable[T]) -> None:
            self.__origin: Iterator[T] = iter(origin)
            self.__cur: Iterator[T] = deepcopy(self.__origin)
        def __next__(self) -> T:
            try:
                ret: T = next(self.__cur)
            except StopIteration:
                self.__cur = deepcopy(self.__origin)
                ret: T = next(self.__cur)
            return ret

    @staticmethod
    def cycle(origin: Iterable[T]) -> Self: # pyright: ignore
        """Creates a generator that cycles between the given values"""
        it: InfGenerator.__Cycler = InfGenerator.__Cycler(origin)
        return InfGenerator(None, lambda _: next(it))
