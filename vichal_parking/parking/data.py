"""
Vichal Parking Management System
---------------------------------
Pure Python in-memory data store + business logic.
No database / SQL used — everything is held in Python
data structures (dict/list) for the lifetime of the server process.
"""

from datetime import datetime

# ---------------------------------------------------------------------
# In-memory "tables" (plain Python data structures)
# ---------------------------------------------------------------------

# Parking slots: slot_id -> slot info
parking_slots = {
    1: {"occupied": False, "vehicle_type": None, "vehicle_number": None},
    2: {"occupied": False, "vehicle_type": None, "vehicle_number": None},
    3: {"occupied": False, "vehicle_type": None, "vehicle_number": None},
    4: {"occupied": False, "vehicle_type": None, "vehicle_number": None},
    5: {"occupied": False, "vehicle_type": None, "vehicle_number": None},
    6: {"occupied": False, "vehicle_type": None, "vehicle_number": None},
}

# Currently parked vehicles: vehicle_number -> details
vehicles = {}

# History of completed visits (for reports / dashboard)
history = []

# Hourly parking rate per vehicle type
RATE_PER_HOUR = {
    "car": 20,
    "bike": 10,
    "truck": 40,
}

MIN_BILL_HOURS = 1  # minimum 1 hour is always charged


# ---------------------------------------------------------------------
# Core business logic
# ---------------------------------------------------------------------

def get_available_slot():
    """Return the id of the first free slot, or None if full."""
    for slot_id, slot in parking_slots.items():
        if not slot["occupied"]:
            return slot_id
    return None


def allocate_slot(vehicle_number, vehicle_type):
    """
    Allocate a free slot to an incoming vehicle.
    Returns the slot_id on success, or None if parking is full
    or the vehicle is already parked.
    """
    vehicle_number = vehicle_number.strip().upper()

    if vehicle_number in vehicles:
        return "ALREADY_PARKED"

    slot_id = get_available_slot()
    if slot_id is None:
        return None  # parking full

    parking_slots[slot_id] = {
        "occupied": True,
        "vehicle_type": vehicle_type,
        "vehicle_number": vehicle_number,
    }

    vehicles[vehicle_number] = {
        "vehicle_number": vehicle_number,
        "vehicle_type": vehicle_type,
        "slot_id": slot_id,
        "entry_time": datetime.now(),
    }

    return slot_id


def calculate_duration_hours(entry_time, exit_time):
    seconds = (exit_time - entry_time).total_seconds()
    hours = seconds / 3600
    return max(hours, MIN_BILL_HOURS)  # always bill at least 1 hour


def process_exit(vehicle_number):
    """
    Process a vehicle leaving the parking lot.
    Frees the slot, calculates the bill, stores a history record.
    Returns a dict with bill details, or None if vehicle not found.
    """
    vehicle_number = vehicle_number.strip().upper()
    vehicle = vehicles.get(vehicle_number)

    if not vehicle:
        return None

    exit_time = datetime.now()
    duration_hours = calculate_duration_hours(vehicle["entry_time"], exit_time)
    rate = RATE_PER_HOUR.get(vehicle["vehicle_type"], 20)
    amount = round(duration_hours * rate, 2)

    # free the slot
    slot_id = vehicle["slot_id"]
    parking_slots[slot_id] = {
        "occupied": False,
        "vehicle_type": None,
        "vehicle_number": None,
    }

    record = {
        "vehicle_number": vehicle_number,
        "vehicle_type": vehicle["vehicle_type"],
        "slot_id": slot_id,
        "entry_time": vehicle["entry_time"],
        "exit_time": exit_time,
        "duration_hours": round(duration_hours, 2),
        "amount": amount,
    }
    history.append(record)

    # remove from active vehicles
    del vehicles[vehicle_number]

    return record


def get_dashboard_stats():
    """Aggregate stats for the dashboard page."""
    total_slots = len(parking_slots)
    occupied_slots = sum(1 for s in parking_slots.values() if s["occupied"])
    available_slots = total_slots - occupied_slots
    total_revenue = round(sum(r["amount"] for r in history), 2)
    total_visits = len(history)

    return {
        "total_slots": total_slots,
        "occupied_slots": occupied_slots,
        "available_slots": available_slots,
        "total_revenue": total_revenue,
        "total_visits": total_visits,
    }
