"""
ticket.py
---------
Ticket – records entry/exit time and calculates the parking fee.
Demonstrates datetime usage + fee calculation (polymorphism via vehicle.hourly_rate()).
"""

import math
from datetime import datetime
from typing import Optional
from vehicle import Vehicle
from parking_slot import ParkingSlot


class Ticket:
    """
    Created when a vehicle parks. Closed (exit recorded) on departure.
    Fee = ceil(duration_hours) * (vehicle.hourly_rate() + slot.surcharge)
    Minimum billing: 1 hour.
    """

    def __init__(self, ticket_id: str, vehicle: Vehicle, slot: ParkingSlot):
        self._ticket_id  = ticket_id
        self._vehicle    = vehicle
        self._slot       = slot
        self._entry_time: datetime = datetime.now()
        self._exit_time:  Optional[datetime] = None
        self._fee:        Optional[float]    = None

    # ── Getters ───────────────────────────────────────────────────────────
    @property
    def ticket_id(self) -> str:
        return self._ticket_id

    @property
    def vehicle(self) -> Vehicle:
        return self._vehicle

    @property
    def slot(self) -> ParkingSlot:
        return self._slot

    @property
    def entry_time(self) -> datetime:
        return self._entry_time

    @property
    def exit_time(self) -> Optional[datetime]:
        return self._exit_time

    @property
    def fee(self) -> Optional[float]:
        return self._fee

    @property
    def is_active(self) -> bool:
        return self._exit_time is None

    # ── Core logic ────────────────────────────────────────────────────────
    def calculate_fee(self) -> float:
        """
        Calculates fee based on duration.
        Called internally by close_ticket(); also available for preview.
        """
        end = self._exit_time if self._exit_time else datetime.now()
        duration_seconds = (end - self._entry_time).total_seconds()
        duration_hours   = max(duration_seconds / 3600, 1.0)   # minimum 1 hr
        billed_hours     = math.ceil(duration_hours)            # round up
        rate             = self._vehicle.hourly_rate() + self._slot.surcharge
        return round(billed_hours * rate, 2)

    def close_ticket(self) -> float:
        """Record exit time and finalise fee. Returns fee."""
        if not self.is_active:
            raise RuntimeError(f"Ticket {self._ticket_id} already closed.")
        self._exit_time = datetime.now()
        self._fee       = self.calculate_fee()
        return self._fee

    def duration_str(self) -> str:
        end = self._exit_time or datetime.now()
        delta = end - self._entry_time
        hours, rem = divmod(int(delta.total_seconds()), 3600)
        minutes     = rem // 60
        return f"{hours}h {minutes}m"

    # ── Receipt ───────────────────────────────────────────────────────────
    def generate_receipt(self) -> str:
        """Returns a formatted receipt string."""
        sep = "═" * 46
        lines = [
            sep,
            "         🅿  PARKING RECEIPT",
            sep,
            f"  Ticket ID   : {self._ticket_id}",
            f"  Vehicle     : {self._vehicle.vehicle_type}",
            f"  Plate       : {self._vehicle.license_plate}",
            f"  Owner       : {self._vehicle.owner_name}",
            f"  Slot        : {self._slot.slot_id} ({self._slot.slot_type})",
            f"  Entry Time  : {self._entry_time.strftime('%d-%m-%Y %H:%M:%S')}",
        ]
        if self._exit_time:
            lines += [
                f"  Exit Time   : {self._exit_time.strftime('%d-%m-%Y %H:%M:%S')}",
                f"  Duration    : {self.duration_str()}",
                f"  Rate/hr     : ₹{self._vehicle.hourly_rate():.2f} "
                f"+ ₹{self._slot.surcharge:.2f} surcharge",
                f"  Total Fee   : ₹{self._fee:.2f}",
            ]
        else:
            lines += [
                f"  Status      : PARKED (ongoing)",
                f"  Duration    : {self.duration_str()} (so far)",
                f"  Est. Fee    : ₹{self.calculate_fee():.2f}",
            ]
        lines.append(sep)
        return "\n".join(lines)

    # ── Serialisation (for JSON persistence) ─────────────────────────────
    def to_dict(self) -> dict:
        return {
            "ticket_id"   : self._ticket_id,
            "license_plate": self._vehicle.license_plate,
            "owner_name"  : self._vehicle.owner_name,
            "vehicle_type": self._vehicle.vehicle_type,
            "slot_id"     : self._slot.slot_id,
            "slot_type"   : self._slot.slot_type,
            "entry_time"  : self._entry_time.isoformat(),
            "exit_time"   : self._exit_time.isoformat() if self._exit_time else None,
            "fee"         : self._fee,
        }

    def __str__(self):
        return self.generate_receipt()
