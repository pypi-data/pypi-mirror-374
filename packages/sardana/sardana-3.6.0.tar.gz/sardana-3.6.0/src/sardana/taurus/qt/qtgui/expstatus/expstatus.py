# -*- coding: utf-8 -*-

##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
##
## Copyright 2019 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

import sys

import click
import taurus
from taurus.external.qt.QtWidgets import QWidget, QFrame, QCompleter, QGridLayout, \
    QSplitter, QPushButton, QLabel
from taurus.core.util.colors import DEVICE_STATE_DATA
from taurus.external.qt import Qt, QtGui, QtCore
from taurus.qt.qtgui.display import TaurusLabel, TaurusLed

import sardana
from sardana.taurus.qt.qtgui.expstatus import treewidget

from sardana.taurus.core.tango.sardana import registerExtensions


class ExpStatus(QWidget):
    def __init__(self, parent=None, door_arg=None, generate_all_arg=False):
        self.door_name = door_arg
        self.generate_all = generate_all_arg
        # call the parent class init
        QWidget.__init__(self, parent=parent)
        self.setWindowTitle("Experiment Status Widget")
        # set some initial properties for the widget
        self.hasBeenGenerated = False

        # create a grid layout and set it as the widget's layout
        self.gridLayout = Qt.QGridLayout()
        self.setLayout(self.gridLayout)

        self.generateElements()

    def generateElements(self):

        if self.hasBeenGenerated:
            # if the content has already been generated, store the current
            # panel elements and buttons in temporary variables
            panelElementsTemp = self.panelElements

            panelButtonsTemp = self.panelButtons

        self.nameList = []
        self.itemsList = []

        # create the panel elements and buttons for the new content
        self.panelElements = self.panelElementsCreation()
        self.panelButtons = self.panelButtonsCreation()

        if self.hasBeenGenerated:
            # if the content has already been generated, hide the previous
            # panel elements and buttons
            panelElementsTemp.hide()
            panelButtonsTemp.hide()

        # add the new panel elements and buttons to the layout
        self.splitter = QSplitter()
        self.splitter.addWidget(self.panelButtons)
        self.splitter.addWidget(self.panelElements)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)

        self.gridLayout.addWidget(self.splitter)
        self.hasBeenGenerated = True  # set the 'hasBeenGenerated' flag to True
        self.setMouseTracking(True)
        # set the minimum size of the widget to accommodate the new content
        self.resize(1300, 900)

    def generateButtonAll(self):
        self.generateElements()

    def regenerate(self):
        self.generate_all = False
        self.panelElements = self.panelElementsCreation()
        self.splitter.replaceWidget(1, self.panelElements)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)

    def regenerateAll(self):
        self.generate_all = True
        self.panelElements = self.panelElementsCreation()
        self.splitter.replaceWidget(1, self.panelElements)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 4)

    # Macro stack panel creation
    def panelButtonsCreation(self):
        # create a frame to hold the panel
        leftFrame = QFrame()
        leftFrame.setFrameShape(QFrame.Shape.Box)
        # create a grid layout for the panel
        leftLayout = Qt.QGridLayout()
        leftFrame.setLayout(leftLayout)

        # add a button for the user to generate the panel with the selected lab
        self.labSelectorButton = QPushButton("Show macro elements")
        self.labSelectorButton.clicked.connect(self.regenerate)
        leftLayout.addWidget(self.labSelectorButton, 0, 0, 1, 2)

        self.labSelectorButtonAll = QPushButton("Show all elements")
        self.labSelectorButtonAll.clicked.connect(self.regenerateAll)
        leftLayout.addWidget(self.labSelectorButtonAll, 0, 2, 1, 2)

        # get the door for the selected lab
        registerExtensions()
        door_device = taurus.Device(self.door_name)

        # create a form panel to show the macro status
        formPanel = QFrame()
        formPanel.setFixedHeight(300)
        formPanelLayout = QGridLayout()
        formPanel.setLayout(formPanelLayout)

        # create a label widget to show the status
        statusLabel = TaurusLabel()
        statusLabel.setAlignment(Qt.Qt.AlignLeft | Qt.Qt.AlignVCenter)
        statusLabel.setAutoTrim(False)
        statusLabel.setWordWrap(True)
        statusLabel.setModel(self.door_name + '/status')
        # statusLabel.setFixedWidth(350)

        # create a label widget to name the status
        statusName = QLabel("Status")
        statusName.setFixedSize(40, 125)
        formPanelLayout.addWidget(statusName, 1, 0)
        formPanelLayout.addWidget(statusLabel, 1, 1, 1, 2)

        # create a LED widget to show the state
        stateLabel = TaurusLed()
        stateLabel.setModel(self.door_name + '/state')
        # create a label widget to name the state
        stateName = QLabel("State")
        stateName.setFixedSize(75, 50)
        formPanelLayout.addWidget(stateName, 2, 0)
        formPanelLayout.addWidget(stateLabel, 2, 1, 1, 2)

        # Change color status
        state_string = str(stateLabel.modelObj.rvalue)
        color_data = DEVICE_STATE_DATA[str(state_string)]
        color_str = str(color_data[1]) + ", " + str(color_data[2]) \
                    + ", " + str(color_data[3])
        label_stylesheet = "QLabel { background-color: rgb(" + color_str + \
                           "); border: 2px solid rgba(255, 255, 255, 125);}"
        tooltip_stylesheet = "QToolTip { \
                           background-color: black; \
                           color: white; \
                           border: white solid 1px \
                           }"

        statusLabel.setStyleSheet(label_stylesheet + tooltip_stylesheet)

        # create a spacer widget to expand the panel
        spacer = Qt.QSpacerItem(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)
        formPanelLayout.addItem(spacer, 3, 0, 1, 2)

        # add the form panel to the grid layout
        leftLayout.addWidget(formPanel, 1, 0, 1, 4)

        def stop(self):
            door_device.stop(synch=False)

        def abort(self):
            door_device.abort(synch=False)

        def release(self):
            door_device.release(synch=False)

        self.panelButtons = QFrame()
        panelButtonsLayout = QGridLayout()
        self.panelButtons.setLayout(panelButtonsLayout)
        buttonStop = QPushButton("STOP")
        buttonStop.clicked.connect(stop)
        buttonAbort = QPushButton("ABORT")
        buttonAbort.clicked.connect(abort)
        buttonRelease = QPushButton("RELEASE")
        buttonRelease.clicked.connect(release)
        panelButtonsLayout.addWidget(buttonStop, 0, 0)
        panelButtonsLayout.addWidget(buttonAbort, 0, 1)
        panelButtonsLayout.addWidget(buttonRelease, 0, 2)
        leftLayout.addWidget(self.panelButtons, 2, 0, 1, 4)

        # create a spacer widget to expand the frame
        frameSpacer = Qt.QSpacerItem(10, 10, Qt.QSizePolicy.Ignored,
                                     Qt.QSizePolicy.Expanding)
        leftLayout.addItem(frameSpacer, 3, 0, 1, 4)

        # return the panel
        return leftFrame

    # We create a search bar
    def createSearchBar(self):
        # Create a QLineEdit search bar with placeholder text and connect
        # its textChanged signal to the searchBarFilter slot
        searchBar = QtGui.QLineEdit()
        searchBar.setPlaceholderText("Filter...")
        searchBar.textChanged.connect(self.searchBarFilter)
        # Create a QCompleter object for the search bar with suggestions
        # from the set of names in self.nameList
        completer = QCompleter(sorted(set(self.nameList)))
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        # Set the completer object for the search bar
        searchBar.setCompleter(completer)
        return searchBar

    def searchBarFilter(self):
        # Get the current search filter text from the sender QLineEdit object
        searchFilter = self.sender().text()
        # If the search filter is empty, show all items in self.itemsList
        if searchFilter == "":
            for item in self.itemsList:
                item.setHidden(False)
        else:
            # ignore headers and top level treeWiget items (cannot be hidden)
            items_not_top_level = [item for item in self.itemsList 
                                   if isinstance(item, treewidget.TaurusLabelTreeItem)]
            
            # By default they are all set to hidden
            for i in items_not_top_level:
                i.setHidden(True)

            # For an item to be shown, its parents must be shown as well
            def recursive_unhide_parent(item):
                if isinstance(item, treewidget.TaurusLabelTreeItem):
                    recursive_unhide_parent(item.parent())
                    item.setHidden(False)
            
            # If an item is shown, their childs should be shown as well, 
            # Since they would not match the filter, they are explicitly 
            # set to hidden(False)
            def recursive_unhide_childs(item):
                c_count = item.childCount()
                for i in range(0, c_count):
                    recursive_unhide_childs(item.child(i))
                item.setHidden(False)

            for item in items_not_top_level:
                if searchFilter in item.name:
                    recursive_unhide_parent(item.parent())
                    c_count = item.childCount()
                    for i in range(0, c_count):
                        recursive_unhide_childs(item.child(i))
                    item.setHidden(False)


    def panelElementsCreation(self):
        # Create a QFrame object and a grid layout
        panel = QFrame()
        self.panelElementsGridLayout = QGridLayout()
        panel.setLayout(self.panelElementsGridLayout)

        # Create a TreeWidget object for displaying elements
        self.elementsWidget = treewidget.TreeWidget(
            correctTypes=["Motor", "PseudoMotor", "MeasurementGroup",
                          "ZeroDExpChannel", "TwoDExpChannel",
                          "CTExpChannel", "OneDExpChannel", "Controller",
                          "TriggerGate", "IORegister"],
            fourthColumn="Attribute",
            door_name=self.door_name, onlyReserved=not self.generate_all)
        self.panelElementsGridLayout.addWidget(self.elementsWidget, 1, 0, 1, 2)

        # Get the list of items in the TreeWidget object
        self.itemsList = self.elementsWidget.items

        # Get the list of names of elements in the TreeWidget object
        self.nameList = self.elementsWidget.nameList

        # Create a search bar
        searchBar = self.createSearchBar()
        self.panelElementsGridLayout.addWidget(searchBar, 0, 0, 1, 1)


        # Return the panel
        return panel

    # Refresh the elements in use
    def refresh(self):
        self.elementsWidget.hide()
        splitter = QSplitter(Qt.Qt.Vertical)
        self.panelElementsGridLayout.addWidget(splitter, 1, 0, 1, 2)
        self.elementsWidget = treewidget.TreeWidget(
            correctTypes=["Motor", "PseudoMotor", "MeasurementGroup",
                          "ZeroDExpChannel", "TwoDExpChannel",
                          "CTExpChannel", "OneDExpChannel", "Controller",
                          "TriggerGate", "IORegister"],
            fourthColumn="Attribute",
            door_name=self.door_name, onlyReserved=not self.generate_all)
        splitter.addWidget(self.elementsWidget)
        self.elementsWidget.show()


@click.command("expstatus")
@click.argument("door_name", required=False)
@click.option("-a", "--all/--no-all", required=False, help='Show all elements or only the ones currently being used.')
def expstatus_cmd(door_name, all):
    """Experiment status widget GUI.

    Provides a view of elements reserved by a running macro, allowing to stop them
    if they are stuck.
    """

    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(sys.argv,
                            app_name="expstatus",
                            app_version=sardana.__version__,
                            org_name="sardana",
                            org_domain="sardana-controls.org"
                            )
    if door_name is None:
        from sardana.taurus.qt.qtgui.extra_macroexecutor import \
            TaurusMacroConfigurationDialog
        dialog = TaurusMacroConfigurationDialog()
        accept = dialog.exec_()
        if accept:
            door_name = str(dialog.doorComboBox.currentText())
        else:
            sys.exit()
    expstatus = ExpStatus(door_arg=door_name, generate_all_arg=all)
    expstatus.show()
    sys.exit(app.exec_())


def main():
    expstatus_cmd()


if __name__ == "__main__":
    main()
