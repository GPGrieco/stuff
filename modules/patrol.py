import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import Calendar
import sqlite3, os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from database import DB_FILE


class PatrolFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Split pane: left=calendar, right=roster & incident log
        self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill='both', expand=True)

        # Calendar view frame
        cal_frame = ttk.Frame(self.paned, width=300)
        self.calendar = Calendar(cal_frame, selectmode='day')
        self.calendar.pack(fill='both', expand=True)
        self.calendar.bind("<<CalendarSelected>>", self.on_date_selected)
        self.paned.add(cal_frame)

        # Right frame as Notebook for roster and incidents
        right_nb = ttk.Notebook(self.paned)
        self.paned.add(right_nb)

        # -- Roster Tab --
        roster_tab = ttk.Frame(right_nb)
        right_nb.add(roster_tab, text="Roster")
        cols = ("Shift ID","Date","Time","Crew")
        self.roster_tree = ttk.Treeview(roster_tab, columns=cols, show='headings')
        for col in cols:
            self.roster_tree.heading(col, text=col)
            self.roster_tree.column(col, width=100)
        self.roster_tree.pack(fill='both', expand=True, pady=5)

        btn_frame = ttk.Frame(roster_tab)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Add Shift", command=self.add_shift).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Delete Shift", command=self.delete_shift).pack(side='left', padx=2)
        self.load_shifts()

        # -- Incidents Tab --
        incident_tab = ttk.Frame(right_nb)
        right_nb.add(incident_tab, text="Incidents")
        cols2 = ("ID","Shift","Category","Description","Date")
        self.inc_tree = ttk.Treeview(incident_tab, columns=cols2, show='headings')
        for col in cols2:
            self.inc_tree.heading(col, text=col)
            self.inc_tree.column(col, width=80 if col in ('ID','Shift') else 120)
        self.inc_tree.pack(fill='both', expand=True, pady=5)

        btn_inc = ttk.Frame(incident_tab)
        btn_inc.pack(fill='x', pady=5)
        ttk.Button(btn_inc, text="Log Incident", command=self.log_incident).pack(side='left', padx=2)
        ttk.Button(btn_inc, text="Delete Incident", command=self.delete_incident).pack(side='left', padx=2)
        ttk.Button(btn_inc, text="Export CSV", command=self.export_inc_csv).pack(side='left', padx=2)
        ttk.Button(btn_inc, text="Export PDF", command=self.export_inc_pdf).pack(side='left', padx=2)
        self.load_incidents()

    def on_date_selected(self, event):
        # Called when a date is selected in the calendar.
        # For simplicity, refresh both shifts and incidents to reflect selected date if desired.
        # Currently, just reload lists (could filter by date later).
        self.load_shifts()
        self.load_incidents()

    def db_connect(self):
        return sqlite3.connect(DB_FILE)

    def load_shifts(self):
        for r in self.roster_tree.get_children():
            self.roster_tree.delete(r)
        conn = self.db_connect(); c = conn.cursor()
        selected_date = self.calendar.get_date()
        # Load only shifts matching selected date
        c.execute("SELECT shift_id, date, time_slot, crew FROM Shifts WHERE date=? ORDER BY time_slot", (selected_date,))
        for row in c.fetchall():
            self.roster_tree.insert('', 'end', values=row)
        conn.close()

    def add_shift(self):
        win = tk.Toplevel(self)
        win.title("Add Shift")
        ttk.Label(win, text="Date (YYYY-MM-DD):").grid(row=0, column=0)
        date_var = tk.StringVar(value=self.calendar.get_date())
        ttk.Entry(win, textvariable=date_var).grid(row=0, column=1)
        ttk.Label(win, text="Time Slot:").grid(row=1, column=0)
        time_var = tk.StringVar()
        ttk.Entry(win, textvariable=time_var).grid(row=1, column=1)
        ttk.Label(win, text="Crew:").grid(row=2, column=0)
        crew_var = tk.StringVar()
        ttk.Entry(win, textvariable=crew_var).grid(row=2, column=1)

        def save():
            conn = self.db_connect(); c = conn.cursor()
            c.execute("INSERT INTO Shifts(date,time_slot,crew) VALUES(?,?,?)",
                      (date_var.get(), time_var.get(), crew_var.get()))
            conn.commit(); conn.close()
            win.destroy(); self.load_shifts()

        ttk.Button(win, text="Save", command=save).grid(row=3, column=1, pady=5)

    def delete_shift(self):
        sel = self.roster_tree.selection()
        if not sel: return
        sid = self.roster_tree.item(sel[0])['values'][0]
        if not messagebox.askyesno("Confirm", "Delete selected shift?" ): return
        conn = self.db_connect(); c = conn.cursor()
        c.execute("DELETE FROM Shifts WHERE shift_id=?", (sid,))
        conn.commit(); conn.close()
        self.load_shifts(); self.load_incidents()

    def load_incidents(self):
        for r in self.inc_tree.get_children():
            self.inc_tree.delete(r)
        conn = self.db_connect(); c = conn.cursor()
        selected_date = self.calendar.get_date()
        # Load incidents for selected date
        c.execute("SELECT incident_id, shift_id, category, description, timestamp FROM Incidents WHERE DATE(timestamp)=? ORDER BY timestamp", (selected_date,))
        for iid, sid, cat, desc, ts in c.fetchall():
            self.inc_tree.insert('', 'end', values=(iid, sid, cat, desc[:20], ts.split('T')[0]))
        conn.close()

    def log_incident(self):
        win = tk.Toplevel(self)
        win.title("Log Incident")
        ttk.Label(win, text="Shift ID:").grid(row=0, column=0)
        sid_var = tk.StringVar()
        shifts = [str(r[0]) for r in self.db_connect().cursor().execute("SELECT shift_id FROM Shifts").fetchall()]
        ttk.Combobox(win, textvariable=sid_var, values=shifts).grid(row=0, column=1)
        ttk.Label(win, text="Category:").grid(row=1, column=0)
        cat_var = tk.StringVar()
        ttk.Combobox(win, textvariable=cat_var, values=["Trespasser","Fence Damage","Other"]).grid(row=1, column=1)
        ttk.Label(win, text="Description:").grid(row=2, column=0)
        desc_txt = tk.Text(win, width=40, height=4); desc_txt.grid(row=2, column=1)

        photo_path = [None]
        def add_photo():
            p = filedialog.askopenfilename(filetypes=[("Images","*.jpg *.png")])
            if p:
                dest = os.path.join("images", f"incident_{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(p)[1]}")
                os.makedirs("images", exist_ok=True)
                with open(p, 'rb') as fr, open(dest, 'wb') as fw: fw.write(fr.read())
                photo_path[0] = dest
                ttk.Label(win, text=os.path.basename(dest)).grid(row=3, column=1)
        ttk.Button(win, text="Add Photo", command=add_photo).grid(row=3, column=0)

        ttk.Label(win, text="Latitude:").grid(row=4, column=0)
        lat_var = tk.StringVar(); ttk.Entry(win, textvariable=lat_var).grid(row=4, column=1)
        ttk.Label(win, text="Longitude:").grid(row=5, column=0)
        lon_var = tk.StringVar(); ttk.Entry(win, textvariable=lon_var).grid(row=5, column=1)

        def save():
            ts = datetime.now().isoformat()
            conn = self.db_connect(); c = conn.cursor()
            c.execute("INSERT INTO Incidents(shift_id,category,description,photo_path,latitude,longitude,timestamp) VALUES(?,?,?,?,?,?,?)",
                      (sid_var.get(), cat_var.get(), desc_txt.get("1.0","end").strip(), photo_path[0], lat_var.get() or None, lon_var.get() or None, ts))
            conn.commit(); conn.close()
            win.destroy(); self.load_incidents()
        ttk.Button(win, text="Save", command=save).grid(row=6, column=1, pady=5)

    def delete_incident(self):
        sel = self.inc_tree.selection()
        if not sel: return
        iid = self.inc_tree.item(sel[0])['values'][0]
        if not messagebox.askyesno("Confirm", "Delete selected incident?"): return
        conn = self.db_connect(); c = conn.cursor()
        c.execute("DELETE FROM Incidents WHERE incident_id=?", (iid,))
        conn.commit(); conn.close()
        self.load_incidents()

    def export_inc_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not path: return
        conn = self.db_connect(); c = conn.cursor()
        c.execute("SELECT * FROM Incidents")
        rows = c.fetchall()
        with open(path, "w", newline="") as f:
            import csv
            w = csv.writer(f)
            w.writerow([col[0] for col in c.description])
            w.writerows(rows)
        conn.close()
        messagebox.showinfo("Export CSV", f"Exported {len(rows)} incidents to {path}")

    def export_inc_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf")])
        if not path: return
        c = canvas.Canvas(path, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica", 14)
        c.drawString(40, height - 40, "Incident Report")
        y = height - 80
        conn = self.db_connect(); cur = conn.cursor()
        cur.execute("SELECT incident_id,shift_id,category,description,timestamp FROM Incidents")
        for iid, sid, cat, desc, ts in cur.fetchall():
            text = f"ID:{iid} | Shift:{sid} | {cat} | {desc[:30]} | {ts.split('T')[0]}"
            c.drawString(40, y, text)
            y -= 20
            if y < 40:
                c.showPage(); y = height - 40
        conn.close(); c.save()
        messagebox.showinfo("Export PDF", f"PDF saved to {path}")
