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
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("TEntry", padding=4)
        style.configure("TButton", padding=6)
        style.configure("Primary.TButton", background="#1f4ed8", foreground="white")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        header = ttk.Frame(self.root, padding=16)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Interaktive Buchungsmaske", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="PoC für Bank-Workflow und Buchungslogik", foreground="#475569").grid(row=1, column=0, sticky="w")

        self.status_var = tk.StringVar(value="Bereit")
        ttk.Label(header, textvariable=self.status_var, foreground="#0f766e").grid(row=0, column=1, sticky="e")

        self.content = ttk.Frame(self.root, padding=(16, 0, 16, 16))
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

        card = ttk.LabelFrame(self.content, text="Start", padding=16)
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="Belegnummer/Vorgangsnummer").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=6)
        self.initial_beleg_var = tk.StringVar(value="")
        ttk.Entry(card, textvariable=self.initial_beleg_var, width=30).grid(row=0, column=1, sticky="ew", pady=6)

        button_row = ttk.Frame(card)
        button_row.grid(row=1, column=0, columnspan=2, sticky="w", pady=(12, 0))
        ttk.Button(button_row, text="Neuer Geschäftsvorgang", command=self.start_new_transaction).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(button_row, text="Offene Vorgänge anzeigen", command=self.show_open_transactions).grid(row=0, column=1)

        ttk.Label(card, text="Hinweis: Ein neuer Vorgang erzeugt automatisch eine eindeutige Belegnummer.", foreground="#64748b").grid(row=2, column=0, columnspan=2, sticky="w", pady=(12, 0))
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
        card = ttk.LabelFrame(self.content, text="Buchung erfassen", padding=16)
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(1, weight=1)
        card.columnconfigure(3, weight=1)

        row = 0
        ttk.Label(card, text="Belegnummer/Vorgangsnummer").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=6)
        self.beleg_var = tk.StringVar(value=self.current_record["belegnummer"])
        ttk.Entry(card, textvariable=self.beleg_var, state="readonly", width=20).grid(row=row, column=1, sticky="ew", pady=6)
        ttk.Label(card, text="").grid(row=row, column=2, padx=16)
        ttk.Button(card, text="Zur Kontrolle freigeben", command=self.show_summary).grid(row=row, column=3, sticky="ew", pady=6)

        row += 1
        ttk.Label(card, text="Start-Hauptkonto").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=6)
        self.start_account_var = tk.StringVar(value=self.current_record["start_hauptkonto"])
        ttk.Entry(card, textvariable=self.start_account_var).grid(row=row, column=1, sticky="ew", pady=6)

        ttk.Label(card, text="Ziel-Hauptkonto").grid(row=row, column=2, sticky="w", padx=(16, 10), pady=6)
        self.target_account_var = tk.StringVar(value=self.current_record["ziel_hauptkonto"])
        ttk.Entry(card, textvariable=self.target_account_var).grid(row=row, column=3, sticky="ew", pady=6)

        row += 1
        ttk.Label(card, text="Start-Unterkonto").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=6)
        self.start_subaccount_var = tk.StringVar(value=self.current_record["start_unterkonto"])
        ttk.Entry(card, textvariable=self.start_subaccount_var).grid(row=row, column=1, sticky="ew", pady=6)

        ttk.Label(card, text="Ziel-Unterkonto").grid(row=row, column=2, sticky="w", padx=(16, 10), pady=6)
        self.target_subaccount_var = tk.StringVar(value=self.current_record["ziel_unterkonto"])
        ttk.Entry(card, textvariable=self.target_subaccount_var).grid(row=row, column=3, sticky="ew", pady=6)

        row += 1
        ttk.Label(card, text="Startsystem").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=6)
        self.start_system_var = tk.StringVar(value=self.current_record["start_system"])
        self.start_system_combo = ttk.Combobox(card, textvariable=self.start_system_var, values=["DaBu", "ORAG", "KK", "GNB"], state="readonly")
        self.start_system_combo.grid(row=row, column=1, sticky="ew", pady=6)

        ttk.Label(card, text="Zielsystem").grid(row=row, column=2, sticky="w", padx=(16, 10), pady=6)
        self.target_system_var = tk.StringVar(value=self.current_record["ziel_system"])
        self.target_system_combo = ttk.Combobox(card, textvariable=self.target_system_var, values=["DaBu", "ORAG", "KK", "GNB"], state="readonly")
        self.target_system_combo.grid(row=row, column=3, sticky="ew", pady=6)

        row += 1
        ttk.Label(card, text="Wertstellung").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=6)
        self.value_date_var = tk.StringVar(value=self.current_record["wertstellung"])
        ttk.Entry(card, textvariable=self.value_date_var).grid(row=row, column=1, sticky="ew", pady=6)

        ttk.Label(card, text="Betrag").grid(row=row, column=2, sticky="w", padx=(16, 10), pady=6)
        self.amount_var = tk.StringVar(value=self.current_record["betrag"])
        ttk.Entry(card, textvariable=self.amount_var).grid(row=row, column=3, sticky="ew", pady=6)

        row += 1
        ttk.Label(card, text="Leistungsart").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=6)
        self.performance_type_var = tk.StringVar(value=self.current_record["leistungsart"])
        ttk.Entry(card, textvariable=self.performance_type_var).grid(row=row, column=1, sticky="ew", pady=6)

        ttk.Label(card, text="Verwendungszweck").grid(row=row, column=2, sticky="w", padx=(16, 10), pady=6)
        self.purpose_var = tk.StringVar(value=self.current_record["verwendungszweck"])
        ttk.Entry(card, textvariable=self.purpose_var).grid(row=row, column=3, sticky="ew", pady=6)

        row += 1
        button_row = ttk.Frame(card)
        button_row.grid(row=row, column=0, columnspan=4, sticky="w", pady=(16, 0))
        ttk.Button(button_row, text="Beleg weiter bearbeiten", command=self.return_to_editing).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(button_row, text="Folgeschritt buchen", command=self.next_step).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(button_row, text="Abbruch", command=self.abort_transaction).grid(row=0, column=2)

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

        card = ttk.LabelFrame(self.content, text="Zusammenfassung", padding=16)
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text=f"Belegnummer: {self.current_record['belegnummer']}", style="Header.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        ttk.Label(card, text=f"Wertstellung: {self.current_record['wertstellung']}", foreground="#334155").grid(row=1, column=0, sticky="w")
        ttk.Label(card, text=f"Betrag: {self.current_record['betrag']}", foreground="#334155").grid(row=2, column=0, sticky="w")

        columns = ("Kontonummer", "Soll/Haben", "Betrag")
        tree = ttk.Treeview(card, columns=columns, show="headings", height=3)
        tree.grid(row=3, column=0, sticky="nsew", pady=(12, 8))
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=160, anchor="w")
        tree.insert("", "end", values=(self.current_record["start_hauptkonto"], "Soll", self.current_record["betrag"]))
        tree.insert("", "end", values=(self.current_record["ziel_hauptkonto"], "Haben", self.current_record["betrag"]))

        ttk.Label(card, text=f"Leistungsart: {self.current_record['leistungsart'] or '-'}").grid(row=4, column=0, sticky="w", pady=(8, 0))
        ttk.Label(card, text=f"Verwendungszweck: {self.current_record['verwendungszweck'] or '-'}").grid(row=5, column=0, sticky="w")

        button_row = ttk.Frame(card)
        button_row.grid(row=6, column=0, sticky="w", pady=(16, 0))
        ttk.Button(button_row, text="Freigeben", command=self.release_transaction).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(button_row, text="Bearbeiten", command=self.return_to_editing).grid(row=0, column=1)

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
