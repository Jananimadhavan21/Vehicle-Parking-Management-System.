from django.shortcuts import render, redirect
from django.contrib import messages

from . import data


def home(request):
    """Landing page / dashboard with live slot status and stats."""
    context = {
        "slots": data.parking_slots,
        "stats": data.get_dashboard_stats(),
    }
    return render(request, "parking/home.html", context)


def vehicle_entry(request):
    """Form to register a new vehicle entry and allocate a slot."""
    if request.method == "POST":
        vehicle_number = request.POST.get("vehicle_number", "")
        vehicle_type = request.POST.get("vehicle_type", "car")

        if not vehicle_number:
            messages.error(request, "Vehicle number is required.")
            return redirect("vehicle_entry")

        result = data.allocate_slot(vehicle_number, vehicle_type)

        if result == "ALREADY_PARKED":
            messages.error(request, f"Vehicle {vehicle_number.upper()} is already parked.")
            return redirect("vehicle_entry")

        if result is None:
            messages.error(request, "Sorry, parking is full. No slots available.")
            return redirect("vehicle_entry")

        messages.success(
            request,
            f"Vehicle {vehicle_number.upper()} parked successfully in Slot {result}."
        )
        return redirect("home")

    return render(request, "parking/entry_form.html")


def vehicle_exit(request):
    """Form to process a vehicle exit and generate the bill."""
    bill = None

    if request.method == "POST":
        vehicle_number = request.POST.get("vehicle_number", "")
        record = data.process_exit(vehicle_number)

        if record is None:
            messages.error(request, f"Vehicle {vehicle_number.upper()} not found in parking.")
            return redirect("vehicle_exit")

        bill = record

    return render(request, "parking/exit_form.html", {"bill": bill})


def reports(request):
    """Show parking history / completed visits report."""
    context = {
        "history": list(reversed(data.history)),
        "stats": data.get_dashboard_stats(),
    }
    return render(request, "parking/reports.html", context)
