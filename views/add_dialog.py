from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QPushButton, QHBoxLayout, QLabel, QDateEdit,
                             QDoubleSpinBox, QSpinBox, QTextEdit, QComboBox)
from PyQt6.QtCore import Qt, QDate


class AddDialog(QDialog):
    def __init__(self, table_name, headers, controller, current_data=None):
        super().__init__()
        self.table_name = table_name
        self.controller = controller  # Сохраняем ссылку на контроллер
        self.is_edit = current_data is not None  # Если данные переданы — это редактирование
        self.fields_labels = headers[1:]  # Пропускаем ID
        self.inputs = {}
        self.init_ui()

        if current_data:
            self.fill_data(current_data)

    def init_ui(self):
        # Меняем заголовок в зависимости от режима
        title_prefix = "Редактировать" if self.is_edit else "Добавить"
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
        l = label.lower()

        # 1. СЛОВАРЬ СВЯЗЕЙ (Foreign Keys)
        # Мы ищем ключевое слово в заголовке и сопоставляем его с таблицей в БД
        relations = {
            "клиент": "clients",  # Для "ID Клиента"
            "тип абонемента": "membership_types",  # Для "ID типа абонемента"
            "тренер": "staff",  # Для "ID Тренера"
            "занятие": "classes",  # Для "ID Занятия"
            "зона": "zones",  # Для "ID Зоны"
            "запись": "schedule"  # Для "ID Записи" (ссылка на расписание)
        }

        # Сначала проверяем, не является ли поле выпадающим списком из другой таблицы
        for key, target_table in relations.items():
            if key in l:
                return self._create_foreign_key_combo(target_table)

        # 2. ДАТЫ И ВРЕМЯ
        # Проверяем все возможные упоминания дат из твоего main_window
        date_keywords = ["дата", "регистрация", "куплено", "принят", "начало", "конец", "вход", "выход", "время", "последнее"]
        if any(x in l for x in date_keywords):
            w = QDateEdit()
            w.setCalendarPopup(True)
            w.setDate(QDate.currentDate())
            w.setDisplayFormat("yyyy-MM-dd")
            return w

        # 3. ЧИСЛА И ДЕНЬГИ
        # Денежные поля (Double)
        if any(x in l for x in ["стоимость", "ставка", "сумма", "оплата"]):
            w = QDoubleSpinBox()
            w.setRange(0, 9999999)
            w.setDecimals(2)
            w.setGroupSeparatorShown(True)
            return w

        # Целые числа (Integer)
        if any(x in l for x in ["вместимость", "срок", "уровень", "дни",]):
            w = QSpinBox()
            w.setRange(0, 10000)
            return w

        # 4. ДЛИННЫЙ ТЕКСТ
        if any(x in l for x in ["примечание", "описание", "адрес", "ограничения"]):
            w = QTextEdit()
            w.setMaximumHeight(80)
            return w

        # 5. СТАТУСЫ И БОКИРОВКИ (ComboBox)
        if any(x in l for x in ["блокировка", "статус"]):
            w = QComboBox()
            if "блок" in l:
                # Для базы данных (0 - нет, 1 - да)
                w.addItem("Разблокирован (0)", 0)
                w.addItem("Заблокирован (1)", 1)
            else:
                # Обычные текстовые статусы
                w.addItems(["Записан", "Отменено", "Выполнено", "Исправно", "В ремонте"])
            return w

        # 6. ОБЫЧНАЯ СТРОКА (ФИО, Телефон, Email)
        w = QLineEdit()
        if "телефон" in l:
            w.setPlaceholderText("+7 (999) 000-00-00")
        if "email" in l:
            w.setPlaceholderText("example@mail.com")

        return w

    def _create_foreign_key_combo(self, target_table):
        items = self.controller.get_lookup_data(target_table)

        combo = QComboBox()
        for item_id, item_name in items:
            combo.addItem(str(item_name), item_id)
        return combo

    def get_data(self):
        data = []
        for widget in self.inputs.values():
            if isinstance(widget, QComboBox):
                val = widget.currentData()
                data.append(val if val is not None else widget.currentText())
            elif isinstance(widget, QDateEdit):
                data.append(widget.date().toString("yyyy-MM-dd"))
            elif isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                data.append(widget.value())
            elif isinstance(widget, QTextEdit):
                data.append(widget.toPlainText())
            else:
                data.append(widget.text())
        return data

    def fill_data(self, data):
        for i, (label, widget) in enumerate(self.inputs.items()):
            val = data[i + 1]
            if val is None: continue

            if isinstance(widget, QComboBox):
                index = widget.findData(val)
                if index < 0: index = widget.findText(str(val))
                if index >= 0: widget.setCurrentIndex(index)
            elif isinstance(widget, QDateEdit):
                # Безопасное приведение к дате
                d = QDate.fromString(str(val), "yyyy-MM-dd")
                if d.isValid(): widget.setDate(d)
            elif isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                try:
                    # Если это целое число (SpinBox)
                    if isinstance(widget, QSpinBox):
                        # Сначала в float (на случай если в БД строка "30.0"),
                        # а потом в int для виджета
                        widget.setValue(int(float(val)))
                    else:
                        # Если это DoubleSpinBox
                        widget.setValue(float(val))
                except:
                    widget.setValue(0)
            elif isinstance(widget, QTextEdit):
                widget.setPlainText(str(val))
            else:
                widget.setText(str(val))