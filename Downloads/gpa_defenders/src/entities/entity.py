"""Base class voor alle game entities."""

import pygame
from abc import ABC, abstractmethod


class Entity(ABC):
    """Abstracte base class voor alle objecten in het spel.

    Attributes:
        x: X-positie in pixels.
        y: Y-positie in pixels.
        alive: Of de entity nog actief is.
    """

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.alive = True

    @property
    def position(self) -> tuple[float, float]:
        """Geeft de huidige positie als tuple."""
        return (self.x, self.y)

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update de entity state.

        Args:
            dt: Delta time in seconden sinds laatste frame.
        """
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Teken de entity op het scherm.

        Args:
            screen: Het pygame scherm om op te tekenen.
        """
        pass

    def distance_to(self, other: "Entity") -> float:
        """Bereken afstand tot een andere entity.

        Args:
            other: De andere entity.

        Returns:
            De afstand in pixels.
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx * dx + dy * dy) ** 0.5
