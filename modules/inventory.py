import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import sqlite3, os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from database import DB_FILE


class InventoryFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Top controls: search and actions
        control_frame = ttk.Frame(self)
        control_frame.pack(fill='x', pady=5)
        ttk.Label(control_frame, text="Search:").pack(side='left')
        self.search_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.search_var, width=30).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Go", command=self.load_items).pack(side='left')
        ttk.Button(control_frame, text="Add Item", command=self.add_item).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Edit Item", command=self.edit_item).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Delete Item", command=self.delete_item).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Check-Out", command=self.check_out_item).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Return", command=self.return_item).pack(side='left', padx=5)
        ttk.Button(control_frame, text="View History", command=self.view_history).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Export CSV", command=self.export_items_csv).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Export PDF", command=self.export_items_pdf).pack(side='left', padx=5)

        # Inventory treeview
        cols = ("ID","Name","Category","Location","Qty","Unit","Threshold","Supplier")
        self.tree = ttk.Treeview(self, columns=cols, show='headings', selectmode='browse')
        for col in cols:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c, False))
            self.tree.column(col, width=100 if col=='Name' else 60)
        self.tree.pack(fill='both', expand=True)

        # Style for low stock
        self.tree.tag_configure('low', background='#ffcccc')

        self.load_items()

    def send_low_stock_email(self, message):
        addr = os.getenv('ALERT_EMAIL')
        if not addr:
            return
        from email.message import EmailMessage
        import smtplib
        email = EmailMessage()
        email['Subject'] = 'Low Stock Alert'
        email['From'] = addr
        email['To'] = addr
        email.set_content(message)
        try:
            with smtplib.SMTP('localhost') as s:
                s.send_message(email)
        except Exception as e:
            print('Failed to send alert email:', e)

    def sort_by_column(self, col, descending):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        if col in ('ID', 'Qty', 'Threshold'):
            data.sort(key=lambda t: int(t[0]), reverse=descending)
        else:
            data.sort(key=lambda t: t[0].lower(), reverse=descending)
        for index, (_, child) in enumerate(data):
            self.tree.move(child, '', index)
        self.tree.heading(col, command=lambda c=col: self.sort_by_column(c, not descending))

    def db_connect(self):
        return sqlite3.connect(DB_FILE)

    def load_items(self):
        # Clear existing
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Fetch from DB
        conn = self.db_connect(); c = conn.cursor()
        term = self.search_var.get().strip()
        if term:
            c.execute(
                "SELECT item_id,name,category,location,quantity,unit,threshold,supplier FROM Items WHERE name LIKE ? OR category LIKE ?",
                (f'%{term}%', f'%{term}%')
            )
        else:
            c.execute("SELECT item_id,name,category,location,quantity,unit,threshold,supplier FROM Items")
        rows = c.fetchall()
        low_stock = []
        for item in rows:
            tags = ()
            if item[4] <= item[6]:  # quantity <= threshold
                tags = ('low',)
                low_stock.append((item[1], item[4], item[6]))
            self.tree.insert('', 'end', values=item, tags=tags)
        conn.close()
        if low_stock:
            msg = "\n".join([f"{n}: {q} remaining (threshold {t})" for n, q, t in low_stock])
            messagebox.showwarning("Low Stock Alert", f"The following items are low:\n{msg}")
            self.send_low_stock_email(msg)

    def add_item(self):
        self._item_form()

    def edit_item(self):
        sel = self.tree.selection()
        if not sel: return
        item_id = self.tree.item(sel[0])['values'][0]
        self._item_form(item_id)

    def delete_item(self):
        sel = self.tree.selection()
        if not sel: return
        item_id = self.tree.item(sel[0])['values'][0]
        if not messagebox.askyesno("Confirm", "Delete selected item?"): return
        conn = self.db_connect(); c = conn.cursor()
        c.execute("DELETE FROM Items WHERE item_id=?", (item_id,))
        conn.commit(); conn.close()
        self.load_items()

    def _item_form(self, item_id=None):
        is_edit = item_id is not None
        win = tk.Toplevel(self)
        win.title("Edit Item" if is_edit else "Add Item")
        fields = ["Name","Category","Location","Quantity","Unit","Threshold","Supplier","Supplier Contact","Supplier SKU","Unit Cost"]
        vars = {}
        for i, f in enumerate(fields):
            ttk.Label(win, text=f+":").grid(row=i, column=0, sticky='w')
            var = tk.StringVar()
            ttk.Entry(win, textvariable=var, width=30).grid(row=i, column=1)
            vars[f] = var
        if is_edit:
            conn = self.db_connect(); c = conn.cursor()
            c.execute("SELECT name,category,location,quantity,unit,threshold,supplier,supplier_contact,supplier_sku,unit_cost FROM Items WHERE item_id=?", (item_id,))
            row = c.fetchone(); conn.close()
            for f, val in zip(fields, row):
                vars[f].set(val)
        def save():
            data = [vars[f].get() for f in fields]
            conn = self.db_connect(); c = conn.cursor()
            if is_edit:
                c.execute(
                    "UPDATE Items SET name=?,category=?,location=?,quantity=?,unit=?,threshold=?,supplier=?,supplier_contact=?,supplier_sku=?,unit_cost=? WHERE item_id=?",
                    (*data, item_id)
                )
            else:
                c.execute(
                    "INSERT INTO Items(name,category,location,quantity,unit,threshold,supplier,supplier_contact,supplier_sku,unit_cost) VALUES(?,?,?,?,?,?,?,?,?,?)",
                    data
                )
            conn.commit(); conn.close()
            win.destroy(); self.load_items()
        ttk.Button(win, text="Save", command=save).grid(row=len(fields), column=1, pady=5)

    def check_out_item(self):
        sel = self.tree.selection()
        if not sel: return
        item_id, name, *_ = self.tree.item(sel[0])['values']
        win = tk.Toplevel(self); win.title(f"Check-Out: {name}")
        ttk.Label(win, text="Person:").grid(row=0, column=0)
        person_var = tk.StringVar(); ttk.Entry(win, textvariable=person_var).grid(row=0, column=1)
        ttk.Label(win, text="Expected Return (YYYY-MM-DD):").grid(row=1, column=0)
        ret_var = tk.StringVar(); ttk.Entry(win, textvariable=ret_var).grid(row=1, column=1)
        notes_txt = tk.Text(win, width=40, height=4); notes_txt.grid(row=2, column=1)
        ttk.Label(win, text="Notes:").grid(row=2, column=0)
        photo_path = [None]
        def add_photo():
            p = filedialog.askopenfilename(filetypes=[("Images","*.jpg *.png")])
            if p:
                dest = os.path.join("images", f"trans_out_{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(p)[1]}")
                os.makedirs("images", exist_ok=True)
                with open(p,'rb') as fr, open(dest,'wb') as fw: fw.write(fr.read())
                photo_path[0] = dest
                ttk.Label(win, text=os.path.basename(dest)).grid(row=3, column=1)
        ttk.Button(win, text="Add Photo", command=add_photo).grid(row=3, column=0)
        def save():
            ts = datetime.now().isoformat()
            conn = self.db_connect(); c = conn.cursor()
            c.execute("INSERT INTO Transactions(item_id,person,out_date,expected_return_date,out_notes,out_photo,status) VALUES(?,?,?,?,?,?,?)",
                      (item_id, person_var.get(), ts, ret_var.get(), notes_txt.get("1.0","end").strip(), photo_path[0], 'out'))
            # decrement quantity
            c.execute("UPDATE Items SET quantity = quantity - 1 WHERE item_id=?", (item_id,))
            conn.commit(); conn.close()
            win.destroy(); self.load_items()
        ttk.Button(win, text="Save", command=save).grid(row=4, column=1, pady=5)

    def return_item(self):
        # select from outstanding transactions
        conn = self.db_connect(); c = conn.cursor()
        c.execute("SELECT transaction_id, item_id FROM Transactions WHERE status='out'")
        outs = c.fetchall(); conn.close()
        if not outs: return
        win = tk.Toplevel(self); win.title("Return Item")
        ttk.Label(win, text="Transaction:").grid(row=0, column=0)
        trans_var = tk.StringVar()
        vals = [f"{t[0]} (Item {t[1]})" for t in outs]
        ttk.Combobox(win, textvariable=trans_var, values=vals, width=30).grid(row=0, column=1)
        notes_txt = tk.Text(win, width=40, height=4); notes_txt.grid(row=1, column=1)
        ttk.Label(win, text="Return Notes:").grid(row=1, column=0)
        photo_path = [None]
        def add_photo():
            p = filedialog.askopenfilename(filetypes=[("Images","*.jpg *.png")])
            if p:
                dest = os.path.join("images", f"trans_in_{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(p)[1]}")
                os.makedirs("images", exist_ok=True)
                with open(p,'rb') as fr, open(dest,'wb') as fw: fw.write(fr.read())
                photo_path[0] = dest
                ttk.Label(win, text=os.path.basename(dest)).grid(row=2, column=1)
        ttk.Button(win, text="Add Photo", command=add_photo).grid(row=2, column=0)
        def save():
            sel = trans_var.get().split()[0]
            ts = datetime.now().isoformat()
            conn = self.db_connect(); c = conn.cursor()
            c.execute("UPDATE Transactions SET actual_return_date=?, return_notes=?, return_photo=?, status='returned' WHERE transaction_id=?",
                      (ts, notes_txt.get("1.0","end").strip(), photo_path[0], sel))
            # increment quantity
            # get item_id
            c.execute("SELECT item_id FROM Transactions WHERE transaction_id=?", (sel,))
            iid = c.fetchone()[0]
            c.execute("UPDATE Items SET quantity = quantity + 1 WHERE item_id=?", (iid,))
            conn.commit(); conn.close()
            win.destroy(); self.load_items()
        ttk.Button(win, text="Save", command=save).grid(row=3, column=1, pady=5)

    def view_history(self):
        sel = self.tree.selection()
        # if item selected, filter history for that item; else show all
        item_filter = None
        if sel:
            item_filter = self.tree.item(sel[0])['values'][0]
        win = tk.Toplevel(self); win.title("Transaction History")
        cols = ("Trans ID","Item","Person","Out Date","Return Date","Status")
        tree = ttk.Treeview(win, columns=cols, show='headings')
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.pack(fill='both', expand=True)
        conn = self.db_connect(); c = conn.cursor()
        if item_filter:
            c.execute("SELECT transaction_id,item_id,person,out_date,actual_return_date,status FROM Transactions WHERE item_id=? ORDER BY out_date DESC", (item_filter,))
        else:
            c.execute("SELECT transaction_id,item_id,person,out_date,actual_return_date,status FROM Transactions ORDER BY out_date DESC")
        for row in c.fetchall():
            tree.insert('', 'end', values=row)
        conn.close()

    def export_items_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not path: return
        conn = self.db_connect(); c = conn.cursor()
        term = self.search_var.get().strip()
        if term:
            c.execute("SELECT * FROM Items WHERE name LIKE ? OR category LIKE ?", (f'%{term}%', f'%{term}%'))
        else:
            c.execute("SELECT * FROM Items")
        rows = c.fetchall()
        with open(path, 'w', newline='') as f:
            import csv; w = csv.writer(f)
            w.writerow([col[0] for col in c.description])
            w.writerows(rows)
        conn.close(); messagebox.showinfo("Export CSV", f"Exported {len(rows)} items to {path}")

    def export_items_pdf(self):
        start = simpledialog.askstring("Start Date", "Start date YYYY-MM-DD (leave blank for all)")
        if start is None:
            return
        end = simpledialog.askstring("End Date", "End date YYYY-MM-DD (leave blank for all)")
        if end is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf")])
        if not path:
            return
        conn = self.db_connect(); cur = conn.cursor()
        sql = """SELECT t.transaction_id, i.name, t.person, t.out_date, t.actual_return_date, t.status
                 FROM Transactions t JOIN Items i ON t.item_id=i.item_id"""
        cond = []
        params = []
        if start:
            cond.append("date(t.out_date) >= ?")
            params.append(start)
        if end:
            cond.append("date(t.out_date) <= ?")
            params.append(end)
        if cond:
            sql += " WHERE " + " AND ".join(cond)
        sql += " ORDER BY t.out_date"
        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()

        c = canvas.Canvas(path, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica", 14)
        title = "Equipment Transactions"
        c.drawString(40, height - 40, title)
        y = height - 80
        for tid, name, person, out_d, ret_d, status in rows:
            ret = ret_d.split('T')[0] if ret_d else ''
            text = f"{out_d.split('T')[0]} | {name} | {person} | {status} | {ret}"
            c.drawString(40, y, text)
            y -= 20
            if y < 40:
                c.showPage(); y = height - 40
        c.save()
        messagebox.showinfo("Export PDF", f"PDF saved to {path}")
