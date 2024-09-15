# TODO:
# - make it so you can take (and therefore evaluate) 1 or multiple values
# - later make it so you can evaluate set amount
# of items, so they're ready to be taken so you can improve performance

# NOTE: YOU HAVE TO BE ABLE TO MAP operations that will only be excecuted after a final
# take(), so a big rewrite is gonna happen lol

# TODO:
# - Make a function decorator for making functions
from collections.abc import Callable, Iterable, Iterator
from typing import Any, Optional, Self

type _Func[T] = Callable[[T], T]

# NOTE: considering making a custom queue class, probably not, but possibly faster than a list,
# definitely more type safe at least
type _Transform[T, K] = Callable[[T], K]
type _Mutate[T] = Callable[[T], None]

class __TransformQueue:
    class __Node[T, K]:
        def __init__(self, transform: _Transform[T, K]) -> None:
            self.transform: _Transform = transform
            self.next: Optional[__TransformQueue.__Node] = None

        def eval(self, previous: T) -> K:
            if not self.next:
                return self.transform(previous)
            return self.next.eval(self.transform(previous))

    def __init__(self) -> None:
        self.__first: Optional[__TransformQueue.__Node] = None
        self.__last: Optional[__TransformQueue.__Node] = None

    # really wish it was better typed
    def eval(self, obj: object) -> object:
        if not self.__first:
            return obj
        return self.__first.eval(obj)

    def transform(self, transform: _Transform) -> None:
        if not self.__first:
            self.__first = self.__Node(transform)
            self.__last = self.__first
            return
        new: __TransformQueue.__Node = self.__Node(transform)
        self.__last.next = new # pyright: ignore
        self.__last = new

    def mutate(self, mutation: _Mutate) -> None:
        def wrapper(obj: object) -> object:
            mutation(obj)
            return obj
        self.transform(wrapper)

class TempQueueTypeForTesting(__TransformQueue): ...

class LazyObj[T]:
    """
    Lazily evaluated object

    """
    def __init__(self, obj: T) -> None:
        self.__obj: T = obj


class LazyCollection[T](Iterable):
    """
    Lazily evaluated finite collection

    """

    # TODO: add support for more interesting functions
    def __init__(self, items: Iterable[T]) -> None:
        # self.__operations:
        self.__initial: Iterable[T] = items

    def take(self, n: int = 1) -> list[T]:
        """
        Returns the next n items of the collection
        """
        # NOTE: does not work as intended as it will not continue upon the next iteration
        initial: Iterator[T] = iter(self.__initial)
        return [next(initial) for _ in range(n)]

    def __iter__(self) -> Iterator[T]:
        raise NotImplementedError


class IteratedOverInfiniteCollection(Exception): ...


class InfCollection[T](LazyCollection):
    """
    Lazily evaluated infinite collection

    """

    # TODO: add support for more interesting functions
    def __init__(self, first: T) -> None:
        """
        Constructor for Infinite Collection

        By default it repeats the first value you give
        The first value you give is not evaluated, but used for the first evaluation
        """
        self.__eval: _Func[T] = lambda x: x
        self.__last: T = first

    def func(self, func: _Func[T]) -> None:
        """
        Decorator that sets the function to be used for further evaluation
        """

        def wrapper(arg: T):
            self.__last = func(arg)
            return self.__last

        self.__eval = wrapper

    def take(self, n: int = 1) -> list[T]:
        """
        Returns the next n items of the collection
        """
        # NOTE: will get more complicated as I add pre evaluation and shit
        return [self.__eval(self.__last) for _ in range(n)]

    def __iter__(self) -> Iterator[T]:
        raise IteratedOverInfiniteCollection
