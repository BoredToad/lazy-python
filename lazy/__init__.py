# TODO:
# - make it so you can take (and therefore evaluate) 1 or multiple values
# - later make it so you can evaluate set amount
# of items, so they're ready to be taken so you can improve performance

# TODO:
# - Make a function decorator for making functions
from collections.abc import Callable, Iterable
from typing import Self

type __Func[T] = Callable[[T], T]


class InfCollection[T](Iterable):
    """
    Lazily evaluated infinite collection

    Be careful when iterating over
    it as it will continue forever if not stopped manually
    prefer the take() method
    """

    # TODO: add support for more interesting functions
    def __init__(self, first: T) -> None:
        """
        Constructor for Infinite Collection

        By default it repeats the first value you give
        The first value you give is not evaluated, but used for the first evaluation
        """
        self.__eval: __Func[T] = lambda x: x
        self.__last: T = first

    def func(self, func: __Func[T]) -> None:
        """
        Decorator that sets the function to be used for further evaluation
        """

        def wrapper(arg: T):
            self.__last = func(arg)
            return self.__last

        self.__eval = wrapper

    def take(self, n: int = 1) -> list[T]:
        # NOTE: will get more complicated as I add pre evaluation and shit
        return [self.__eval(self.__last) for _ in range(n)]
