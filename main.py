import sys
import subprocess
import os
import time
import ctypes
import webbrowser
import psutil
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer, QThread, Signal
from design import CustomWindow

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class WorkerThread(QThread):
    """Поток для выполнения тяжелых операций в фоне"""
    finished = Signal()
    error = Signal(str)
    
    def __init__(self, operation, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            self.operation(*self.args, **self.kwargs)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

def run_as_admin():
    try:
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:])
        
        python_exe = sys.executable
        if python_exe.endswith('python.exe'):
            pythonw_exe = python_exe.replace('python.exe', 'pythonw.exe')
        elif python_exe.endswith('pythonw.exe'):
            pythonw_exe = python_exe
        else:
            pythonw_exe = python_exe
        
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            pythonw_exe, 
            params, 
            None, 
            0
        )
        sys.exit(0)
    except Exception as e:
        print(f"Не удалось запросить права администратора: {e}")
        sys.exit(1)

class MainWindow(CustomWindow):
    
    def __init__(self):
        super().__init__()
        
        self.process = None
        self.worker_thread = None
        self.is_switch_locked = False
        
        self.main_switch.toggled.connect(self.on_main_switch_toggled)
        self.github_button.clicked.connect(self.open_github)
        self.telegram_button.clicked.connect(self.open_telegram)
        
        # Подключаем обработчики для кнопок метода
        self.main_button.clicked.connect(self.on_main_method_selected)
        self.alt_button.clicked.connect(self.on_alt_method_selected)
        
        # Таймер для проверки процесса winws.exe
        self.process_check_timer = QTimer(self)
        self.process_check_timer.timeout.connect(self.check_winws_process)
        self.process_check_timer.start(1000)  # Проверка каждую секунду
    
    def check_winws_process(self):
        """Проверяет запущен ли процесс winws.exe и меняет иконку"""
        is_running = self.is_winws_running()
        
        # Меняем иконку в ползунке
        self.main_switch.set_process_running(is_running)
    
    def is_winws_running(self):
        """Проверяет запущен ли процесс winws.exe"""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == 'winws.exe':
                    return True
            return False
        except Exception as e:
            print(f"Ошибка при проверке процесса: {e}")
            return False
    
    def open_github(self):
        webbrowser.open("https://github.com/redjex")
    
    def open_telegram(self):
        webbrowser.open("https://t.me/aether_discord")

    def kill_discord_processes(self):
        discord_processes = ['discord.exe', 'Discord.exe', 'DiscordPTB.exe', 'DiscordCanary.exe']
        
        print("Завершаю процессы Discord...")
        
        for process_name in discord_processes:
            try:
                result = subprocess.run(
                    f'taskkill /F /IM {process_name}',
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"Процесс {process_name} успешно завершен")
                
            except Exception as e:
                print(f"Ошибка при завершении {process_name}: {e}")
        
        time.sleep(2)
        print("Все процессы Discord завершены")
    
    def on_main_method_selected(self):
        """Обработчик выбора основного метода"""
        print("Выбран основной метод")
        
        # Останавливаем все процессы
        self.kill_all_processes()
        
        # Переключаем switch в OFF
        self.main_switch.blockSignals(True)
        self.main_switch.set_checked(False)
        self.main_switch.blockSignals(False)
        
        # Вызываем родительский метод для обновления UI
        self.switch_to_main_method()
    
    def on_alt_method_selected(self):
        """Обработчик выбора альтернативного метода"""
        print("Выбран альтернативный метод")
        
        # Останавливаем все процессы
        self.kill_all_processes()
        
        # Переключаем switch в OFF
        self.main_switch.blockSignals(True)
        self.main_switch.set_checked(False)
        self.main_switch.blockSignals(False)
        
        # Вызываем родительский метод для обновления UI
        self.switch_to_alt_method()
    
    def on_main_switch_toggled(self, checked):
        if self.is_switch_locked:
            print("⚠️ Переключатель заблокирован! Дождитесь завершения операции...")
            self.main_switch.blockSignals(True)
            self.main_switch.animation.stop()
            self.main_switch._checked = not checked
            if not checked:
                self.main_switch._handle_position = self.main_switch.width - self.main_switch.handle_radius * 2 - self.main_switch.handle_margin
            else:
                self.main_switch._handle_position = self.main_switch.handle_margin
            self.main_switch.update()
            self.main_switch.update_icon_position()
            self.main_switch.update_icon()
            self.main_switch.blockSignals(False)
            return
        
        self.is_switch_locked = True
        self.main_switch.setEnabled(False)
        print(f"🔒 Переключатель заблокирован на 500 мс")
        
        if checked:
            print("Переключатель включен, запускаю последовательность в фоне...")
            self.worker_thread = WorkerThread(self._start_processes_background)
            self.worker_thread.finished.connect(self.on_start_finished)
            self.worker_thread.error.connect(self.on_operation_error)
            self.worker_thread.start()
        else:
            print("Главный переключатель: ВЫКЛЮЧЕН (OFF)")
            self.worker_thread = WorkerThread(self._stop_processes_background)
            self.worker_thread.finished.connect(self.on_stop_finished)
            self.worker_thread.error.connect(self.on_operation_error)
            self.worker_thread.start()
        
        QTimer.singleShot(500, self.unlock_switch)
    
    def _start_processes_background(self):
        """Запускаем процессы в фоновом потоке"""
        self.kill_discord_processes()
        
        # Определяем какой bat файл запускать
        if self.is_alternative_mode:
            # Альтернативный режим - используем выбранный из dropdown
            bat_file = self.selected_bat_file
        else:
            # Основной режим - всегда general (ALT).bat
            bat_file = "general (ALT).bat"
        
        bat_path = os.path.abspath(f"general/{bat_file}")
        
        if os.path.exists(bat_path):
            try:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                self.process = subprocess.Popen(
                    ['cmd', '/c', bat_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP,
                    startupinfo=startupinfo,
                    cwd=os.path.dirname(bat_path)
                )
                
                print(f"Запущен файл: {bat_path} (PID: {self.process.pid})")
                time.sleep(2)
                
            except Exception as e:
                print(f"Ошибка при запуске файла: {e}")
                raise e
        else:
            error_msg = f"Файл не найден: {bat_path}"
            print(error_msg)
            raise FileNotFoundError(error_msg)
    
    def on_start_finished(self):
        """Вызывается когда запуск завершен"""
        print("Процессы успешно запущены")
    
    def unlock_switch(self):
        """Разблокирует переключатель после задержки"""
        self.is_switch_locked = False
        self.main_switch.setEnabled(True)
        print("🔓 Переключатель разблокирован")
    
    def _stop_processes_background(self):
        """Останавливаем процессы в фоновом потоке"""
        self.kill_all_processes()
    
    def on_stop_finished(self):
        """Вызывается когда остановка завершена"""
        print("Процессы успешно остановлены")
    
    def on_operation_error(self, error_msg):
        """Вызывается при ошибке в фоновом потоке"""
        print(f"Ошибка в фоновом потоке: {error_msg}")
        QMessageBox.critical(self, "Ошибка", f"Произошла ошибка:\n{error_msg}")
    
    def kill_all_processes(self):
        """Завершает все запущенные процессы"""
        try:
            print("Завершаю все фоновые процессы...")
            
            # Завершаем все процессы winws.exe
            result = subprocess.run(
                'taskkill /F /IM winws.exe',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ Все процессы winws.exe успешно завершены")
            else:
                print("✓ Процессы winws.exe не найдены")
            
            # Завершаем все процессы cmd.exe связанные с bat файлами
            subprocess.run(
                'taskkill /F /FI "WINDOWTITLE eq zapret*"',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                text=True
            )
            print("✓ Процессы cmd.exe завершены")
            
            # Завершаем процесс BAT если он есть
            if self.process is not None:
                try:
                    pid = self.process.pid
                    subprocess.run(
                        f'taskkill /F /T /PID {pid}',
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    print(f"✓ Завершен процесс BAT с PID: {pid}")
                except:
                    pass
                
                self.process = None
            
            print("✅ Все фоновые процессы успешно завершены")
            
        except Exception as e:
            print(f"Ошибка при завершении процесса: {e}")
    
    def closeEvent(self, event):
        """Обработчик закрытия приложения"""
        print("Закрытие приложения...")
        self.process_check_timer.stop()
        self.kill_all_processes()
        event.accept()

def main():
    if not is_admin():
        run_as_admin()
    
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.setWindowTitle("Aether")
    
    icon_path = "img/aether.ico"
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()