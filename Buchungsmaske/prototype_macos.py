import csv
import json
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QGroupBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class BookingPrototypeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interaktive Buchungsmaske (macOS PoC)")
        self.resize(1100, 780)
        self.setMinimumSize(980, 720)
        self.setStyleSheet("background-color: #f5f8ff;")

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
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        header = QWidget(self)
        header.setStyleSheet("background: #f8fbff;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 18, 18, 18)
        header_layout.setSpacing(12)

        title = QLabel("Interaktive Buchungsmaske", self)
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #0f172a;")
        subtitle = QLabel("PoC für Bank-Workflow und Buchungslogik", self)
        subtitle.setStyleSheet("font-size: 12px; color: #475569;")

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)

        header_layout.addLayout(text_layout)
        header_layout.addStretch(1)

        self.status_label = QLabel("Bereit", self)
        self.status_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #0f766e;")
        header_layout.addWidget(self.status_label, alignment=Qt.AlignRight | Qt.AlignVCenter)

        self.main_layout.addWidget(header)

        self.content = QWidget(self)
        self.content.setStyleSheet("background: #f8fbff;")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(16, 16, 16, 16)
        self.content_layout.setSpacing(16)
        self.main_layout.addWidget(self.content)

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

        card = self._make_card("Start")
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(18)
        form_layout.setVerticalSpacing(12)
        card.setLayout(form_layout)

        self.initial_beleg_edit = QLineEdit(self)
        self.initial_beleg_edit.setPlaceholderText("Belegnummer oder Vorgangsnummer eingeben")
        self.initial_beleg_edit.setFixedWidth(260)

        self._place_field(form_layout, 0, 0, "Belegnummer/Vorgangsnummer", self.initial_beleg_edit)
        self._place_field(form_layout, 0, 2, "", self._make_button("Offene Vorgänge anzeigen", self.show_open_transactions, "secondary"))
        self._place_field(form_layout, 0, 3, "", self._make_button("Neuer Geschäftsvorgang", self.start_new_transaction, "primary"))

        hint = QLabel("Hinweis: Ein neuer Vorgang erzeugt automatisch eine eindeutige Belegnummer.", self)
        hint.setStyleSheet("color: #64748b;")
        form_layout.addWidget(hint, 2, 0, 1, 4)

        self.content_layout.addWidget(card)
        self.status_label.setText("Bereit")

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
        self.status_label.setText("Neuer Geschäftsvorgang gestartet")

    def build_form(self):
        card = self._make_card("Buchung erfassen")
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(18)
        form_layout.setVerticalSpacing(12)
        card.setLayout(form_layout)

        self.beleg_edit = self._make_line_edit(self.current_record["belegnummer"], readonly=True)
        self.start_account_edit = self._make_line_edit(self.current_record["start_hauptkonto"])
        self.start_system_combo = self._make_combo_box(self.current_record["start_system"], ["DaBu", "ORAG", "KK", "GNB"])
        self.target_account_edit = self._make_line_edit(self.current_record["ziel_hauptkonto"])
        self.target_system_combo = self._make_combo_box(self.current_record["ziel_system"], ["DaBu", "ORAG", "KK", "GNB"])
        self.start_subaccount_edit = self._make_line_edit(self.current_record["start_unterkonto"])
        self.target_subaccount_edit = self._make_line_edit(self.current_record["ziel_unterkonto"])
        self.amount_edit = self._make_line_edit(self.current_record["betrag"])
        self.value_date_edit = self._make_line_edit(self.current_record["wertstellung"])
        self.performance_type_edit = self._make_line_edit(self.current_record["leistungsart"])
        self.purpose_edit = self._make_line_edit(self.current_record["verwendungszweck"])

        self._place_field(form_layout, 0, 0, "Belegnummer/Vorgangsnummer", self.beleg_edit)
        self._place_field(form_layout, 1, 0, "Start-Hauptkonto", self.start_account_edit)
        self._place_field(form_layout, 1, 1, "Startsystem", self.start_system_combo)
        self._place_field(form_layout, 1, 2, "Ziel-Hauptkonto", self.target_account_edit)
        self._place_field(form_layout, 1, 3, "Zielsystem", self.target_system_combo)
        self._place_field(form_layout, 2, 0, "Start-Unterkonto", self.start_subaccount_edit)
        self._place_field(form_layout, 2, 2, "Ziel-Unterkonto", self.target_subaccount_edit)
        self._place_field(form_layout, 3, 0, "Betrag", self.amount_edit)
        self._place_field(form_layout, 3, 1, "Wertstellung", self.value_date_edit)
        self._place_field(form_layout, 4, 0, "Leistungsart", self.performance_type_edit)
        self._place_field(form_layout, 4, 1, "Verwendungszweck", self.purpose_edit)

        self._place_button(form_layout, 5, 0, "Beleg weiter bearbeiten", self.return_to_editing, "secondary")
        self._place_button(form_layout, 5, 1, "Folgeschritt buchen", self.next_step, "secondary")
        self._place_button(form_layout, 5, 2, "Zur Kontrolle freigeben", self.show_summary, "primary")
        self._place_button(form_layout, 5, 3, "Abbruch", self.abort_transaction, "danger")

        self.content_layout.addWidget(card)

    def return_to_editing(self):
        self.current_state = "editing"
        self.status_label.setText("Bearbeitung fortgesetzt")
        if self.current_record:
            self.current_record.update(self.collect_record_from_form())
        self.build_form()

    def next_step(self):
        if not self.validate_required_fields():
            self.status_label.setText("Nicht alle Pflichtfelder sind ausgefüllt")
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
        self.status_label.setText("Folgeschritt vorbereitet")

    def show_summary(self):
        if not self.validate_required_fields():
            self.status_label.setText("Nicht alle Pflichtfelder sind ausgefüllt")
            return
        self.current_record.update(self.collect_record_from_form())
        self.current_state = "summary"
        self.clear_content()

        card = self._make_card("Zusammenfassung")
        summary_layout = QVBoxLayout()
        summary_layout.setSpacing(12)
        card.setLayout(summary_layout)

        summary_layout.addWidget(self._make_summary_label(f"Belegnummer: {self.current_record['belegnummer']}"))
        summary_layout.addWidget(self._make_summary_label(f"Wertstellung: {self.current_record['wertstellung']}"))
        summary_layout.addWidget(self._make_summary_label(f"Betrag: {self.current_record['betrag']}"))

        table = QTableWidget(2, 3, self)
        table.setHorizontalHeaderLabels(["Kontonummer", "Soll/Haben", "Betrag"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setFocusPolicy(Qt.NoFocus)
        table.setStyleSheet("QTableWidget { background: white; border: 1px solid #dbeafe; }")
        table.setFixedHeight(150)
        table.setItem(0, 0, QTableWidgetItem(self.current_record["start_hauptkonto"]))
        table.setItem(0, 1, QTableWidgetItem("Soll"))
        table.setItem(0, 2, QTableWidgetItem(self.current_record["betrag"]))
        table.setItem(1, 0, QTableWidgetItem(self.current_record["ziel_hauptkonto"]))
        table.setItem(1, 1, QTableWidgetItem("Haben"))
        table.setItem(1, 2, QTableWidgetItem(self.current_record["betrag"]))
        table.resizeColumnsToContents()
        summary_layout.addWidget(table)

        summary_layout.addWidget(self._make_summary_label(f"Leistungsart: {self.current_record['leistungsart'] or '-'}"))
        summary_layout.addWidget(self._make_summary_label(f"Verwendungszweck: {self.current_record['verwendungszweck'] or '-'}"))

        button_row = QHBoxLayout()
        button_row.setSpacing(12)
        button_row.addWidget(self._make_button("Freigeben", self.release_transaction, "primary"))
        button_row.addWidget(self._make_button("Bearbeiten", self.return_to_editing, "secondary"))
        summary_layout.addLayout(button_row)

        self.content_layout.addWidget(card)

    def release_transaction(self):
        self.current_record.update(self.collect_record_from_form())
        self.transactions.append(self.current_record)
        self.save_transactions()
        self.status_label.setText("Buchung freigegeben")
        self.show_initial_state()
        QMessageBox.information(self, "Erfolgreich", "Die Buchung wurde gespeichert.")

    def abort_transaction(self):
        self.current_state = "initial"
        self.current_record = {}
        self.show_initial_state()

    def collect_record_from_form(self):
        return {
            "belegnummer": self.beleg_edit.text() if hasattr(self, "beleg_edit") else self.current_record.get("belegnummer", ""),
            "start_hauptkonto": self.start_account_edit.text() if hasattr(self, "start_account_edit") else "",
            "ziel_hauptkonto": self.target_account_edit.text() if hasattr(self, "target_account_edit") else "",
            "start_unterkonto": self.start_subaccount_edit.text() if hasattr(self, "start_subaccount_edit") else "",
            "ziel_unterkonto": self.target_subaccount_edit.text() if hasattr(self, "target_subaccount_edit") else "",
            "start_system": self.start_system_combo.currentText() if hasattr(self, "start_system_combo") else "",
            "ziel_system": self.target_system_combo.currentText() if hasattr(self, "target_system_combo") else "",
            "wertstellung": self.value_date_edit.text() if hasattr(self, "value_date_edit") else "",
            "betrag": self.amount_edit.text() if hasattr(self, "amount_edit") else "",
            "leistungsart": self.performance_type_edit.text() if hasattr(self, "performance_type_edit") else "",
            "verwendungszweck": self.purpose_edit.text() if hasattr(self, "purpose_edit") else "",
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
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _make_card(self, title_text):
        card = QGroupBox(title_text, self)
        card.setStyleSheet(
            "QGroupBox { background: white; border: 1px solid #dbeafe; border-radius: 12px; margin-top: 18px; }"
            "QGroupBox:title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; color: #1f4ed8; font-weight: 700; }"
        )
        return card

    def _make_line_edit(self, text="", readonly=False):
        edit = QLineEdit(self)
        edit.setText(text)
        edit.setStyleSheet(
            "QLineEdit { background: #eaf4ff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px; }"
            "QLineEdit:read-only { background: #e5e7eb; }"
        )
        if readonly:
            edit.setReadOnly(True)
        return edit

    def _make_combo_box(self, current, values):
        combo = QComboBox(self)
        combo.addItems(values)
        if current in values:
            combo.setCurrentText(current)
        combo.setStyleSheet(
            "QComboBox { background: #eaf4ff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 8px; }"
            "QComboBox::drop-down { border: none; }"
        )
        return combo

    def _make_button(self, text, callback, variant="primary"):
        button = QPushButton(text, self)
        button.clicked.connect(callback)
        button.setFixedHeight(40)
        button.setStyleSheet(
            "QPushButton { border-radius: 10px; font-weight: 700; padding: 0 16px; }"
            + (
                "QPushButton { background: #1f4ed8; color: white; } QPushButton:hover { background: #2563eb; }"
                if variant == "primary"
                else "QPushButton { background: #e2e8f0; color: #0f172a; } QPushButton:hover { background: #cbd5e1; }"
                if variant == "secondary"
                else "QPushButton { background: #ef4444; color: white; } QPushButton:hover { background: #dc2626; }"
            )
        )
        return button

    def _make_summary_label(self, text):
        label = QLabel(text, self)
        label.setStyleSheet("color: #0f172a; font-size: 13px;")
        return label

    def _place_field(self, layout, row, column, label_text, widget):
        label = QLabel(label_text, self)
        label.setStyleSheet("color: #0f172a;")
        layout.addWidget(label, row * 2, column)
        layout.addWidget(widget, row * 2 + 1, column)

    def _place_button(self, layout, row, column, text, callback, variant="primary"):
        button = self._make_button(text, callback, variant)
        layout.addWidget(button, row * 2, column)

    def show_open_transactions(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Offene Vorgänge")
        dialog.resize(600, 400)

        dialog_layout = QVBoxLayout(dialog)
        listbox = QListWidget(dialog)
        if self.transactions:
            for entry in self.transactions:
                listbox.addItem(f"{entry.get('belegnummer', '-')} | {entry.get('start_hauptkonto', '-')} -> {entry.get('ziel_hauptkonto', '-')}")
        else:
            listbox.addItem("Keine Buchungen vorhanden")

        dialog_layout.addWidget(listbox)
        dialog.exec()


def main():
    app = QApplication([])
    window = BookingPrototypeApp()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
