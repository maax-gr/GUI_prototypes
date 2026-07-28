import json
import os
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox


class BookingPrototypeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interaktive Buchungsmaske (PoC)")
        self.root.geometry("980x720")
        self.root.minsize(900, 680)

        self.data_file = Path(__file__).with_name("bookings.json")
        self.data = self._load_data()

        self.current_receipt = ""
        self.current_booking = None

        self._build_ui()
        self._show_start_screen()

    def _load_data(self):
        if self.data_file.exists():
            try:
                with self.data_file.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    if isinstance(data, dict):
                        return data
            except json.JSONDecodeError:
                pass

        return {"next_receipt_number": 1000, "bookings": []}

    def _save_data(self):
        with self.data_file.open("w", encoding="utf-8") as fh:
            json.dump(self.data, fh, indent=2, ensure_ascii=False)

    def _build_ui(self):
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill="both", expand=True)

        self.header = ttk.Label(
            self.main_frame,
            text="Bank-Booking Prototype",
            font=("Segoe UI", 18, "bold"),
        )
        self.header.pack(anchor="w", pady=(0, 12))

        self.status_var = tk.StringVar(value="Bereit")
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, foreground="#1f4e79")
        self.status_bar.pack(anchor="w", pady=(0, 8))

        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True)

        self.start_frame = ttk.LabelFrame(self.content_frame, text="Beleg-Start", padding=16)
        self.start_frame.pack(fill="x", pady=(0, 12))

        self.receipt_label = ttk.Label(self.start_frame, text="Belegnummer")
        self.receipt_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=4)
        self.receipt_entry = ttk.Entry(self.start_frame, width=20)
        self.receipt_entry.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=4)
        self.enter_button = ttk.Button(self.start_frame, text="Enter", command=self.on_enter_click)
        self.enter_button.grid(row=0, column=2, sticky="w", pady=4)

        self.start_frame.columnconfigure(3, weight=1)

        self.form_frame = ttk.LabelFrame(self.content_frame, text="Buchungsdetails", padding=16)
        self.form_frame.pack(fill="both", expand=True)

        self.form_frame.grid_columnconfigure(0, weight=1)
        self.form_frame.grid_columnconfigure(1, weight=1)

        self.fields = {}
        row = 0
        for label, key, widget_type, kwargs in [
            ("Start-Konto", "start_account", "entry", {"width": 24}),
            ("Start-System", "start_system", "combo", {"values": ["ORAG", "KK", "GNB"], "state": "readonly"}),
            ("Ziel-Konto", "target_account", "entry", {"width": 24}),
            ("Ziel-System", "target_system", "combo", {"values": ["ORAG", "KK", "GNB"], "state": "readonly"}),
            ("Wertstellung", "value_date", "entry", {"width": 24}),
            ("Betrag", "amount", "entry", {"width": 24}),
            ("Leistungsart", "service_type", "entry", {"width": 24}),
        ]:
            ttk.Label(self.form_frame, text=label).grid(row=row, column=0, sticky="w", pady=4)
            if widget_type == "entry":
                entry = ttk.Entry(self.form_frame, **kwargs)
                entry.grid(row=row, column=1, sticky="ew", pady=4)
                self.fields[key] = entry
            else:
                combo = ttk.Combobox(self.form_frame, **kwargs)
                combo.grid(row=row, column=1, sticky="ew", pady=4)
                self.fields[key] = combo
            row += 1

        self.fields["start_system"].set("ORAG")
        self.fields["target_system"].set("KK")
        self.fields["value_date"].insert(0, datetime.now().strftime("%d.%m.%Y"))

        self.actions_frame = ttk.Frame(self.form_frame)
        self.actions_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        self.actions_frame.grid_columnconfigure(0, weight=1)
        self.actions_frame.grid_columnconfigure(1, weight=1)
        self.actions_frame.grid_columnconfigure(2, weight=1)

        self.release_button = ttk.Button(self.actions_frame, text="Zur Kontrolle freigeben", command=self.on_release_click)
        self.release_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.next_step_button = ttk.Button(self.actions_frame, text="Weiteren Buchungsschritt buchen", command=self.on_next_step_click)
        self.next_step_button.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.abort_button = ttk.Button(self.actions_frame, text="Abbruch", command=self.on_abort_click)
        self.abort_button.grid(row=0, column=2, sticky="ew")

        self.summary_frame = ttk.LabelFrame(self.content_frame, text="Beleg-Übersicht", padding=12)
        self.summary_frame.pack(fill="both", expand=True, pady=(12, 0))

        self.summary_text = tk.Text(self.summary_frame, height=10, wrap="word", state="disabled")
        self.summary_text.pack(fill="both", expand=True)

    def _show_start_screen(self):
        self.current_receipt = ""
        self.receipt_entry.delete(0, tk.END)
        self._set_form_state(False)
        self._refresh_summary()
        self.status_var.set("Bitte Belegnummer eingeben oder Enter drücken")

    def _set_form_state(self, enabled):
        for widget in self.fields.values():
            if hasattr(widget, "config"):
                widget.config(state="normal" if enabled else "disabled")
        self.release_button.config(state="normal" if enabled else "disabled")
        self.next_step_button.config(state="normal" if enabled else "disabled")
        self.abort_button.config(state="normal" if enabled else "disabled")

        if not enabled:
            for widget in self.fields.values():
                if hasattr(widget, "delete"):
                    widget.delete(0, tk.END)
            self.fields["value_date"].insert(0, datetime.now().strftime("%d.%m.%Y"))
            self.fields["start_system"].set("ORAG")
            self.fields["target_system"].set("KK")

    def _refresh_summary(self):
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", tk.END)
        entries = [item for item in self.data.get("bookings", []) if item.get("receipt_number") == self.current_receipt]
        if not entries:
            self.summary_text.insert("1.0", "Noch keine Buchungen für diesen Beleg vorhanden.\n")
        else:
            for idx, item in enumerate(entries, 1):
                self.summary_text.insert(
                    "end",
                    f"{idx}. {item['value_date']} | {item['start_account']} -> {item['target_account']} | {item['amount']} EUR | Status: {item['status']}\n",
                )
        self.summary_text.configure(state="disabled")

    def on_enter_click(self):
        receipt_text = self.receipt_entry.get().strip()
        if receipt_text:
            self.current_receipt = receipt_text
        else:
            self.current_receipt = str(self.data.get("next_receipt_number", 1000))
            self.receipt_entry.delete(0, tk.END)
            self.receipt_entry.insert(0, self.current_receipt)
            self.data["next_receipt_number"] = int(self.current_receipt) + 1
            self._save_data()

        self._set_form_state(True)
        self._refresh_summary()
        self.status_var.set(f"Beleg {self.current_receipt} aktiv")

    def _collect_form_values(self):
        values = {key: widget.get().strip() for key, widget in self.fields.items()}
        return values

    def _validate_form(self, values):
        if not values["start_account"] or not values["target_account"]:
            raise ValueError("Start- und Ziel-Konto müssen ausgefüllt sein.")
        if len(values["start_account"]) != 8 or not values["start_account"].isdigit():
            raise ValueError("Start-Konto muss genau 8 Stellen und numerisch sein.")
        if len(values["target_account"]) != 8 or not values["target_account"].isdigit():
            raise ValueError("Ziel-Konto muss genau 8 Stellen und numerisch sein.")
        if not values["amount"]:
            raise ValueError("Betrag muss angegeben werden.")
        try:
            float(values["amount"].replace(",", "."))
        except ValueError as exc:
            raise ValueError("Betrag muss eine gültige Zahl sein.") from exc
        try:
            datetime.strptime(values["value_date"], "%d.%m.%Y")
        except ValueError as exc:
            raise ValueError("Wertstellung muss im Format DD.MM.YYYY angegeben werden.") from exc
        if not values["service_type"].isdigit() or not (1 <= len(values["service_type"]) <= 3):
            raise ValueError("Leistungsart muss 1 bis 3 Ziffern enthalten.")
        return True

    def on_release_click(self):
        values = self._collect_form_values()
        try:
            self._validate_form(values)
        except ValueError as exc:
            messagebox.showerror("Eingabe prüfen", str(exc))
            return

        self.current_booking = {
            "receipt_number": self.current_receipt,
            "start_account": values["start_account"],
            "start_system": values["start_system"],
            "target_account": values["target_account"],
            "target_system": values["target_system"],
            "value_date": values["value_date"],
            "amount": values["amount"].replace(",", "."),
            "service_type": values["service_type"],
            "status": "freigegeben",
            "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        }
        self._open_summary_window()

    def _open_summary_window(self):
        window = tk.Toplevel(self.root)
        window.title(f"Zusammenfassung Beleg {self.current_receipt}")
        window.geometry("720x480")

        ttk.Label(window, text="Zusammenfassung der Buchung", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=16, pady=(12, 8))

        fields_frame = ttk.LabelFrame(window, text="Buchungsdaten", padding=12)
        fields_frame.pack(fill="x", padx=16, pady=(0, 12))

        for label, value in [
            ("Belegnummer", self.current_receipt),
            ("Start-Konto", self.current_booking["start_account"]),
            ("Start-System", self.current_booking["start_system"]),
            ("Ziel-Konto", self.current_booking["target_account"]),
            ("Ziel-System", self.current_booking["target_system"]),
            ("Wertstellung", self.current_booking["value_date"]),
            ("Betrag", self.current_booking["amount"]),
            ("Leistungsart", self.current_booking["service_type"]),
        ]:
            row = ttk.Frame(fields_frame)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=f"{label}:", width=18, anchor="w").pack(side="left")
            ttk.Label(row, text=value, width=40, anchor="w").pack(side="left")

        table_frame = ttk.LabelFrame(window, text="Buchhaltung", padding=10)
        table_frame.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        columns = ("konto", "soll_haben", "betrag")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=4)
        tree.heading("konto", text="Konto")
        tree.heading("soll_haben", text="Soll/Haben")
        tree.heading("betrag", text="Betrag")
        tree.column("konto", width=180, anchor="center")
        tree.column("soll_haben", width=100, anchor="center")
        tree.column("betrag", width=120, anchor="center")
        tree.pack(fill="both", expand=True)

        tree.insert("", "end", values=(self.current_booking["start_account"], "Soll", self.current_booking["amount"]))
        tree.insert("", "end", values=(self.current_booking["target_account"], "Haben", self.current_booking["amount"]))

        actions = ttk.Frame(window)
        actions.pack(fill="x", padx=16, pady=(0, 12))
        ttk.Button(actions, text="Freigeben", command=lambda: self.confirm_release(window)).pack(side="right")

    def confirm_release(self, window):
        self.data.setdefault("bookings", []).append(self.current_booking)
        self._save_data()
        window.destroy()
        self._refresh_summary()
        self._set_form_state(False)
        self.current_booking = None
        self.receipt_entry.delete(0, tk.END)
        self.receipt_entry.insert(0, self.current_receipt)
        self.status_var.set("Buchung freigegeben")
        messagebox.showinfo("Erfolg", "Buchung wurde freigegeben und gespeichert.")

    def on_next_step_click(self):
        values = self._collect_form_values()
        try:
            self._validate_form(values)
        except ValueError as exc:
            messagebox.showerror("Eingabe prüfen", str(exc))
            return

        self.fields["start_account"].delete(0, tk.END)
        self.fields["start_account"].insert(0, values["target_account"])
        self.fields["start_system"].set(values["target_system"])
        self.fields["target_account"].delete(0, tk.END)
        self.fields["target_system"].set("KK")
        self.fields["value_date"].delete(0, tk.END)
        self.fields["value_date"].insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.fields["amount"].delete(0, tk.END)
        self.fields["service_type"].delete(0, tk.END)
        self.status_var.set("Weiterer Buchungsschritt vorbereitet")

    def on_abort_click(self):
        self._show_start_screen()
        self.status_var.set("Vorgang abgebrochen")


if __name__ == "__main__":
    root = tk.Tk()
    app = BookingPrototypeApp(root)
    root.mainloop()
