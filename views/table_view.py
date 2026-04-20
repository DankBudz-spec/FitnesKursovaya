from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QHeaderView, QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt
from controllers.table_controller import TableController
from views.add_dialog import AddDialog
from PyQt6.QtCore import QDate


class TableView(QWidget):
    def __init__(self, table_name, russian_headers, role="Администратор"):
        super().__init__()
        self.table_name = table_name
        self.russian_headers = russian_headers
        self.controller = TableController()
        self.init_ui()
        self.refresh_data()

        # Логика прав доступа к кнопкам
        if role == "Клиент":
            self.btn_add.hide()
            self.btn_delete.hide()
            self.btn_edit.hide()
        elif role == "Тренер":
            # Тренеру можно редактировать, но нельзя удалять/добавлять во многих таблицах
            if table_name in ["staff", "payments", "membership_types"]:
                self.btn_add.hide()
                self.btn_delete.hide()
        elif role == "Менеджер":
            # Менеджеру нельзя редактировать справочники (Зоны, Типы абонементов)
            # Это задача Администрации [cite: 40]
            forbidden_tables = ["membership_types", "zones", "staff", "classes"]
            if table_name in forbidden_tables:
                self.btn_add.hide()
                self.btn_delete.hide()
                self.btn_edit.hide()

            # Удалять клиентов или платежи менеджеру запретим
            if table_name in ["clients", "payments"]:
                self.btn_delete.hide()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Создаем таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.russian_headers))
        self.table.setHorizontalHeaderLabels(self.russian_headers)

        for i, header in enumerate(self.russian_headers):
            # Если в заголовке есть слово "Фото", "Заметки" или "Пароль" — скрываем
            if header in ["Фото", "Логин", "Пароль"]:
                self.table.setColumnHidden(i, True)

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

        # НОВАЯ КНОПКА ЦЕНЫ
        self.btn_price = QPushButton("💰 Узнать цену")
        self.btn_price.clicked.connect(self.show_price_logic)

        self.btn_freeze = QPushButton("❄️ Заморозить")

        # Показываем только в абонементах
        if self.table_name != "client_subscriptions":
            self.btn_price.hide()
            self.btn_freeze.hide()

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_price)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_freeze)
        btn_layout.addWidget(self.btn_refresh)

        layout.addLayout(btn_layout)

        # 4. Подключаем сигналы (события)
        self.btn_add.clicked.connect(self.add_row)
        self.btn_delete.clicked.connect(self.delete_row)
        self.btn_refresh.clicked.connect(lambda: self.refresh_data(show_msg=True))
        self.btn_edit.clicked.connect(self.edit_row)
        self.btn_freeze.clicked.connect(self.freeze_logic)

    def refresh_data(self, show_msg=False):
        try:
            self.controller.sync_table(self.table, self.table_name)
            if show_msg:
                QMessageBox.information(self, "Успех", "Данные успешно обновлены")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить данные: {str(e)}")


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
        id_item = self.table.item(row, 0)
        if not id_item:
            return

        record_id = id_item.text()

        # 3. Интеллектуальное подтверждение каскадного удаления (Пункт 3 Лаб. 9)
        warning_text = f"Вы уверены, что хотите удалить запись с ID {record_id}?"

        # Если удаляем "Родительские" таблицы, предупреждаем о каскаде
        cascade_tables = {
            "clients": "ВСЕ абонементы, платежи, посещения и записи этого клиента",
            "zones": "ВСЕ оборудование в этой зоне и связанное с ней расписание",
            "membership_types": "ВСЕ активные абонементы данного типа у всех клиентов",
            "staff": "ВСЕ записи расписания, закрепленные за этим тренером",
            "classes": "ВСЕ тренировки этого вида из расписания"
        }

        if self.table_name in cascade_tables:
            warning_text += f"\n\n⚠️ ВНИМАНИЕ: Произойдет КАСКАДНОЕ УДАЛЕНИЕ!\nБудут безвозвратно удалены: {cascade_tables[self.table_name]}."

        # 3. Подтверждение удаления
        confirm = QMessageBox.question(
            self, "Подтверждение",
            warning_text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        # 4. Выполняем удаление через контроллер
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

    def show_price_logic(self):
        """Метод для кнопки 'Узнать цену' в главном окне"""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Сначала выберите строку с абонементом!")
            return

        row = selected[0].row()
        sub_id = self.table.item(row, 0).text()

        # ИСПОЛЬЗУЕМ КОНТРОЛЛЕР! Никакого SQL в интерфейсе.
        c_id, t_id = self.controller.get_subscription_info(sub_id)

        if c_id and t_id:
            info = self.controller.get_membership_data(t_id)
            reg_date = self.controller.get_client_reg_date(c_id)

            if not info: return

            price = info['price']
            msg = ""
            if reg_date:
                days = (QDate.currentDate().toPyDate() - reg_date).days
                if days >= 1095:
                    price = float(price) * 0.9
                    msg = f"\n\n🎉 У клиента скидка 10% (стаж {days} дн.)"

            QMessageBox.information(self, "Расчет", f"Цена: {price:.2f} руб.{msg}")

    def freeze_logic(self):
        """Метод для кнопки 'Заморозить'"""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Сначала выберите строку с абонементом!")
            return

        row = selected[0].row()
        sub_id = self.table.item(row, 0).text()

        # Вызываем стандартное окошко ввода числа от PyQt6
        days, ok = QInputDialog.getInt(
            self,
            "Заморозка абонемента",
            "Введите количество дней (макс. 30):",
            value=7, min=1, max=30, step=1
        )

        # Если пользователь нажал "ОК" и ввел число
        if ok:
            success, msg = self.controller.freeze_subscription(sub_id, days)
            if success:
                QMessageBox.information(self, "Успех", msg)
                self.refresh_data()  # Обновляем таблицу, чтобы показать новые данные
            else:
                QMessageBox.warning(self, "Ошибка", msg)
