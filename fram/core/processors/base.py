from abc import ABC, abstractmethod
from pathlib import Path
from typing import TypeVar

from fram.core.errors import InvalidOperation
from fram.core.operations import Operation

T = TypeVar("T")


class MediaProcessor(ABC):
    @abstractmethod
    def run(self, input_path: Path, operations: list[Operation], output_path: Path) -> Path:
        raise NotImplementedError

    def expect(self, value: object, expected_type: type[T]) -> T:
        if not isinstance(value, expected_type):
            expected = expected_type.__name__
            actual = type(value).__name__
            raise InvalidOperation(f"Expected {expected}, got {actual}.")
        return value
