from typing import Dict, Generator, List, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from ..test import TestInterface


class Registry[T]:
    _registry: Dict[str, T] = {}
    _container: List[T] = []

    @classmethod
    def clear(cls):
        cls._registry = {}
        cls._container = []

    @classmethod
    def register(cls, key: str, value: T) -> None:
        cls._registry[key] = value

    @classmethod
    def deregister(cls, key: str) -> None:
        del cls._registry[key]

    @classmethod
    def get(cls, key: str) -> T:
        return cls._registry[key]

    @classmethod
    def add(cls, value: T) -> None:
        cls._container.append(value)

    @classmethod
    def extend(cls, values: Sequence[T]) -> None:
        cls._container.extend(values)

    @classmethod
    def remove(cls, value: T) -> None:
        cls._container.remove(value)

    @classmethod
    def iterate(cls) -> Generator[T, None, None]:
        yield from cls._container


TestRegistry = Registry[TestInterface]
