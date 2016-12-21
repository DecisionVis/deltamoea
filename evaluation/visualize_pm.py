from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QOpenGLContext
from PyQt5.QtGui import QOpenGLVersionProfile
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtGui import QOpenGLShader
from PyQt5.QtGui import QOpenGLShaderProgram
from PyQt5.QtGui import QVector3D
from PyQt5.QtGui import QMatrix4x4
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QRect
from PyQt5.QtCore import Qt
import sys
import numpy

class HelloTriangle(QOpenGLWidget): #rename to PMHistogram
    def __init__(self, *args, **kwargs):
        super(HelloTriangle, self).__init__(*args, **kwargs)
        self.vp = QOpenGLVersionProfile()
        self.shader_program = QOpenGLShaderProgram(self)

    def initializeGL(self):
        """
        Things that don't work in initializeGL:
            * setAttributeArray
            * not calling link() and bind()
        """
        self.vp.setVersion(2,1)
        vertex_program_text = """
        #version 130
        in vec3 position;

        void main(){
            gl_Position = vec4(position.x, position.y, position.z, 1.0);
        }
        """
        fragment_program_text = """
        #version 130

        void main(){
            gl_FragColor = vec4(0.0, 0.5, 0.0, 0.5);
        }
        """
        self.shader_program.addShaderFromSourceCode(
            QOpenGLShader.Vertex,
            vertex_program_text)
        self.shader_program.addShaderFromSourceCode(
            QOpenGLShader.Fragment,
            fragment_program_text)
        self.shader_program.link() # Necessary
        self.shader_program.bind() # Necessary

    def resizeGL(self, width, height):
        fun = QOpenGLContext.currentContext().versionFunctions(self.vp)
        fun.glClearColor(1.0, 1.0, 1.0, 1.0)
        fun.glClear(fun.GL_COLOR_BUFFER_BIT)

    def paintGL(self):
        painter = QPainter(self)
        painter.fillRect(QRect(0,0,100,100),QBrush(QColor(255,50,50,255)))
        painter.beginNativePainting()
        fun = QOpenGLContext.currentContext().versionFunctions(self.vp)
        fun.glEnable(fun.GL_BLEND)
        fun.glBlendFunc(fun.GL_SRC_ALPHA, fun.GL_ONE_MINUS_SRC_ALPHA)
        self.shader_program.bind()
        vertices = numpy.array((
            (-0.9, 0.9, 0),
            (-0.9, 0.0, 0),
            (-0.8, 0.9, 0),))
        self.shader_program.setAttributeArray(
            'position', vertices)
        self.shader_program.enableAttributeArray('position')
        fun.glDrawArrays(fun.GL_TRIANGLES, 0, 3)
        self.shader_program.disableAttributeArray('position')
        painter.endNativePainting()
        painter.fillRect(QRect(75,75,100,100),QBrush(QColor(50,50,255,128)))
qapp = QApplication(sys.argv)
hello_triangle = HelloTriangle()
hello_triangle.show()
qapp.exec_()
