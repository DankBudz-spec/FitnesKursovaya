from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QHeaderView, QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt


class ClientDashboardView(QWidget):
    def __init__(self, controller, client_id):
        super().__init__()
        self.controller = controller
        self.client_id = client_id
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- ПРОФИЛЬ КЛИЕНТА ---
        self.lbl_profile = QLabel("Загрузка профиля...")
        self.lbl_profile.setStyleSheet("""
            background-color: #2c3e50; color: white; 
            font-size: 16px; font-weight: bold; 
            padding: 15px; border-radius: 8px;
        """)
        main_layout.addWidget(self.lbl_profile)

        content_layout = QHBoxLayout()

        # --- ЛЕВАЯ ПАНЕЛЬ: ДОСТУПНЫЕ ЗАНЯТИЯ ---
        schedule_group = QGroupBox("📅 Расписание занятий")
        schedule_layout = QVBoxLayout()

        self.table_schedule = QTableWidget()
        self.table_schedule.setColumnCount(7)
        self.table_schedule.setHorizontalHeaderLabels(
            ["ID", "Занятие", "Тренер", "Зал", "Начало", "Конец", "Своб. мест"])
        self.table_schedule.setColumnHidden(0, True)  # Прячем ID
        self.table_schedule.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_schedule.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        schedule_layout.addWidget(self.table_schedule)

        self.btn_register = QPushButton("✍️ Записаться на тренировку")
        self.btn_register.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; height: 35px;")
        self.btn_register.clicked.connect(self.on_register)
        schedule_layout.addWidget(self.btn_register)

        schedule_group.setLayout(schedule_layout)
        content_layout.addWidget(schedule_group, 6)  # Пропорция ширины 60%

        # --- ПРАВАЯ ПАНЕЛЬ: МОИ ЗАПИСИ ---
        my_reg_group = QGroupBox("📋 Мои записи")
        my_reg_layout = QVBoxLayout()

        self.table_my_regs = QTableWidget()
        self.table_my_regs.setColumnCount(4)
        self.table_my_regs.setHorizontalHeaderLabels(["ID", "Занятие", "Время", "Статус"])
        self.table_my_regs.setColumnHidden(0, True)  # Прячем ID
        self.table_my_regs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_my_regs.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        my_reg_layout.addWidget(self.table_my_regs)

        self.btn_cancel = QPushButton("❌ Отменить запись")
        self.btn_cancel.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; height: 35px;")
        self.btn_cancel.clicked.connect(self.on_cancel)
        my_reg_layout.addWidget(self.btn_cancel)

        my_reg_group.setLayout(my_reg_layout)
        content_layout.addWidget(my_reg_group, 4)  # Пропорция ширины 40%

        main_layout.addLayout(content_layout)
        self.load_data()

    def load_data(self):
        try:
            # 1. Профиль
            profile = self.controller.get_profile_info(self.client_id)
            if profile:
                title, start, end, freeze, is_blocked, access = profile
                status_text = "ЗАБЛОКИРОВАН" if is_blocked == 1 else "АКТИВЕН"
                self.lbl_profile.setText(
                    f"🎟 Абонемент: {title} (Уровень: {access}) | Статус: {status_text} | "
                    f"Действует до: {end} | Доступно дней заморозки: {freeze}"
                )
            else:
                self.lbl_profile.setText("⚠️ У вас нет активного абонемента. Обратитесь к менеджеру.")

            # 2. Общее расписание
            schedule_data = self.controller.get_available_schedule()
            self.table_schedule.setRowCount(0)
            if schedule_data:
                for row_idx, row_data in enumerate(schedule_data):
                    self.table_schedule.insertRow(row_idx)
                    # Берем все колонки кроме последней (required_access_level)
                    for col_idx, value in enumerate(row_data[:-1]):
                        self.table_schedule.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

            # 3. Мои записи
            my_regs = self.controller.get_my_registrations(self.client_id)
            self.table_my_regs.setRowCount(0)
            if my_regs:
                for row_idx, row_data in enumerate(my_regs):
                    self.table_my_regs.insertRow(row_idx)
                    for col_idx, value in enumerate(row_data):
                        self.table_my_regs.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        except Exception as e:
            QMessageBox.critical(self, "Критическая ошибка", f"Не удалось загрузить данные личного кабинета:\n{str(e)}")

    def on_register(self):
        selected = self.table_schedule.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите занятие из расписания!")
            return

        schedule_id = self.table_schedule.item(selected[0].row(), 0).text()
        success, msg = self.controller.register_for_class(self.client_id, schedule_id)

        if success:
            QMessageBox.information(self, "Успех", msg)
            self.load_data()
        else:
            QMessageBox.critical(self, "Ошибка записи", msg)

    def on_cancel(self):
        selected = self.table_my_regs.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите вашу запись для отмены!")
            return

        status = self.table_my_regs.item(selected[0].row(), 3).text()
        if status != "Записан":
            QMessageBox.warning(self, "Внимание", "Можно отменить только актуальную запись!")
            return

        reg_id = self.table_my_regs.item(selected[0].row(), 0).text()
        success, msg = self.controller.cancel_registration(reg_id)

        if success:
            QMessageBox.information(self, "Успех", msg)
            self.load_data()
        else:
            QMessageBox.critical(self, "Ошибка отмены", msg)