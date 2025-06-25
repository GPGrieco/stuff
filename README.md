# Safety Management Suite

This application provides several tools for managing hazards, patrols, incidents, and inventory.
It is built with Tkinter and stores data in a local SQLite database. The main features include:

- **Hazard Mapping & Reporting** – log hazard locations on an interactive map, filter them by severity and status, and export reports.
- **Patrol Scheduling & Incident Logging** – maintain patrol shifts and record incidents with optional photos and location data.
- **Equipment & Resource Tracking** – manage inventory items, record check‑outs/returns, and view transaction history.

## Requirements

- Python 3.x
- `tkinter` (usually included with Python)
- `tkcalendar`
- `tkintermapview`
- `reportlab`

Install the additional packages using pip:

```bash
pip install tkcalendar tkintermapview reportlab
```

## Running the Application

1. Ensure dependencies are installed.
2. Run the application:

```bash
python main.py
```

The database is created automatically (`safety_app.db`) on first run.
