from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt
from moeadv.operators import pm_inner

class PMHistogram(QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super(PMHistogram, self).__init__(*args, **kwargs)
        self.operator = pm_inner(0, 1, 15)
    def paintGL(self):
        pass

import sys
qapp = QApplication(sys.argv)
widget = PMHistogram()
widget.show()
qapp.exec_()
