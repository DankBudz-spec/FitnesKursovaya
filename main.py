import sys
from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from controllers.main_controller import MainController


def main():
    # Инициализация графической оболочки
    app = QApplication(sys.argv)

    # Применяем тему оформления (как было в твоем MainWindow)
    apply_stylesheet(app, theme='dark_blue.xml')

    # Создаем главный контроллер
    controller = MainController()

    # Запускаем логику перехода. Если она вернула True — запускаем приложение.
    if controller.start_app():
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()