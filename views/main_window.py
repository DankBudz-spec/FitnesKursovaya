import sys
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication, QDialog
from qt_material import apply_stylesheet
from views.table_view import TableView
from views.login_window import LoginWindow


class MainWindow(QMainWindow):
    def __init__(self, user_role, user_name):
        super().__init__()
        # Сохраняем данные пользователя
        self.user_role = user_role
        self.user_name = user_name

        self.setWindowTitle(f"Fintes — {self.user_name} ({self.user_role})")
        self.resize(1500, 800)

        self.tabs = QTabWidget()
        self.tabs.setMovable(True)
        self.setCentralWidget(self.tabs)

        # 1. Сначала инициализируем все возможные вкладки
        self.init_all_tabs()

        # 2. Затем скрываем лишние согласно роли
        self.apply_permissions()

    def apply_permissions(self):
        """
        Оставляет только те вкладки, которые разрешены данной роли.
        """
        permissions = {
            "Администратор": None,
            "Менеджер": ["👥 Клиенты", "💳 Типы абонементов", "📜 Активные абонементы", "🚪 Посещения", "💰 Платежи"],
            "Тренер": ["📅 Расписание", "📝 Записи", "⚙️ Оборудование", "🏃 Виды занятий"],
            "Клиент": ["📅 Расписание", "📝 Записи"]
        }

        allowed_tabs = permissions.get(self.user_role)

        # Если роль не Администратор (у него None, т.е. разрешено всё)
        if allowed_tabs is not None:
            # Проходим по вкладкам с конца, чтобы индексы не сбивались при удалении
            for i in range(self.tabs.count() - 1, -1, -1):
                tab_text = self.tabs.tabText(i)
                if tab_text not in allowed_tabs:
                    self.tabs.removeTab(i)

    def init_all_tabs(self):
        # Конфигурация остается как у тебя, только добавим заголовки в нужном порядке
        tables_config = {
            "membership_types": [["ID", "Название", "Стоимость", "Срок", "Доступ"], "💳 Типы абонементов"],
            "clients": [
                ["ID", "ФИО", "Телефон", "Доп. тел.", "Email", "Дата рожд.", "Адрес", "Регистрация", "Заметки", "Фото",
                 "Логин", "Пароль"], "👥 Клиенты"],
            "staff": [["ID", "ФИО", "Должность", "Специализация", "Ставка", "Телефон", "Принят", "Логин", "Пароль"],
                      "👔 Персонал"],
            "classes": [["ID", "Название", "Описание"], "🏃 Виды занятий"],
            "zones": [["ID", "Название", "Вместимость", "Уровень"], "📍 Зоны"],
            "equipment": [["ID", "Зона", "Название", "Куплено", "Последнее ТО", "Состояние"], "⚙️ Оборудование"],
            "client_subscriptions": [["ID", "Клиент", "Тип абонемента", "Начало", "Конец", "Заморозка", "Блокировка"],
                                     "📜 Активные абонементы"],
            "schedule": [["ID", "Занятие", "Тренер", "Зона", "Начало", "Конец"], "📅 Расписание"],
            "class_registrations": [["ID", "Запись", "Клиент", "Время", "Статус"], "📝 Записи"],
            "attendance_log": [["ID", "Клиент", "Вход", "Выход"], "🚪 Посещения"],
            "payments": [["ID", "Клиент", "Сумма", "Дата", "Метод"], "💰 Платежи"]
        }

        for table_db_name, info in tables_config.items():
            tab_widget = TableView(table_db_name, info[0], role=self.user_role)
            self.tabs.addTab(tab_widget, info[1])
