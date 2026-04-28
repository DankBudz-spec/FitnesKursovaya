from PyQt6.QtWidgets import QDialog
from views.login_window import LoginWindow
from views.main_window import MainWindow


class MainController:
    def __init__(self):
        self.main_window = None

    def start_app(self):
        """Начальная точка запуска"""
        return self.show_login()

    def show_login(self):
        """Отображает окно авторизации"""
        # Если главное окно открыто — закрываем его
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        login_dialog = LoginWindow()

        if login_dialog.exec() == QDialog.DialogCode.Accepted:
            user_role = getattr(login_dialog, 'user_role', "Администратор")
            user_name = getattr(login_dialog, 'user_name', "Пользователь")
            user_id = getattr(login_dialog, 'user_id', None)

            # Переходим к созданию главного окна
            self.show_main_window(user_role, user_name, user_id)
            return True

        return False

    def show_main_window(self, user_role, user_name, user_id):
        """Инициализирует и показывает главное окно"""
        self.main_window = MainWindow(user_role, user_name, user_id)

        # ПОДПИСЫВАЕМСЯ НА СИГНАЛ ВЫХОДА
        # Когда в главном окне нажмут "Выйти", контроллер снова вызовет show_login
        self.main_window.logout_requested.connect(self.show_login)

        self.main_window.show()