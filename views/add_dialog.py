from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QPushButton, QHBoxLayout, QLabel, QDateEdit,
                             QDoubleSpinBox, QSpinBox, QTextEdit, QComboBox)
from PyQt6.QtCore import Qt, QDate


class AddDialog(QDialog):
    def __init__(self, table_name, headers, current_data=None):
        super().__init__()
        self.table_name = table_name
        self.fields_labels = headers[1:]  # Пропускаем ID
        self.inputs = {}
        self.init_ui()

        if current_data:
            self.fill_data(current_data)

    def init_ui(self):
        # Меняем заголовок в зависимости от режима
        title_prefix = "Редактировать" if hasattr(self, 'is_edit') else "Добавить"
        self.setWindowTitle(f"{title_prefix} запись: {self.table_name}")
        self.setFixedWidth(450)

        # Основной лейаут
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Форма ввода
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(15)
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Динамическое создание умных виджетов
        for label_text in self.fields_labels:
            widget = self._create_input_widget(label_text)
            self.form_layout.addRow(QLabel(f"<b>{label_text}:</b>"), widget)
            self.inputs[label_text] = widget

        layout.addLayout(self.form_layout)

        # Разделительная линия
        line = QLabel()
        line.setStyleSheet("background-color: #444; min-height: 1px;")
        layout.addWidget(line)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_save = QPushButton("💾 Сохранить")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setMinimumHeight(35)
        self.btn_save.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")

        self.btn_cancel = QPushButton("❌ Отмена")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setMinimumHeight(35)

        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def _create_input_widget(self, label):
        """Фабрика виджетов: выбирает тип поля на основе названия заголовка"""
        l = label.lower()

        # 1. Поля даты
        if "дата" in l or "день" in l or "_dt" in l or "регистрация" in l:
            w = QDateEdit()
            w.setCalendarPopup(True)
            w.setDate(QDate.currentDate())
            w.setDisplayFormat("yyyy-MM-dd")
            return w

        # 2. Денежные суммы (дробные числа)
        if "цена" in l or "сумма" in l or "ставка" in l or "оплата" in l:
            w = QDoubleSpinBox()
            w.setRange(0, 1000000)
            w.setPrefix("$ ")  # Или руб.
            w.setDecimals(2)
            return w

        # 3. Целые числа (уровень доступа, количество)
        if "уровень" in l or "дней" in l or "вместимость" in l or "freeze" in l:
            w = QSpinBox()
            w.setRange(0, 1000)
            return w

        # 4. Длинные тексты (заметки, описания)
        if "примечание" in l or "описание" in l or "notes" in l or "адрес" in l:
            w = QTextEdit()
            w.setMaximumHeight(80)
            return w

        # 5. Статусы и Булевы значения (0/1)
        if "заблокирован" in l or "статус" in l:
            w = QComboBox()
            if "заблокирован" in l:
                w.addItems(["0", "1"])
            else:
                w.addItems(["Записан", "Отменено", "Выполнено", "Исправно", "В ремонте"])
            return w

        # 6. Обычная строка (ФИО, телефон, email)
        w = QLineEdit()
        if "телефон" in l: w.setPlaceholderText("+7 (___) ___-__-__")
        if "email" in l: w.setPlaceholderText("example@mail.com")
        return w

    def get_data(self):
        """Собирает данные из разных типов виджетов в один список"""
        data = []
        for widget in self.inputs.values():
            if isinstance(widget, QDateEdit):
                data.append(widget.date().toString("yyyy-MM-dd"))
            elif isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                data.append(widget.value())
            elif isinstance(widget, QTextEdit):
                data.append(widget.toPlainText())
            elif isinstance(widget, QComboBox):
                data.append(widget.currentText())
            else:  # QLineEdit
                data.append(widget.text())
        return data

    def fill_data(self, data):
        """Заполняет виджеты данными из БД с учетом их типа"""
        # Начинаем с 1, так как 0 - это ID
        for i, (label, widget) in enumerate(self.inputs.items()):
            val = data[i + 1]
            if val is None: val = ""

            if isinstance(widget, QDateEdit):
                widget.setDate(QDate.fromString(str(val), "yyyy-MM-dd"))
            elif isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                try:
                    widget.setValue(float(val))
                except:
                    widget.setValue(0)
            elif isinstance(widget, QTextEdit):
                widget.setPlainText(str(val))
            elif isinstance(widget, QComboBox):
                index = widget.findText(str(val))
                if index >= 0: widget.setCurrentIndex(index)
            else:  # QLineEdit
                widget.setText(str(val))