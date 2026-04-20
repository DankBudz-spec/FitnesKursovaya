from PyQt6.QtWidgets import QDialog
from views.login_window import LoginWindow
from views.main_window import MainWindow


class MainController:
    def __init__(self):
        # Храним ссылку на главное окно, чтобы оно не удалилось из памяти
        self.main_window = None

    def start_app(self):
        """
        Управляет переходом: Авторизация -> Главный экран.
        Возвращает True, если приложение должно продолжать работу.
        """
        # Создаем экземпляр окна входа
        login_dialog = LoginWindow()

        # Запускаем модальный диалог входа
        # Метод exec() блокирует выполнение, пока диалог не будет закрыт
        if login_dialog.exec() == QDialog.DialogCode.Accepted:
            # Если в login_window.py вызвана self.accept(), извлекаем данные
            user_role = getattr(login_dialog, 'user_role', "Администратор")
            user_name = getattr(login_dialog, 'user_name', "Пользователь")

            # Инициализируем главное окно, передавая роль и имя
            self.main_window = MainWindow(user_role, user_name)
            self.main_window.show()

            return True  # Сигнал для main.py запустить цикл событий

        return False  # Если пользователь закрыл окно входа