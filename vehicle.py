"""
vehicle.py
----------
Base class: Vehicle
Subclasses: Car, Bike, Truck  (demonstrates Inheritance + Polymorphism)
"""


class Vehicle:
    """
    Abstract-like base class for all vehicle types.
    Encapsulates common attributes; subclasses override hourly_rate().
    """

    def __init__(self, license_plate: str, owner_name: str):
        self._license_plate = license_plate   # encapsulated (protected)
        self._owner_name = owner_name
        self._vehicle_type = "Vehicle"

    # ── Getters (Encapsulation) ───────────────────────────────────────────
    @property
    def license_plate(self) -> str:
        return self._license_plate

    @property
    def owner_name(self) -> str:
        return self._owner_name

    @property
    def vehicle_type(self) -> str:
        return self._vehicle_type

    # ── Polymorphic method (overridden in every subclass) ─────────────────
    def hourly_rate(self) -> float:
        """Returns fee per hour in rupees. Must be overridden."""
        raise NotImplementedError("Subclasses must implement hourly_rate()")

    def __str__(self):
        return (f"{self._vehicle_type} | Plate: {self._license_plate} "
                f"| Owner: {self._owner_name} | Rate: ₹{self.hourly_rate()}/hr")


# ── Subclass 1 ────────────────────────────────────────────────────────────
class Car(Vehicle):
    """Standard 4-wheeler. Mid-tier rate."""

    HOURLY_RATE = 40.0   # ₹ per hour

    def __init__(self, license_plate: str, owner_name: str):
        super().__init__(license_plate, owner_name)
        self._vehicle_type = "Car"

    def hourly_rate(self) -> float:         # Polymorphism
        return Car.HOURLY_RATE


# ── Subclass 2 ────────────────────────────────────────────────────────────
class Bike(Vehicle):
    """2-wheeler. Lowest rate."""

    HOURLY_RATE = 20.0

    def __init__(self, license_plate: str, owner_name: str):
        super().__init__(license_plate, owner_name)
        self._vehicle_type = "Bike"

    def hourly_rate(self) -> float:
        return Bike.HOURLY_RATE


# ── Subclass 3 (Extension / Bonus) ───────────────────────────────────────
class Truck(Vehicle):
    """Heavy vehicle. Highest rate."""

    HOURLY_RATE = 80.0

    def __init__(self, license_plate: str, owner_name: str):
        super().__init__(license_plate, owner_name)
        self._vehicle_type = "Truck"

    def hourly_rate(self) -> float:
        return Truck.HOURLY_RATE
