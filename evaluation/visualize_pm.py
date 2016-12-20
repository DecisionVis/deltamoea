from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QOpenGLVersionProfile
from PyQt5.QtGui import QOpenGLShader
from PyQt5.QtGui import QOpenGLShaderProgram
from PyQt5.QtGui import QOpenGLContext
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtCore import Qt
import numpy
from moeadv.operators import pm_inner

class PMHistogram(QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super(PMHistogram, self).__init__(*args, **kwargs)
        self.operator = pm_inner(0, 1, 15)
        self.vp = QOpenGLVersionProfile()
        self.shader_program = QOpenGLShaderProgram(self)

    def initializeGL(self):
        print("initializeGL")
        self.vp.setVersion(2,1)
        self.vp.setProfile(QSurfaceFormat.CoreProfile)
        vertex_program_text = """
        #version 130
        in vec3 position;

        void main(){gl_Position = vec4(position, 1.0);}
        """
        fragment_program_text = """
        #version 130
        out vec4 color;

        void main(){
            color = vec4(1.0, 0.2, 0.8, 1.0);
        }
        """
        self.shader_program.create()
        self.shader_program.bind()
        self.shader_program.addShaderFromSourceCode(
            QOpenGLShader.Vertex,
            vertex_program_text)
        self.shader_program.addShaderFromSourceCode(
            QOpenGLShader.Fragment,
            fragment_program_text)
        self.shader_program.link()

    def resizeGL(self, width, height):
        fun = QOpenGLContext.currentContext().versionFunctions(self.vp)
        fun.glViewport(0, 0, width, height)
        fun.glClear(fun.GL_COLOR_BUFFER_BIT)

    def paintGL(self):
        print("paintgl called")
        vertices = numpy.array((
                (-0.5, 0, 0),
                ( 0.5, 0, 0),
                ( 0, 0.5 * 2**0.5, 0)))
        self.shader_program.setAttributeArray(
            "position", vertices)
        print(vertices)
        print("loaded vertices")
        #painter = QPainter(self)
        #painter.beginNativePainting()
        fun = QOpenGLContext.currentContext().versionFunctions(self.vp)
        fun.glClearColor(0.2, 0.3, 0.3, 1.0)
        fun.glClear(fun.GL_COLOR_BUFFER_BIT)
        self.shader_program.enableAttributeArray('position')
        fun.glDrawArrays(fun.GL_TRIANGLES, 0, 3)
        self.shader_program.disableAttributeArray('position')
        #painter.endNativePainting()

import sys
qapp = QApplication(sys.argv)
widget = PMHistogram()
print("created widget")
widget.show()
print("showed widget")
widget.repaint()
qapp.exec_()
