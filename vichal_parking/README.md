# Vichal Parking Management System

A simple **Vehicle Parking Management System** built using **pure Python and Django**
(no SQL / database used — all data is stored and managed using in-memory Python
data structures: dictionaries and lists).

## Features

- **Dashboard** — live view of all parking slots (free/occupied) + summary stats
  (total slots, available, occupied, total revenue)
- **Vehicle Entry** — register a new vehicle, automatically allocate the next
  free slot, handles "parking full" and "already parked" cases
- **Vehicle Exit & Billing** — process exit, calculate fee based on duration
  and vehicle type, free up the slot, generate a bill
- **Reports** — full history of completed visits with entry/exit time,
  duration, and amount charged

## Tech Stack

- **Python 3** — all business logic (slot allocation, billing calculation)
- **Django** — web framework (views, URL routing, templates, forms, messages)
- **No database / SQL** — data lives in Python dict/list structures in
  `parking/data.py` for the lifetime of the server process

## Project Structure

```
vichal_parking/
├── manage.py
├── vichal_parking/          # project settings & root urls
│   ├── settings.py
│   ├── urls.py
├── parking/                 # main app
│   ├── data.py              # in-memory data store + business logic (pure Python)
│   ├── views.py             # Django views
│   ├── urls.py               # app-level URL routes
│   └── templates/parking/
│       ├── base.html
│       ├── home.html
│       ├── entry_form.html
│       ├── exit_form.html
│       └── reports.html
```

## How the logic works

- `parking_slots` — a dict of slot_id -> {occupied, vehicle_type, vehicle_number}
- `vehicles` — a dict of currently parked vehicles, keyed by vehicle number
- `history` — a list of completed visit records (used for reports)
- `RATE_PER_HOUR` — dict mapping vehicle type to hourly rate (car ₹20, bike ₹10, truck ₹40)
- Minimum billing is 1 hour even for short stays.

All of this lives in `parking/data.py` and is imported by `views.py` —
this is the part of the project that demonstrates core Python skills
(functions, dictionaries, datetime handling) on top of the Django framework.

## Setup & Run

```bash
# 1. Install Django
pip install django

# 2. Apply Django's built-in migrations (for admin/auth/sessions — 
#    NOT used for parking data, only Django's internal framework tables)
python manage.py migrate

# 3. Run the development server
python manage.py runserver

# 4. Open in browser
http://127.0.0.1:8000/
```

## Notes for Interview Discussion

- Since the requirement was **Python + Django only**, this project intentionally
  avoids Django's ORM/database layer for the parking data itself, and instead
  uses plain Python data structures — a good way to demonstrate strong core
  Python fundamentals (functions, dict/list manipulation, datetime arithmetic)
  while still showing Django skills (MVT pattern, URL routing, template
  inheritance, Django forms/messages framework).
- Trade-off to mention: in-memory data resets every time the server restarts,
  and won't work across multiple server processes. In a production setting,
  this would be replaced with Django models + a real database (SQLite/MySQL/PostgreSQL).
- Possible extensions to mention in an interview: add Django authentication
  for admin/staff login, switch to Django ORM models for persistence, add
  REST API endpoints (Django REST Framework), add unit tests for the billing logic.
