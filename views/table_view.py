from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt


class TableView(QWidget):
    def __init__(self, table_name, russian_headers):
        super().__init__()
        self.table_name = table_name
        self.russian_headers = russian_headers
        self.init_ui()

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

    # --- МЕТОДЫ-ЗАГЛУШКИ ДЛЯ CRUD ---

    def refresh_data(self):
        """Пункт 1: Просмотр (загрузка данных из БД)"""
        print(f"Обновляем таблицу {self.table_name}...")
        # Сюда мы позже впишем вызов DBManager

    def add_row(self):
        """Пункт 2: Добавление"""
        print(f"Открываем форму добавления для {self.table_name}")
        # Здесь будет всплывающее окно с полями ввода

    def delete_row(self):
        """Пункт 3: Удаление"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для удаления!")
            return

        row = selected_items[0].row()
        confirm = QMessageBox.question(self, "Подтверждение",
                                       "Вы уверены, что хотите удалить эту запись?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            print(f"Удаляем строку {row} из {self.table_name}")
            self.table.removeRow(row)