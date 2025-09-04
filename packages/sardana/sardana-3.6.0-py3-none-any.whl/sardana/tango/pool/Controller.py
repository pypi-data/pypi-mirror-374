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

""" """

__all__ = ["Controller", "ControllerClass"]

__docformat__ = 'restructuredtext'

import time

from PyTango import Util, DevFailed, Except
from PyTango import DevVoid, DevLong, DevString
from PyTango import DevVarStringArray, DevVarLongArray
from PyTango import DispLevel, DevState, AttrQuality
from PyTango import SCALAR, SPECTRUM
from PyTango import READ_WRITE, READ

from taurus.core.util.log import DebugIt
from taurus.core.util.containers import CaselessDict

from sardana import sardanacustomsettings
from sardana import DataType, DataFormat
from sardana import State, SardanaServer
from sardana.sardanaattribute import SardanaAttribute
from sardana.sardanautils import (
    interleaved_list_to_dict,
    interleave_two_lists
)
from sardana.tango.core.util import to_tango_attr_info

from .PoolDevice import PoolDevice, PoolDeviceClass


def to_bool(s):
    return s.lower() == "true"


class Controller(PoolDevice):

    def __init__(self, dclass, name):
        self._use_physical_roles_property = getattr(
            sardanacustomsettings, "USE_PHYSICAL_ROLES_PROPERTY", True
        )
        PoolDevice.__init__(self, dclass, name)

    def init(self, name):
        PoolDevice.init(self, name)

    def get_ctrl(self):
        return self.element

    def set_ctrl(self, ctrl):
        self.element = ctrl

    ctrl = property(get_ctrl, set_ctrl)

    @DebugIt()
    def delete_device(self):
        PoolDevice.delete_device(self)
        ctrl = self.ctrl
        if ctrl is not None:
            ctrl.remove_listener(self.on_controller_changed)
        self.ctrl = None

    @DebugIt()
    def init_device(self):
        PoolDevice.init_device(self)

        detect_evts = "state", "status"
        non_detect_evts = "elementlist",
        self.set_change_events(detect_evts, non_detect_evts)

        if not self.pool.use_numeric_element_ids:
            db = self.get_database()
            if len(db.get_device_property(self.get_name(), "id")["id"]) > 0:
                self.warning(
                    "Forcing sardanacustomsettings.USE_NUMERIC_ELEMENT_IDS=True "
                    "because numeric element ids are still configured in Tango DB.")
                self.pool.use_numeric_element_ids = True

        id_ = self.get_id()
        try:
            self.ctrl = ctrl = self.pool.get_element_by_id(id_)
        except KeyError:
            role_ids = self.get_role_ids()
            full_name = self.get_full_name()
            name = self.alias or full_name
            args = dict(type=self.Type, name=name, full_name=full_name,
                        library=self.Library, klass=self.Klass,
                        id = id_, role_ids=role_ids,
                        properties=self._get_ctrl_properties())
            ctrl = self.pool.create_controller(**args)
            self.ctrl = ctrl
            self.set_state(DevState.ON)
            # self.set_state(to_tango_state(ctrl.get_state()))
            # self.set_status(ctrl.get_status())
        else:
            # TODO: consider adding `_properties` either as 
            #  a `PoolController` property or a `re_init()` argument
            ctrl._properties = self._get_ctrl_properties()
            ctrl.re_init()
        ctrl.add_listener(self.on_controller_changed)
    
    def initialize_attribute_values(self):
        """Initialize attribute values."""
        memorized_values = self.get_memorized_values()
        self.ctrl.init_attribute_values(memorized_values)
    
    def _migrate_role_property(self, db, old_property_name, old_property_value):
        physical_roles = interleave_two_lists(
                self._get_ctrl_roles(), old_property_value
        )
        db.put_device_property(self.get_name(), {'physical_roles': physical_roles})
        db.delete_device_property(self.get_name(), old_property_name)
    
    def _get_role_ids_using_old_properties(self, db):
        property_name = None
        role_ids = db.get_device_property(self.get_name(), ['motor_role_ids'])[
            'motor_role_ids']
        if len(role_ids) == 0:
            role_ids = db.get_device_property(self.get_name(), ['counter_role_ids'])[
                'counter_role_ids']
            if len(role_ids) == 0:
                role_ids = self.Role_ids
                if len(role_ids) > 0:
                    property_name = 'Role_ids'
            else:
                property_name = 'counter_role_ids'
        else:
            property_name = 'motor_role_ids'
        return role_ids, property_name

    def get_role_ids(self):
        db = Util.instance().get_database()
        if db is None:
            return []
        
        if self._use_physical_roles_property:
            role_ids_prop = db.get_device_property(self.get_name(), ['physical_roles'])[
            'physical_roles']
            if len(role_ids_prop) == 0:
                role_ids, property_to_migrate = self._get_role_ids_using_old_properties(db)
                if property_to_migrate is not None:                
                    self._migrate_role_property(db, property_to_migrate, role_ids)
            else:
                role_ids_map = interleaved_list_to_dict(role_ids_prop)
                role_ids = []
                for role in self._get_ctrl_roles():
                    role_ids.append(role_ids_map[role])
        else:
            role_ids, _ = self._get_role_ids_using_old_properties(db)
        
        if self.pool.use_numeric_element_ids:
            role_ids = list(map(int, role_ids))
        
        return role_ids
    
    def _get_ctrl_roles(self):
        ctrl_info = self.pool.get_controller_class_info(self.Klass)
        try:
            return ctrl_info.motor_roles
        except AttributeError:
            return ctrl_info.counter_roles

    def _get_ctrl_properties(self):
        try:
            ctrl_info = self.pool.get_controller_class_info(self.Klass)
            prop_infos = ctrl_info.ctrl_properties
        except:
            return {}
        db = Util.instance().get_database()

        if db is None:
            return {}

        props = {}
        if prop_infos:
            props.update(db.get_device_property(
                self.get_name(), list(prop_infos.keys())))
        for p in list(props.keys()):
            if len(props[p]) == 0:
                props[p] = None

        ret = {}
        missing_props = []
        for prop_name, prop_value in list(props.items()):
            if prop_value is None:
                dv = prop_infos[prop_name].default_value
                if dv is None:
                    missing_props.append(prop_name)
                ret[prop_name] = dv
                continue
            prop_info = prop_infos[prop_name]
            dtype, dformat = prop_info.dtype, prop_info.dformat

            op = str
            if dtype == DataType.Integer:
                op = int
            elif dtype == DataType.Double:
                op = float
            elif dtype == DataType.Boolean:
                op = to_bool
            prop_value = list(map(op, prop_value))
            if dformat == DataFormat.Scalar:
                prop_value = prop_value[0]
            ret[prop_name] = prop_value

        if missing_props:
            self.set_state(DevState.ALARM)
            missing_props = ", ".join(missing_props)
            self.set_status("Controller has missing properties: %s"
                            % missing_props)

        return ret

    def always_executed_hook(self):
        pass

    def read_attr_hardware(self, data):
        pass

    def dev_state(self):
        if self.ctrl is None or not self.ctrl.is_online():
            return DevState.FAULT
        return DevState.ON

    def dev_status(self):
        if self.ctrl is None or not self.ctrl.is_online():
            self._status = self.ctrl.get_ctrl_error_str()
        else:
            self._status = PoolDevice.dev_status(self)
        return self._status

    def read_ElementList(self, attr):
        attr.set_value(self.get_element_names())

    def CreateElement(self, argin):
        pass

    def DeleteElement(self, argin):
        pass

    def get_element_names(self):
        elements = self.ctrl.get_elements()
        return [elements[id].get_name() for id in sorted(elements)]

    def on_controller_changed(self, event_src, event_type, event_value):
        # during server startup and shutdown avoid processing element
        # creation events
        if SardanaServer.server_state != State.Running:
            return
        timestamp = time.time()
        name = event_type.name.lower()
        multi_attr = self.get_device_attr()
        try:
            attr = multi_attr.get_attr_by_name(name)
        except DevFailed:
            return
        quality = AttrQuality.ATTR_VALID
        priority = event_type.priority
        error = None

        if name == "state":
            event_value = self.calculate_tango_state(event_value)
        elif name == "status":
            event_value = self.calculate_tango_status(event_value)
        else:
            if isinstance(event_value, SardanaAttribute):
                if event_value.error:
                    error = Except.to_dev_failed(*event_value.exc_info)
                timestamp = event_value.timestamp
                event_value = event_value.value
        self.set_attribute(attr, value=event_value, timestamp=timestamp,
                           quality=quality, priority=priority, error=error,
                           synch=False)

    def get_dynamic_attributes(self):
        if hasattr(self, "_dynamic_attributes_cache"):
            return self._standard_attributes_cache, self._dynamic_attributes_cache
        info = self.ctrl.ctrl_info
        if info is None:
            self.warning(
                "Controller %s doesn't have any information", self.ctrl)
            return PoolDevice.get_dynamic_attributes(self)
        self._dynamic_attributes_cache = dyn_attrs = CaselessDict()
        self._standard_attributes_cache = std_attrs = CaselessDict()
        for attr_data in list(info.ctrl_attributes.values()):
            attr_name = attr_data.name
            name, tg_info = to_tango_attr_info(attr_name, attr_data)
            dyn_attrs[attr_name] = attr_name, tg_info, attr_data
        return std_attrs, dyn_attrs

    def read_DynamicAttribute(self, attr):
        attr_name = attr.get_name()
        attr.set_value(self.ctrl.get_ctrl_attr(attr_name))

    def write_DynamicAttribute(self, attr):
        v = attr.get_write_value()
        attr_name = attr.get_name()
        self.ctrl.set_ctrl_attr(attr_name, v)

    def read_LogLevel(self, attr):
        l = self.ctrl.get_log_level()
        self.debug(l)
        attr.set_value(l)

    def write_LogLevel(self, attr):
        self.ctrl.set_log_level(attr.get_write_value())


class ControllerClass(PoolDeviceClass):

    #    Class Properties
    class_property_list = {
    }
    class_property_list.update(PoolDeviceClass.class_property_list)

    #    Device Properties
    device_property_list = {
        'Type':           [DevString, "", None],
        'Library':        [DevString, "", None],
        'Klass':          [DevString, "", None],
        'Role_ids':       [DevVarLongArray, "", []],
    }
    device_property_list.update(PoolDeviceClass.device_property_list)

    #    Command definitions
    cmd_list = {
        'CreateElement': [[DevVarStringArray, ""], [DevVoid, ""]],
        'DeleteElement': [[DevString, ""], [DevVoid, ""]],
    }
    cmd_list.update(PoolDeviceClass.cmd_list)

    #    Attribute definitions
    attr_list = {
        'ElementList':   [[DevString, SPECTRUM, READ, 4096]],
        'LogLevel':      [[DevLong, SCALAR, READ_WRITE],
                          {'Memorized': "true_without_hard_applied",
                           'label': "Log level",
                           'Display level': DispLevel.EXPERT}],
    }
    attr_list.update(PoolDeviceClass.attr_list)

    def _get_class_properties(self):
        ret = PoolDeviceClass._get_class_properties(self)
        ret['Description'] = "Controller device class"
        ret['InheritedFrom'].insert(0, 'PoolDevice')
        return ret
