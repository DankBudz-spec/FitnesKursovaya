from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QListWidget, QGroupBox, QPushButton, QComboBox)
from PyQt6.QtCore import Qt
import matplotlib

matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class DashboardView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        # Используем вертикальный лейаут как основной, чтобы сверху была панель управления
        main_layout = QVBoxLayout(self)

        # --- ВЕРХНЯЯ ПАНЕЛЬ (Кнопка обновления) ---
        top_bar = QHBoxLayout()
        self.btn_refresh = QPushButton("🔄 Обновить дашборд")
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setMinimumHeight(35)
        self.btn_refresh.setStyleSheet(
            "background-color: #3498db; color: white; font-weight: bold; border-radius: 5px; padding: 0 20px;"
        )
        self.btn_refresh.clicked.connect(self.load_data)  # Привязываем полное обновление
        top_bar.addWidget(self.btn_refresh)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        # --- ЦЕНТРАЛЬНАЯ ЧАСТЬ (Списки и График) ---
        content_layout = QHBoxLayout()

        # ЛЕВАЯ ПАНЕЛЬ (KPI и списки)
        left_panel = QVBoxLayout()

        # 1. Карточка: Активные клиенты
        self.lbl_active_clients = QLabel("Активных клиентов: ...")
        self.lbl_active_clients.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 10px; background-color: #2E7D32; color: white; border-radius: 5px;"
        )
        left_panel.addWidget(self.lbl_active_clients)

        # 2. Список: Должники
        debtors_group = QGroupBox("⚠️Заблокированные абонементы")
        debtors_layout = QVBoxLayout()
        self.list_debtors = QListWidget()
        self.list_debtors.setStyleSheet("font-size: 14px;")
        debtors_layout.addWidget(self.list_debtors)
        debtors_group.setLayout(debtors_layout)
        left_panel.addWidget(debtors_group)

        # 3. Список: Сломанное оборудование
        eq_group = QGroupBox("🔧 Оборудование в ремонте")
        eq_group.setStyleSheet("color: #e67e22; font-weight: bold;")  # Оранжевый акцент
        eq_layout = QVBoxLayout()
        self.list_eq = QListWidget()
        self.list_eq.setStyleSheet("font-size: 14px; color: white; font-weight: normal;")
        eq_layout.addWidget(self.list_eq)
        eq_group.setLayout(eq_layout)
        left_panel.addWidget(eq_group)

        content_layout.addLayout(left_panel, 1)

        # ПРАВАЯ ПАНЕЛЬ (График)
        right_panel = QVBoxLayout()

        # Элементы управления графиком
        chart_controls = QHBoxLayout()
        chart_controls.addWidget(QLabel("<b>Период графика:</b>"))
        self.combo_period = QComboBox()
        self.combo_period.addItems(["За день (сегодня)", "За неделю", "За месяц"])
        # При смене периода перерисовываем только график
        self.combo_period.currentIndexChanged.connect(self.update_chart)
        chart_controls.addWidget(self.combo_period)
        chart_controls.addStretch()
        right_panel.addLayout(chart_controls)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        right_panel.addWidget(self.canvas)

        content_layout.addLayout(right_panel, 2)

        main_layout.addLayout(content_layout)

        # Загружаем данные при старте
        self.load_data()

    def load_data(self):
        """Полное обновление всех данных на дашборде"""
        metrics = self.controller.get_dashboard_metrics()

        # Обновляем KPI
        self.lbl_active_clients.setText(f"Активных клиентов: {metrics.get('active_clients', 0)}")

        # Обновляем Должников
        self.list_debtors.clear()
        for debtor in metrics.get('debtors', []):
            name, phone, date = debtor
            self.list_debtors.addItem(f"{name} | 📞 {phone} | 📅 с {date}")
        if not metrics.get('debtors'):
            self.list_debtors.addItem("✅ Заблокированных абонементов нет!")

        # Обновляем Оборудование
        self.list_eq.clear()
        for eq in metrics.get('broken_eq', []):
            zone, name, date = eq
            self.list_eq.addItem(f"[{zone}] {name} (ТО: {date})")
        if not metrics.get('broken_eq'):
            self.list_eq.addItem("✅ Всё оборудование исправно!")

        # Обновляем график
        self.update_chart()

    def update_chart(self):
        """Перерисовывает график в зависимости от выбранного периода"""
        idx = self.combo_period.currentIndex()
        period = "day" if idx == 0 else ("month" if idx == 2 else "week")

        stats = self.controller.get_chart_data(period)
        self.ax.clear()

        if stats:
            if period == "day":
                # Для дня выводим часы
                labels = [f"{int(row[0])}:00" for row in stats]
                title_text = "Посещаемость за сегодня (по часам)"
            else:
                # Для недели/месяца выводим ММ-ДД
                labels = [str(row[0])[-5:] for row in stats]
                title_text = "Посещаемость за последние 30 дней" if period == "month" else "Посещаемость за последние 7 дней"

            visits = [row[1] for row in stats]

            self.ax.bar(labels, visits, color='#1976D2')
            self.ax.set_title(title_text)
            self.ax.set_ylabel('Количество входов')
            self.ax.grid(axis='y', linestyle='--', alpha=0.7)

            # Если это месяц, наклоняем подписи, чтобы не слипались
            if period == "month":
                self.ax.tick_params(axis='x', rotation=45)
            else:
                self.ax.tick_params(axis='x', rotation=0)
        else:
            self.ax.text(0.5, 0.5, "Нет данных за выбранный период", ha='center', va='center')

        self.figure.tight_layout()
        self.canvas.draw()