"""
test_parking_system.py
-----------------------
Full automated tests for all classes.
Run: python test_parking_system.py
"""

import time
import sys
import os

# Make sure imports resolve from same folder
sys.path.insert(0, os.path.dirname(__file__))

from vehicle import Vehicle, Car, Bike, Truck
from parking_slot import ParkingSlot
from parking_lot import ParkingLot
from ticket import Ticket

PASS = "✅ PASS"
FAIL = "❌ FAIL"

results = []


def test(name: str, condition: bool, detail: str = ""):
    status = PASS if condition else FAIL
    results.append((name, condition))
    line = f"  {status}  {name}"
    if detail:
        line += f"  ({detail})"
    print(line)


def section(title: str):
    print(f"\n{'─'*52}")
    print(f"  {title}")
    print(f"{'─'*52}")


# ══════════════════════════════════════════════════════
#  1. Vehicle Hierarchy & Polymorphism
# ══════════════════════════════════════════════════════
section("1. Vehicle Classes & Polymorphism")

car   = Car("TN01AB1234", "Arjun")
bike  = Bike("TN02CD5678", "Meena")
truck = Truck("TN03EF9012", "Rajan")

test("Car vehicle_type",   car.vehicle_type == "Car")
test("Bike vehicle_type",  bike.vehicle_type == "Bike")
test("Truck vehicle_type", truck.vehicle_type == "Truck")

test("Car hourly rate ₹40",   car.hourly_rate()   == 40.0)
test("Bike hourly rate ₹20",  bike.hourly_rate()  == 20.0)
test("Truck hourly rate ₹80", truck.hourly_rate() == 80.0)

# Polymorphism: same call, different result
vehicles = [car, bike, truck]
rates = [v.hourly_rate() for v in vehicles]
test("Polymorphic rates are all different", len(set(rates)) == 3)

# Inheritance check
test("Car is a Vehicle",   isinstance(car, Vehicle))
test("Bike is a Vehicle",  isinstance(bike, Vehicle))
test("Truck is a Vehicle", isinstance(truck, Vehicle))

# Encapsulation: direct attribute access should be protected
test("License plate via property", car.license_plate == "TN01AB1234")
test("Owner via property",         car.owner_name    == "Arjun")


# ══════════════════════════════════════════════════════
#  2. ParkingSlot
# ══════════════════════════════════════════════════════
section("2. ParkingSlot")

slot_gen = ParkingSlot("G01", "General")
slot_cov = ParkingSlot("C01", "Covered")
slot_ev  = ParkingSlot("E01", "EV")

test("General slot free initially",  not slot_gen.is_occupied)
test("Covered surcharge ₹10",        slot_cov.surcharge == 10.0)
test("EV surcharge ₹15",             slot_ev.surcharge  == 15.0)
test("General surcharge ₹0",         slot_gen.surcharge == 0.0)

slot_gen.assign_vehicle(car)
test("Slot occupied after assign",   slot_gen.is_occupied)
test("Slot holds correct vehicle",   slot_gen.vehicle.license_plate == "TN01AB1234")

# Double-assign should raise
try:
    slot_gen.assign_vehicle(bike)
    test("Double-assign raises RuntimeError", False)
except RuntimeError:
    test("Double-assign raises RuntimeError", True)

slot_gen.free_slot()
test("Slot free after free_slot()",  not slot_gen.is_occupied)
test("Slot vehicle is None",         slot_gen.vehicle is None)

# Invalid slot type
try:
    bad = ParkingSlot("X01", "Invalid")
    test("Invalid slot type raises ValueError", False)
except ValueError:
    test("Invalid slot type raises ValueError", True)


# ══════════════════════════════════════════════════════
#  3. Ticket & Fee Calculation
# ══════════════════════════════════════════════════════
section("3. Ticket & Fee Calculation")

slot_t = ParkingSlot("T01", "Covered")   # surcharge ₹10
slot_t.assign_vehicle(car)
ticket = Ticket("TKT-TEST01", car, slot_t)

test("Ticket is active on creation",  ticket.is_active)
test("Ticket entry time set",         ticket.entry_time is not None)
test("Ticket exit time is None",      ticket.exit_time  is None)

# Estimated fee before closing (minimum 1 hr)
est_fee = ticket.calculate_fee()
expected_min = 1 * (40.0 + 10.0)   # 1 hr * (car rate + covered surcharge)
test("Estimated fee ≥ minimum ₹50",  est_fee >= expected_min,
     f"got ₹{est_fee}")

time.sleep(0.1)   # tiny sleep so duration > 0

fee = ticket.close_ticket()
test("Fee after close > 0",           fee > 0, f"₹{fee}")
test("Ticket no longer active",       not ticket.is_active)
test("Fee equals calculate_fee()",    ticket.fee == fee)

# Double-close should raise
try:
    ticket.close_ticket()
    test("Double close raises RuntimeError", False)
except RuntimeError:
    test("Double close raises RuntimeError", True)

# Receipt generation
receipt = ticket.generate_receipt()
test("Receipt contains ticket ID",    "TKT-TEST01" in receipt)
test("Receipt contains plate",        "TN01AB1234"  in receipt)
test("Receipt contains fee",          "₹" in receipt)

# Serialisation
d = ticket.to_dict()
test("to_dict has required keys",
     all(k in d for k in ["ticket_id","license_plate","fee","entry_time"]))


# ══════════════════════════════════════════════════════
#  4. ParkingLot Integration
# ══════════════════════════════════════════════════════
section("4. ParkingLot Integration")

lot = ParkingLot("Test Lot", slot_config=[
    ("G01", "General"), ("G02", "General"),
    ("C01", "Covered"),
    ("E01", "EV"),
])

car2   = Car("KA01AA0001",  "Suresh")
bike2  = Bike("KA02BB0002", "Priya")
truck2 = Truck("KA03CC0003","Venkat")

t1 = lot.park_vehicle(car2,   "General")
t2 = lot.park_vehicle(bike2,  "Covered")
t3 = lot.park_vehicle(truck2, "EV")

test("3 vehicles parked successfully", t1 and t2 and t3)

# Park duplicate plate
try:
    lot.park_vehicle(Car("KA01AA0001","Dup"), "General")
    test("Duplicate plate raises ValueError", False)
except ValueError:
    test("Duplicate plate raises ValueError", True)

# Exit car
finished = lot.exit_vehicle("KA01AA0001")
test("Exited vehicle ticket closed",  not finished.is_active)
test("Exited vehicle fee set",        finished.fee is not None)

# Slot freed after exit
freed_slot = finished.slot
test("Slot freed after exit",         not freed_slot.is_occupied)

# Exit non-existent
try:
    lot.exit_vehicle("XXXXXX")
    test("Exit unknown plate raises ValueError", False)
except ValueError:
    test("Exit unknown plate raises ValueError", True)

# Overflow – fill all slots then try one more
lot2 = ParkingLot("Tiny Lot", slot_config=[("X01","General")])
lot2.park_vehicle(Car("AA0001","A"), "General")
try:
    lot2.park_vehicle(Car("AA0002","B"), "General")
    test("Full lot raises RuntimeError", False)
except RuntimeError:
    test("Full lot raises RuntimeError", True)


# ══════════════════════════════════════════════════════
#  Summary
# ══════════════════════════════════════════════════════
section("TEST SUMMARY")
passed = sum(1 for _, ok in results if ok)
total  = len(results)
print(f"\n  {passed}/{total} tests passed\n")
if passed == total:
    print("  🎉  All tests passed!\n")
else:
    failed = [n for n, ok in results if not ok]
    print("  Failed tests:")
    for n in failed:
        print(f"    • {n}")
    print()
