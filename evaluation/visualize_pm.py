from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSlider
from PyQt5.QtWidgets import QSplitter
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
import weakref
from moeadv.operators import pm_inner

def _return_none():
    return None

class PMHistogramState(object):
    def __init__(self, di, x_parent, samples, nbins):
        self.di = di
        self.x_parent = x_parent
        self.samples = samples
        self.nbins = nbins
        self._data = _return_none
        self._counts = _return_none
        self._bins = _return_none

    def _sample(self):
        operator = pm_inner(0.0, 1.0, self.di)
        vf = numpy.vectorize(operator)
        starting_data = numpy.ones(self.samples, dtype='f') * self.x_parent
        samples = vf(starting_data)
        return samples

    def counts(self):
        """
        Return (counts, bin_edges) where counts.shape[0] is nbins and
        bin_edges.shape[0] is nbins+1.
        """
        counts = self._counts()
        bins = self._bins()
        if counts is None or bins is None:
            data = self._data()
            if data is None:
                data = self._sample()
                self._data = weakref.ref(data)
            counts, bins = numpy.histogram(data, bins=self.nbins, range=(0.0,1.0))
            self._counts = weakref.ref(counts)
            self._bins = weakref.ref(bins)
        return counts, bins

    def update_di(self, di):
        """
        return a new state with the new DI
        """
        if di == self.di:
            return self
        new_state = PMHistogramState(di, self.x_parent, self.samples, self.nbins)
        return new_state

    def update_x_parent(self, x_parent):
        """
        return a new state with the new parent X
        """
        if x_parent == self.x_parent:
            return self
        new_state = PMHistogramState(self.di, x_parent, self.samples, self.nbins)
        return new_state

    def update_samples(self, samples):
        """ return a new state with the new number of samples """
        if samples == self.samples:
            return self
        new_state = PMHistogramState(self.di, self.x_parent, samples, self.nbins)
        return new_state

    def update_nbins(self, nbins):
        """ return a new state with the new number of bins """
        if nbins == self.nbins:
            return self
        new_state = PMHistogramState(self.di, self.x_parent, self.samples, nbins)
        new_state._data = self._data # means we don't have to resample!
        return new_state


class PMHistogramWidget(QOpenGLWidget):
    def __init__(self, initial_state, *args, **kwargs):
        super(PMHistogramWidget, self).__init__(*args, **kwargs)
        self.pixel_width = 100
        self.pixel_height = 100
        # label_height: pixels to reserve for label
        self.label_height = 20.0
        self.vp = QOpenGLVersionProfile()
        self.shader_program = QOpenGLShaderProgram(self)
        self.state = initial_state

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
        painter.beginNativePainting()
        fun = QOpenGLContext.currentContext().versionFunctions(self.vp)
        fun.glClearColor(1.0, 1.0, 1.0, 1.0)
        fun.glClear(fun.GL_COLOR_BUFFER_BIT)
        painter.endNativePainting()
        painter.setPen(QPen(QBrush(QColor(200,200,200)), 2))
        _, bin_edges = self.state.counts()
        # here let's assume bin_edges is from 0-1
        working_width = self.pixel_width - 20
        for bin_edge in bin_edges:
            pixel_x = int(10 + working_width * bin_edge)
            painter.drawLine(pixel_x, self.pixel_height - self.label_height,
                             pixel_x, self.label_height)
 
        painter.beginNativePainting()
        fun = QOpenGLContext.currentContext().versionFunctions(self.vp)
        fun.glEnable(fun.GL_BLEND)
        fun.glBlendFunc(fun.GL_SRC_ALPHA, fun.GL_ONE_MINUS_SRC_ALPHA)
        self.shader_program.bind()
        vertices = self.vertices()
        self.shader_program.setAttributeArray(
            'position', vertices)
        self.shader_program.setUniformValue("x_margin", self.x_margin)
        self.shader_program.setUniformValue("y_margin", self.y_margin)
        self.shader_program.enableAttributeArray('position')
        fun.glDrawArrays(fun.GL_TRIANGLES, 0, vertices.shape[0])
        self.shader_program.disableAttributeArray('position')
        painter.endNativePainting()
        painter.setPen(QPen(QBrush(QColor(80,80,80)), 1))
        limit = bin_edges.shape[0]
        step = limit // 10
        ii = 0
        while ii < limit:
            bin_edge = bin_edges[ii]
            ii += step
            text = "{:.2f}".format(bin_edge)
            working_width = self.pixel_width - 20
            pixel_x = int(10 + bin_edge * working_width)
            pixel_y = int(self.pixel_height - 8)
            painter.drawText(pixel_x, pixel_y, text)

    def vertices(self):
        counts, bin_edges = self.state.counts()
        maxcount = counts.max()
        nbins = counts.shape[0]
        # scale vertices into 0,1 square
        binscale = 1.0 / (bin_edges.max() - bin_edges.min())
        unitheight = 1.0 / maxcount
        left = bin_edges[:-1] * binscale
        right = bin_edges[1:] * binscale
        unflattened_xx = numpy.array(
            (left, right, left, right, left, right))
        xx = unflattened_xx.flatten("F")
        bottom = numpy.zeros(nbins)
        top = numpy.array(counts) * unitheight
        unflattened_yy = numpy.array(
            (bottom, bottom, top, bottom, top, top))
        yy = unflattened_yy.flatten("F")
        vertices = numpy.array((xx, yy)).T
        return vertices

    def set_state(self, state):
        self.state = state
        self.update()

class OperatorInspectionFrame(QFrame):
    def __init__(self, *args, **kwargs):
        super(OperatorInspectionFrame, self).__init__(*args, **kwargs)
        # prepare state
        initial_state = PMHistogramState(15, 0.5, 100000, 100)
        self.states = [initial_state]
        self.state_index = 0
        self.last_state_index = -1

        # prepare layout and sliders
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(self)
        main_layout.addWidget(splitter)
        control_panel = QFrame(self)
        splitter.addWidget(control_panel)
        self.plot = PMHistogramWidget(initial_state, self)
        splitter.addWidget(self.plot)
        splitter.setStretchFactor(0,1)
        splitter.setStretchFactor(1,4)

        # assemble control panel
        cp_layout = QVBoxLayout(control_panel)
        self.bins_label = QLabel(control_panel)
        cp_layout.addWidget(self.bins_label)
        self.bins_slider = QSlider(Qt.Horizontal, control_panel)
        cp_layout.addWidget(self.bins_slider)
        cp_layout.addStretch()
        self.bins_slider.setMinimum(0)
        self.bins_slider.setMaximum(100)
        self.bins_label.setText("{} bins".format(initial_state.nbins))
        self.bins_slider.setValue(
            self._nbins_to_bin_slider(initial_state.nbins))
        self.bins_slider.valueChanged.connect(self._nbins_changed)

        # set up heartbeat
        # connect heartbeat to updating plot state

    def _bin_slider_to_nbins(self, bin_slider_position):
        nbins = bin_slider_position ** 2
        return nbins

    def _nbins_to_bin_slider(self, nbins):
        bin_slider_position = int(nbins ** 0.5)
        return bin_slider_position

    def _nbins_changed(self, bin_slider_position):
        nbins = self._bin_slider_to_nbins(bin_slider_position)
        new_state = self.states[self.state_index].update_nbins(nbins)
        self.bins_label.setText("{} bins".format(nbins))
        self.do(new_state)

    def do(self, state):
        self.states = self.states[:self.state_index + 1]
        self.states.append(state)
        self.state_index += 1

    def undo(self):
        if self.state_index > 0:
            self.state_index -= 1

    def redo(self):
        if self.state_index + 1 < len(self.states):
            self.state_index += 1

qapp = QApplication(sys.argv)
oif = OperatorInspectionFrame()
oif.show()
qapp.exec_()
