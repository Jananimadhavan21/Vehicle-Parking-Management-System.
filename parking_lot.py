"""
parking_lot.py
--------------
ParkingLot – central manager.
  • Holds all ParkingSlots.
  • Allocates / frees slots.
  • Creates / closes Tickets.
  • Persists records to JSON.
  • Generates summary reports.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from vehicle import Vehicle, Car, Bike, Truck
from parking_slot import ParkingSlot
from ticket import Ticket


class ParkingLot:
    """
    Manages the full lifecycle of parking operations.

    Encapsulation : _slots, _active_tickets, _history are private.
    Composition   : ParkingLot has-a list of ParkingSlots.
    """

    RECORDS_FILE = "parking_records.json"

    def __init__(self, name: str, slot_config: Optional[List[tuple]] = None):
        """
        Args:
            name        : Display name of the parking lot.
            slot_config : List of (slot_id, slot_type) tuples.
                          Defaults to a demo layout if None.
        """
        self._name = name
        self._slots: Dict[str, ParkingSlot] = {}
        self._active_tickets: Dict[str, Ticket] = {}   # plate → Ticket
        self._history: List[dict] = []

        # Default demo slot layout
        if slot_config is None:
            slot_config = (
                [("G{:02d}".format(i), "General") for i in range(1, 6)] +
                [("C{:02d}".format(i), "Covered") for i in range(1, 4)] +
                [("E{:02d}".format(i), "EV")      for i in range(1, 3)]
            )

        for slot_id, slot_type in slot_config:
            self._slots[slot_id] = ParkingSlot(slot_id, slot_type)

        self._load_records()

    # ═══════════════════════════════════════════════════════════════════════
    #  PUBLIC API
    # ═══════════════════════════════════════════════════════════════════════

    def park_vehicle(self, vehicle: Vehicle,
                     preferred_slot_type: str = "General") -> Ticket:
        """
        Allocate a free slot and create a Ticket.
        Tries preferred_slot_type first, falls back to any free slot.
        """
        if vehicle.license_plate in self._active_tickets:
            raise ValueError(
                f"Vehicle {vehicle.license_plate} is already parked!"
            )

        slot = self._find_free_slot(preferred_slot_type)
        if slot is None:
            raise RuntimeError("No free parking slots available!")

        slot.assign_vehicle(vehicle)
        ticket_id = "TKT-" + str(uuid.uuid4())[:8].upper()
        ticket = Ticket(ticket_id, vehicle, slot)
        self._active_tickets[vehicle.license_plate] = ticket

        print(f"\n✅  Vehicle parked successfully!")
        print(f"    Slot    : {slot.slot_id} ({slot.slot_type})")
        print(f"    Ticket  : {ticket_id}")
        print(f"    Entry   : {ticket.entry_time.strftime('%H:%M:%S')}")
        return ticket

    def exit_vehicle(self, license_plate: str) -> Ticket:
        """
        Close the ticket, free the slot, persist record, print receipt.
        """
        ticket = self._active_tickets.get(license_plate)
        if ticket is None:
            raise ValueError(
                f"No active parking record for plate '{license_plate}'."
            )

        fee = ticket.close_ticket()
        ticket.slot.free_slot()
        del self._active_tickets[license_plate]

        record = ticket.to_dict()
        self._history.append(record)
        self._save_records()

        print(ticket.generate_receipt())
        return ticket

    def display_available_slots(self) -> None:
        """Print a table of all slots and their current status."""
        print("\n" + "─" * 48)
        print(f"   🅿  {self._name}  –  Slot Status")
        print("─" * 48)
        free_count = 0
        for slot in self._slots.values():
            print(" ", slot.status_str())
            if not slot.is_occupied:
                free_count += 1
        print("─" * 48)
        print(f"   Free: {free_count}  |  Occupied: "
              f"{len(self._slots) - free_count}  |  Total: {len(self._slots)}")
        print("─" * 48)

    def display_active_vehicles(self) -> None:
        """Print a table of all currently parked vehicles."""
        print("\n" + "─" * 60)
        print("   Currently Parked Vehicles")
        print("─" * 60)
        if not self._active_tickets:
            print("   (No vehicles currently parked)")
        else:
            fmt = "  {:<10} {:<10} {:<8} {:<10} {:<12}"
            print(fmt.format("Plate", "Owner", "Type", "Slot", "Entry Time"))
            print("  " + "-" * 58)
            for t in self._active_tickets.values():
                print(fmt.format(
                    t.vehicle.license_plate,
                    t.vehicle.owner_name[:9],
                    t.vehicle.vehicle_type,
                    t.slot.slot_id,
                    t.entry_time.strftime("%H:%M:%S"),
                ))
        print("─" * 60)

    def generate_report(self) -> None:
        """Print a summary of all completed parking sessions."""
        print("\n" + "═" * 60)
        print("   📊  PARKING LOT REPORT")
        print("═" * 60)
        if not self._history:
            print("   No completed sessions yet.")
        else:
            total_revenue = sum(r["fee"] or 0 for r in self._history)
            print(f"   Total sessions  : {len(self._history)}")
            print(f"   Total revenue   : ₹{total_revenue:.2f}")
            print()
            fmt = "  {:<10} {:<8} {:<10} {:<10} {:<8}"
            print(fmt.format("Plate", "Type", "Slot", "Duration", "Fee"))
            print("  " + "-" * 55)
            for r in self._history[-10:]:          # show last 10
                entry = datetime.fromisoformat(r["entry_time"])
                exit_ = datetime.fromisoformat(r["exit_time"])
                delta = exit_ - entry
                hrs, rem = divmod(int(delta.total_seconds()), 3600)
                mins = rem // 60
                print(fmt.format(
                    r["license_plate"],
                    r["vehicle_type"],
                    r["slot_id"],
                    f"{hrs}h {mins}m",
                    f"₹{r['fee']:.2f}",
                ))
        print("═" * 60)

    # ═══════════════════════════════════════════════════════════════════════
    #  PRIVATE HELPERS
    # ═══════════════════════════════════════════════════════════════════════

    def _find_free_slot(self, preferred_type: str) -> Optional[ParkingSlot]:
        """Try preferred type first, then any free slot."""
        for slot in self._slots.values():
            if not slot.is_occupied and slot.slot_type == preferred_type:
                return slot
        for slot in self._slots.values():
            if not slot.is_occupied:
                return slot
        return None

    def _save_records(self) -> None:
        """Persist completed ticket history to JSON."""
        with open(self.RECORDS_FILE, "w") as f:
            json.dump(self._history, f, indent=2)

    def _load_records(self) -> None:
        """Load previous records from JSON if file exists."""
        try:
            with open(self.RECORDS_FILE, "r") as f:
                self._history = json.load(f)
            print(f"   Loaded {len(self._history)} historical record(s).")
        except FileNotFoundError:
            self._history = []
