import sys
import subprocess
import os
import time
import ctypes
import webbrowser
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon
from design import CustomWindow

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

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
        self.main_switch.toggled.connect(self.on_main_switch_toggled)
        self.github_button.clicked.connect(self.open_github)
        self.telegram_button.clicked.connect(self.open_telegram)
    
    def open_github(self):
        import webbrowser
        webbrowser.open("https://github.com/redjex")
    
    def open_telegram(self):
        import webbrowser
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
    
    def on_main_switch_toggled(self, checked):
        if checked:
            print("Переключатель включен, запускаю последовательность...")
            
            self.kill_discord_processes()
            
            bat_path = os.path.abspath("general/general (ALT).bat")
            
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
                    QMessageBox.critical(self, "Ошибка", f"Не удалось запустить файл:\n{e}")
            else:
                print(f"Файл не найден: {bat_path}")
                QMessageBox.warning(self, "Предупреждение", f"Файл не найден:\n{bat_path}")
        else:
            print("Главный переключатель: ВЫКЛЮЧЕН (OFF)")
            self.kill_process()
    
    def kill_process(self):
        try:
            print("Завершаю все процессы winws.exe...")
            
            result = subprocess.run(
                'taskkill /F /IM winws.exe',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                text=True
            )
            
            if result.returncode == 0:
                print("Все процессы winws.exe успешно завершены")
            else:
                print("Процессы winws.exe не найдены или уже завершены")
            
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
                    print(f"Завершен процесс BAT с PID: {pid}")
                except:
                    pass
                
                self.process = None
            
        except Exception as e:
            print(f"Ошибка при завершении процесса: {e}")

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