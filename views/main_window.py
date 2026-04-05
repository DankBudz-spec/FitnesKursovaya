import sys
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication
from qt_material import apply_stylesheet
from views.table_view import TableView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fintes — Система управления")
        self.resize(1500, 800)

        # Создаем виджет вкладок
        self.tabs = QTabWidget()
        # Разрешаем перетаскивание вкладок для удобства (опционально)
        self.tabs.setMovable(True)
        self.setCentralWidget(self.tabs)

        # Добавляем все 11 таблиц
        self.init_all_tabs()

    def init_all_tabs(self):
        tables_config = {
            "membership_types": [
                ["ID", "Название", "Цена", "Срок (дн)", "Уровень"], "💳 Типы абонементов"
            ],
            "clients": [
                ["ID", "ФИО", "Телефон", "Доп. телефон", "Email", "Дата рожд.", "Адрес", "Регистрация", "Заметки",
                 "Фото"], "👥 Клиенты"
            ],
            "staff": [
                ["ID", "ФИО", "Должность", "Специализация", "Ставка", "Телефон", "Принят"], "👔 Персонал"
            ],
            "classes": [
                ["ID", "Название", "Описание"], "🏃 Виды занятий"
            ],
            "zones": [
                ["ID", "Название", "Мест", "Уровень"], "📍 Зоны"
            ],
            "equipment": [
                ["ID", "ID Зоны", "Название", "Куплено", "Последнее ТО", "Статус"], "⚙️ Оборудование"
            ],
            "client_subscriptions": [
                ["ID", "ID Клиента", "ID Тарифа", "Начало", "Конец", "Заморозка", "Блок"], "📜 Активные абонементы"
            ],
            "schedule": [
                ["ID", "ID Занятия", "ID Тренера", "ID Зоны", "Начало", "Конец"], "📅 Расписание"
            ],
            "class_registrations": [
                ["ID", "ID Записи", "ID Клиента", "Время записи", "Статус"], "📝 Записи"
            ],
            "attendance_log": [
                ["ID", "ID Клиента", "Вход", "Выход"], "🚪 Посещения"
            ],
            "payments": [
                ["ID", "ID Клиента", "Сумма", "Дата", "Метод"], "💰 Платежи"
            ]
        }

        # Циклом создаем все вкладки
        for table_db_name, info in tables_config.items():
            headers = info[0]
            tab_label = info[1]

            # Создаем экземпляр нашей универсальной таблицы
            tab_widget = TableView(table_db_name, headers)
            self.tabs.addTab(tab_widget, tab_label)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Применяем современную темную тему
    # 'dark_teal.xml' или 'dark_amber.xml' выглядят очень солидно
    apply_stylesheet(app, theme='dark_blue.xml')

    window = MainWindow()
    window.show()
    sys.exit(app.exec())