import tkinter as tk
from tkinter import ttk
from database import init_db
from modules.hazard_map import HazardMapFrame
from modules.patrol import PatrolFrame
from modules.inventory import InventoryFrame


class SafetyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Safety Management Suite")
        self.geometry("1200x800")

        # Initialize database
        init_db()

        # Setup notebook (tabs)
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True)

        # Hazard Mapping & Reporting Tool tab
        hazard_frame = HazardMapFrame(notebook)
        notebook.add(hazard_frame, text="Hazards")

        # Patrol Scheduling & Incident Log tab
        patrol_frame = PatrolFrame(notebook)
        notebook.add(patrol_frame, text="Patrols & Incidents")

        # Equipment & Resource Tracker tab
        inventory_frame = InventoryFrame(notebook)
        notebook.add(inventory_frame, text="Inventory")


if __name__ == "__main__":
    app = SafetyApp()
    app.mainloop()
