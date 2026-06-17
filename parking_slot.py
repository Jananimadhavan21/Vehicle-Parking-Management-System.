"""
parking_slot.py
---------------
ParkingSlot – tracks whether a slot is free or occupied.
Encapsulates slot state; status changed only through methods.
"""

from typing import Optional
from vehicle import Vehicle


class ParkingSlot:
    """
    Represents a single parking bay.

    Slot types (Extension):
        "General"   – standard slot
        "Covered"   – extra ₹10/hr surcharge
        "EV"        – EV charging slot, extra ₹15/hr surcharge
    """

    SURCHARGE = {
        "General": 0.0,
        "Covered": 10.0,
        "EV":      15.0,
    }

    def __init__(self, slot_id: str, slot_type: str = "General"):
        if slot_type not in ParkingSlot.SURCHARGE:
            raise ValueError(f"Invalid slot type '{slot_type}'. "
                             f"Choose from {list(ParkingSlot.SURCHARGE)}")
        self._slot_id   = slot_id
        self._slot_type = slot_type
        self._is_occupied: bool = False
        self._vehicle: Optional[Vehicle] = None

    # ── Getters ───────────────────────────────────────────────────────────
    @property
    def slot_id(self) -> str:
        return self._slot_id

    @property
    def slot_type(self) -> str:
        return self._slot_type

    @property
    def is_occupied(self) -> bool:
        return self._is_occupied

    @property
    def vehicle(self) -> Optional[Vehicle]:
        return self._vehicle

    @property
    def surcharge(self) -> float:
        return ParkingSlot.SURCHARGE[self._slot_type]

    # ── State mutators (Encapsulation) ────────────────────────────────────
    def assign_vehicle(self, vehicle: Vehicle) -> None:
        if self._is_occupied:
            raise RuntimeError(f"Slot {self._slot_id} is already occupied.")
        self._vehicle    = vehicle
        self._is_occupied = True

    def free_slot(self) -> None:
        self._vehicle    = None
        self._is_occupied = False

    # ── Display ───────────────────────────────────────────────────────────
    def status_str(self) -> str:
        if self._is_occupied:
            return (f"[{self._slot_id}] {self._slot_type:8s} → "
                    f"OCCUPIED by {self._vehicle.license_plate} "
                    f"({self._vehicle.vehicle_type})")
        return f"[{self._slot_id}] {self._slot_type:8s} → FREE"

    def __str__(self):
        return self.status_str()
