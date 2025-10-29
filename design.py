# -*- coding: utf-8 -*-

from PySide6.QtCore import (Qt, QRect, QPropertyAnimation, QEasingCurve, 
                           QPoint, Signal, QSize, Property)
from PySide6.QtGui import (QPainter, QColor, QBrush, QPen, QPixmap, 
                          QMouseEvent, QPaintEvent, QIcon)
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QLabel,
                              QPushButton, QWidget, QGraphicsDropShadowEffect)


class AnimatedSwitch(QWidget):
    """Анимированный переключатель с поддержкой перетаскивания"""
    toggled = Signal(bool)
    
    def __init__(self, parent=None, width=351, height=121, handle_radius=55):
        super().__init__(parent)
        self.setFixedSize(width, height)
        
        # Параметры переключателя
        self.width = width
        self.height = height
        self.handle_radius = handle_radius
        self.handle_margin = 5
        
        # Состояние
        self._checked = False
        self._handle_position = self.handle_margin
        self.is_dragging = False
        self.drag_start_x = 0
        
        # Настройка анимации
        self.animation = QPropertyAnimation(self, b"handle_position")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # Иконка в центре ползунка
        self.icon_label = QLabel(self)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        # Тема по умолчанию
        self.is_dark_theme = False
        self.update_icon()
        
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_icon_position()
    
    def get_handle_position(self):
        return self._handle_position
    
    def set_handle_position(self, pos):
        self._handle_position = pos
        self.update()
        self.update_icon_position()
    
    handle_position = Property(float, get_handle_position, set_handle_position)
    
    def update_icon_position(self):
        """Обновляет позицию иконки в центре ползунка"""
        icon_size = 40
        x = int(self._handle_position + (self.handle_radius * 2 - icon_size) / 2)
        y = int((self.height - icon_size) / 2)
        self.icon_label.setGeometry(x, y, icon_size, icon_size)
    
    def update_icon(self):
        """Обновляет иконку в зависимости от состояния и темы"""
        if self._checked:
            icon_path = "img/logo_main_g.png"
        else:
            icon_path = "img/logo_main_w.png" if self.is_dark_theme else "img/logo_main_n.png"
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, 
                                         Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(scaled_pixmap)
    
    def set_theme(self, is_dark):
        """Устанавливает тему"""
        self.is_dark_theme = is_dark
        self.update_icon()
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Фон переключателя (траектория ползунка) — всегда одинаковый
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#A2A2A2")))  # Не меняется
        painter.drawRoundedRect(0, 0, self.width, self.height, 
                            self.height / 2, self.height / 2)
        
        # Ползунок — цвет зависит от темы
        if self.is_dark_theme:
            painter.setBrush(QBrush(QColor(0, 0, 0)))  # Белый в тёмной теме
        else:
            painter.setBrush(QBrush(QColor(255, 255, 255)))  # Чёрный в светлой теме
        
        handle_y = (self.height - self.handle_radius * 2) / 2
        painter.drawEllipse(int(self._handle_position), int(handle_y),
                        self.handle_radius * 2, self.handle_radius * 2)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            handle_rect = QRect(int(self._handle_position), 
                            int((self.height - self.handle_radius * 2) / 2),
                            self.handle_radius * 2, self.handle_radius * 2)
            
            # Останавливаем анимацию, чтобы получить актуальную позицию
            self.animation.stop()
            
            if handle_rect.contains(event.position().toPoint()):
                # Клик на ползунок — просто переключаем состояние (без перетаскивания)
                self.toggle()
            else:
                # Клик на дорожку — переключаем состояние
                self.toggle()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            new_pos = event.position().x() - self.drag_start_x
            min_pos = self.handle_margin
            max_pos = self.width - self.handle_radius * 2 - self.handle_margin
            
            self._handle_position = max(min_pos, min(new_pos, max_pos))
            self.update()
            self.update_icon_position()

    def mouseReleaseEvent(self, event):
        if self.is_dragging:
            self.is_dragging = False
            
            middle = self.width / 2
            if self._handle_position + self.handle_radius > middle:
                self.set_checked(True)
            else:
                self.set_checked(False)
    
    def toggle(self):
        self.set_checked(not self._checked)
    
    def set_checked(self, checked):
        self._checked = checked
        
        end_position = (self.width - self.handle_radius * 2 - self.handle_margin 
                       if checked else self.handle_margin)
        
        self.animation.setStartValue(self._handle_position)
        self.animation.setEndValue(end_position)
        self.animation.start()
        
        self.update_icon()
        self.toggled.emit(checked)
    
    def is_checked(self):
        return self._checked


class SmallSwitch(QWidget):
    """Маленький переключатель для выбора темы"""
    toggled = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)
        
        self._checked = False
        self._handle_position = 0
        
        self.is_dark_theme = False  # ← тема интерфейса (не состояние!)
        
        self.animation = QPropertyAnimation(self, b"handle_position")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def get_handle_position(self):
        return self._handle_position
    
    def set_handle_position(self, pos):
        self._handle_position = pos
        self.update()
    
    handle_position = Property(float, get_handle_position, set_handle_position)
    
    def set_theme(self, is_dark):
        """Устанавливает текущую тему интерфейса (для цвета ползунка)"""
        self.is_dark_theme = is_dark
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 1. Фон — всегда #A2A2A2
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#A2A2A2")))
        painter.drawRoundedRect(0, 0, 60, 30, 15, 15)
        
        # 2. Ползунок — цвет зависит от ГЛОБАЛЬНОЙ темы интерфейса
        painter.setOpacity(1.0)
        painter.setPen(Qt.PenStyle.NoPen)
        if self.is_dark_theme:
            painter.setBrush(QBrush(QColor(0, 0, 0)))      # чёрный в тёмной теме
        else:
            painter.setBrush(QBrush(QColor(255, 255, 255)))  # белый в светлой теме
        painter.drawRoundedRect(int(self._handle_position), 0, 30, 30, 15, 15)
        
        sun_pixmap = QPixmap("img/sun.png")
        if not sun_pixmap.isNull():
            scaled_sun = sun_pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
            # Если темная тема - полупрозрачное, если светлая - полностью видимое
            if not self.is_dark_theme:
                painter.setOpacity(1.0)
            else:
                painter.setOpacity(0.3)
            painter.drawPixmap(5, 5, scaled_sun)
        
        # Луна справа (белая при темной теме)
        painter.setOpacity(1.0)
        moon_pixmap = QPixmap("img/moon.png")
        if not moon_pixmap.isNull():
            scaled_moon = moon_pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
            # Инвертируем цвета луны для белого цвета в темной теме
            if self.is_dark_theme:
                from PySide6.QtGui import QImage
                img = scaled_moon.toImage()
                img.invertPixels()
                scaled_moon = QPixmap.fromImage(img)
            else:
                painter.setOpacity(0.3)
            painter.drawPixmap(35, 5, scaled_moon)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle()
    
    def toggle(self):
        self.set_checked(not self._checked)
    
    def set_checked(self, checked):
        self._checked = checked
        end_position = 30 if checked else 0
        self.animation.setStartValue(self._handle_position)
        self.animation.setEndValue(end_position)
        self.animation.start()
        self.toggled.emit(checked)
    
    def is_checked(self):
        return self._checked

class CustomWindow(QDialog):
    def __init__(self):
        super().__init__()
        
        # Текущая тема (инициализируем ДО setupUi)
        self.is_dark_theme = False
        
        # Для перемещения окна
        self.dragging = False
        self.drag_position = QPoint()
        
        self.setupUi()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
    def setupUi(self):
        self.setObjectName("Dialog")
        self.setFixedSize(380, 400)  # Фиксированный размер + отступы для тени
        
        # Главный контейнер с тенью
        self.main_container = QWidget(self)
        self.main_container.setGeometry(5, 5, 372, 362)
        self.main_container.setStyleSheet("""
            QWidget {
                background: rgb(255, 255, 255);
                border-radius: 25px;
            }
        """)
        
        # Добавляем эффект тени
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 5)
        self.main_container.setGraphicsEffect(shadow)
        
        # Главный переключатель
        self.main_switch = AnimatedSwitch(self.main_container, 351, 121, 55)
        self.main_switch.setGeometry(10, 70, 351, 200)
        self.main_switch.setStyleSheet("""
                QAnimatedSwitch {
                    font-size: 24px;
                    font-weight: bold;
                    border: none;
                    background: white;
                }
                QAnimatedSwitch:hover {
                    border-radius: 15px;
                    background: transparent;
                    color: rgba(0, 0, 0, 0.1);
                }
        """)
        self.main_switch.toggled.connect(self.change_switch_icon)
        
        # Кнопка закрытия
        self.close_button = QPushButton("×", self.main_container)
        self.close_button.setObjectName("close_button")
        self.close_button.setGeometry(330, 10, 31, 31)
        self.close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: black;
                font-size: 24px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                border-radius: 15px;
                background: transparent;
                color: rgba(0, 0, 0, 0.7);
            }
        """)
        self.close_button.clicked.connect(self.close)
        
        # Кнопка сворачивания
        self.minimize_button = QPushButton("−", self.main_container)
        self.minimize_button.setObjectName("minimize_button")
        self.minimize_button.setGeometry(300, 10, 31, 31)
        self.minimize_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: black;
                font-size: 24px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                border-radius: 15px;
                background: transparent;
                color: rgba(0, 0, 0, 0.7);
            }
        """)
        self.minimize_button.clicked.connect(self.showMinimized)
        
        # Фрейм с кнопками "Основной" и "Альтернативный"
        self.frame_2 = QFrame(self.main_container)
        self.frame_2.setObjectName("frame_2")
        self.frame_2.setGeometry(10, 200, 351, 40)
        self.frame_2.setStyleSheet("""
            QFrame {
                border-radius: 20px;
                background: rgb(162, 162, 162);
            }
        """)
        
        self.main_button = QPushButton("Основной", self.frame_2)
        self.main_button.setObjectName("main_button")
        self.main_button.setGeometry(2, 2, 171, 36)
        self.main_button.setStyleSheet("""
            QPushButton {
                border-radius: 17px;
                background: rgb(255, 255, 255);
                color: black;
                font-weight: bold;
            }
        """)
        
        self.alt_button = QPushButton("Альтернативный", self.frame_2)
        self.alt_button.setObjectName("alt_button")
        self.alt_button.setGeometry(178, 2, 171, 36)
        self.alt_button.setStyleSheet("""
            QPushButton {
                border-radius: 17px;
                background: rgb(162, 162, 162);
                color: rgb(0, 0, 0);
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgb(142, 142, 142);
            }
        """)
        
        # Логотип
        self.logo_label = QLabel(self.main_container)
        self.logo_label.setObjectName("logo_label")
        self.logo_label.setGeometry(15, 10, 120, 40)
        self.update_logo()
        
        # Кнопка Telegram
        self.telegram_button = QPushButton(self.main_container)
        self.telegram_button.setObjectName("telegram_button")
        self.telegram_button.setGeometry(330, 315, 40, 40)
        self.telegram_button.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                background: rgb(162, 162, 162);
                border: none;
                padding: 8px;
            }
            QPushButton:hover {
                background: rgb(142, 142, 142);
            }
        """)
        self.set_button_icon(self.telegram_button, "img/telegram.png", shift_left=1)
        
        # Кнопка GitHub
        self.github_button = QPushButton(self.main_container)
        self.github_button.setObjectName("github_button")
        self.github_button.setGeometry(245, 315, 80, 40)
        self.github_button.setStyleSheet("""
            QPushButton {
                border-radius: 20px;
                background: rgb(162, 162, 162);
                border: none;
                padding: 8px;
            }
            QPushButton:hover {
                background: rgb(142, 142, 142);
            }
        """)
        self.set_button_icon(self.github_button, "img/github.png")
        github_icon = QIcon("img/github.png")
        self.github_button.setIcon(github_icon)
        self.github_button.setIconSize(QSize(64, 32))
        self.github_button.setCursor(Qt.PointingHandCursor)


        # Переключатель темы
        self.theme_switch = SmallSwitch(self.main_container)
        self.theme_switch.setGeometry(10, 320, 60, 30)
        self.theme_switch.set_theme(self.is_dark_theme)
        self.theme_switch.toggled.connect(self.change_theme)

    def change_switch_icon(self, checked):
        icon_path = "img/logo_main_g.png" if checked else "img/logo_main.png"
        self.main_switch.setIcon(QIcon(icon_path))
    def set_button_icon(self, button, icon_path, shift_left=0):
        """Устанавливает иконку и смещает её влево на shift_left пикселей"""
        pixmap = QPixmap(icon_path)
        if pixmap.isNull():
            button.setIcon(QIcon())
            return

        # Масштабируем иконку до нужного размера (например, 24x24)
        icon_size = QSize(28, 28)
        scaled_pixmap = pixmap.scaled(icon_size, Qt.AspectRatioMode.KeepAspectRatio, 
                                    Qt.TransformationMode.SmoothTransformation)

        button_size = QSize(40, 40)
        shifted_pixmap = QPixmap(button_size)
        shifted_pixmap.fill(Qt.GlobalColor.transparent)

        # Рисуем иконку со смещением влево: x = (40 - 24)/2 - shift_left
        painter = QPainter(shifted_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        x = (button_size.width() - icon_size.width()) // 2 - shift_left
        y = (button_size.height() - icon_size.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()

        button.setIcon(QIcon(shifted_pixmap))
        button.setIconSize(button_size)  # чтобы иконка заполнила всю область
    
    def update_logo(self):
        """Обновляет логотип в зависимости от темы"""
        logo_path = "img/logo_w.png" if self.is_dark_theme else "img/logo_n.png"
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
    
    def change_theme(self, is_dark):
        """Изменяет тему приложения"""
        self.is_dark_theme = is_dark
        self.main_switch.set_theme(is_dark)
        self.theme_switch.set_theme(is_dark)
        self.update_logo()

        self.set_button_icon(self.telegram_button, "img/telegram.png", shift_left=1)
        self.set_button_icon(self.github_button, "img/github.png")
        github_icon = QIcon("img/github.png")
        self.github_button.setIcon(github_icon)
        self.github_button.setIconSize(QSize(64, 32))
        self.github_button.setCursor(Qt.PointingHandCursor)
        # Изменяем цвет фона
        if is_dark:
            self.main_container.setStyleSheet("""
                QWidget {
                    background: rgb(0, 0, 0);
                    border-radius: 25px;
                }
            """)
            self.main_switch.setStyleSheet("""
                QAnimatedSwitch {
                    font-size: 24px;
                    font-weight: bold;
                    border: none;
                    border-radius: 15px;
                    background: black;
                }
                QAnimatedSwitch:hover {
                    border-radius: 15px;
                }
            """)
            self.close_button.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    border-radius: 15px;
                    background: transparent;
                    color: rgba(255, 255, 255, 0.7);
                }
            """)
            self.minimize_button.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    border-radius: 15px;
                    background: transparent;
                    color: rgba(255, 255, 255, 0.7);
                }
            """)
            self.main_button.setStyleSheet("""
                QPushButton {
                    border-radius: 17px;
                    background: rgb(0, 0, 0);
                    color: white;
                    font-weight: bold;
                }
            """)
            self.alt_button.setStyleSheet("""
                QPushButton {
                    border-radius: 17px;
                    background: rgb(162, 162, 162);
                    color: rgb(0, 0, 0);
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgb(142, 142, 142);
                }
            """)
        else:
            self.main_container.setStyleSheet("""
                QWidget {
                    background: rgb(255, 255, 255);
                    border-radius: 25px;
                }
            """)
            self.main_switch.setStyleSheet("""
                QAnimatedSwitch {
                    font-size: 24px;
                    font-weight: bold;
                    border: none;
                    background: white;
                }
                QAnimatedSwitch:hover {
                    border-radius: 15px;
                    background: transparent;
                    color: rgba(0, 0, 0, 0.1);
                }
            """)
            self.close_button.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: black;
                    font-size: 24px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    border-radius: 15px;
                    background: transparent;
                    color: rgba(255, 255, 255, 0.7);
                }
            """)
            self.minimize_button.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: black;
                    font-size: 24px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    border-radius: 15px;
                    background: transparent;
                    color: rgba(255, 255, 255, 0.7);
                }
            """)
            self.main_button.setStyleSheet("""
                QPushButton {
                    border-radius: 17px;
                    background: rgb(255, 255, 255);
                    color: black;
                    font-weight: bold;
                }
            """)
            self.alt_button.setStyleSheet("""
                QPushButton {
                    border-radius: 17px;
                    background: rgb(162, 162, 162);
                    color: rgb(0, 0, 0);
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgb(142, 142, 142);
                }
            """)

    def mousePressEvent(self, event):
        """Начало перетаскивания окна"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Проверяем, что клик не на элементах управления
            if event.y() < 50 and event.x() < 290:
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        """Перетаскивание окна"""
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
    
    def mouseReleaseEvent(self, event):
        """Окончание перетаскивания"""
        self.dragging = False