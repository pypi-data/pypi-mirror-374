#!/usr/bin/env python

##############################################################################
##
# This file is part of Sardana
##
# http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
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


"""This module is part of the Python Pool library. It defines the classes
for the synchronization"""

__all__ = ["PoolSynchronization", "MultiSynchDescription", "SynchDescription", "TGChannel"]

import copy
import time
import threading
from functools import partial
from typing import Any, List, Union, Dict, Tuple

import sardana
from taurus.core.util.codecs import CodecFactory
from taurus.core.util.log import DebugIt
from sardana import State
from sardana.sardanathreadpool import get_thread_pool
from sardana.pool.pooldefs import SynchDomain, SynchParam
from sardana.pool.poolaction import ActionContext, PoolActionItem, PoolAction
from sardana.util.funcgenerator import FunctionGenerator
from sardana.pool.poolmotor import PoolMotor
from sardana.pool.poolpseudomotor import PoolPseudoMotor

# The purpose of this class was inspired on the CTAcquisition concept


class TGChannel(PoolActionItem):
    """An item involved in the trigger/gate generation.
    Maps directly to a trigger object

    .. note::
        The TGChannel class has been included in Sardana
        on a provisional basis. Backwards incompatible changes
        (up to and including removal of the module) may occur if
        deemed necessary by the core developers.
    """

    def __init__(self, trigger_gate, info=None):
        PoolActionItem.__init__(self, trigger_gate)
        if info:
            self.__dict__.update(info)

    def __getattr__(self, name):
        return getattr(self.element, name)


class SynchDescription(list):
    """Synchronization description. It is composed from groups - repetitions
    of equidistant synchronization events. Each group is described by
    :class:`~sardana.pool.pooldefs.SynchParam` parameters which may have
    values in :class:`~sardana.pool.pooldefs.SynchDomain` domains.
    """

    def __init__(self, *args, **kwargs):
        """Cast SynchParam and SynchDomain keys from strings to enums."""
        super().__init__()
        for group_str in list(*args, **kwargs):
            group = {}
            for param_str, conf_str in group_str.items():
                try:
                    param = SynchParam(int(param_str))
                except ValueError:
                    param = SynchParam.fromStr(param_str)
                if isinstance(conf_str, dict):
                    conf = {}
                    for domain_str, value in conf_str.items():
                        try:
                            domain = SynchDomain(int(domain_str))
                        except ValueError:
                            domain = SynchDomain.fromStr(domain_str)
                        conf[domain] = value
                else:
                    conf = conf_str
                group[param] = conf
            self.append(group)

    @property
    def repetitions(self):
        repetitions = 0
        for group in self:
            repetitions += group[SynchParam.Repeats]
        return repetitions
    
    @property
    def delay_time(self):
        return self._get_param(SynchParam.Delay)

    @property
    def active_time(self):
        return self._get_param(SynchParam.Active)

    @property
    def total_time(self):
        return self._get_param(SynchParam.Total)

    @property
    def passive_time(self):
        return self.total_time - self.active_time
    
    @property
    def integration_time(self):
        integration_time = self.active_time
        if isinstance(integration_time, float):
            return integration_time
        elif len(integration_time) == 0:
            raise Exception("The synchronization description group has not "
                            "been initialized")
        elif len(integration_time) > 1:
            raise Exception("There are more than one synchronization "
                            "description groups")
        else:
            raise Exception("Synchronization description wrong format")

    def _get_param(self, param: sardana.pool.pooldefs.SynchDomain, domain: Any = SynchDomain.Time) -> Union[float, List[float]]:
        """
        Extract parameter from synchronization description and its groups. If
        there is only one group in the synchronization description then
        returns float with the value. Otherwise a list of floats with
        different values.

        :param param: parameter type
        :param domain: domain
        :return: parameter value(s)
        :rtype float or [float]
        """

        if len(self) == 1:
            return self[0][param][domain]

        values = []
        for group in self:
            value = group[param][domain]
            repeats = group[SynchParam.Repeats]
            values += [value] * repeats
        return values
    
    def to_dial(self, sign: int, offset: float) -> "SynchDescription":
        """Convert position domain group parameters to dial position
        
        Maintain time domain group parameters (if present) as they are.

        Formula is: pos = sign * dial + offset.

        :param sign: sign (1 or -1) to apply in the formula
        :param offset: offset to apply in the formula
        :return: new synchronization description in dial position
        """
        synch = copy.deepcopy(self)
        for group in synch:
            try:
                pos = group[SynchParam.Initial][SynchDomain.Position]
            except KeyError:
                pass
            else:
                group[SynchParam.Initial][SynchDomain.Position] = (pos - offset) / sign
            for param in (SynchParam.Delay,
                          SynchParam.Active,
                          SynchParam.Total):
                try:
                    disp = group[param][SynchDomain.Position]
                except KeyError:
                    continue
                group[param][SynchDomain.Position] = disp / sign
        return synch


class MultiSynchDescription(dict):
    """Multiple synchronization descriptions. It is formed from pairs of
    :class:`~sardana.pool.controller.Synchronizer` names and 
    :class:`~sardana.pool.poolsynchronization.SynchDescription` objects. 
    A dictionary must be provided where keys are the synchronizer names as strings 
    and values are either a 
    :class:`~sardana.pool.poolsynchronization.SynchDescription` object 
    or the equivalent :class:`List`.

    To assign a description to software synchronized elements, use the key `"software"`.
    """

    def __init__(self, *args, **kwargs):
        # Initialize the dictionary with converted values
        super().__init__()
        self.update(*args, **kwargs)
        self._check_all_values_same()

    def _check_all_values_same(self):
        # Check if all values in the dictionary are the same
        values = list(self.values())
        if values and all(v == values[0] for v in values):
            self.integration_time = values[0].integration_time
            self.passive_time = values[0].passive_time
            self.total_time = values[0].total_time
            self.active_time = values[0].active_time
            self.delay_time = values[0].delay_time
            self.repetitions = values[0].repetitions

    def __setitem__(self, key, value):
        super().__setitem__(key, SynchDescription(value))

    def update(self, *args, **kwargs):
        """Cast dictionary values to 
        :class:`~sardana.pool.poolsynchronization.SynchDescription` objects.
        """
        # Convert all values to strings during update
        for k, v in dict(*args, **kwargs).items():
            self[k] = SynchDescription(v)

    @staticmethod
    def from_json(synch_description_json: str) -> "MultiSynchDescription":
        """JSON decode multi synchronization description data structure and 
        return :class:`~sardana.pool.poolsynchronization.MultiSynchDescription`.

        :param synch_description_json: json-like multiple synchronization description
        :return: new multi synchronization description

        .. todo:: At some point remove the backwards compatibility
          for memorized values created with Python 2. In Python 2 IntEnum was
          serialized to "<class>.<attr>" e.g. "SynchDomain.Time" and we were
          using a class method `fromStr` to interpret the enumeration objects.
        """
        synch_description_dict = CodecFactory().decode(('json', synch_description_json))        
        return MultiSynchDescription(synch_description_dict)


class PoolSynchronization(PoolAction):
    """Synchronization action.

    It coordinates trigger/gate elements and software synchronizer.

    .. todo: Think of moving the ready/busy mechanism to PoolAction
    """

    def __init__(self, main_element, name="Synchronization"):
        PoolAction.__init__(self, main_element, name)
        # Even if rest of Sardana is using "." in logger names use "-" as
        # sepator. This is in order to avoid confusion about the logger
        # hierary - by default python logging use "." to indicate loggers'
        # hirarchy in case parent-children relation is established between the
        # loggers.
        # TODO: review if it is possible in Sardana to use a common separator.
        soft_synch_name = main_element.name + "-SoftSynch"
        self._synch_soft = FunctionGenerator(name=soft_synch_name)
        self._listener = None
        self._ready = threading.Event()
        self._ready.set()

    def _is_ready(self):
        return self._ready.is_set()

    def _wait(self, timeout=None):
        return self._ready.wait(timeout)

    def _set_ready(self, _=None):
        self._ready.set()

    def _is_busy(self):
        return not self._ready.is_set()

    def _set_busy(self):
        self._ready.clear()

    def add_listener(self, listener):
        self._listener = listener

    def start_action(self, ctrls: List, multi_synch_description: MultiSynchDescription, 
                     moveable: Union[PoolMotor, PoolPseudoMotor, None] = None,
                     software_synchronizer_initial_domain: Any = None,
                     *args: Any, **kwargs: Any) -> None:
        """Start synchronization action.

        :param ctrls: list of enabled trigger/gate controllers
        :param multi_synch_description: synchronization description 
          for each synchronizer.
        :param moveable: (optional) moveable object used as the
         synchronization source in the Position domain
         :class:`~sardana.pool.poolpseudomotor.PoolPseudoMotor`
        :param software_synchronizer_initial_domain: (optional) -
         initial domain for software synchronizer, can be either
         :obj:`~sardana.pool.pooldefs.SynchDomain.Time` or
         :obj:`~sardana.pool.pooldefs.SynchDomain.Position`
        """

        def pre_synch_one(pool_ctrl, axis, synch_description):
            ret = pool_ctrl.ctrl.PreSynchOne(axis, synch_description)
            if not ret:
                msg = ("%s.PreSynchOne(%d) returns False" %
                    (ctrl.name, axis))
                raise Exception(msg)

        with ActionContext(self):
            # loads synchronization description
            for ctrl in ctrls:
                pool_ctrl = ctrl.element
                pool_ctrl.ctrl.PreSynchAll()
                dial_synch_description = None
                for channel in ctrl.get_channels(enabled=True):
                    synch_description = multi_synch_description[channel.name]
                    axis = channel.axis
                    # for backwards compatibility only translates to dial position
                    # when one use "moveable on input" feature
                    if (moveable is not None 
                            and channel.moveable_on_input is not None):
                        if dial_synch_description is None:
                            dial_synch_description = synch_description.to_dial(
                                sign=moveable.sign.value,
                                offset=moveable.offset.value
                            )
                        pre_synch_one(pool_ctrl, axis, dial_synch_description)
                        pool_ctrl.ctrl.SynchOne(axis, dial_synch_description)
                    else:
                        pre_synch_one(pool_ctrl, axis, synch_description)
                        pool_ctrl.ctrl.SynchOne(axis, synch_description)
                pool_ctrl.ctrl.SynchAll()

            # attaching listener (usually acquisition action)
            # to the software trigger gate generator
            if self._listener is not None:
                # Get software synchronization
                synch_description = multi_synch_description["software"]
                if software_synchronizer_initial_domain is not None:
                    self._synch_soft.initial_domain = software_synchronizer_initial_domain
                self._synch_soft.set_configuration(synch_description)
                self._synch_soft.add_listener(self._listener)
                remove_acq_listener = partial(self._synch_soft.remove_listener,
                                              self._listener)
                self.add_finish_hook(remove_acq_listener, False)
                self._synch_soft.add_listener(
                    self.main_element.on_element_changed)
                remove_mg_listener = partial(self._synch_soft.remove_listener,
                                             self.main_element)
                self.add_finish_hook(remove_mg_listener, False)
            # subscribing to the position change events to generate events
            # in position domain
            if moveable is not None:
                position = moveable.get_position_attribute()
                position.add_listener(self._synch_soft)
                remove_pos_listener = partial(position.remove_listener,
                                              self._synch_soft)
                self.add_finish_hook(remove_pos_listener, False)

            # start software synchronizer
            if self._listener is not None:
                self._synch_soft.start()
                get_thread_pool().add(self._synch_soft.run)

            # PreStartAll on all controllers
            for ctrl in ctrls:
                pool_ctrl = ctrl.element
                pool_ctrl.ctrl.PreStartAll()

            # PreStartOne & StartOne on all elements
            for ctrl in ctrls:
                pool_ctrl = ctrl.element
                for channel in ctrl.get_channels(enabled=True):
                    axis = channel.axis
                    ret = pool_ctrl.ctrl.PreStartOne(axis)
                    if not ret:
                        raise Exception("%s.PreStartOne(%d) returns False"
                                        % (pool_ctrl.name, axis))
                    pool_ctrl.ctrl.StartOne(axis)

            # set the state of all elements to inform their listeners
            self._channels = []
            for ctrl in ctrls:
                for channel in ctrl.get_channels(enabled=True):
                    channel.set_state(State.Moving, propagate=2)
                    self._channels.append(channel)

            # StartAll on all controllers
            for ctrl in ctrls:
                pool_ctrl = ctrl.element
                pool_ctrl.ctrl.StartAll()

    def is_triggering(self, states: Dict[sardana.pool.poolelement.PoolElement, Tuple[Tuple[int, str], str]]) -> bool:
        """Determines if we are synchronizing or not based on the states
        returned by the controller(s) and the software synchronizer.

        :param states: a map containing state information as returned by
                       read_state_info: ((state, status), exception_error)
        :return: returns True if is triggering or False otherwise
        """
        for elem in states:
            state_info_idx = 0
            state_idx = 0
            state_tggate = states[elem][state_info_idx][state_idx]
            if self._is_in_action(state_tggate):
                return True
        return False

    @DebugIt()
    def action_loop(self):
        """action_loop method
        """
        states = {}
        for channel in self._channels:
            element = channel.element
            states[element] = None

        # Triggering loop
        # TODO: make nap configurable (see motion or acquisition loops)
        nap = 0.01
        while True:
            self.read_state_info(ret=states)
            if not self.is_triggering(states):
                break
            time.sleep(nap)

        # Set element states after ending the triggering
        for element, state_info in list(states.items()):
            with element:
                element.clear_operation()
                state_info = element._from_ctrl_state_info(state_info)
                element.set_state_info(state_info, propagate=2)

        # wait for software synchronizer to finish
        if self._listener is not None:
            while True:
                if not self._synch_soft.is_started():
                    break
                time.sleep(0.01)
