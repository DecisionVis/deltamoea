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
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QRect
from PyQt5.QtCore import Qt
import sys
import numpy
from moeadv.operators import pm_inner

class PMHistogramState(object):
    def __init__(self, di, x_parent, samples, nbins):
        self.di = di
        self.x_parent = x_parent
        self.samples = samples
        self.nbins = nbins
        self.data = None # lazy sampling

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
        if self.data is None:
            self.data = self._sample()
        counts, bins = numpy.histogram(self.data, bins=self.nbins, range=(0.0, 1.0))
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
        new_state.data = self.data
        return new_state

    def release_data(self):
        """ stop holding a reference to the data """
        self.data = None

class PMHistogramWidget(QOpenGLWidget):
    def __init__(self, initial_state, *args, **kwargs):
        super(PMHistogramWidget, self).__init__(*args, **kwargs)
        self.pixel_width = 100
        self.pixel_height = 100
        # label_height: pixels to reserve for label
        self.label_height = 20.0
        self.vp = QOpenGLVersionProfile()
        self.shader_program = QOpenGLShaderProgram(self)
        self.counts, self.bin_edges = initial_state.counts()
        self.selected_bin = None
        self.setMouseTracking(True)

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
        maxcount = self.counts.max()
        # here let's assume bin_edges is from 0-1
        working_width = self.pixel_width - 20
        working_height = self.pixel_height - 2 * self.label_height
        pixel_y_0 = self.pixel_height - self.label_height
        if working_width * 1.0 / len(self.bin_edges) >= 5:
            # don't bother if < 5 pixels wide
            for ii, bin_edge in enumerate(self.bin_edges):
                if ii == 0:
                    count = self.counts[0]
                elif ii == len(self.counts):
                    count = self.counts[-1]
                else:
                    count = max(self.counts[ii-1], self.counts[ii])
                bar_height = count * 1.0 / maxcount
                # plus 1 to correct for line width of 2
                pixel_y = working_height * (1-bar_height) + self.label_height + 1
                pixel_x = int(10 + working_width * bin_edge)
                painter.drawLine(pixel_x, pixel_y_0, pixel_x, pixel_y)
 
        painter.beginNativePainting()
        fun = QOpenGLContext.currentContext().versionFunctions(self.vp)
        fun.glEnable(fun.GL_BLEND)
        fun.glBlendFunc(fun.GL_SRC_ALPHA, fun.GL_ONE_MINUS_SRC_ALPHA)
        self.shader_program.bind()
        vertices = self.vertices()
        self.shader_program.setAttributeArray('position', vertices)
        self.shader_program.setUniformValue("x_margin", self.x_margin)
        self.shader_program.setUniformValue("y_margin", self.y_margin)
        self.shader_program.enableAttributeArray('position')
        fun.glDrawArrays(fun.GL_TRIANGLES, 0, vertices.shape[0])
        self.shader_program.disableAttributeArray('position')
        painter.endNativePainting()
        painter.setPen(QPen(QBrush(QColor(80,80,80)), 1))
        limit = self.bin_edges.shape[0]
        step = limit // 10
        ii = 0
        while ii < limit:
            bin_edge = self.bin_edges[ii]
            ii += step
            text = "{:.2f}".format(bin_edge)
            working_width = self.pixel_width - 20
            pixel_x = int(10 + bin_edge * working_width)
            pixel_y = int(self.pixel_height - 8)
            painter.drawText(pixel_x, pixel_y, text)

    def get_picked_bar(self, pixel_x, pixel_y):
        if pixel_x < 10 or pixel_x > self.pixel_width - 10:
            return None
        if pixel_y < self.label_height or pixel_y > self.pixel_height - self.label_height:
            return None
        x_scaled = (pixel_x - 10) * 1.0 / (self.pixel_width - 2 * 10)
        where_lt = numpy.where(self.bin_edges <= x_scaled)[0]
        if where_lt.size == 0:
            return None
        where_gt = numpy.where(self.bin_edges > x_scaled)[0]
        if where_gt.size == 0:
            return None
        last_lt = where_lt[-1]
        first_gt = where_gt[0]
        if first_gt - last_lt != 1:
            return None
        # return last_lt here if you don't like the "only on the bin" feature
        # implemented below
        count = self.counts[last_lt]
        y_scaled = 1 - count / self.counts.max()
        y_offset = y_scaled * (self.pixel_height - 2 * self.label_height)
        # the 0.05 is so that you can inspect low-count bins
        pixel_y_min = self.label_height + y_offset - 0.05 * self.pixel_height
        if pixel_y < pixel_y_min:
            return None
        return last_lt

    def mouseMoveEvent(self, the_event):
        the_event.accept()
        pos = the_event.pos()
        pixel_x = pos.x()
        pixel_y = pos.y()
        self.selected_bin = self.get_picked_bar(pixel_x, pixel_y)
        if self.selected_bin is not None:
            print(self.counts[self.selected_bin])

    def vertices(self):
        maxcount = self.counts.max()
        nbins = self.counts.shape[0]
        # scale vertices into 0,1 square
        binscale = 1.0 / (self.bin_edges.max() - self.bin_edges.min())
        unitheight = 1.0 / maxcount
        left = self.bin_edges[:-1] * binscale
        right = self.bin_edges[1:] * binscale
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

    def set_state(self, state):
        self.counts, self.bin_edges = state.counts()
        self.update()

class OperatorInspectionFrame(QFrame):
    def __init__(self, *args, **kwargs):
        super(OperatorInspectionFrame, self).__init__(*args, **kwargs)
        # prepare state
        initial_state = PMHistogramState(15, 0.5, 10000, 100)
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
        self.bins_slider.setMinimum(4)
        self.bins_slider.setMaximum(100)
        self.bins_label.setText("{} bins".format(initial_state.nbins))
        self.bins_slider.setValue(
            self._nbins_to_bin_slider(initial_state.nbins))
        self.bins_slider.valueChanged.connect(self._nbins_changed)

        self.parent_label = QLabel(control_panel)
        cp_layout.addWidget(self.parent_label)
        self.parent_slider = QSlider(Qt.Horizontal, control_panel)
        cp_layout.addWidget(self.parent_slider)
        self.parent_slider.setMinimum(0)
        self.parent_slider.setMaximum(100)
        self.parent_label.setText("x = {:.2f}".format(initial_state.x_parent))
        self.parent_slider.setValue(
            self._parent_x_to_slider(initial_state.x_parent))
        self.parent_slider.valueChanged.connect(self._x_parent_changed)

        self.samples_label = QLabel(control_panel)
        cp_layout.addWidget(self.samples_label)
        self.samples_slider = QSlider(Qt.Horizontal, control_panel)
        cp_layout.addWidget(self.samples_slider)
        self.samples_slider.setMinimum(20)
        self.samples_slider.setMaximum(50)
        self.samples_label.setText("{} samples".format(initial_state.samples))
        self.samples_slider.setValue(
            self._samples_to_slider(initial_state.samples))
        self.samples_slider.valueChanged.connect(self._samples_changed)

        self.di_label = QLabel(control_panel)
        cp_layout.addWidget(self.di_label)
        self.di_slider = QSlider(Qt.Horizontal, control_panel)
        cp_layout.addWidget(self.di_slider)
        self.di_slider.setMinimum(0)
        self.di_slider.setMaximum(100)
        self.di_label.setText("di {}".format(initial_state.di))
        self.di_slider.setValue(initial_state.di)
        self.di_slider.valueChanged.connect(self._di_changed)

        cp_layout.addStretch()

        # set up heartbeat
        self.heartbeat = QTimer()
        self.heartbeat.timeout.connect(self.poll)
        self.heartbeat.start(100)

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

    def _parent_x_to_slider(self, x_parent):
        slider = int(100 * x_parent)
        return slider

    def _slider_to_parent_x(self, slider):
        x_parent = 0.01 * slider
        return x_parent

    def _x_parent_changed(self, slider_position):
        x_parent = self._slider_to_parent_x(slider_position)
        new_state = self.states[self.state_index].update_x_parent(x_parent)
        self.parent_label.setText("x = {:.2f}".format(x_parent))
        self.do(new_state)

    def _samples_to_slider(self, samples):
        slider = int(10 * numpy.log10(samples)) # use decibel-style scaling
        return slider

    def _slider_to_samples(self, slider):
        samples = int(10 ** (slider / 10))
        return samples

    def _samples_changed(self, slider_position):
        samples = self._slider_to_samples(slider_position)
        new_state = self.states[self.state_index].update_samples(samples)
        self.samples_label.setText("{} samples".format(samples))
        self.do(new_state)

    def _di_changed(self, slider_position):
        new_state = self.states[self.state_index].update_di(slider_position)
        self.di_label.setText("di {}".format(slider_position))
        self.do(new_state)

    def keyReleaseEvent(self, the_event):
        if the_event.matches(QKeySequence.Undo):
            the_event.accept()
            self.undo()
        elif the_event.matches(QKeySequence.Redo):
            the_event.accept()
            self.redo()
        else:
            super(OperatorInspectionFrame, self).keyReleaseEvent(the_event)

    def do(self, state):
        if self.state_index == self.last_state_index:
            self.states = self.states[:self.state_index + 1]
            self.states.append(state)
            self.state_index += 1
        else:
            # overwrite the unused state
            self.states[self.state_index] = state

    def undo(self):
        if self.state_index > 0:
            self.state_index -= 1
            self.update_gui()

    def update_gui(self):
        state = self.states[self.state_index]
        self.bins_slider.setValue(
            self._nbins_to_bin_slider(state.nbins))
        self.bins_label.setText("{} bins".format(state.nbins))
        self.parent_slider.setValue(
            self._parent_x_to_slider(state.x_parent))
        self.parent_label.setText("x = {:.2f}".format(state.x_parent))
        self.samples_slider.setValue(
            self._samples_to_slider(state.samples))
        self.samples_label.setText("{} samples".format(state.samples))
        self.di_slider.setValue(state.di)
        self.di_label.setText("di {}".format(state.di))

    def redo(self):
        if self.state_index + 1 < len(self.states):
            self.state_index += 1
            self.update_gui()

    def poll(self):
        if self.last_state_index != self.state_index:
            self.plot.set_state(self.states[self.state_index])
            self.last_state_index = self.state_index

            # release old data if needed
            ii = self.state_index
            data = self.states[ii].data
            retained_samples = 0
            retaining = True
            while ii > 0:
                ii -= 1
                state = self.states[ii]
                if retaining:
                    if data is state.data:
                        continue
                    if state.data is None:
                        continue
                    retained_samples += state.data.size
                    data = state.data
                    retaining = retained_samples < 500000
                else:
                    state.release_data()

        self.plot.get_picked_bar(100,100)

qapp = QApplication(sys.argv)
oif = OperatorInspectionFrame()
oif.show()
qapp.exec_()
