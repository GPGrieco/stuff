# Safety Management Suite

This application provides several tools for managing hazards, patrols, incidents, and inventory.
It is built with Tkinter and stores data in a local SQLite database. The main features include:

- **Hazard Mapping & Reporting** – log hazard locations on an interactive map, filter them by severity and status, and export reports.
- **Patrol Scheduling & Incident Logging** – maintain patrol shifts and record incidents with optional photos and location data.
- **Equipment & Resource Tracking** – manage inventory items with supplier info, record check‑outs/returns with photos, highlight low stock and optionally email alerts (set `ALERT_EMAIL` env var), and view transaction history.

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

Set the `ALERT_EMAIL` environment variable if you want low-stock warnings sent to that address (requires a local SMTP server).

### Inventory Reports

- CSV export respects the current search filters.
- PDF export prompts for a date range and includes all check-in/out transactions for that period.
