"""
main.py
-------
CLI entry point for the Vehicle Parking Management System.
Demonstrates all OOP concepts via an interactive menu.
"""

from vehicle import Car, Bike, Truck
from parking_lot import ParkingLot


# ── Helpers ───────────────────────────────────────────────────────────────

def get_vehicle_from_user() -> "Vehicle":
    """Prompt user to enter vehicle details and return the right subclass."""
    print("\n  Vehicle Type:")
    print("  [1] Car   (₹40/hr)")
    print("  [2] Bike  (₹20/hr)")
    print("  [3] Truck (₹80/hr)")
    choice = input("  Choose type (1/2/3): ").strip()

    plate = input("  License plate      : ").strip().upper()
    owner = input("  Owner name         : ").strip()

    if choice == "1":
        return Car(plate, owner)
    elif choice == "2":
        return Bike(plate, owner)
    elif choice == "3":
        return Truck(plate, owner)
    else:
        print("  Invalid choice. Defaulting to Car.")
        return Car(plate, owner)


def get_slot_preference() -> str:
    """Ask user which slot type they prefer."""
    print("\n  Slot Type Preference:")
    print("  [1] General  (no surcharge)")
    print("  [2] Covered  (+₹10/hr)")
    print("  [3] EV       (+₹15/hr)")
    choice = input("  Choose (1/2/3) [default: 1]: ").strip()
    return {"1": "General", "2": "Covered", "3": "EV"}.get(choice, "General")


def print_banner():
    print("""
╔══════════════════════════════════════════════════════╗
║       🚗  VEHICLE PARKING MANAGEMENT SYSTEM  🚗      ║
║          OOP Demo — Car | Bike | Truck               ║
╚══════════════════════════════════════════════════════╝""")


def print_menu():
    print("""
┌─────────────────────────────────────────┐
│  [1] Park a Vehicle                     │
│  [2] Exit a Vehicle (generate receipt)  │
│  [3] View Slot Availability             │
│  [4] View Currently Parked Vehicles     │
│  [5] View Session Report                │
│  [6] Exit Program                       │
└─────────────────────────────────────────┘""")


# ── Main loop ─────────────────────────────────────────────────────────────

def main():
    print_banner()

    lot = ParkingLot(
        name="City Centre Parking",
        # Uncomment below to customise slots; otherwise uses default layout.
        # slot_config=[("A1","General"),("A2","Covered"),("B1","EV")]
    )

    while True:
        print_menu()
        choice = input("  Your choice: ").strip()

        if choice == "1":
            try:
                vehicle  = get_vehicle_from_user()
                pref     = get_slot_preference()
                lot.park_vehicle(vehicle, preferred_slot_type=pref)
            except (ValueError, RuntimeError) as e:
                print(f"\n  ❌  {e}")

        elif choice == "2":
            plate = input("\n  Enter license plate to exit: ").strip().upper()
            try:
                lot.exit_vehicle(plate)
            except (ValueError, RuntimeError) as e:
                print(f"\n  ❌  {e}")

        elif choice == "3":
            lot.display_available_slots()

        elif choice == "4":
            lot.display_active_vehicles()

        elif choice == "5":
            lot.generate_report()

        elif choice == "6":
            print("\n  👋  Goodbye! Drive safe.\n")
            break

        else:
            print("  ⚠️  Invalid option. Please choose 1–6.")


if __name__ == "__main__":
    main()
