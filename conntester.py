"""
Application for monitoring internet connection
"""
import sys
import os
import configparser
from time import sleep
from statistics import mean
from datetime import datetime
from threading import Thread

from ping3 import ping as p3p
from PyQt5.QtGui import QIcon, QPainter
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QMainWindow,
    QDesktopWidget
)
from PyQt5.QtChart import QChart, QLineSeries, QDateTimeAxis, QValueAxis

from mainwindow import Ui_MainWindow


def resource_path(relative_path):
    """
    Loads resourse from app path on prod on source path on dev
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)  # pylint: disable=no-member,protected-access
    return os.path.join(os.path.abspath("."), relative_path)

def resource_image(image):
    """
    Loads resourse image
    """
    return resource_path(os.path.join("images", image))

class ConnTester():
    """
    Main application class
    """
    config = configparser.ConfigParser()
    host = "8.8.8.8"
    timeout = 1
    interval = 1
    results = []
    STATUS = {
        'GOOD': 0,
        'BAD': 1,
        'LOST': 2,
    }
    STATUS_QICONS = {}

    def __init__(self):
        self.config.read('conntester.ini')
        self.host = self.config.get('MAIN', 'host')
        self.timeout = int(self.config.get('MAIN', 'timeout'))
        self.interval = int(self.config.get('MAIN', 'interval'))
        self.history = int(self.config.get('MAIN', 'history'))
        self.ping_tresh = int(self.config.get('MAIN', 'ping_tresh'))
        self.loss_tresh = int(self.config.get('MAIN', 'loss_tresh'))
        self.app = QApplication(sys.argv)
        self.icon = QIcon(resource_image("icon.png"))
        self.window = MainWindow(self.host)
        self.tray = QSystemTrayIcon(parent=self.window)
        self.window.setWindowIcon(self.icon)
        self.ping_thread = Thread(target=self.init_timer)
        self.ping_running = False
        self.load_status_icons()
        self.current_status = 0
        self.current_tray_icon = 0

    def load_status_icons(self):
        """
        Loads icons from resourses
        """
        for (name, code) in self.STATUS.items():
            self.STATUS_QICONS[code] = QIcon(resource_image(name.lower()))

    def ping(self):
        """
        Pings host and record result
        """
        started = datetime.now()
        delay = p3p(self.host, timeout=self.timeout, unit='ms')
        res = {
            'started': started,
            'time': delay
        }
        self.add_result(res)
        self.window.add_series(res)
        self.process_results()

    def process_results(self):
        """
        Update state based on results
        """
        info = "\n".join([
            f"Mean {self.get_mean_ping()} ms",
            f"Last {self.get_last_ping()} ms",
            f"Loss {self.get_loss_ping()} %",
        ])
        self.tray.setToolTip(info)
        self.get_overall_status()
        self.update_tray_icon()
        self.window.set_labels(
            self.get_mean_ping(),
            self.get_last_ping(),
            self.get_loss_ping(),
        )

    def update_tray_icon(self):
        """
        Change icon on status change
        """
        if self.current_status != self.current_tray_icon:
            self.tray.setIcon(self.STATUS_QICONS[self.current_status])
            self.current_tray_icon = self.current_status

    def add_result(self, res):
        """
        Add result to queue
        """
        if len(self.results) > self.history:
            self.results.pop(0)
        self.results.append(res)

    def get_responses(self):
        """
        Filter pings without response
        """
        return list(filter(lambda r: r["time"] is not None, self.results))

    def get_mean_ping(self):
        """
        Calculate mean ping time in ms
        """
        responses = self.get_responses()
        if len(responses) == 0:
            return None
        m_ping = mean([r["time"] for r in responses])
        return int(round(m_ping, 0))

    def get_last_ping(self):
        """
        Get last ping time in ms
        """
        responses = self.get_responses()
        if len(responses) == 0:
            return None
        l_ping = responses[-1]["time"]
        return int(round(l_ping, 0))

    def get_loss_ping(self):
        """
        Get lost ping percent
        """
        if len(self.results) == 0:
            return 0
        loss = sum(r["time"] is None for r in self.results) / len(self.results) * 100
        return int(round(loss, 0))

    def get_ping_status(self):
        """
        Ping status
        """
        mean_ping = self.get_mean_ping()
        if mean_ping is None:
            return self.STATUS['LOST']
        if  mean_ping > self.ping_tresh:
            return self.STATUS['BAD']
        return self.STATUS['GOOD']

    def get_loss_status(self):
        """
        Loss status
        """
        loss = self.get_loss_ping()
        if loss is None:
            return self.STATUS['LOST']
        if  loss > self.loss_tresh:
            return self.STATUS['BAD']
        return self.STATUS['GOOD']

    def get_overall_status(self):
        """
        Overall status
        """
        self.current_status = max([
            self.get_loss_status(),
            self.get_ping_status(),
        ])
        return self.current_status

    def init_interface(self):
        """
        Init tray icon and interface
        """
        self.app.setQuitOnLastWindowClosed(False)
        self.tray.setIcon(self.STATUS_QICONS[0])
        self.tray.show()
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


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Main application window
    """
    WIDTH = 150
    HEIGHT = 50
    MARGIN = 5
    def __init__(self, host, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.host = host
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.position_to_dock()
        self.series = QLineSeries()
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle(f"Connection to {self.host}")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        axisX = QDateTimeAxis()
        axisX.setTickCount(4)
        axisX.setFormat("HH:mm:ss")
        axisX.setTitleText("Time")
        axisX.setRange(QDateTime.currentDateTime().addSecs(-120), QDateTime.currentDateTime())
        self.chart.setAxisX(axisX, self.series)
        # self.series.attachAxis(axisX)
        axisY = QValueAxis()
        axisY.setLabelFormat("%i")
        axisY.setTitleText("Delay")
        self.chart.addAxis(axisY, Qt.AlignLeft)
        self.chart.setAxisY(axisY, self.series)
        # self.series.attachAxis(axisY)
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self.chartWidget.setChart(self.chart)
        self.chartWidget.setRenderHint(QPainter.Antialiasing)

    def add_series(self, data):
        """
        Append series data
        """
        # FIXME!!!1111
        self.series.append(QDateTime.currentDateTime().toMSecsSinceEpoch(), data["time"])
        self.chart.scroll(10, 0)
        self.chart.axisX().setRange(QDateTime.currentDateTime().addSecs(-120), QDateTime.currentDateTime())

    def set_series(self, data):
        """
        Replace series data
        """
        self.series.clear()
        for d_point in data.items():
            self.series.append(d_point["started"].timestamp * 1000, d_point["time"])

    def position_to_dock(self):
        """
        Adjust main window position according to it's size and desktop
        """
        desktop_geometry = QDesktopWidget().availableGeometry()
        self.setGeometry(
            desktop_geometry.width() - self.width() - self.MARGIN,
            desktop_geometry.height() - self.height() - self.MARGIN,
            self.width(),
            self.height()
        )

    def set_labels(self, mean_=None, curr=None, loss=None):
        """
        Update window text
        """
        mean_text = curr_text = loss_text = "No connection"
        if mean_ is not None:
            mean_text = f"Mean ping: {mean_}ms"
        if curr is not None:
            curr_text = f"Last ping: {curr}ms"
        if loss is not None:
            loss_text = f"Ping loss: {loss}%"
        self.meanLabel.setText(mean_text)
        self.currLabel.setText(curr_text)
        self.lossLabel.setText(loss_text)

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
