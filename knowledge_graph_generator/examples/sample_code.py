"""
Sample Python code for testing the Knowledge Graph Generator.
This file demonstrates various code structures that can be analyzed.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import json


class Animal(ABC):
    """Abstract base class for animals."""

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    @abstractmethod
    def speak(self) -> str:
        """Make the animal speak."""
        pass

    def describe(self) -> str:
        """Return a description of the animal."""
        return f"{self.name} is {self.age} years old"


class Dog(Animal):
    """A dog that can bark and fetch."""

    def __init__(self, name: str, age: int, breed: str):
        super().__init__(name, age)
        self.breed = breed

    def speak(self) -> str:
        return "Woof!"

    def fetch(self, item: str) -> str:
        return f"{self.name} fetches the {item}"


class Cat(Animal):
    """A cat that can meow and purr."""

    def __init__(self, name: str, age: int, indoor: bool = True):
        super().__init__(name, age)
        self.indoor = indoor

    def speak(self) -> str:
        return "Meow!"

    def purr(self) -> str:
        return f"{self.name} is purring..."


class PetStore:
    """A store that manages pets."""

    def __init__(self):
        self.pets: List[Animal] = []

    def add_pet(self, pet: Animal) -> None:
        """Add a pet to the store."""
        self.pets.append(pet)

    def find_pet(self, name: str) -> Optional[Animal]:
        """Find a pet by name."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def list_pets(self) -> List[str]:
        """List all pets in the store."""
        return [pet.describe() for pet in self.pets]

    def to_json(self) -> str:
        """Export pets to JSON format."""
        data = [
            {"name": pet.name, "age": pet.age, "type": type(pet).__name__}
            for pet in self.pets
        ]
        return json.dumps(data, indent=2)


def create_sample_store() -> PetStore:
    """Create a sample pet store with some animals."""
    store = PetStore()

    dog1 = Dog("Buddy", 3, "Golden Retriever")
    dog2 = Dog("Max", 5, "German Shepherd")
    cat1 = Cat("Whiskers", 2)
    cat2 = Cat("Luna", 4, indoor=False)

    store.add_pet(dog1)
    store.add_pet(dog2)
    store.add_pet(cat1)
    store.add_pet(cat2)

    return store


if __name__ == "__main__":
    store = create_sample_store()
    print("Pets in store:")
    for description in store.list_pets():
        print(f"  - {description}")
    print("\nJSON export:")
    print(store.to_json())
