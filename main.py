import sys
import traceback
from datetime import timedelta, datetime
from random import randint
import time
import pandas as pd

import plotly
import plotly.offline as po
import plotly.graph_objs as go
import plotly.express as px

import cx_Oracle
from PyQt5 import QtWidgets
from PyQt5.QtCore import QPropertyAnimation, QPoint, QThread, QRunnable, QObject, pyqtSignal, QThreadPool, pyqtSlot, \
    QTimer, QBasicTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QTableWidgetItem, QProgressBar
from numpy.distutils.fcompiler import pg
from pandas import np
from qtpy import QtCore
import mode.styles
import mode.windows
import gui_main  # Это наш конвертированный файл дизайна
import setting

cx_Oracle.init_oracle_client(lib_dir="/Users/vladimirsizonenko/Downloads/instantclient_19_3-2")

one_day = datetime.now() - timedelta(days=1)
now = datetime.now()

conn = cx_Oracle.connect(setting.connet)
cursor = conn.cursor()
cursor.execute(setting.client)
client = cursor.fetchall()
cursor.execute(setting.vendor)
vendor = cursor.fetchall()
cursor.close()
conn.close()


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class MainWindow(QtWidgets.QMainWindow, gui_main.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # Animation
        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(800)
        self.doShow()
        # ProgressBar
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(False)
        # Buttons
        self.to_page_action.clicked.connect(self.action)
        self.to_page_setting.clicked.connect(self.setting)
        self.to_page_home.clicked.connect(self.home)
        self.to_page_graph.clicked.connect(self.Graph)
        self.setTable.clicked.connect(self.set_to_table)
        self.setGraph.clicked.connect(self.set_to_graph)
        self.export_to_xls_.clicked.connect(self.resetBar)
        # SET
        self.from_data.setDateTime(one_day)
        self.to_date.setDateTime(now)
        self.MCCMNC.setText("*")
        self.ANI.setText("*")
        self.Client.addItem(None)
        self.Vendor.addItem(None)
        # Combo_box
        for i in client:
            self.Client.addItem(i[1])
        for s in vendor:
            self.Vendor.addItem(s[1])

        self.threadpool = QThreadPool()


    def set_to_table(self):
        worker = Worker(self.UserData)
        worker.signals.result.connect(self.run_to_table)
        #worker.signals.finished.connect(self.thread_complete)
        #worker.signals.progress.connect(self.progress_fn)
        self.threadpool.start(worker)

    def set_to_graph(self):
        worker = Worker(self.UserData)
        self.doAction()
        worker.signals.result.connect(self.WebGraph)
        worker.signals.finished.connect(self.resetBar)
        self.threadpool.start(worker)

    def flow(self):
        print('Start')
        worker = Worker(self.UserData)
        self.threadpool.start(worker)

    def doAction(self):
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(0)
        self.progressBar.setMinimum(0)
        if self.progressBar.minimum() != self.progressBar.maximum():
            self.timer = QTimer(self, timeout=self.onTimeout)
            self.timer.start(randint(1, 3) * 1000)

    def resetBar(self):
        self.step = 0
        self.progressBar.setValue(0)
        self.timer.stop()

    def onTimeout(self):
        if self.progressBar.value() >= 100:
            self.timer.stop()
            self.timer.deleteLater()
            del self.timer
            return
        self.progressBar.setValue(self.progressBar.value() + 1)

    def UserData(self):
        fr = self.from_data.dateTime()
        star = fr.toPyDateTime()
        to = self.to_date.dateTime()
        en = to.toPyDateTime()
        mnc = self.MCCMNC.text()
        ani = self.ANI.text()
        cli = self.Client.currentText()
        vnd = self.Vendor.currentText()
        conn = cx_Oracle.connect(setting.connet)
        cursor = conn.cursor()
        cursor.execute(setting.url, src=cli, dst=vnd, st=star, en=en, mnc=mnc, ani=ani)
        result = cursor.fetchall()
        attempts = []
        for row in result:
            attempts.append(row)
        cursor.close()
        conn.close()
        print('OK')
        # print(attempts)
        return attempts

    def WebGraph(self, s):
        self.stackedWidget.setCurrentWidget(self.page_chart)
        attempts = s
        labels = ['Date', 'attempts', 'ok']
        df = pd.DataFrame.from_records(attempts, columns=labels)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Date'], y=df['attempts'], name='Attempts'))
        fig.add_trace(go.Scatter(x=df['Date'], y=df['ok'], name='Delivrd OK'))
        fig.update_layout(legend_orientation="h", template="plotly_dark",
                          legend=dict(x=.5, xanchor="center"),
                          hovermode="x",
                          margin=dict(l=0, r=0, t=0, b=0))

        fig.update_traces(hoverinfo="all", hovertemplate=" %{x}<br>%{y}")
        raw_html = '<html><head><meta charset="utf-8" />'
        raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        raw_html += '<body>'
        raw_html += plotly.offline.plot(fig, include_plotlyjs=False, output_type='div',
                                        config=dict(displayModeBar=False))
        raw_html += '</body></html>'

        self.webGraph.setHtml(raw_html)

    def run_to_table(self, s):
        attempts = s
        self.TABLE.setRowCount(len(attempts))
        self.TABLE.setColumnCount(len(attempts[0]))
        for row_num, row in enumerate(attempts):
            for cell_num, cell_attem in enumerate(row):
                self.TABLE.setItem(row_num, cell_num, QTableWidgetItem(str(cell_attem)))

    def Graph(self):
        self.stackedWidget.setCurrentWidget(self.page_chart)

    def setting(self):
        self.stackedWidget.setCurrentWidget(self.page_setting)

    def action(self):
        self.stackedWidget.setCurrentWidget(self.page_action)

    def home(self):
        self.stackedWidget.setCurrentWidget(self.page_home)

    def doShow(self):
        try:
            self.animation.finished.disconnect(self.close)
        except:
            pass
        self.animation.stop()
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

        self.show()


def main():
    app = QtWidgets.QApplication(sys.argv)
    mode.styles.dark(app)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
