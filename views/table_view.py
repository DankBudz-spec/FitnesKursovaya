from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt
from controllers.table_controller import TableController
from views.add_dialog import AddDialog


class TableView(QWidget):
    def __init__(self, table_name, russian_headers):
        super().__init__()
        self.table_name = table_name
        self.russian_headers = russian_headers
        self.controller = TableController()
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Создаем таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.russian_headers))
        self.table.setHorizontalHeaderLabels(self.russian_headers)

        # Настройки внешнего вида таблицы
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)  # Скрываем номера строк слева

        layout.addWidget(self.table)

        # Панель кнопок
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("➕ Добавить")
        self.btn_add.setObjectName("btn_add")  # ID для QSS

        self.btn_edit = QPushButton("📝 Редактировать")

        self.btn_delete = QPushButton("🗑 Удалить")
        self.btn_delete.setObjectName("btn_delete")  # ID для QSS

        self.btn_refresh = QPushButton("🔄 Обновить данные")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)

        layout.addLayout(btn_layout)

        # 4. Подключаем сигналы (события)
        self.btn_add.clicked.connect(self.add_row)
        self.btn_delete.clicked.connect(self.delete_row)
        self.btn_refresh.clicked.connect(self.refresh_data)
        self.btn_edit.clicked.connect(self.edit_row)

    # --- МЕТОДЫ-ЗАГЛУШКИ ДЛЯ CRUD ---

    def refresh_data(self):
        self.controller.sync_table(self.table, self.table_name)

    def add_row(self):
        dialog = AddDialog(self.table_name, self.russian_headers, self.controller)

        while True:
            if dialog.exec():  # Если пользователь нажал "Сохранить"
                new_data = dialog.get_data()

                # 2. Отправляем в контроллер
                success, message = self.controller.add_record(self.table_name, new_data)

                if success:
                    QMessageBox.information(self, "Успех", message)
                    self.refresh_data()
                    break
                else:
                    ru_message = self.controller.translate_error(message)
                    QMessageBox.critical(dialog, "Ошибка", f"Ошибка: {ru_message}")
            else:
                break

    def delete_row(self):
        # 1. Проверяем, выбрана ли строка
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите строку в таблице!")
            return

        # Получаем индекс строки
        row = selected_items[0].row()

        # 2. Вытаскиваем ID (он у нас всегда в первой колонке, индекс 0)
        record_id = self.table.item(row, 0).text()

        # 3. Подтверждение удаления
        confirm = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить запись с ID {record_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            # 4. Отправляем запрос в контроллер
            success = self.controller.delete_record(self.table_name, record_id)

            # 5. Обновляем таблицу, если всё прошло успешно
            if confirm == QMessageBox.StandardButton.Yes:
                success, message = self.controller.delete_record(self.table_name, record_id)

                if success:
                    QMessageBox.information(self, "Успех", message)
                    self.refresh_data()
                else:
                    ru_message = self.controller.translate_error(message)
                    QMessageBox.critical(self, "Ошибка", f"Ошибка: {ru_message}")

    def edit_row(self):
        # 1. Проверяем, выбрана ли строка
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для редактирования!")
            return

        row = selected_items[0].row()

        # 2. Собираем текущие данные из таблицы (чтобы предзаполнить окно)
        current_values = []
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            current_values.append(item.text() if item else "")

        record_id = current_values[0]  # ID всегда первый

        # 3. Открываем диалог, передавая в него текущие данные
        dialog = AddDialog(self.table_name, self.russian_headers, self.controller, current_data=current_values)

        while True:
            if dialog.exec():
                new_data = dialog.get_data()

                # 4. Отправляем в контроллер
                success, message = self.controller.update_record(self.table_name, record_id, new_data)

                if success:
                    QMessageBox.information(dialog, "Успех", "Запись успешно обновлена!")
                    self.refresh_data()
                    break
                else:
                    ru_message = self.controller.translate_error(message)
                    QMessageBox.critical(dialog, "Ошибка", f"Ошибка: {ru_message}")
            else:
                break
