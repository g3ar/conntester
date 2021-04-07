import configparser
import queue
from statistics import mean
from datetime import datetime
from time import sleep

from ping3 import ping as p3p
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ConnTester():
    config = configparser.ConfigParser()
    host = "8.8.8.8"
    timeout = 1
    interval = 1
    results = queue.Queue(60)
    app = QApplication([])
    icon = QIcon("icon.png")
    tray = QSystemTrayIcon()

    def __init__(self):
        self.config.read('conntester.ini')
        self.host = self.config.get('MAIN', 'host')
        self.timeout = int(self.config.get('MAIN', 'timeout'))
        self.interval = int(self.config.get('MAIN', 'interval'))
    
    def ping(self, host):
        """
        Pings specified host and returns ping time in ms
        """
        return p3p(host, timeout=self.timeout, unit='ms')
    
    def add_result(self, r):
        """
        Add result to queue
        """
        if self.results.full():
            self.results.get()
        self.results.put(r)
    
    def get_mean_ping(self):
        """
        Calculate mean ping time in ms
        """
        if self.results.empty():
            return 999
        return mean([r["time"] for r in list(self.results.queue)])
    
    def get_last_ping(self):
        """
        Get last ping time in ms
        """
        return list(self.results.queue)[-1]["time"]
    
    def init_interface(self):
        """
        Init tray icon and interface
        """
        self.app.setQuitOnLastWindowClosed(False)
        self.tray.setIcon(self.icon)
        self.tray.setVisible(True)
        menu = QMenu()
        quit = QAction("Quit")
        quit.triggered.connect(self.app.quit)
        menu.addAction(quit)
        self.tray.setContextMenu(menu)

    def run(self):
        """
        Entrypoint
        """
        self.app.exec_()
        # while True:
        #     started = datetime.now()
        #     time = self.ping(self.host)
        #     self.add_result({
        #         'started': started,
        #         'time': time
        #     })
        #     self.tray.setToolTip(f"Mean ping {self.get_mean_ping()}")
        #     sleep(self.interval)

if __name__ == '__main__':
    ct = ConnTester()
    ct.run()
