"""
Application for monitoring internet connection
"""
import sys
import configparser
from time import sleep
from statistics import mean
from datetime import datetime
from threading import Thread

from ping3 import ping as p3p
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QMainWindow,
    QLabel
)


class ConnTester():
    """
    Main application class
    """
    config = configparser.ConfigParser()
    host = "8.8.8.8"
    timeout = 1
    interval = 1
    results = []

    def __init__(self):
        self.config.read('conntester.ini')
        self.host = self.config.get('MAIN', 'host')
        self.timeout = int(self.config.get('MAIN', 'timeout'))
        self.interval = int(self.config.get('MAIN', 'interval'))
        self.history = int(self.config.get('MAIN', 'history'))
        self.app = QApplication(sys.argv)
        self.icon = QIcon("icon.png")
        self.tray = QSystemTrayIcon()
        self.window = MainWindow()
        self.window.setWindowIcon(self.icon)
        self.ping_thread = Thread(target=self.init_timer)
        self.ping_running = False

    def ping(self):
        """
        Pings host and record result
        """
        started = datetime.now()
        delay = p3p(self.host, timeout=self.timeout, unit='ms')
        self.add_result({
            'started': started,
            'time': delay
        })
        info = f"Mean ping {self.get_mean_ping()}\nLast ping {self.get_last_ping()}"
        self.tray.setToolTip(info)
        self.window.set_label(info)

    def add_result(self, res):
        """
        Add result to queue
        """
        if len(self.results) > self.history:
            self.results.pop(0)
        self.results.append(res)

    def get_mean_ping(self):
        """
        Calculate mean ping time in ms
        """
        if len(self.results) == 0:
            return 999
        return mean([r["time"] for r in self.results])

    def get_last_ping(self):
        """
        Get last ping time in ms
        """
        return self.results[-1]["time"]

    def init_interface(self):
        """
        Init tray icon and interface
        """
        self.app.setQuitOnLastWindowClosed(False)
        self.tray.setIcon(self.icon)
        self.tray.setVisible(True)
        self.tray.activated.connect(self.window.toggle)
        menu = QMenu()
        quit_a = QAction("Quit")
        quit_a.triggered.connect(self.app.quit)
        menu.addAction(quit_a)
        self.tray.setContextMenu(menu)
        self.app.aboutToQuit.connect(self.stop)
        sys.exit(self.app.exec_())

    def init_timer(self):
        """
        Ping loop
        """
        self.ping_running = True
        while self.ping_running:
            Thread(target=self.ping).start()
            sleep(self.interval)

    def run(self):
        """
        Entry point
        """
        self.ping_thread.start()
        self.init_interface()

    def stop(self):
        """
        Exit point
        """
        self.ping_running = False


class MainWindow(QMainWindow):
    """
    Main application window
    """

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("ConnTester")
        self.label = QLabel("Ping...")
        self.label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.label)

    def set_label(self, text):
        """
        Update window text
        """
        self.label.setText(text)
        self.label.repaint()

    def toggle(self, reason):
        """
        Toggle window visibility
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick: # pylint: disable=no-member
            self.setVisible(not self.isVisible())
            if self.isVisible():
                self.activateWindow()


if __name__ == '__main__':
    ct = ConnTester()
    ct.run()
