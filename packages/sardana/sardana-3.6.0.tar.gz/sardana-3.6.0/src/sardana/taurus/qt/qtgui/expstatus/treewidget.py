# -*- coding: utf-8 -*-
import logging
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

import taurus
from tango import DevFailed
from taurus.core import TaurusException
from taurus.external.qt import QtGui
from taurus.external.qt.QtWidgets import QTreeWidget, QTreeWidgetItem, QFrame, \
    QGridLayout, QPushButton
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.display import TaurusLabel

from sardana.taurus.core.tango.sardana import registerExtensions
from sardana.taurus.qt.qtgui.expstatus.responsivetauruslabel import ResponsiveTaurusLabel
from sardana.taurus.qt.qtgui.extra_macroexecutor import MacroButton


# Class used to operate with pseudomotors hierarchy.
class ExperimentStatusPseudomotor:
    def __init__(self, name, elements, parent, is_top=True):
        self.name = name
        self.elements = elements
        self.parent = parent
        self.isTop = is_top


registerExtensions()


# Custom QTreeWidgetItem with Widgets
class TaurusLabelTreeItem(QtGui.QTreeWidgetItem):
    def columnResized(self, column, oldSize, newSize):
        if newSize < self._minColumnWidth:
            self._treeWidget.setColumnWidth(column, self._minColumnWidth)
            return
        if column == 2:
            self.statusLabel.setFixedWidth(newSize)

        elif column == 3:
            self.valueLabel.setFixedWidth(newSize)

    def __init__(self, treeWidget, name, model, fourthColumn,
                 parent=None, door_name=None):
        '''
        treeWidget (QTreeWidget) : Item's QTreeWidget parent.
        name       (str)         : Item's name. just an example.
        '''

        # Initialize the super class (QtGui.QTreeWidgetItem)
        super(TaurusLabelTreeItem, self).__init__(parent)

        self._treeWidget = treeWidget
        self._minColumnWidth = 70
        self.name = name
        treeWidget.header().sectionResized.connect(self.columnResized)

        # Column 1 - Text:
        self.setText(0, name)
        self.device_treeItem = taurus.Device(model)

        # Column 2 - State
        self.stateLabel = TaurusLabel()
        self.stateLabel.setModel(model + "/state")
        self.stateLabel.setBgRole("rvalue")
        treeWidget.setItemWidget(self, 1, self.stateLabel)

        # Column 3 - Status
        self.statusLabel = ResponsiveTaurusLabel()
        self.statusLabel.setFixedWidth(treeWidget.columnWidth(2))
        self.statusLabel.setAutoTrim(True)
        self.statusLabel.setWordWrap(True)
        self.statusLabel.setModel(model + "/status")
        treeWidget.setItemWidget(self, 2, self.statusLabel)

        # Column 4 - Value
        self.valueLabel = ResponsiveTaurusLabel()
        if not fourthColumn == "Empty":
            self.valueLabel.setAutoTrim(True)
            self.valueLabel.setWordWrap(True)
            self.valueLabel.setModel(model + "/" + fourthColumn)
        treeWidget.setItemWidget(self, 3, self.valueLabel)

        # Column 5 - Panel buttons
        self.panelButtons = QFrame()
        panelButtonsLayout = QGridLayout()
        self.panelButtons.setLayout(panelButtonsLayout)
        buttonStop = QPushButton("STOP")
        buttonStop.setMaximumWidth(80)
        buttonStop.clicked.connect(self.stop)
        buttonAbort = QPushButton("ABORT")
        buttonAbort.setMaximumWidth(80)
        buttonAbort.clicked.connect(self.abort)
        buttonRelease = QPushButton("RELEASE")
        buttonRelease.setMaximumWidth(80)
        buttonRelease.clicked.connect(self.release)

        buttonReconfig = MacroButton()
        buttonReconfig.setModel(door_name)
        buttonReconfig.setMacroName("reconfig")
        buttonReconfig.setButtonText("RECONFIG")
        buttonReconfig.updateMacroArgument(0, name)
        buttonReconfig.setMinimumWidth(80)
        buttonReconfig.setMinimumHeight(60)
        buttonReconfig.statusUpdated.connect(self.stop_after_reconfig)

        panelButtonsLayout.addWidget(buttonStop, 0, 1, 1, 1)
        panelButtonsLayout.addWidget(buttonAbort, 1, 1, 1, 1)
        panelButtonsLayout.addWidget(buttonRelease, 0, 2, 2, 1)
        panelButtonsLayout.addWidget(buttonReconfig, 0, 0, 2, 1)
        self.panelButtons.setMaximumWidth(300)

        if fourthColumn:
            treeWidget.setItemWidget(self, 4, self.panelButtons)
        else:
            treeWidget.setItemWidget(self, 3, self.panelButtons)

    def stop(self):
        self.device_treeItem.stop(synch=False)

    def abort(self):
        self.device_treeItem.abort(synch=False)

    def release(self):
        self.device_treeItem.release()
    
    def stop_after_reconfig(self, value):
        # Recieves signar PyQtSignal from the macrobutton
        # We need to execute the Stop() command to force the refresh of the states
        # See https://www.tango-controls.org/community/forum/c/general/development/push-state-change-event-during-devrestart/?page=1#post-5227
        # for more details, and ideally remove it whenever Tango supports that.
        if value['state'] == 'finish':
            self.device_treeItem.stop(synch=False)


class TreeWidget(QTreeWidget):
    def __init__(self, correctTypes, fourthColumn=None, parent=None,
                 door_name=None, onlyReserved=False):
        QTreeWidget.__init__(self, parent=parent)
        self.nameList = []

        # Define the number of columns and their widths depending on whether
        # a fourth column is passed as an argument
        if fourthColumn:
            self.setColumnCount(5)
            self.setHeaderLabels(["Elements", "State", "Status",
                                  fourthColumn, "Actions"])
            self.setColumnWidth(0, 150)
            self.setColumnWidth(2, 150)
            self.setColumnWidth(3, 150)
        else:
            self.setColumnCount(4)
            self.setHeaderLabels(["Elements", "State", "Status", "Actions"])
            self.setColumnWidth(0, 150)
            self.setColumnWidth(2, 150)

        try:
            device_door = taurus.Device(door_name)
        except TaurusException as e:
            self.showErrorMessage(door_name, e)
        except DevFailed as e:
            self.showErrorMessage(door_name, e, custom_msg="Could not connect to: " + door_name)

        # TODO: instead of reading 'elements' from the macroserver, using Door.macro_server.
        # getElementsInfo() would make the code easier to read and understand, along with a
        # more simple data structure.
        try:
            device_macroserver = device_door.macro_server
        except AttributeError as e:
            self.showErrorMessage(door_name, e)
        elements = device_macroserver.read_attribute('Elements')
        import json
        data = elements.value[1]
        jess_dict = json.loads(data)

        # Create an empty dictionary and lists for pseudomotors and controllers
        data = {}
        pseudomotors = []
        controllers = []

        try:
            if onlyReserved:
                elements = device_door.getReservedElements()[0]["elements"]
        except IndexError as e:
            text = (
                "Unable to retrieve reserved elements.\n"
                "Probably no macro is running or the running macro is not reserving elements.\n"
                "Use 'Show macro elements' button check again or 'Show all elements' buttons to show all."
            )
            logging.debug(text)

            from taurus.external.qt.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(text)
            msg.setWindowTitle("Information")
            msg.exec_()

            elements = []

        # Loop over the "new" list in the jess_dict dictionary
        for dict in jess_dict["new"]:
            # If the element type is already in the data dictionary
            # and is one of the correct types
            if dict["type"] in data and dict["type"] in correctTypes:
                if not onlyReserved or (onlyReserved and dict["name"] in elements):
                    # If it's a MeasurementGroup, add it to the existing list
                    if dict["type"] == "MeasurementGroup":
                        mg = {}
                        mg[dict["name"]] = dict["elements"]
                        data[dict["type"]].append(mg)
                    # If it's a PseudoMotor, create a new
                    # ExperimentStatusPseudomotor object and add it to the list
                    elif dict["type"] == "PseudoMotor":
                        result = dict["elements"]
                        # Remove repeated elements from list
                        result = list(dict.fromkeys(result))
                        pm = ExperimentStatusPseudomotor(dict["name"], result,
                                                         dict["parent"])
                        pseudomotors.append(pm)
                        data[dict["type"]].append(pm)
                    # If it's a Controller, just add it to the controllers list
                    elif dict["type"] == "Controller":
                        controllers.append(dict)
                    # If it's any other type, just add the name to the list
                    else:
                        data[dict["type"]].append(dict["name"])
            # If the element type is one of the correct types but not in the
            # data dictionary yet
            elif dict["type"] in correctTypes:
                if not onlyReserved or (onlyReserved and dict["name"] in elements):
                    # If it's a MeasurementGroup, create a new list with it
                    if dict["type"] == "MeasurementGroup":
                        mg = {}
                        mg[dict["name"]] = dict["elements"]
                        data[dict["type"]] = [mg]
                    # If it's a PseudoMotor, create a new ExperimentStatusPseudomotor
                    # object and add it to the list
                    elif dict["type"] == "PseudoMotor":
                        result = dict["elements"]

                        # Remove repeated elements from list
                        result = list(dict.fromkeys(result))
                        pm = ExperimentStatusPseudomotor(dict["name"], result,
                                                         dict["parent"])
                        pseudomotors.append(pm)
                        data[dict["type"]] = [pm]
                    # If it's a Controller, just add it to the controllers list
                    elif dict["type"] == "Controller":
                        controllers.append(dict)
                    # If it's any other type, create a new list with the name in it
                    else:
                        data[dict["type"]] = [dict["name"]]

        # iterate over the controllers list
        # data["PseudoMotor"] = []
        for controller in controllers:
            # get the main type of the current controller
            mainType = controller["main_type"]
            # check if the main type is "PseudoMotor"
            if mainType == "PseudoMotor":
                # get the name and parent of the current controller
                name = controller["name"]
                # create an empty list to store the elements
                elements = []
                # iterate over the pseudomotors list
                for pm in pseudomotors:
                    # check if the parent of the current pseudomotor matches
                    # the name of the current controller
                    if pm.parent == name:
                        # add the pseudomotor to the list of elements
                        elements.append(pm)

        def propagatePseudomotors(pm, pseudomotors):
            for pseudo in pseudomotors:
                for i, el in enumerate(pseudo.elements):
                    if pm.name == el:
                        pseudo.elements[i] = pm

        # Propagate all pseudomotors
        for pm in pseudomotors:
            propagatePseudomotors(pm, pseudomotors)

        # Store each pseudomotor in a dictionary to access them faster
        # If using "Generate" there might be no PseudoMotor, just making sure.
        if "PseudoMotor" in data:
            pm_dict = {pm.name: pm for pm in data["PseudoMotor"]}

            # Recursively inspect all pseudomotors and its subpseudomotors
            # Identifying which of them have subpseudomotors.
            def pm_is_top(pm, level=0):
                if type(pm) is str:
                    return
                if level == 0:
                    for sub_pm in pm.elements:
                        pm_is_top(sub_pm, level + 1)
                else:
                    pm_dict[pm.name].isTop = False

            for pm in data["PseudoMotor"]:
                pm_is_top(pm, 0)

            # set only the top pseudomotors from which they will be exapanded
            # with its subpseudomotors
            data["PseudoMotor"] = [pm for pm in pm_dict.values() if pm.isTop]

        # create an empty list to store the items
        self.items = []
        # iterate over the sorted items in the data dictionary
        for key, values in sorted(data.items()):
            # create a QTreeWidgetItem with the key as the label
            item = QTreeWidgetItem([key])
            # iterate over the values
            for value in values:
                # try to create a new item depending on the key
                try:
                    # if the key is "MeasurementGroup", get the name of the
                    # device and create a TaurusLabelTreeItem with it
                    if key == "MeasurementGroup":
                        name = list(value.keys())[0]
                        child = TaurusLabelTreeItem(self, name, name, "Empty",
                                                    parent=item,
                                                    door_name=door_name)
                        # iterate over the elements in the value and create new
                        # TaurusLabelTreeItems for each one
                        for element in list(value.values())[0]:
                            second_level_child = TaurusLabelTreeItem(self, element,
                                                                     element, "Value",
                                                                     parent=child,
                                                                     door_name=door_name)
                            child.addChild(second_level_child)
                            self.nameList.append(element)
                            self.items.append(second_level_child)

                        # add the name of the device to the nameList and the new
                        # item to the items list
                        self.nameList.append(name)
                        # add the new item as a child of the current item
                        self.items.append(child)
                        item.addChild(child)

                    elif key == "PseudoMotor":
                        # Call the `createPseudomotorRow` function to create a row
                        # in the tree view for this pseudomotor.
                        self.createPseudomotorRow(value, item, door_name)

                    # If the key is not "PseudoMotor", create a row in the tree view for
                    # the corresponding value.
                    else:
                        # Depending on the key and fourthColumn values, create a different
                        # type of child for the item.
                        if fourthColumn == "Attribute":
                            fourthColumnValue = {
                                "Motor": 'Position',
                                "MeasurementGroup": 'Empty',
                                "CTExpChannel": 'Value',
                                "ZeroDExpChannel": 'Value',
                                "OneDExpChannel": 'Empty',
                                "TwoDExpChannel": 'Empty',
                                "PseudoMotor": 'Position',
                                "TriggerGate": 'Empty',
                                "IORegister": 'Empty'
                            }
                            child = TaurusLabelTreeItem(self, value, value, fourthColumnValue[key],
                                                        parent=item,
                                                        door_name=door_name)

                        else:
                            child = TaurusLabelTreeItem(self, value, value, fourthColumn,
                                                        parent=item,
                                                        door_name=door_name)

                        # Add the child to the item's children list.
                        self.nameList.append(value)
                        self.items.append(child)
                        item.addChild(child)
                except Exception as e:
                    # TODO: find out which type Exception and properly handle it. Currently it catches everything...
                    print(e)

            # Append the item to the list of items.
            self.items.append(item)

        self.insertTopLevelItems(0, self.items)

        for item in self.items:
            item.setExpanded(True)
        # self.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        # self.header().setStretchLastSection(False)

    def showErrorMessage(self, door_name, e, custom_msg=None):
        from taurus.external.qt.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        if type(e.args[0]) is str:
            msg.setText("Error: " + e.args[0])
        else:
            msg.setText("Error: " + e.args[0].desc)
        if custom_msg is not None:
            msg.setInformativeText(custom_msg)
        else:
            msg.setInformativeText('Ensure this Door "'
                                   + door_name + '" exists and try again.\n\n'
                                                 'A name is composed by 3 fields. The first field is named domain'
                                                 ', the second field is named family and the last field is named '
                                                 'member.\n\nExample: "door/demo/1" ')
        msg.setWindowTitle("Error")
        msg.exec_()
        sys.exit()

    # This method creates a pseudomotor row in the widget recursively
    def createPseudomotorRow(self, pseudomotor, parent, door):
        # if the pseudomotor has elements
        if type(pseudomotor) == ExperimentStatusPseudomotor:
            # we create a row for the pseudomotor and a row for each element
            treeItem = TaurusLabelTreeItem(self, pseudomotor.name, pseudomotor.name,
                                           "Position", parent=parent,
                                           door_name=door)
            self.nameList.append(pseudomotor.name)
            self.items.append(treeItem)
            parent.addChild(treeItem)
            for element in pseudomotor.elements:
                # recursive here
                if type(element) == ExperimentStatusPseudomotor:
                    self.createPseudomotorRow(element, treeItem, door)
                else:
                    elementTreeItem = TaurusLabelTreeItem(self, element, element,
                                                          "Position", parent=treeItem,
                                                          door_name=door)
                    self.nameList.append(element)
                    self.items.append(elementTreeItem)
                    parent.addChild(elementTreeItem)
        else:
            # the pseudomotor has no elements
            treeItem = TaurusLabelTreeItem(self, pseudomotor, pseudomotor, "Position",
                                           parent=parent,
                                           door_name=door)
            self.nameList.append(pseudomotor)
            self.items.append(treeItem)
            parent.addChild(treeItem)


if __name__ == "__main__":
    app = TaurusApplication()

    treeWidget = TreeWidget(
        correctTypes=["MeasurementGroup", "Motor", "PseudoMotor", "Controller",
                      "CTExpChannel", "ZeroDExpChannel", "OneDExpChannel",
                      "TwoDExpChannel", "TriggerGate", "IORegister"],
                      fourthColumn="Position")

    treeWidget.show()

    sys.exit(app.exec())
