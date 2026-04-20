import hashlib
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QPushButton,
                             QLabel, QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from database.db_manager import DBManager
from database.queries import SQLQueries

class LoginWindow(QDialog):
    login_success = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.db = DBManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Вход в систему — Fintes")
        self.setFixedSize(400, 450)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(50, 20, 50, 20)

        # --- ЦЕНТРИРОВАНИЕ: Добавляем верхнюю распорку ---
        layout.addStretch()

        # Заголовок
        header = QLabel("АВТОРИЗАЦИЯ")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #3498db; margin-bottom: 20px;")
        layout.addWidget(header)

        # Поле Логин
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин (Телефон)")
        self.login_input.setMinimumHeight(45)
        self.login_input.setStyleSheet("padding-left: 10px;")
        layout.addWidget(self.login_input)

        # Поле Пароль
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(45)
        self.password_input.setStyleSheet("padding-left: 10px;")
        layout.addWidget(self.password_input)

        # Кнопка Войти
        self.btn_login = QPushButton("ВОЙТИ")
        self.btn_login.setMinimumHeight(50)
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white; 
                font-weight: bold; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_login.clicked.connect(self.check_auth)
        layout.addWidget(self.btn_login)

        # --- ЦЕНТРИРОВАНИЕ: Добавляем нижнюю распорку ---
        layout.addStretch()

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def check_auth(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        #hashed_pw = self._hash_password(password)

        # Проверяем последовательно: сначала сотрудников, потом клиентов
        for user_type in ["staff", "clients"]:
            query = SQLQueries.get_auth_query(user_type) # Используем метод из queries.py
            response = self.db.execute_query(query, params=(login,), fetch=True)

            if response and response[0]:
                user_data = response[0][0]
                db_full_name = user_data[0]
                db_role = user_data[1] # Для клиентов вернет 'Клиент'
                db_hash = user_data[2]

                if password == db_hash:
                    self.user_role = db_role
                    self.user_name = db_full_name
                    self.login_success.emit(db_role, db_full_name)
                    self.accept()
                    return

        QMessageBox.critical(self, "Ошибка доступа", "Неверный логин или пароль!")