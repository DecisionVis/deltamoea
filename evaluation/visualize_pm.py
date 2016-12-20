from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QOpenGLContext
from PyQt5.QtGui import QOpenGLVersionProfile
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtGui import QOpenGLShader
from PyQt5.QtGui import QOpenGLShaderProgram
from PyQt5.QtGui import QVector3D
from PyQt5.QtGui import QMatrix4x4
import sys

class HelloTriangle(QOpenGLWidget): #rename to PMHistogram
    def __init__(self, *args, **kwargs):
        super(HelloTriangle, self).__init__(*args, **kwargs)
        self.vp = QOpenGLVersionProfile()
        # create the shader program here
    def initializeGL(self):
        self.vp.setVersion(2,1)
        # rename to vertex_program_text
        shader_program_text = """
        #version 130
        in vec3 position;

        void main(){
            gl_Position = vec4(position, 1.0);
        }
        """
        # rename to fragment_program_text
        fragment_shader_text = """
        #version 130

        void main(){
            gl_FragColor = vec4(1.0, 1.0, 0.0, 1.0);
        }
        """
        self.shader_program = QOpenGLShaderProgram(self)
        self.shader_program.create() # try to remove?
        self.shader_program.bind() # try to remove?
        self.shader_program.addShaderFromSourceCode(
            QOpenGLShader.Vertex,
            shader_program_text)
        self.shader_program.addShaderFromSourceCode(
            QOpenGLShader.Fragment,
            fragment_shader_text)
        self.shader_program.link()
        self.shader_program.bind() # try to remove?
        vertices = [ # replace with ndarray
            QVector3D(-0.5, 0, 0),
            QVector3D( 0.5, 0, 0),
            QVector3D( 0.0, 0.5* 2**0.5, 0),]
        self.shader_program.setAttributeArray(
            'position', vertices)
    def resizeGL(self, width, height):
        fun = QOpenGLContext.currentContext().versionFunctions(self.vp)
        fun.glClearColor(0.2, 0.3, 0.3, 1.0) # choose a less ugly color
        fun.glClear(fun.GL_COLOR_BUFFER_BIT)
    def paintGL(self):
        fun = QOpenGLContext.currentContext().versionFunctions(self.vp)
        fun.glClearColor(0.2, 0.3, 0.3, 1.0) # choose a less ugly color
        fun.glClear(fun.GL_COLOR_BUFFER_BIT)
        self.shader_program.enableAttributeArray('position')
        fun.glDrawArrays(fun.GL_TRIANGLES, 0, 3)
        self.shader_program.disableAttributeArray('position')
qapp = QApplication(sys.argv)
hello_triangle = HelloTriangle()
hello_triangle.show()
qapp.exec_()
