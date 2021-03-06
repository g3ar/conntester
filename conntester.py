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
from PyQt5.QtCore import Qt, QDateTime, QMargins
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QMainWindow,
    QDesktopWidget
)
from PyQt5.QtChart import QChart, QLineSeries, QDateTimeAxis, QValueAxis
import simpleaudio as sa

from mainwindow import Ui_MainWindow


def resource_path(relative_path):
    """
    Loads resourse from app path on prod on source path on dev
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)  # pylint: disable=no-member,protected-access
    return os.path.join(os.path.abspath("."), relative_path)

def resource_image(name):
    """
    Loads resourse image
    """
    return resource_path(os.path.join("images", name))

def resource_sound(name):
    """
    Loads resourse sound
    """
    return resource_path(os.path.join("sounds", name))

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
    STATUS_SOUNDS = {}

    def __init__(self):
        self.config.read('conntester.ini')
        self.host = self.config.get('MAIN', 'host')
        self.timeout = int(self.config.get('MAIN', 'timeout'))
        self.interval = int(self.config.get('MAIN', 'interval'))
        self.history = int(self.config.get('MAIN', 'history'))
        self.history_size = int(self.history / self.interval)
        self.ping_tresh = int(self.config.get('MAIN', 'ping_tresh'))
        self.loss_tresh = int(self.config.get('MAIN', 'loss_tresh'))
        self.loss_tresh_lost = int(self.config.get('MAIN', 'loss_tresh_lost'))
        self.sound_enable = int(self.config.get('MAIN', 'sound_enable'))
        self.app = QApplication(sys.argv)
        self.icon = QIcon(resource_image("icon.png"))
        self.window = MainWindow(self.host, self.history, self.history_size)
        self.tray = QSystemTrayIcon(parent=self.window)
        self.window.setWindowIcon(self.icon)
        self.ping_thread = Thread(target=self.init_timer)
        self.ping_running = False
        self.load_status_icons()
        self.load_status_sounds()
        self.current_status = 0
        self.current_tray_icon = 0

    def load_status_icons(self):
        """
        Loads icons from resourses
        """
        for (name, code) in self.STATUS.items():
            self.STATUS_QICONS[code] = QIcon(resource_image(name.lower()))
    
    def load_status_sounds(self):
        """
        Loads sound locations
        """
        for (name, code) in self.STATUS.items():
            self.STATUS_SOUNDS[code] = resource_sound(f"{name.lower()}.wav")

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
        self.window.set_labels(
            self.get_mean_ping(),
            self.get_last_ping(),
            self.get_loss_ping(),
        )
        self.window.add_series(
            self.get_last_ping(),
            self.get_loss_ping()
        )

    def update_tray_icon(self, status):
        """
        Change tray icon
        """
        self.tray.setIcon(self.STATUS_QICONS[status])

    def add_result(self, res):
        """
        Add result to queue
        """
        if len(self.results) > self.history_size:
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
        if loss > self.loss_tresh_lost:
            return self.STATUS['LOST']
        if  loss > self.loss_tresh:
            return self.STATUS['BAD']
        return self.STATUS['GOOD']

    def get_overall_status(self):
        """
        Overall status
        """
        new_status = max([
            self.get_loss_status(),
            self.get_ping_status(),
        ])
        if self.current_status != new_status:
            self.process_status_change(self.current_status, new_status)
            self.current_status = new_status
        return self.current_status
    
    def process_status_change(self, old_status, new_status):
        """
        Actions on status change
        """
        self.play_sound(new_status)
        self.update_tray_icon(new_status)
    
    def play_sound(self, status):
        """
        Play sound
        """
        def _play(snd):
            wave = sa.WaveObject.from_wave_file(resource_sound(snd))
            play_obj = wave.play()
            play_obj.wait_done()
        name = self.STATUS_SOUNDS[status]
        Thread(target=_play, args=(name,)).start()

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
    max_ping = 0
    max_loss = 0
    def __init__(self, host, history, history_size, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.host = host
        self.history = history
        self.history_size = history_size
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.position_to_dock()
        self.series_delay = QLineSeries()
        self.series_loss = QLineSeries()
        self.axis_X = QDateTimeAxis() # pylint: disable=invalid-name
        self.axis_X.setTickCount(3)
        self.axis_X.setFormat("HH:mm")
        self.axis_X.setTitleText("Time")
        self.chart = QChart()
        self.chart.addSeries(self.series_delay)
        self.chart.addSeries(self.series_loss)
        self.chart.setTitle(f"Connection to {self.host}")
        self.init_series(self.series_delay, "Delay ms")
        self.init_series(self.series_loss, "Loss %")
        self.chart.legend().setVisible(False)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self.chart.layout().setContentsMargins(0, 0, 0, 0)
        self.chart.setBackgroundRoundness(0)
        self.chart.setMargins(QMargins(0,0,0,0))
        self.chartWidget.setChart(self.chart)
        self.chartWidget.setRenderHint(QPainter.Antialiasing)

    def init_series(self, series, label):
        """
        Series settings
        """
        self.chart.setAxisX(self.axis_X, series)
        axis_Y = QValueAxis() # pylint: disable=invalid-name
        axis_Y.setLabelFormat("%i")
        axis_Y.setTitleText(label)
        axis_Y.setRange(0, 100)
        self.chart.addAxis(axis_Y, Qt.AlignLeft)
        self.chart.setAxisY(axis_Y, series)

    def add_series(self, ping, loss):
        """
        Append series data
        """
        self.max_ping = max(ping or 0, self.max_ping)
        self.max_loss = max(loss, self.max_loss)
        if self.series_delay.count() > self.history_size:
            self.series_delay.remove(0)
        self.series_delay.append(QDateTime.currentDateTime().toMSecsSinceEpoch(), ping or 0)
        if self.series_loss.count() > self.history_size:
            self.series_loss.remove(0)
        self.series_loss.append(QDateTime.currentDateTime().toMSecsSinceEpoch(), loss)
        self.axis_X.setRange(
            QDateTime.currentDateTime().addSecs(-self.history),
            QDateTime.currentDateTime()
        )
        self.chart.axisY().setRange(0, self.max_ping + self.MARGIN)

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
