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
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QRect
from PyQt5.QtCore import Qt
import sys
import numpy

class PMHistogram(QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super(PMHistogram, self).__init__(*args, **kwargs)
        self.pixel_width = 100
        self.pixel_height = 100
        # label_height: pixels to reserve for label
        self.label_height = 20.0
        self.vp = QOpenGLVersionProfile()
        self.shader_program = QOpenGLShaderProgram(self)
        self.bins = list()
        self.counts = list()

    def initializeGL(self):
        """
        Things that don't work in initializeGL:
            * setAttributeArray
            * not calling link() and bind()
        """
        self.vp.setVersion(2,1)
        # vertex program scales 0,1 into -1,1
        vertex_program_text = """
        #version 130
        in vec2 position;
        uniform float x_margin;
        uniform float y_margin;

        void main(){
            gl_Position = vec4(
                (2*position.x-1) * (2.0 - x_margin*2.0)/2.0,
                (2*position.y-1) * (2.0 - y_margin*2.0)/2.0,
                0, 1.0);
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
        self.shader_program.link()
        self.shader_program.bind()

    def resizeGL(self, width, height):
        fun = QOpenGLContext.currentContext().versionFunctions(self.vp)
        fun.glClearColor(1.0, 1.0, 1.0, 1.0)
        fun.glClear(fun.GL_COLOR_BUFFER_BIT)
        self.pixel_width = width
        self.pixel_height = height
        # what's ten pixels as a fraction of two?
        self.x_margin = 2 * 10.0 / width
        self.y_margin = 2 * self.label_height / height

    def paintGL(self):
        painter = QPainter(self)
        painter.setPen(QPen(QBrush(QColor(200,200,200)), 2))
        for ii, bin in enumerate(self.bins):
            working_width = self.pixel_width - 20
            pixel_x = int(10 + working_width * ii * 1.0 / (len(self.bins)))
            painter.drawLine(pixel_x, self.pixel_height - self.label_height,
                             pixel_x, self.label_height)
 
        painter.beginNativePainting()
        fun = QOpenGLContext.currentContext().versionFunctions(self.vp)
        fun.glEnable(fun.GL_BLEND)
        fun.glBlendFunc(fun.GL_SRC_ALPHA, fun.GL_ONE_MINUS_SRC_ALPHA)
        self.shader_program.bind()
        vertices = self.vertices()
        #vertices = numpy.array((
        #    (0.1, 0.9),
        #    (0.1, 0.0),
        #    (0.05, 0.9),))
        self.shader_program.setAttributeArray(
            'position', vertices)
        self.shader_program.setUniformValue("x_margin", self.x_margin)
        self.shader_program.setUniformValue("y_margin", self.y_margin)
        self.shader_program.enableAttributeArray('position')
        fun.glDrawArrays(fun.GL_TRIANGLES, 0, vertices.shape[0])
        self.shader_program.disableAttributeArray('position')
        painter.endNativePainting()
        painter.setPen(QPen(QBrush(QColor(80,80,80)), 1))
        step = len(self.bins) // 10
        ii = 0
        while ii < len(self.bins):
            bin = self.bins[ii]
            ii += step
            bintext = "{:.2f}".format(bin)
            # scale 0,1 into widget width minus 20 pixels
            working_width = self.pixel_width - 20
            pixel_x = int(10 + bin * working_width)
            pixel_y = int(self.pixel_height - 8)

            painter.drawText(pixel_x, pixel_y, bintext)

    def vertices(self):
        nbins = len(self.bins)
        maxcount = max(self.counts)
        # scale vertices into 0,1 square
        binwidth = 1.0 / nbins
        unitheight = 1.0 / maxcount
        left = numpy.arange(0,1 - 0.1*binwidth, binwidth)
        right = left + binwidth
        unflattened_xx = numpy.array(
            (left, right, left, right, left, right))
        xx = unflattened_xx.flatten("F")
        bottom = numpy.zeros(nbins)
        top = numpy.array(self.counts) * unitheight
        unflattened_yy = numpy.array(
            (bottom, bottom, top, bottom, top, top))
        yy = unflattened_yy.flatten("F")
        vertices = numpy.array((xx, yy)).T
        return vertices

    def update_counts(self, bins, counts):
        self.bins = bins
        self.counts = counts

qapp = QApplication(sys.argv)
pm_histogram = PMHistogram()
nbins = 200
counts = dict((b,0) for b in range(nbins+1))
from moeadv.operators import pm_inner
operator = pm_inner(0,1,100)
for _ in range(100000):
    x_child = operator(0.025)
    counts[int(numpy.floor(x_child*nbins))] += 1
bins = sorted(list(counts.keys()))
counts = [counts[b] for b in bins]
bins = numpy.array(bins) / (nbins + 1.0)
counts = numpy.array(counts)
pm_histogram.update_counts(bins, counts)
pm_histogram.show()
qapp.exec_()
