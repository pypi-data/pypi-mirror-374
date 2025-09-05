"""Api response models"""

from enum import Enum


class VehicleMode(Enum):
    """Describe the possible vehicle modes."""

    UNDEFINED = 0
    BUS = 1
    TRAM = 2
    COACH = 3
