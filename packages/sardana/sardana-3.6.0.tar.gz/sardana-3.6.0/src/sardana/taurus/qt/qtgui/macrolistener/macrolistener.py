#!/usr/bin/env python

##############################################################################
##
# This file is part of Sardana
##
# http://www.sardana-controls.org/
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Sardana is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Sardana is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""
This module provides objects to manage macro-related tasks. Its primary use is
to be used within a TaurusGui for managing panels for:
- setting preferences in the sardana control system for data I/O
- displaying results of macro executions, including creating/removing panels
  for plotting results of scans
- editing macros

.. note:: This module was originally implemented in taurus as
          `taurus.qt.qtgui.taurusgui.macrolistener`
"""
import datetime
import itertools

import numpy

try:
    import pyqtgraph
except ImportError:
    pyqtgraph = None

from taurus.external.qt import Qt, QtGui
from taurus.core.util.containers import ArrayBuffer
from taurus.qt.qtgui.base import TaurusBaseComponent

from sardana.taurus.core.tango.sardana import PlotType


__all__ = [
    'MultiPlotWidget',  'MacroBroker', 'PlotManager', 'DynamicPlotManager',
    'assertPlotAvailability'
]

__docformat__ = 'restructuredtext'

COLORS = [Qt.QColor(Qt.Qt.red),
          Qt.QColor(Qt.Qt.green),
          Qt.QColor(Qt.Qt.magenta),
          Qt.QColor(Qt.Qt.blue),
          Qt.QColor(Qt.Qt.cyan),
          Qt.QColor(Qt.Qt.yellow),
          Qt.QColor(Qt.Qt.white)]

SYMBOLS = ['x', 'o', 't', 't1', 't2', 't3', 's', 'p']

CURVE_STYLES = [(color, symbol) for symbol in SYMBOLS for color in COLORS]

NO_PLOT_MESSAGE = 'Plots cannot be displayed (pyqtgraph not installed)'


def assertPlotAvailability(exit_on_error=True):
    if pyqtgraph is None:
        Qt.QMessageBox.critical(None, 'Plot error', NO_PLOT_MESSAGE)
        if exit_on_error:
            exit(1)


def empty_data(nb_points):
    return ArrayBuffer(numpy.full(nb_points, numpy.nan))


def find_nearest(array, value):
    return (numpy.abs(array.contents() - value)).argmin()


class Plot:

    LinePen = pyqtgraph.mkPen(color='w', width=1)

    def __init__(self, x_axis, curves, styles, nb_points=2**16, parent=None):
        nb_curves = len(curves)
        self.parent = parent
        labels = dict(bottom=x_axis['label'])
        if nb_curves == 1:
            labels['left'] = curves[0]['label']

        self.plot = pyqtgraph.PlotItem(labels=labels)
        self.plot.showGrid(x=True, y=True)
        x_range = x_axis.get('range')
        if None not in x_range:
            self.plot.setXRange(*x_range)
        self.vLine = pyqtgraph.InfiniteLine(angle=90,
                                            pen=self.LinePen,
                                            movable=False)
        if nb_curves > 1:
            self.plot.addLegend()
        self.x_axis = dict(x_axis, data=empty_data(nb_points))
        self.curves = []
        for curve in curves:
            pen, symbol = next(styles)
            style = dict(pen=pen, symbol=symbol,
                         symbolSize=5, symbolPen=pen, symbolBrush=pen)
            curve_item = self.plot.plot(name=curve['label'], **style)
            curve_item.curve_data = empty_data(nb_points)
            curve_item.curve_id = curve['name']
            self.curves.append(curve_item)
        self.highlights = pyqtgraph.ScatterPlotItem(
            pos=(),
            symbol="s",
            brush="white",
            pxMode=True,
            size=10,
        )
        self.highlights._UImodifiable = False

    def add_inspector_context_menu(self, enabled=False):
        # Add toggle inspector in context menu
        menu = self.plot.getViewBox().menu
        self._inspector_checkbox = QtGui.QAction(
            "Inspector", menu
        )
        self._inspector_checkbox.setCheckable(True)
        self._inspector_checkbox.setChecked(enabled)
        self._inspector_checkbox.triggered.connect(self.on_inspector_checkbox_changed)
        menu.addAction(self._inspector_checkbox)
        # Since it may be checked to remember last selection in previous
        # plots managed by MultiPlotWidget, we need to update state
        self.on_inspector_checkbox_changed()

    def is_inspector_enabled(self):
        return self._inspector_checkbox.isChecked()

    def on_inspector_checkbox_changed(self):
        if self.is_inspector_enabled():
            self.plot.addItem(self.vLine, ignoreBounds=True)
            self.plot.addItem(self.highlights, ignoreBounds=True)
        else:
            self.plot.removeItem(self.vLine)
            self.plot.removeItem(self.highlights)
        
        self.parent.update_global_inspector_state()

    def on_new_point(self,  data):
        x_axis = self.x_axis
        x_data = x_axis['data']
        x_data.append(data[x_axis['name']])
        for curve in self.curves:
            y_data = curve.curve_data
            y_data.append(data[curve.curve_id])

    def do_update(self):
        x_axis = self.x_axis
        x_data = x_axis['data'].contents()
        for curve in self.curves:
            y_data = curve.curve_data.contents()
            curve.setData(x_data, y_data)

    def point_inside(self, point):
        plot = self.plot
        if plot.vb.sceneBoundingRect().contains(point):
            view_point = plot.vb.mapSceneToView(point)
            x_data = self.x_axis['data']
            index = find_nearest(x_data, view_point.x())
            if index >= 0 and index < len(x_data):
                return view_point, index

    def on_mouse_move(self, point):
        info = self.point_inside(point)
        highlights = ()
        if info is not None:
            view_point, index = info
            x_axis = self.x_axis
            x_value = x_axis['data'][index]
            highlights = [(x_value, curve.curve_data[index])
                          for curve in self.curves]
            self.vLine.setPos(view_point.x())
        self.vLine.setVisible(info is not None)
        self.highlights.setData(pos=highlights)
        return info


class MultiPlotWidget(Qt.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = Qt.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.win = pyqtgraph.GraphicsLayoutWidget()
        self.inspector_label = Qt.QLabel()
        self.inspector_label.setStyleSheet("padding-left: 5px;")
        self.layout.addWidget(self.win)
        self._plots = []
        self._timer = None
        self._event_nb = 0
        self._last_event_nb = 0
        self._inspectorEnabled = False
        self._sig_proxy = None

    def on_mouse_move(self, evt):
        point = evt[0]
        info = None
        curves = []
        for plot in self._plots:
            curves.extend(plot.curves)
            i = plot.on_mouse_move(point)
            if i is not None:
                info = plot, i
        if info is None:
            text = 'No point selected'
        else:
            focus_plot, (view_point, index) = info
            x_axis = plot.x_axis
            x_value = x_axis['data'][index]
            points_text = []
            for curve in curves:
                txt = '{}={:.3f}'.format(curve.name(), curve.curve_data[index])
                if curve in focus_plot.curves:
                    txt = '<b>{}</b>'.format(txt)
                points_text.append(txt)
            text = 'x={:.3f} y={:.3f} | {}={:.3f} {}'.format(
                view_point.x(), view_point.y(), x_axis['label'],
                x_value, ' '.join(points_text))
        self.inspector_label.setText(text)

    def update_global_inspector_state(self):
        self._inspectorEnabled = any(plot.is_inspector_enabled() for plot in self._plots)
        if self._inspectorEnabled:
            if not self._sig_proxy:
                scene = self.win.scene()
                self._sig_proxy = pyqtgraph.SignalProxy(
                    scene.sigMouseMoved, rateLimit=20, slot=self.on_mouse_move)            
            if self.inspector_label not in self.layout.children():
                self.layout.addWidget(self.inspector_label)
        else:
            self._sig_proxy = None
            self.layout.removeWidget(self.inspector_label)

    def prepare(self, plots, nb_points=None):
        self.win.clear()
        plts = []
        nb_points = 2**16 if nb_points is None else nb_points
        plots_per_row = int(len(plots)**0.5)
        styles = itertools.cycle(CURVE_STYLES)
        for idx, plot in enumerate(plots):
            x_axis, curves = plot['x_axis'], plot['curves']
            if idx % plots_per_row == 0:
                self.win.nextRow()
            plot = Plot(x_axis, curves, styles, nb_points, parent=self)
            # Use _inspectorEnabled to remember last state of this option
            plot.add_inspector_context_menu(self._inspectorEnabled)
            plts.append(plot)
            self.win.addItem(plot.plot)
            
        self._plots = plts
        self._event_nb = 0
        self._last_event_nb = 0
        self._start_update()

    def on_new_point(self, data):
        # update internal data and mark the new event
        for plot in self._plots:
            plot.on_new_point(data)
        self._event_nb += 1

    def onEnd(self, data):
        self.do_update()
        self._end_update()

    def do_update(self):
        if self._event_nb == self._last_event_nb:
            return
        self._last_event_nb = self._event_nb
        for plot in self._plots:
            plot.do_update()

    def _start_update(self):
        self._end_update()
        timer = Qt.QTimer()
        timer.timeout.connect(self.do_update)
        # refresh curves at a fix rate of ~5Hz
        timer.start(200)
        self._timer = timer

    def _end_update(self):
        if self._timer:
            self._timer.stop()
        self._timer = None


class PlotManager(Qt.QObject, TaurusBaseComponent):
    '''
    This is a manager of plots related to the execution of macros.
    It dynamically creates/removes plots according to the configuration made by
    an ExperimentConfiguration widget.

    Currently it supports only 1D scan trends (2D scans are only half-baked)

    To use it simply instantiate it and pass it a door name as a model.
    '''

    plots_available = pyqtgraph is not None

    newShortMessage = Qt.pyqtSignal('QString')

    Single = 'single'  # each curve has its own plot
    XAxis = 'x-axis'   # group curves with same X-Axis

    def __init__(self, plot=None, parent=None):
        Qt.QObject.__init__(self, parent)
        TaurusBaseComponent.__init__(self, self.__class__.__name__)

        self._group_mode = self.XAxis

        self.plot = plot or MultiPlotWidget()

    def setGroupMode(self, group):
        assert group in (self.Single, self.XAxis)
        self._group_mode = group

    def groupMode(self):
        return self._group_mode

    def setModel(self, doorname):
        '''reimplemented from :meth:`TaurusBaseComponent`

        :param doorname: (str) device name corresponding to a Door device.
        '''
        TaurusBaseComponent.setModel(self, doorname)
        # self._onDoorChanged(doorname)
        if not doorname:
            return
        self.door = self.getModelObj()
        if not isinstance(self.door, Qt.QObject):
            msg = "Unexpected type (%s) for %s" % (repr(type(self.door)),
                                                   doorname)
            Qt.QMessageBox.critical(
                self.parent(), 'Door connection error', msg)
            return

        self._checkJsonRecorder()

        self.door.recordDataUpdated.connect(self.onRecordDataUpdated)
        self.message_template = 'Ready!'

    def _checkJsonRecorder(self):
        '''Checks if JsonRecorder env var is set and offers to set it'''
        door = self.getModelObj()
        if 'JsonRecorder' not in door.getEnvironment():
            msg = ('JsonRecorder environment variable is not set, but it '
                   + 'is needed for displaying trend plots.\n'
                   + 'Enable it globally for %s?') % door.getFullName()
            result = Qt.QMessageBox.question(
                self.parent(), 'JsonRecorder not set', msg,
                Qt.QMessageBox.Yes | Qt.QMessageBox.No)
            if result == Qt.QMessageBox.Yes:
                door.putEnvironment('JsonRecorder', True)
                self.info('JsonRecorder Enabled for %s' % door.getFullName())

    def onRecordDataUpdated(self, arg):
        """
        Receive RecordDataUpdated tuple, the method detects when the event
        type is 'data_desc' (come with new data description), it will call
        to 'onExpConfChanged' to refresh the plots configuration,
        adding/removing plots based in the new Experimental configuration.

        Note: After the plots reorder, the data description event is resend
        to reconfig the plot with the new data description.

        :param arg: RecordData Tuple
        :return:
        """
        data = arg[1]
        if 'type' in data:
            event_type = data['type']
            if event_type == 'data_desc':
                self.prepare(data)
            elif event_type == 'record_data':
                self.new_point(data)
            elif event_type == 'record_end':
                self.end(data)

    def prepare(self, data_desc):
        """
        Prepare UI for a new scan. Rebuilds plots as necessary to adapt to the
        new scan channels and moveables
        """
        data = data_desc['data']
        col_map = {column['name']: column for column in data['column_desc']}

        # Build list of curves. Each curve has the same column info from the
        # event and additionally the x-axis it should be plot against
        curves = []
        x_ranges = {}
        for column in data['column_desc']:
            ch_name = column['name']
            ptype = column.get('plot_type', PlotType.No)
            if ptype == PlotType.No:
                continue
            elif ptype == PlotType.Image:
                self.warning('Unsupported image plot for %s', ch_name)
                continue
            x_axes = ['point_nb' if axis == '<idx>' else axis
                      for axis in column.get('plot_axes', ())]
            ndim = column.get('ndim', 0) or 0
            if ptype == PlotType.Spectrum:
                if ndim == 0:  # this is a trend
                    for x_axis in x_axes:
                        x_label = col_map[x_axis]['label']
                        x_ranges[x_axis] = (
                            col_map[x_axis].get('min_value'),
                            col_map[x_axis].get('max_value')
                            )
                        curve = dict(column, x_axis=x_axis,
                                     x_axis_label=x_label)
                        curves.append(curve)
                else:
                    self.warning('Cannot create spectrum plot for %d dims '
                                 'channel %r', ndim, ch_name)

        if self._group_mode == self.Single:
            plots = []
            for curve in curves:
                plot = dict(x_axis=dict(name=curve['x_axis'],
                                        label=curve['x_axis_label'],
                                        range=x_ranges[curve['x_axis']]),
                            curves=[curve])
                plots.append(plot)
        elif self._group_mode == self.XAxis:
            plot_map = {}
            for curve in curves:
                x_axis = curve['x_axis']
                plot = plot_map.get(x_axis)
                if plot is None:
                    plot = dict(x_axis=dict(name=curve['x_axis'],
                                            label=curve['x_axis_label'],
                                            range=x_ranges[x_axis]),
                                curves=[])
                    plot_map[x_axis] = plot
                plot['curves'].append(curve)
            plots = tuple(plot_map.values())
        else:
            raise NotImplementedError

        nb_points = data.get('total_scan_intervals', 2**16 - 1) + 1
        self.plot.prepare(plots, nb_points=nb_points)

        # build status message
        serialno = 'Scan #{}'.format(data.get('serialno', '?'))
        title = data.get('title', 'unnamed operation')
        if data.get('scandir') and data.get('scanfile'):
            scan_file = data['scanfile']
            if isinstance(scan_file, (list, tuple)):
                scan_file = '&'.join(data['scanfile'])
            saving = data['scandir'] + '/' + scan_file
        else:
            saving = 'no saving!'
        started = 'Started ' + data.get('starttime', '?')
        progress = '{progress}'
        self.message_template = ' | '.join((serialno, title, started,
                                            progress, saving))
        self.newShortMessage.emit(
            self.message_template.format(progress='Preparing...'))

    def new_point(self, point):
        data = point['data']
        self.plot.on_new_point(data)
        point_nb = 'Point #{}'.format(data['point_nb'])
        msg = self.message_template.format(progress=point_nb)
        self.newShortMessage.emit(msg)

    def end(self, end_data):
        data = end_data['data']
        self.plot.onEnd(data)
        progress = 'Ended {}'.format(data['endtime'])
        msg = self.message_template.format(progress=progress)
        self.newShortMessage.emit(msg)


class DynamicPlotManager(PlotManager):
    '''This is a manager of plots related to the execution of macros.
    It dynamically creates/removes plots according to the configuration made by
    an ExperimentConfiguration widget.

    Currently it supports only 1D scan trends (2D scans are only half-baked)

    To use it simply instantiate it and pass it a door name as a model.
    '''

    def __init__(self, *args, **kwargs):
        PlotManager.__init__(self, *args, **kwargs)
        self.__panels = {}
        self.createPanel(
            self.plot, 'Scan plot', registerconfig=False, permanent=False)

    def createPanel(self, widget, name, **kwargs):
        '''Creates a "panel" from a widget. In this basic implementation this
        means that the widgets is shown as a non-modal top window

        :param widget: (QWidget) widget to be used for the panel
        :param name: (str) name of the panel. Must be unique.

        Note: for backawards compatibility, this implementation accepts
        arbitrary keyword arguments which are just ignored
        '''
        widget.setWindowTitle(name)
        widget.show()
        self.__panels[name] = widget

    def getPanelWidget(self, name):
        '''Returns the widget associated to a panel name

        :param name: (str) name of the panel. KeyError is raised if not found

        :return: (QWidget)
        '''
        return self.__panels[name]

    def removePanel(self, name):
        '''stop managing the given panel

        :param name: (str) name of the panel'''
        widget = self.__panels.pop(name)
        if hasattr(widget, 'setModel'):
            widget.setModel(None)
        widget.setParent(None)
        widget.close()


class MacroBroker(DynamicPlotManager):
    '''A manager of all macro-related panels of a TaurusGui.

    It creates, destroys and manages connections for the following objects:

        - Macro Configuration dialog
        - Experiment Configuration panel
        - Macro Executor panel
        - Sequencer panel
        - Macro description viewer
        - Door output, result and debug panels
        - Macro editor
        - Macro "panic" button (to abort macros)
        - Dynamic plots (see :class:`DynamicPlotManager`)
    '''

    def __init__(self, parent):
        '''Passing the parent object (the main window) is mandatory'''
        DynamicPlotManager.__init__(self, parent=parent)

        self._createPermanentPanels()

        # connect the broker to shared data
        Qt.qApp.SDM.connectReader("doorName", self.setModel)
        Qt.qApp.SDM.connectWriter("shortMessage", self, 'newShortMessage')

    def setModel(self, doorname):
        ''' Reimplemented from :class:`DynamicPlotManager`.'''
        # disconnect the previous door
        door = self.getModelObj()
        if door is not None:  # disconnect it from *all* shared data providing
            SDM = Qt.qApp.SDM
            try:
                SDM.disconnectWriter("macroStatus", door,
                                     "macroStatusUpdated")
            except Exception:
                self.info("Could not disconnect macroStatusUpdated")
            try:
                SDM.disconnectWriter("doorOutputChanged", door,
                                     "outputUpdated")
            except Exception:
                self.info("Could not disconnect outputUpdated")
            try:
                SDM.disconnectWriter("doorInfoChanged", door, "infoUpdated")
            except Exception:
                self.info("Could not disconnect infoUpdated")
            try:
                SDM.disconnectWriter("doorWarningChanged", door,
                                     "warningUpdated")
            except Exception:
                self.info("Could not disconnect warningUpdated")
            try:
                SDM.disconnectWriter("doorErrorChanged", door, "errorUpdated")
            except Exception:
                self.info("Could not disconnect errorUpdated")
            try:
                SDM.disconnectWriter("doorDebugChanged", door, "debugUpdated")
            except Exception:
                self.info("Could not disconnect debugUpdated")
            try:
                SDM.disconnectWriter("doorResultChanged", door,
                                     "resultUpdated")
            except Exception:
                self.info("Could not disconnect resultUpdated")
            try:
                SDM.disconnectWriter("expConfChanged", door,
                                     "experimentConfigurationChanged")
            except Exception:
                self.info(
                    "Could not disconnect experimentConfigurationChanged")
        # set the model
        DynamicPlotManager.setModel(self, doorname)

        # connect the new door
        door = self.getModelObj()
        if door is not None:
            SDM = Qt.qApp.SDM
            SDM.connectWriter("macroStatus", door, "macroStatusUpdated")
            SDM.connectWriter("doorOutputChanged", door, "outputUpdated")
            SDM.connectWriter("doorInfoChanged", door, "infoUpdated")
            SDM.connectWriter("doorWarningChanged", door, "warningUpdated")
            SDM.connectWriter("doorErrorChanged", door, "errorUpdated")
            SDM.connectWriter("doorDebugChanged", door, "debugUpdated")
            SDM.connectWriter("doorResultChanged", door, "resultUpdated")
            SDM.connectWriter("expConfChanged", door,
                              "experimentConfigurationChanged")

    def _createPermanentPanels(self):
        '''creates panels on the main window'''
        from sardana.taurus.qt.qtgui.extra_macroexecutor import \
            TaurusMacroExecutorWidget, TaurusSequencerWidget, \
            TaurusMacroConfigurationDialog, TaurusMacroDescriptionViewer, \
            DoorOutput, DoorDebug, DoorResult

        from sardana.taurus.qt.qtgui.extra_sardana import \
            ExpDescriptionEditor

        mainwindow = self.parent()

        # Create macroconfiguration dialog & action
        self.__macroConfigurationDialog = \
            TaurusMacroConfigurationDialog(mainwindow)
        self.macroConfigurationAction = mainwindow.taurusMenu.addAction(
            Qt.QIcon.fromTheme("preferences-system-session"),
            "Macro execution configuration...",
            self.__macroConfigurationDialog.show)

        SDM = Qt.qApp.SDM
        SDM.connectReader("macroserverName",
                          self.__macroConfigurationDialog.selectMacroServer)
        SDM.connectReader("doorName",
                          self.__macroConfigurationDialog.selectDoor)
        SDM.connectWriter("macroserverName", self.__macroConfigurationDialog,
                          'macroserverNameChanged')
        SDM.connectWriter("doorName", self.__macroConfigurationDialog,
                          'doorNameChanged')

        # Create ExpDescriptionEditor dialog
        self.__expDescriptionEditor = ExpDescriptionEditor()
        SDM.connectReader("doorName", self.__expDescriptionEditor.setModel)
        mainwindow.createPanel(self.__expDescriptionEditor,
                               'Experiment Config',
                               registerconfig=True,
                               icon=Qt.QIcon.fromTheme('preferences-system'),
                               permanent=True)
        ###############################
        # TODO: These lines can be removed once the door does emit
        # "experimentConfigurationChanged" signals
        SDM.connectWriter("expConfChanged", self.__expDescriptionEditor,
                          "experimentConfigurationChanged")
        ################################

        # put a Macro Executor
        self.__macroExecutor = TaurusMacroExecutorWidget()
        SDM.connectReader("macroserverName", self.__macroExecutor.setModel)
        SDM.connectReader("doorName", self.__macroExecutor.onDoorChanged)
        SDM.connectReader("macroStatus",
                          self.__macroExecutor.onMacroStatusUpdated)
        SDM.connectWriter("macroName", self.__macroExecutor,
                          "macroNameChanged")
        SDM.connectWriter("executionStarted", self.__macroExecutor,
                          "macroStarted")
        SDM.connectWriter("plotablesFilter", self.__macroExecutor,
                          "plotablesFilterChanged")
        SDM.connectWriter("shortMessage", self.__macroExecutor,
                          "shortMessageEmitted")
        mainwindow.createPanel(self.__macroExecutor, 'Macros',
                               registerconfig=True, permanent=True)

        # put a Sequencer
        self.__sequencer = TaurusSequencerWidget()
        SDM.connectReader("macroserverName", self.__sequencer.setModel)
        SDM.connectReader("doorName", self.__sequencer.onDoorChanged)
        SDM.connectReader("macroStatus",
                          self.__sequencer.onMacroStatusUpdated)
        SDM.connectWriter("macroName", self.__sequencer.tree,
                          "macroNameChanged")
        SDM.connectWriter("macroName", self.__sequencer,
                          "macroNameChanged")
        SDM.connectWriter("executionStarted", self.__sequencer,
                          "macroStarted")
        SDM.connectWriter("plotablesFilter", self.__sequencer,
                          "plotablesFilterChanged")
        SDM.connectWriter("shortMessage", self.__sequencer,
                          "shortMessageEmitted")
        mainwindow.createPanel(self.__sequencer, 'Sequences',
                               registerconfig=True, permanent=True)

        # puts a macrodescriptionviewer
        self.__macroDescriptionViewer = TaurusMacroDescriptionViewer()
        SDM.connectReader("macroserverName",
                          self.__macroDescriptionViewer.setModel)
        SDM.connectReader("macroName",
                          self.__macroDescriptionViewer.onMacroNameChanged)
        mainwindow.createPanel(self.__macroDescriptionViewer,
                               'MacroDescription', registerconfig=True,
                               permanent=True)

        # puts a doorOutput
        self.__doorOutput = DoorOutput()
        SDM.connectReader("doorOutputChanged",
                          self.__doorOutput.onDoorOutputChanged)
        SDM.connectReader("doorInfoChanged",
                          self.__doorOutput.onDoorInfoChanged)
        SDM.connectReader("doorWarningChanged",
                          self.__doorOutput.onDoorWarningChanged)
        SDM.connectReader("doorErrorChanged",
                          self.__doorOutput.onDoorErrorChanged)
        SDM.connectReader("doorDebugChanged",
                          self.__doorOutput.onDoorDebugChanged)
        mainwindow.createPanel(self.__doorOutput, 'DoorOutput',
                               registerconfig=False, permanent=True)

        # puts doorResult
        self.__doorResult = DoorResult(mainwindow)
        SDM.connectReader("doorResultChanged",
                          self.__doorResult.onDoorResultChanged)
        mainwindow.createPanel(self.__doorResult, 'DoorResult',
                               registerconfig=False, permanent=True)

        # add panic button for aborting the door
        text = "Panic Button: stops the macro and the pools (double-click for abort)"
        self.doorAbortAction = mainwindow.jorgsBar.addAction(
            Qt.QIcon("actions:process-stop.svg"),
            text, self.__onDoorAbort)

        # store beginning of times as a datetime
        self.__lastAbortTime = datetime.datetime(1, 1, 1)

        # store doubleclick interval as a timedelta
        td = datetime.timedelta(0, 0, 1000 * Qt.qApp.doubleClickInterval())
        self.__doubleclickInterval = td

    def __onDoorAbort(self):
        '''slot to be called when the abort action is triggered.
        It sends stop command to the pools (or abort if the action
        has been triggered twice in less than self.__doubleclickInterval

        .. note:: An abort command is always preceded by an stop command
        '''
        # decide whether to send stop or abort
        now = datetime.datetime.now()
        if now - self.__lastAbortTime < self.__doubleclickInterval:
            cmd = 'abort'
        else:
            cmd = 'stop'

        door = self.getModelObj()
        if door is None:
            raise Exception("no Door selected, can not {}".format(cmd))

        # stop/abort the door
        try:
            door.command_inout('{}macro'.format(cmd))
        except Exception:
            self.info("%s command failed on %s", cmd, door.getFullName(),
                       exc_info=1)
        short_message = "%smacro command sent to the door" % cmd
        # send stop/abort to all pools
        pools = door.macro_server.getElementsOfType('Pool')
        for pool in list(pools.values()):
            self.info('Sending %s command to %s' % (cmd, pool.getFullName()))
            try:
                pool.getObj().command_inout(cmd)
            except Exception:
                self.info('%s command failed on %s', cmd, pool.getFullName(),
                          exc_info=1)
        short_message += " and %s command sent to all pools" % cmd
        self.newShortMessage.emit(short_message)
        self.__lastAbortTime = now

    def createPanel(self, widget, name, **kwargs):
        ''' Reimplemented from :class:`DynamicPlotManager` to delegate panel
        management to the parent widget (a TaurusGui)'''
        mainwindow = self.parent()
        return mainwindow.createPanel(widget, name, **kwargs)

    def getPanelWidget(self, name):
        ''' Reimplemented from :class:`DynamicPlotManager` to delegate panel
        management to the parent widget (a TaurusGui)'''
        mainwindow = self.parent()
        return mainwindow.getPanel(name).widget()

    def removePanel(self, name):
        ''' Reimplemented from :class:`DynamicPlotManager` to delegate panel
        management to the parent widget (a TaurusGui)'''
        mainwindow = self.parent()
        mainwindow.removePanel(name)

    def removeTemporaryPanels(self, names=None):
        '''Remove temporary panels managed by this widget'''
        # for now, the only temporary panels are the plots
        DynamicPlotManager.removePanels(self, names=names)


if __name__ == "__main__":
    import sys
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication()

    b = DynamicPlotManager(None)

    b.setModel('door/cp1/1')

    print('...')
    sys.exit(app.exec_())
