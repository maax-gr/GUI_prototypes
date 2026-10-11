import csv
import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from decimal import Decimal, InvalidOperation


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
        self.history_entries = []

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
        self.content.rowconfigure(1, weight=0)

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
        self.pending_steps = []
        self.history_entries = []

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
        self._place_field(card, 1, 3, "", self._make_button(parent=card, text="Beleg bearbeiten", command=self.start_edit_existing_beleg, accent="secondary"))
        self._place_field(card, 1, 4, "", self._make_button(parent=card, text="Neuer Geschäftsvorgang", command=self.start_new_transaction, accent="primary"))

        tk.Label(card, text="Hinweis: Ein neuer Vorgang erzeugt automatisch eine eindeutige Belegnummer.", bg="#ffffff", fg="#64748b").grid(row=2, column=0, columnspan=4, sticky="w", pady=(14, 0))
        self.status_var.set("Bereit")

    def start_new_transaction(self):
        self.current_state = "editing"
        self.history_entries = []
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

    def start_edit_existing_beleg(self):
        belegnummer = self.initial_beleg_var.get().strip()
        if not belegnummer:
            self.status_var.set("Bitte geben Sie eine Belegnummer ein")
            messagebox.showwarning("Fehler", "Bitte geben Sie eine Belegnummer ein.")
            return

        matching = [t for t in self.transactions if str(t.get("belegnummer", "")).strip() == belegnummer]
        if not matching:
            self.status_var.set("Belegnummer nicht gefunden")
            messagebox.showwarning("Nicht gefunden", "Die Belegnummer ist nicht vorhanden.")
            self.show_initial_state()
            return

        self.current_state = "editing"
        self.pending_steps = []
        existing_records = self.get_beleg_records(belegnummer)
        self.history_entries = self.build_history_entries(existing_records, self.pending_steps)
        first_record = sorted(existing_records, key=lambda r: self.parse_date(r.get("wertstellung", "")))[0]
        self.clear_content()
        primary_account = first_record.get("ziel_hauptkonto") or first_record.get("start_hauptkonto")
        primary_subaccount = first_record.get("ziel_unterkonto") or first_record.get("start_unterkonto")
        primary_system = first_record.get("ziel_system") or first_record.get("start_system")
        self.current_record = {
            "belegnummer": belegnummer,
            "start_hauptkonto": primary_account,
            "start_system": primary_system,
            "start_unterkonto": primary_subaccount,
            "ziel_hauptkonto": "",
            "ziel_system": "",
            "ziel_unterkonto": "",
            "wertstellung": datetime.now().strftime("%d.%m.%Y"),
            "betrag": "",
            "leistungsart": "",
            "verwendungszweck": "",
        }
        self.build_form()
        self.status_var.set(f"Beleg {belegnummer} bearbeiten")

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

        self._place_button(card, 6, 1, "Beleg weiter bearbeiten", self.continue_beleg_editing, accent="secondary")
        self._place_button(card, 6, 2, "Folgeschritt buchen", self.next_step, accent="secondary")
        self._place_button(card, 6, 3, "Zur Kontrolle freigeben", self.show_summary, accent="primary")
        self._place_button(card, 6, 4, "Abbruch", self.abort_transaction, accent="danger")

        if self.history_entries:
            self.build_history_view()

    def return_to_editing(self):
        self.current_state = "editing"
        self.status_var.set("Bearbeitung fortgesetzt")
        if self.current_record:
            self.current_record.update(self.collect_record_from_form())
        self.build_form()

    def continue_beleg_editing(self):
        if not self.validate_required_fields():
            self.status_var.set("Nicht alle Pflichtfelder sind ausgefüllt")
            return
        self.current_record.update(self.collect_record_from_form())
        self.pending_steps.append(dict(self.current_record))
        self.history_entries = self.build_history_entries(self.get_beleg_records(self.current_record["belegnummer"]), self.pending_steps)
        self.current_record["ziel_hauptkonto"] = ""
        self.current_record["ziel_unterkonto"] = ""
        self.current_record["ziel_system"] = ""
        self.current_record["betrag"] = ""
        self.current_record["wertstellung"] = datetime.now().strftime("%d.%m.%Y")
        self.current_record["leistungsart"] = ""
        self.current_record["verwendungszweck"] = ""
        self.current_state = "editing"
        self.build_form()
        self.status_var.set("Beleg weiter bearbeiten: Startwerte beibehalten")

    def next_step(self):
        if not self.validate_required_fields():
            self.status_var.set("Nicht alle Pflichtfelder sind ausgefüllt")
            return
        self.current_record.update(self.collect_record_from_form())
        self.pending_steps.append(dict(self.current_record))
        self.history_entries = self.build_history_entries(self.get_beleg_records(self.current_record["belegnummer"]), self.pending_steps)
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
        history_records = self.get_beleg_records(self.current_record["belegnummer"])
        self.history_entries = self.build_history_entries(history_records, self.pending_steps + [dict(self.current_record)])
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
        steps_to_save = list(self.pending_steps)
        if self.validate_required_fields():
            steps_to_save.append(dict(self.current_record))
        for step in steps_to_save:
            self.transactions.append(step)
        self.pending_steps = []
        self.history_entries = []
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

    def get_beleg_records(self, belegnummer):
        return [t for t in self.transactions if str(t.get("belegnummer", "")).strip() == str(belegnummer).strip()]

    def build_history_view(self):
        history_card = tk.LabelFrame(
            self.content,
            text="Historie",
            padx=12,
            pady=12,
            bg="#ffffff",
            fg="#1f4ed8",
            font=("Segoe UI", 11, "bold"),
            borderwidth=2,
            relief="solid",
            highlightbackground="#1f4ed8",
            highlightcolor="#1f4ed8",
        )
        history_card.grid(row=1, column=0, sticky="nsew", pady=(16, 0))
        history_card.columnconfigure(tuple(range(10)), weight=1)

        headers = [
            "Betrag",
            "Währung",
            "Leistungsart - Verwendungszweck",
            "Konto",
            "Wertstellungsdatum",
        ]
        for index, header_text in enumerate(headers):
            label = tk.Label(history_card, text=header_text, bg="#ffffff", fg="#0f172a", font=("Segoe UI", 10, "bold"))
            label.grid(row=0, column=index * 2, sticky="w", padx=(0, 4), pady=(0, 6))
            button = tk.Button(history_card, text="i", command=lambda: None, bg="#e2e8f0", fg="#0f172a", relief="flat", bd=0, width=2, font=("Segoe UI", 9, "bold"))
            button.grid(row=0, column=index * 2 + 1, sticky="e", padx=(0, 10), pady=(0, 6))

        current_row = 1
        for index, entry in enumerate(self.history_entries):
            tk.Label(history_card, text=entry["amount"], bg="#ffffff", fg="#0f172a").grid(row=current_row, column=0, sticky="w", padx=(0, 4), pady=(2, 2))
            tk.Label(history_card, text=entry["currency"], bg="#ffffff", fg="#0f172a").grid(row=current_row, column=2, sticky="w", padx=(0, 4), pady=(2, 2))
            tk.Label(history_card, text=entry["description"], bg="#ffffff", fg="#0f172a").grid(row=current_row, column=4, sticky="w", padx=(0, 4), pady=(2, 2))
            tk.Label(history_card, text=entry["account"], bg="#ffffff", fg="#0f172a").grid(row=current_row, column=6, sticky="w", padx=(0, 4), pady=(2, 2))
            tk.Label(history_card, text=entry["wertstellung"], bg="#ffffff", fg="#0f172a").grid(row=current_row, column=8, sticky="w", padx=(0, 4), pady=(2, 2))
            if index == 0:
                separator = tk.Frame(history_card, bg="#cbd5e1", height=1)
                separator.grid(row=current_row + 1, column=0, columnspan=10, sticky="ew", pady=(4, 6))
                current_row += 2
            else:
                current_row += 1

    def build_history_entries(self, records, pending_records=None):
        all_records = list(records) + list(pending_records or [])
        sorted_records = sorted(all_records, key=lambda r: self.parse_date(r.get("wertstellung", "")))
        entries = []
        # determine primary account (Ursprungszielkonto) from first record
        primary_account = None
        if sorted_records:
            first_rec = sorted_records[0]
            primary_account = first_rec.get("ziel_hauptkonto") or first_rec.get("start_hauptkonto")

        previous_target = None
        for index, record in enumerate(sorted_records):
            perf = str(record.get("leistungsart", "") or "").strip()
            purpose = str(record.get("verwendungszweck", "") or "").strip()
            if perf and purpose:
                description = f"{perf} - {purpose}"
            elif perf:
                description = perf
            elif purpose:
                description = f"- {purpose}"
            else:
                description = ""

            amount_text = str(record.get("betrag", "") or "")
            # show arrow only when this step starts from the previous step's target
            # BUT never show arrow for bookings whose start account is the primary (Ursprungszielkonto)
            if index > 0 and previous_target and str(record.get("start_hauptkonto", "")).strip() == str(previous_target).strip():
                if not primary_account or str(record.get("start_hauptkonto", "")).strip() != str(primary_account).strip():
                    amount_text = f"->{amount_text}"

            entries.append({
                "amount": amount_text,
                "currency": "EUR",
                "description": description,
                "account": record.get("ziel_hauptkonto", ""),
                "wertstellung": record.get("wertstellung", ""),
                "source_record": record,
            })
            previous_target = record.get("ziel_hauptkonto", "")

        if sorted_records:
            first_record = sorted_records[0]
            primary_account = first_record.get("ziel_hauptkonto") or first_record.get("start_hauptkonto")
            initial_amount = self.parse_amount(first_record.get("betrag", ""))
            outgoing_amount = Decimal("0")
            for record in sorted_records[1:]:
                if str(record.get("start_hauptkonto", "")).strip() == str(primary_account).strip():
                    outgoing_amount += self.parse_amount(record.get("betrag", ""))
            remaining = initial_amount - outgoing_amount
            entries.append({
                "amount": f"{remaining:.2f}",
                "currency": "EUR",
                "description": "ungeklärt/offen",
                "account": primary_account,
                "wertstellung": "--------",
                "source_record": first_record,
            })
        return entries

    def parse_date(self, value):
        try:
            return datetime.strptime(str(value), "%d.%m.%Y")
        except (ValueError, TypeError):
            return datetime(1900, 1, 1)

    def parse_amount(self, value):
        try:
            text = str(value).replace(",", ".").strip()
            if not text:
                return Decimal("0")
            return Decimal(text)
        except (InvalidOperation, ValueError, TypeError):
            return Decimal("0")

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
