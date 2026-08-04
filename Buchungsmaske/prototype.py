import csv
import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime


class BookingPrototypeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interaktive Buchungsmaske (PoC)")
        self.root.geometry("1100x780")
        self.root.minsize(980, 720)
        self.root.configure(bg="#f5f8ff")

        self.base_dir = Path(__file__).resolve().parent
        self.json_path = self.base_dir / "bookings.json"
        self.csv_path = self.base_dir / "bookings.csv"

        self.transactions = []
        self.current_state = "initial"
        self.current_record = {}

        self.load_transactions()
        self.build_ui()
        self.show_initial_state()

    def build_ui(self):
        self.root.configure(bg="#f8fbff")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TLabel", background="#f8fbff", foreground="#0f172a", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#f8fbff", foreground="#0f172a", font=("Segoe UI", 11, "bold"))
        style.configure("Muted.TLabel", background="#f8fbff", foreground="#64748b", font=("Segoe UI", 10))
        style.configure("TEntry", padding=4, fieldbackground="#eaf4ff")
        style.configure("TButton", padding=8, font=("Segoe UI", 10, "bold"))
        style.configure("Primary.TButton", background="#1f4ed8", foreground="white", padding=(12, 8))
        style.map("Primary.TButton", background=[("active", "#2563eb"), ("pressed", "#1d4ed8")], foreground=[("active", "white"), ("pressed", "white")])
        style.configure("Secondary.TButton", background="#e2e8f0", foreground="#0f172a", padding=(12, 8))
        style.map("Secondary.TButton", background=[("active", "#cbd5e1"), ("pressed", "#94a3b8")], foreground=[("active", "#0f172a"), ("pressed", "#0f172a")])
        style.configure("Field.TCombobox", fieldbackground="#eaf4ff", background="#ffffff")
        style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", rowheight=24)
        style.configure("Treeview.Heading", background="#dbeafe", foreground="#1f4ed8", font=("Segoe UI", 10, "bold"))

        header = tk.Frame(self.root, bg="#f8fbff", padx=18, pady=18)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        tk.Label(header, text="Interaktive Buchungsmaske", bg="#f8fbff", fg="#0f172a", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(header, text="PoC für Bank-Workflow und Buchungslogik", bg="#f8fbff", fg="#475569", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.status_var = tk.StringVar(value="Bereit")
        tk.Label(header, textvariable=self.status_var, bg="#f8fbff", fg="#0f766e", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="e")

        self.content = tk.Frame(self.root, bg="#f8fbff", padx=16, pady=16)
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

    def load_transactions(self):
        if self.json_path.exists():
            try:
                self.transactions = json.loads(self.json_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.transactions = []
        else:
            self.transactions = []

    def save_transactions(self):
        self.json_path.write_text(json.dumps(self.transactions, ensure_ascii=False, indent=2), encoding="utf-8")
        with self.csv_path.open("w", newline="", encoding="utf-8") as handle:
            fieldnames = [
                "belegnummer",
                "start_hauptkonto",
                "ziel_hauptkonto",
                "start_unterkonto",
                "ziel_unterkonto",
                "start_system",
                "ziel_system",
                "wertstellung",
                "betrag",
                "leistungsart",
                "verwendungszweck",
            ]
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for record in self.transactions:
                writer.writerow({key: record.get(key, "") for key in fieldnames})

    def show_initial_state(self):
        self.current_state = "initial"
        self.clear_content()
        self.current_record = {}

        card = tk.LabelFrame(
            self.content,
            text="Start",
            padx=18,
            pady=18,
            bg="#ffffff",
            fg="#1f4ed8",
            font=("Segoe UI", 11, "bold"),
            borderwidth=2,
            relief="solid",
            highlightbackground="#1f4ed8",
            highlightcolor="#1f4ed8",
        )
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)
        card.columnconfigure(2, weight=1)
        card.columnconfigure(3, weight=1)

        self.initial_beleg_var = tk.StringVar(value="")
        self._place_field(card, 1, 1, "Belegnummer/Vorgangsnummer", self._make_entry(parent=card, textvariable=self.initial_beleg_var, width=24))
        self._place_field(card, 1, 3, "", self._make_button(parent=card, text="Offene Vorgänge anzeigen", command=self.show_open_transactions, accent="secondary"))
        self._place_field(card, 1, 4, "", self._make_button(parent=card, text="Neuer Geschäftsvorgang", command=self.start_new_transaction, accent="primary"))

        tk.Label(card, text="Hinweis: Ein neuer Vorgang erzeugt automatisch eine eindeutige Belegnummer.", bg="#ffffff", fg="#64748b").grid(row=2, column=0, columnspan=4, sticky="w", pady=(14, 0))
        self.status_var.set("Bereit")

    def start_new_transaction(self):
        self.current_state = "editing"
        self.clear_content()
        self.current_record = {
            "belegnummer": self.generate_belegnummer(),
            "start_hauptkonto": "",
            "ziel_hauptkonto": "",
            "start_unterkonto": "",
            "ziel_unterkonto": "",
            "start_system": "",
            "ziel_system": "",
            "wertstellung": datetime.now().strftime("%d.%m.%Y"),
            "betrag": "",
            "leistungsart": "",
            "verwendungszweck": "",
        }
        self.build_form()
        self.status_var.set("Neuer Geschäftsvorgang gestartet")

    def build_form(self):
        card = tk.LabelFrame(
            self.content,
            text="Buchung erfassen",
            padx=18,
            pady=18,
            bg="#ffffff",
            fg="#1f4ed8",
            font=("Segoe UI", 11, "bold"),
            borderwidth=2,
            relief="solid",
            highlightbackground="#1f4ed8",
            highlightcolor="#1f4ed8",
        )
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)
        card.columnconfigure(2, weight=1)
        card.columnconfigure(3, weight=1)

        self.beleg_var = tk.StringVar(value=self.current_record["belegnummer"])
        self._place_field(card, 1, 1, "Belegnummer/Vorgangsnummer", self._make_entry(parent=card, textvariable=self.beleg_var, state="readonly", width=20, readonly_bg="#e5e7eb"))

        self.start_account_var = tk.StringVar(value=self.current_record["start_hauptkonto"])
        self._place_field(card, 2, 1, "Start-Hauptkonto", self._make_entry(parent=card, textvariable=self.start_account_var))

        self.start_system_var = tk.StringVar(value=self.current_record["start_system"])
        self._place_field(card, 2, 2, "Startsystem", self._make_combobox(parent=card, textvariable=self.start_system_var, values=["DaBu", "ORAG", "KK", "GNB"]))

        self.target_account_var = tk.StringVar(value=self.current_record["ziel_hauptkonto"])
        self._place_field(card, 2, 3, "Ziel-Hauptkonto", self._make_entry(parent=card, textvariable=self.target_account_var))

        self.target_system_var = tk.StringVar(value=self.current_record["ziel_system"])
        self._place_field(card, 2, 4, "Zielsystem", self._make_combobox(parent=card, textvariable=self.target_system_var, values=["DaBu", "ORAG", "KK", "GNB"]))

        self.start_subaccount_var = tk.StringVar(value=self.current_record["start_unterkonto"])
        self._place_field(card, 3, 1, "Start-Unterkonto", self._make_entry(parent=card, textvariable=self.start_subaccount_var))

        self.target_subaccount_var = tk.StringVar(value=self.current_record["ziel_unterkonto"])
        self._place_field(card, 3, 3, "Ziel-Unterkonto", self._make_entry(parent=card, textvariable=self.target_subaccount_var))

        self.amount_var = tk.StringVar(value=self.current_record["betrag"])
        self._place_field(card, 4, 1, "Betrag", self._make_entry(parent=card, textvariable=self.amount_var))

        self.value_date_var = tk.StringVar(value=self.current_record["wertstellung"])
        self._place_field(card, 4, 2, "Wertstellung", self._make_entry(parent=card, textvariable=self.value_date_var))

        self.performance_type_var = tk.StringVar(value=self.current_record["leistungsart"])
        self._place_field(card, 5, 1, "Leistungsart", self._make_entry(parent=card, textvariable=self.performance_type_var))

        self.purpose_var = tk.StringVar(value=self.current_record["verwendungszweck"])
        self._place_field(card, 5, 2, "Verwendungszweck", self._make_entry(parent=card, textvariable=self.purpose_var))

        self._place_button(card, 6, 1, "Beleg weiter bearbeiten", self.return_to_editing, accent="secondary")
        self._place_button(card, 6, 2, "Folgeschritt buchen", self.next_step, accent="secondary")
        self._place_button(card, 6, 3, "Zur Kontrolle freigeben", self.show_summary, accent="primary")
        self._place_button(card, 6, 4, "Abbruch", self.abort_transaction, accent="danger")

    def return_to_editing(self):
        self.current_state = "editing"
        self.status_var.set("Bearbeitung fortgesetzt")
        if self.current_record:
            self.current_record.update(self.collect_record_from_form())
        self.build_form()

    def next_step(self):
        if not self.validate_required_fields():
            self.status_var.set("Nicht alle Pflichtfelder sind ausgefüllt")
            return
        self.current_record.update(self.collect_record_from_form())
        self.current_record["belegnummer"] = self.current_record.get("belegnummer", "")
        self.current_record["start_hauptkonto"] = self.current_record.get("ziel_hauptkonto", "")
        self.current_record["start_system"] = self.current_record.get("ziel_system", "")
        self.current_record["start_unterkonto"] = self.current_record.get("ziel_unterkonto", "")
        self.current_record["ziel_hauptkonto"] = ""
        self.current_record["ziel_system"] = ""
        self.current_record["ziel_unterkonto"] = ""
        self.current_record["leistungsart"] = ""
        self.current_record["verwendungszweck"] = ""
        self.current_record["betrag"] = ""
        self.current_record["wertstellung"] = datetime.now().strftime("%d.%m.%Y")
        self.current_state = "editing"
        self.build_form()
        self.status_var.set("Folgeschritt vorbereitet")

    def show_summary(self):
        if not self.validate_required_fields():
            self.status_var.set("Nicht alle Pflichtfelder sind ausgefüllt")
            return
        self.current_record.update(self.collect_record_from_form())
        self.current_state = "summary"
        self.clear_content()

        card = tk.LabelFrame(
            self.content,
            text="Zusammenfassung",
            padx=18,
            pady=18,
            bg="#ffffff",
            fg="#1f4ed8",
            font=("Segoe UI", 11, "bold"),
            borderwidth=2,
            relief="solid",
            highlightbackground="#1f4ed8",
            highlightcolor="#1f4ed8",
        )
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)

        tk.Label(card, text=f"Belegnummer: {self.current_record['belegnummer']}", bg="#ffffff", fg="#0f172a", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))
        tk.Label(card, text=f"Wertstellung: {self.current_record['wertstellung']}", bg="#ffffff", fg="#334155").grid(row=1, column=0, sticky="w")
        tk.Label(card, text=f"Betrag: {self.current_record['betrag']}", bg="#ffffff", fg="#334155").grid(row=2, column=0, sticky="w")

        columns = ("Kontonummer", "Soll/Haben", "Betrag")
        tree = ttk.Treeview(card, columns=columns, show="headings", height=3)
        tree.grid(row=3, column=0, sticky="nsew", pady=(12, 8))
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=160, anchor="w")
        tree.insert("", "end", values=(self.current_record["start_hauptkonto"], "Soll", self.current_record["betrag"]))
        tree.insert("", "end", values=(self.current_record["ziel_hauptkonto"], "Haben", self.current_record["betrag"]))

        tk.Label(card, text=f"Leistungsart: {self.current_record['leistungsart'] or '-'}", bg="#ffffff", fg="#0f172a").grid(row=4, column=0, sticky="w", pady=(8, 0))
        tk.Label(card, text=f"Verwendungszweck: {self.current_record['verwendungszweck'] or '-'}", bg="#ffffff", fg="#0f172a").grid(row=5, column=0, sticky="w")

        button_row = tk.Frame(card, bg="#ffffff")
        button_row.grid(row=6, column=0, sticky="w", pady=(16, 0))
        tk.Button(button_row, text="Freigeben", command=self.release_transaction, bg="#1f4ed8", fg="white", activebackground="#2563eb", activeforeground="white", relief="flat", bd=0, padx=12, pady=8, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, padx=(0, 8))
        tk.Button(button_row, text="Bearbeiten", command=self.return_to_editing, bg="#e2e8f0", fg="#0f172a", activebackground="#cbd5e1", activeforeground="#0f172a", relief="flat", bd=0, padx=12, pady=8, font=("Segoe UI", 10, "bold")).grid(row=0, column=1)

    def release_transaction(self):
        self.current_record.update(self.collect_record_from_form())
        self.transactions.append(self.current_record)
        self.save_transactions()
        self.status_var.set("Buchung freigegeben")
        self.show_initial_state()
        messagebox.showinfo("Erfolgreich", "Die Buchung wurde gespeichert.")

    def abort_transaction(self):
        self.current_state = "initial"
        self.current_record = {}
        self.show_initial_state()

    def collect_record_from_form(self):
        return {
            "belegnummer": self.beleg_var.get() if hasattr(self, "beleg_var") else self.current_record.get("belegnummer", ""),
            "start_hauptkonto": self.start_account_var.get() if hasattr(self, "start_account_var") else "",
            "ziel_hauptkonto": self.target_account_var.get() if hasattr(self, "target_account_var") else "",
            "start_unterkonto": self.start_subaccount_var.get() if hasattr(self, "start_subaccount_var") else "",
            "ziel_unterkonto": self.target_subaccount_var.get() if hasattr(self, "target_subaccount_var") else "",
            "start_system": self.start_system_var.get() if hasattr(self, "start_system_var") else "",
            "ziel_system": self.target_system_var.get() if hasattr(self, "target_system_var") else "",
            "wertstellung": self.value_date_var.get() if hasattr(self, "value_date_var") else "",
            "betrag": self.amount_var.get() if hasattr(self, "amount_var") else "",
            "leistungsart": self.performance_type_var.get() if hasattr(self, "performance_type_var") else "",
            "verwendungszweck": self.purpose_var.get() if hasattr(self, "purpose_var") else "",
        }

    def validate_required_fields(self):
        record = self.collect_record_from_form()
        required = [
            ("belegnummer", "Belegnummer"),
            ("start_hauptkonto", "Start-Hauptkonto"),
            ("ziel_hauptkonto", "Ziel-Hauptkonto"),
            ("start_system", "Startsystem"),
            ("ziel_system", "Zielsystem"),
            ("wertstellung", "Wertstellung"),
            ("betrag", "Betrag"),
        ]
        for key, label in required:
            if not str(record.get(key, "")).strip():
                return False
        if not str(record.get("leistungsart", "")).strip() and not str(record.get("verwendungszweck", "")).strip():
            return False
        return True

    def generate_belegnummer(self):
        existing = [int(t.get("belegnummer", "0")) for t in self.transactions if str(t.get("belegnummer", "")).isdigit()]
        if not existing:
            return "0001"
        return f"{max(existing) + 1:04d}"

    def clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def _place_field(self, parent, row, column, label_text, widget, var=None):
        label = tk.Label(parent, text=label_text, bg="#ffffff", fg="#0f172a")
        label.grid(row=row * 2 - 1, column=column - 1, sticky="w", padx=(0, 10), pady=(8, 2))
        widget.grid(row=row * 2, column=column - 1, sticky="ew", padx=(0, 10), pady=(0, 8))
        if var is not None:
            var.set("")

    def _make_entry(self, parent, textvariable=None, state="normal", width=24, readonly_bg=None):
        bg = "#eaf4ff"
        fg = "#0f172a"
        if readonly_bg:
            bg = readonly_bg
        entry = tk.Entry(
            parent,
            textvariable=textvariable,
            state=state,
            width=width,
            bg=bg,
            fg=fg,
            relief="solid",
            bd=1,
            insertbackground="#0f172a",
        )
        return entry

    def _make_combobox(self, parent, textvariable, values):
        return ttk.Combobox(
            parent,
            textvariable=textvariable,
            values=values,
            state="readonly",
            style="Field.TCombobox",
        )

    def _make_button(self, parent, text, command, accent="primary"):
        if accent == "primary":
            bg, fg = "#1f4ed8", "white"
            active_bg, active_fg = "#2563eb", "white"
        elif accent == "secondary":
            bg, fg = "#e2e8f0", "#0f172a"
            active_bg, active_fg = "#cbd5e1", "#0f172a"
        else:
            bg, fg = "#ef4444", "white"
            active_bg, active_fg = "#dc2626", "white"
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=active_fg,
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            font=("Segoe UI", 10, "bold"),
        )

    def _place_button(self, parent, row, column, text, command, accent="primary"):
        button = self._make_button(parent, text, command, accent=accent)
        button.grid(row=row * 2, column=column - 1, sticky="ew", padx=(0, 10), pady=(10, 8))

    def show_open_transactions(self):
        window = tk.Toplevel(self.root)
        window.title("Offene Vorgänge")
        window.geometry("600x400")
        listbox = tk.Listbox(window, width=100, height=20)
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        if self.transactions:
            for entry in self.transactions:
                listbox.insert("end", f"{entry.get('belegnummer', '-')} | {entry.get('start_hauptkonto', '-')} -> {entry.get('ziel_hauptkonto', '-')} | {entry.get('betrag', '-')}")
        else:
            listbox.insert("end", "Keine Buchungen vorhanden")


def main():
    root = tk.Tk()
    app = BookingPrototypeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
