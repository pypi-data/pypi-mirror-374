"""Encapsulates the output datasets and collections for a Tool."""

from typing import Any, List

from .dataset import AbstractData, Dataset, DatasetCollection


class Outputs:
    """Contains the output datasets and collections for a Tool."""

    def __init__(self) -> None:
        self.data: List[AbstractData] = []

    def __iter__(self) -> Any:
        """Iterator."""
        self._iterator = 0
        return self

    def __next__(self) -> AbstractData:
        """Get next element for iterator."""
        if self._iterator >= len(self.data):
            raise StopIteration
        d = self.data[self._iterator]
        self._iterator += 1
        return d

    def add_output(self, data: AbstractData) -> None:
        self.data.append(data)

    def get_dataset(self, name: str) -> AbstractData:
        try:
            return next(filter(lambda x: isinstance(x, Dataset) and x.name == name, self.data))
        except StopIteration as e:
            raise Exception(f"There is no dataset: {name}") from e

    def get_collection(self, name: str) -> AbstractData:
        try:
            return next(filter(lambda x: isinstance(x, DatasetCollection) and x.name == name, self.data))
        except StopIteration as e:
            raise Exception(f"There is no dataset collection: {name}") from e
