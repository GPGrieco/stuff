import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkintermapview import TkinterMapView
import sqlite3, os, csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
from database import DB_FILE


class HazardMapFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Split pane: left=map, right=controls/list
        self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill='both', expand=True)

        # Map widget
        map_frame = ttk.Frame(self.paned)
        self.map_widget = TkinterMapView(map_frame, width=800, height=600, corner_radius=0)
        self.map_widget.set_position(0, 0)  # default
        self.map_widget.set_zoom(2)
        self.map_widget.pack(fill='both', expand=True)
        self.map_widget.add_left_click_map_command(self.on_map_left_click)
        self.paned.add(map_frame)

        # Control frame
        ctrl_frame = ttk.Frame(self.paned, width=400)
        self.paned.add(ctrl_frame)

        # Filter controls
        filter_frame = ttk.Frame(ctrl_frame)
        filter_frame.pack(fill='x', pady=5)
        ttk.Label(filter_frame, text="Severity:").pack(side='left')
        self.sev_var = tk.StringVar(value="All")
        cmb_sev = ttk.Combobox(
            filter_frame,
            textvariable=self.sev_var,
            values=["All", "Low", "Med", "High", "Area Closed"],
            width=12
        )
        cmb_sev.pack(side='left', padx=5)

        ttk.Label(filter_frame, text="Status:").pack(side='left')
        self.stat_var = tk.StringVar(value="All")
        cmb_stat = ttk.Combobox(
            filter_frame,
            textvariable=self.stat_var,
            values=["All", "Logged", "In Progress", "Mitigated"],
            width=12
        )
        cmb_stat.pack(side='left', padx=5)

        ttk.Button(filter_frame, text="Apply Filters", command=self.refresh_hazards).pack(side='left', padx=5)

        # List of hazards
        cols = ("ID","Description","Severity","Status","Date")
        self.tree = ttk.Treeview(ctrl_frame, columns=cols, show='headings', height=20)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80 if col=='ID' else 120)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.pack(fill='both', expand=True, pady=5)

        # Buttons
        btn_frame = ttk.Frame(ctrl_frame)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Import CSV", command=self.import_csv).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Export CSV", command=self.export_csv).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Export PDF", command=self.export_pdf).pack(side='left', padx=2)

        # Load initial hazards
        self.refresh_hazards()

    def db_connect(self):
        return sqlite3.connect(DB_FILE)

    def on_map_left_click(self, coords):
        lat, lon = coords
        # Create new hazard record
        conn = self.db_connect()
        c = conn.cursor()
        date_reported = datetime.now().isoformat()
        c.execute("INSERT INTO Hazards (latitude,longitude,description,severity,status,date_reported) VALUES (?,?,?,?,?,?)",
                  (lat, lon, "", "Low", "Logged", date_reported))
        hazard_id = c.lastrowid
        conn.commit()
        conn.close()
        # Add marker
        marker = self.map_widget.set_marker(lat, lon, text=f"ID:{hazard_id}")
        marker.data = hazard_id
        # tkintermapview markers expose a `command` attribute that is executed on
        # click. Use this instead of the nonexistent `set_text_marker_callback`.
        marker.command = lambda m=marker: self.open_hazard_detail(m.data)
        # Refresh list
        self.refresh_hazards()
        # Open detail form
        self.open_hazard_detail(hazard_id)

    def refresh_hazards(self):
        # Clear map markers and tree
        self.map_widget.delete_all_marker()
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Query DB
        conn = self.db_connect(); c = conn.cursor()
        sql = "SELECT id,latitude,longitude,description,severity,status,date_reported FROM Hazards"
        filters = []
        if self.sev_var.get() != "All":
            filters.append(f"severity = '{self.sev_var.get()}'")
        if self.stat_var.get() != "All":
            filters.append(f"status = '{self.stat_var.get()}'")
        if filters:
            sql += " WHERE " + " AND ".join(filters)
        c.execute(sql)
        for hid,lat,lon,desc,sev,stat,dt in c.fetchall():
            # Add to tree
            self.tree.insert('', 'end', values=(hid, desc[:20], sev, stat, dt.split('T')[0]))
            # Add marker
            m = self.map_widget.set_marker(lat, lon, text=f"ID:{hid}")
            m.data = hid
            # Configure the click callback using the marker's `command` attribute.
            m.command = lambda m=m: self.open_hazard_detail(m.data)
        conn.close()

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        hid = self.tree.item(sel[0])['values'][0]
        # Center map
        conn = self.db_connect(); c = conn.cursor()
        c.execute("SELECT latitude,longitude FROM Hazards WHERE id=?", (hid,))
        row = c.fetchone(); conn.close()
        if row:
            self.map_widget.set_position(row[0], row[1], zoom=15)
            self.open_hazard_detail(hid)

    def open_hazard_detail(self, hazard_id):
        # Fetch hazard data
        conn = self.db_connect(); c = conn.cursor()
        c.execute("SELECT * FROM Hazards WHERE id=?", (hazard_id,))
        data = c.fetchone(); conn.close()
        if not data: return
        # Detail window
        win = tk.Toplevel(self)
        win.title(f"Hazard {hazard_id} Details")
        # Description
        ttk.Label(win, text="Description:").grid(row=0, column=0, sticky='w')
        desc_var = tk.StringVar(value=data[3])
        ttk.Entry(win, textvariable=desc_var, width=50).grid(row=0, column=1, columnspan=3, pady=2)
        # Severity
        ttk.Label(win, text="Severity:").grid(row=1, column=0, sticky='w')
        sev_var = tk.StringVar(value=data[4])
        ttk.Combobox(win, textvariable=sev_var, values=["Low","Med","High","Area Closed"]).grid(row=1, column=1)
        # Status
        ttk.Label(win, text="Status:").grid(row=1, column=2, sticky='w')
        stat_var = tk.StringVar(value=data[5])
        ttk.Combobox(win, textvariable=stat_var, values=["Logged","In Progress","Mitigated"]).grid(row=1, column=3)
        # Photo upload button
        photo_frame = ttk.Frame(win)
        photo_frame.grid(row=2, column=0, columnspan=4, pady=5)
        photo_paths = []
        def add_photo():
            path = filedialog.askopenfilename(filetypes=[("Images","*.jpg *.png *.jpeg")])
            if path:
                dest = os.path.join("images", f"hazard_{hazard_id}_{len(photo_paths)}" + os.path.splitext(path)[1])
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(path, 'rb') as fr, open(dest, 'wb') as fw:
                    fw.write(fr.read())
                photo_paths.append(dest)
                ttk.Label(photo_frame, text=os.path.basename(dest)).pack(side='left', padx=2)
        ttk.Button(win, text="Add Photo", command=add_photo).grid(row=2, column=4)
        # TODO: Display mitigation notes (list) and allow adding notes
        # Save button
        def save():
            conn = self.db_connect(); c = conn.cursor()
            c.execute("UPDATE Hazards SET description=?,severity=?,status=? WHERE id=?",
                      (desc_var.get(), sev_var.get(), stat_var.get(), hazard_id))
            conn.commit(); conn.close()
            win.destroy(); self.refresh_hazards()
        ttk.Button(win, text="Save", command=save).grid(row=10, column=3, pady=10)

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV","*.csv")])
        if not path: return
        conn = self.db_connect(); c = conn.cursor()
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                c.execute("INSERT INTO Hazards (latitude,longitude,description,severity,status,date_reported) VALUES (?,?,?,?,?,?)",
                          (float(row['latitude']), float(row['longitude']), row.get('description',''),
                           row.get('severity','Low'), row.get('status','Logged'), row.get('date_reported',datetime.now().isoformat())))
        conn.commit(); conn.close(); self.refresh_hazards()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[("CSV","*.csv")])
        if not path: return
        # get current filtered hazards
        conn = self.db_connect(); c = conn.cursor()
        sql = "SELECT * FROM Hazards"
        filters = []
        if self.sev_var.get() != "All": filters.append(f"severity = '{self.sev_var.get()}'")
        if self.stat_var.get() != "All": filters.append(f"status = '{self.stat_var.get()}'")
        if filters: sql += " WHERE " + " AND ".join(filters)
        c.execute(sql)
        rows = c.fetchall(); conn.close()
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([d[0] for d in c.description])
            writer.writerows(rows)
        messagebox.showinfo("Export CSV", f"Exported {len(rows)} hazards to {path}")

    def export_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=[("PDF","*.pdf")])
        if not path: return
        c = canvas.Canvas(path, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica", 14)
        c.drawString(40, height - 40, "Hazard Report")
        y = height - 80
        conn = self.db_connect(); cur = conn.cursor()
        cur.execute("SELECT id,description,severity,status,date_reported FROM Hazards")
        for hid,desc,sev,stat,dt in cur.fetchall():
            text = f"ID:{hid} | {desc[:30]} | {sev} | {stat} | {dt.split('T')[0]}"
            c.drawString(40, y, text)
            y -= 20
            if y < 40:
                c.showPage()
                y = height - 40
        conn.close()
        c.save()
        messagebox.showinfo("Export PDF", f"PDF report saved to {path}")
