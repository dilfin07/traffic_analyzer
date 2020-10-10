import sys
from datetime import datetime, timedelta
from os.path import join, dirname, abspath

from PyQt5 import QtCore
import cx_Oracle
from PyQt5.QtCore import Qt, QPropertyAnimation
from qtpy import uic
from qtpy.QtWidgets import QApplication, QMainWindow
import setting
import sourc, fil
import mode.styles
import mode.windows

cx_Oracle.init_oracle_client(lib_dir="/Users/vladimirsizonenko/Downloads/instantclient_19_3-2")

_UI = join(dirname(abspath(__file__)), 'login_main.ui')
UI = join(dirname(abspath(__file__)), 'gui.ui')

one_day = datetime.now() - timedelta(days=1)
now = datetime.now()

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi(UI, self)  # GUI
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.show()
        # Button
        self.Button_action.clicked.connect(self.action)
        #self.Button_setting.clicked.connect(self.setting)
        self.Button_Graph_2.clicked.connect(self.Graph)
        #self.Button_run.clicked.connect(self.run)
        self.Button_Graph.clicked.connect(self.GraphVie)
        #SET
        self.date_from.setDateTime(one_day)
        self.date_to.setDateTime(now)
        self.mccmnc.setText("*")
        self.ani.setText("*")

    def GraphVie(self):
        fr = self.date_from.dateTime()
        star = fr.toPyDateTime()
        to = self.date_to.dateTime()
        en = to.toPyDateTime()
        mnc = self.mccmnc.text()
        ani = self.ani.text()
        attempts = []
        conn = cx_Oracle.connect(setting.connet)
        cursor = conn.cursor()
        cursor.execute(setting.url, st=star, en=en, mnc=mnc, ani=ani)
        result = cursor.fetchall()
        for row in result:
            attempts.append(row[1])
        cursor.close()
        conn.close()
        print(attempts)
        self.graphicsView.plot(attempts)

    def Graph(self):
        self.stackedWidget.setCurrentWidget(self.page_2)

    def action(self):
        self.stackedWidget.setCurrentWidget(self.page)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mode.styles.dark(app)
    mw = mode.windows.ModernWindow(MainWindow())
    mw.show()

    sys.exit(app.exec_())
