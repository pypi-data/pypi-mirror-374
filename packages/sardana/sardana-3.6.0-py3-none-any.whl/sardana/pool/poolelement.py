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

"""This module is part of the Python Pool library. It defines the base classes
for"""

__all__ = ["PoolElement", "PoolElementFrontend"]

__docformat__ = 'restructuredtext'

import weakref
from typing import Optional, Dict, Any, Sequence

import sardana
from sardana.sardanaevent import EventType
from sardana.util.string import camel_to_snake
from sardana.pool.controller import (
    DefaultValue,
    Memorize,
    Memorized,
    MemorizedNoInit,
)
from sardana.pool.poolbaseelement import PoolBaseElement


class PoolElement(PoolBaseElement):
    """A Pool element is an Pool object which is controlled by a controller.
       Therefore it contains a _ctrl_id and a _axis (the id of the element in
       the controller)."""

    def __init__(self, **kwargs):
        ctrl = kwargs.pop('ctrl')
        self._ctrl = weakref.ref(ctrl)
        self._axis = kwargs.pop('axis')
        self._ctrl_id = ctrl.get_id()
        self._deleted = False
        try:
            instrument = kwargs.pop('instrument')
            self.set_instrument(instrument)
        except KeyError:
            self._instrument = None
        super(PoolElement, self).__init__(**kwargs)

    def serialize(self, *args, **kwargs):
        kwargs = PoolBaseElement.serialize(self, *args, **kwargs)
        kwargs['controller'] = self.controller.full_name
        kwargs['axis'] = self.axis
        kwargs['source'] = self.get_source()
        return kwargs

    def get_parent(self):
        return self.get_controller()

    def get_controller(self):
        if self._ctrl is None:
            return None
        return self._ctrl()

    def get_controller_id(self):
        return self._ctrl_id

    def get_axis(self):
        return self._axis

    def is_deleted(self):
        return self._deleted

    def set_deleted(self, deleted):
        self._deleted = deleted

    def set_action_cache(self, action_cache):
        self._action_cache = action_cache
        action_cache.add_element(self)

    def get_source(self):
        return "{0}/{1}".format(self.full_name, self.get_default_acquisition_channel())
    
    def _set_attribute_value(self, attr_name, value):
        is_extra_attr = attr_name in self.controller.ctrl.axis_attributes
        if is_extra_attr:
            self.set_extra_par(attr_name, value)
        else:
            prop_name = camel_to_snake(attr_name)
            setattr(self, prop_name, value)
    
    def init_attribute_values(self, attr_values: Optional[Dict[str, Any]] = None) -> None:
        """Initialize attributes with (default) values.
        
        Set values to attributes as passed in `attr_values`.
        In lack of attribute value apply default value.
        In lack of default value do nothing.

        :param attr_values: map of attribute names and values
        """
        super().init_attribute_values(attr_values)
        if attr_values is None:
            attr_values = {}
        attrs = self.controller.get_axis_attributes(self.axis)
        for attr_name, attr_def in attrs.items():
            value = None
            memorize = attr_def.get(Memorize, Memorized)
            if memorize == MemorizedNoInit:
                continue
            if memorize == Memorized:
                value = attr_values.get(attr_name)
            if value is None:
                value = attr_def.get(DefaultValue)
            if value is None:
                continue
            try:
                self._set_attribute_value(attr_name, value)
            except:
                self._failed_init_attrs.append(attr_name)
                self.debug(
                    "{} failed to init with {}".format(attr_name, value),
                    exc_info=True
                )

    # --------------------------------------------------------------------------
    # dependent elements
    # --------------------------------------------------------------------------

    def get_dependent_elements(self) -> Sequence[sardana.pool.poolbaseelement.PoolBaseElement]:
        """Get elements which depend on this element.
        
        Get elements e.g. pseudo elements or groups, which depend on this
        element.
        
        :return: dependent elements
        """
        dependent_elements = []
        for listener in self.get_listeners():
            try:
                elem = listener().__self__
            except AttributeError:
                continue
            if isinstance(elem, PoolBaseElement):
                dependent_elements.append(elem)
        
        return dependent_elements

    def has_dependent_elements(self):
        return len(self.get_dependent_elements()) > 0

    # --------------------------------------------------------------------------
    # instrument
    # --------------------------------------------------------------------------

    def get_instrument(self):
        if self._instrument is None:
            return None
        return self._instrument()

    def set_instrument(self, instrument, propagate=1):
        self._set_instrument(instrument, propagate=propagate)

    def _set_instrument(self, instrument, propagate=1):
        if self._instrument is not None:
            self._instrument().remove_element(self)
        new_instrument_name = ""
        if instrument is None:
            self._instrument = None
        else:
            self._instrument = weakref.ref(instrument)
            new_instrument_name = instrument.full_name
            instrument.add_element(self)
        if not propagate:
            return
        self.fire_event(EventType("instrument", priority=propagate),
                        new_instrument_name)

    # --------------------------------------------------------------------------
    # stop
    # --------------------------------------------------------------------------

    def stop(self):
        self.info("Stop!")
        PoolBaseElement.stop(self)
        self.controller.stop_element(self)

    # --------------------------------------------------------------------------
    # abort
    # --------------------------------------------------------------------------

    def abort(self):
        self.info("Abort!")
        PoolBaseElement.abort(self)
        self.controller.abort_element(self)

    def get_par(self, name):
        return self.controller.get_axis_par(self.axis, name)

    def set_par(self, name, value):
        return self.controller.set_axis_par(self.axis, name, value)

    def get_extra_par(self, name):
        return self.controller.get_axis_attr(self.axis, name)

    def set_extra_par(self, name, value):
        return self.controller.set_axis_attr(self.axis, name, value)

    axis = property(get_axis, doc="element axis")
    controller = property(get_controller, doc="element controller")
    controller_id = property(get_controller_id, doc="element controller id")
    instrument = property(get_instrument, set_instrument,
                          doc="element instrument")
    deleted = property(is_deleted, set_deleted,
                       doc="element is deleted from pool (experimental API)")
