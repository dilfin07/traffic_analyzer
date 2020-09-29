import sys
from os.path import join, dirname, abspath

from qtpy import uic
from qtpy.QtCore import Slot, QThread, Signal, QPropertyAnimation
from qtpy.QtWidgets import QApplication, QMainWindow, QMessageBox, QTreeWidgetItem

import mode.styles
import mode.windows


_UI = join(dirname(abspath(__file__)), 'mainwindow.ui')



class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        uic.loadUi(_UI, self)  # GUI

        self.actionLight.triggered.connect(self.lightTheme)
        self.actionDark.triggered.connect(self.darkTheme)
        self.actionGraphView.triggered.connect(self.GraphView)
        self.pushButton_10.clicked.connect(self.GraphView)
        self.actionTest.triggered.connect(self.main_menu)
        self.actionTest_2.triggered.connect(self.GraphView)
        
    def lightTheme(self):
        mode.styles.light(QApplication.instance())

    def darkTheme(self):
        mode.styles.dark(QApplication.instance())

    def GraphView(self):
        self.stackedWidget.setCurrentWidget(self.page_2)

    def main_menu(self):
        self.stackedWidget.setCurrentWidget(self.page)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    import sys
    from PyQt5.QtWidgets import QApplication
    mode.styles.dark(app)
    mw = mode.windows.ModernWindow(MainWindow())
    mw.show()

    sys.exit(app.exec_())
