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

__all__ = ["PoolMeasurementGroup", "MeasurementConfiguration",
           "ControllerConfiguration", "ChannelConfiguration",
           "SynchronizerConfiguration", "build_measurement_configuration"]

__docformat__ = 'restructuredtext'

import threading
import weakref
from typing import Any, Optional, Dict, Union, List

from taurus.core.tango.tangovalidator import TangoAttributeNameValidator

import sardana
from sardana import State, ElementType, TYPE_EXP_CHANNEL_ELEMENTS
from sardana.sardanaevent import EventType
from sardana.pool.pooldefs import AcqMode, SynchParam, AcqSynch, \
    SynchDomain, AcqSynchType

from sardana.util.string import camel_to_snake
from sardana.pool.poolgroupelement import PoolGroupElement
from sardana.pool.poolacquisition import PoolAcquisition
from sardana.pool.poolsynchronization import SynchDescription, MultiSynchDescription
from sardana.pool.poolexternal import PoolExternalObject
from sardana.pool.poolcontroller import PoolController

from sardana.taurus.core.tango.sardana import PlotType, Normalization


# ----------------------------------------------
# Measurement Group Configuration information
# ----------------------------------------------
# dict <str, obj> with (at least) keys:
#    - 'controllers' : dict<Controller, dict> where:
#        - key: ctrl
#        - value: dict<str, dict> with (at least) keys:
#                - 'timer' : the timer channel name / timer channel id
#                - 'monitor' : the monitor channel name / monitor channel id
#                - 'synchronization' : 'Gate'/'Software'
#                - 'channels' where value is a dict<str, obj> with (at least)
#                   keys:
#                    - 'id' : the channel name ( channel id )
#                    optional keys:
#                    - 'enabled' : True/False (default is True)
#                    any hints:
#                    - 'output' : True/False (default is True)
#                    - 'plot_type' : 'No'/'1D'/'2D' (default is 'No')
#                    - 'plot_axes' : list<str> 'where str is channel
#                                    name/'step#/'index#' (default is [])
#                    - 'label' : prefered label (default is channel name)
#                    - 'scale' : <float, float> with min/max (defaults to
#                                channel range if it is defined
#                    - 'plot_color' : int representing RGB
#    optional keys:
#    - 'label' : measurement group label (defaults to measurement group name)
#    - 'description' : measurement group description

# <MeasurementGroupConfiguration>
#  <timer>UxTimer</timer>
#  <monitor>CT1</monitor>
# </MeasurementGroupConfiguration>

# Example: 2 NI cards, where channel 1 of card 1 is wired to channel 1 of
# card 2 at configuration time we should set:

# ni0ctrl.setCtrlPar(0, 'synchronization', AcqSynch.SoftwareTrigger)
# ni0ctrl.setCtrlPar(0, 'timer', 1) # channel 1 is the timer
# ni0ctrl.setCtrlPar(0, 'monitor', 4) # channel 4 is the monitor
# ni1ctrl.setCtrlPar(0, 'synchronization', AcqSynch.HardwareTrigger)
# ni1ctrl.setCtrlPar(0, 'master', 0)

# when we count for 1.5 seconds:
# ni1ctrl.Load(1.5)
# ni0ctrl.Load(1.5)
# ni1ctrl.Start()
# ni0ctrl.Start()

"""

"""


def _to_fqdn(name, logger=None):
    full_name = name
    # try to use Taurus 4 to retrieve FQDN
    try:
        from taurus.core.tango.tangovalidator import TangoDeviceNameValidator
        full_name, _, _ = TangoDeviceNameValidator().getNames(name)
    # if Taurus3 in use just continue
    except ImportError:
        pass
    if full_name is None:
        full_name = name
    if full_name != name and logger:
        msg = ("PQDN full name is deprecated in favor of FQDN full name."
               " Re-apply configuration in order to upgrade.")
        logger.warning(msg)
    return full_name

def _get_ctrl_synchronizer(ctrl: "TimerableControllerConfiguration") -> str:
    if ctrl.synchronizer == "software":
        return ctrl.synchronizer
    return ctrl.synchronizer.name

def _filter_ctrls(ctrls: Union[List["TimerableControllerConfiguration"],
                               List["ControllerConfiguration"]],
                  enabled: Optional[bool] = None,
                  synchronizer: Optional[str] = None
                  ) -> Union[List["TimerableControllerConfiguration"],
                             List["ControllerConfiguration"]]:
    if enabled is None and synchronizer is None:
        return ctrls

    filtered_ctrls = []
    for ctrl in ctrls:
        conditions = True
        if enabled is not None:
            conditions = conditions and ctrl.enabled == enabled
        if synchronizer is not None:
            conditions = conditions and _get_ctrl_synchronizer(ctrl) == synchronizer
        if conditions:
            filtered_ctrls.append(ctrl)
    return filtered_ctrls


def _get_timerable_ctrls(
        ctrls: Dict[AcqSynch, List["TimerableControllerConfiguration"]],
        acq_synch: Optional[Union[AcqSynch, List[AcqSynch]]] = None,
        enabled: Optional[bool] = None,
        synchronizer: Optional[str] = None
        ) -> List["TimerableControllerConfiguration"]:
    timerable_ctrls = []
    if acq_synch is None:
        for ctrls in list(ctrls.values()):
            timerable_ctrls += ctrls
    elif isinstance(acq_synch, list):
        acq_synch_list = acq_synch
        for acq_synch in acq_synch_list:
            timerable_ctrls += ctrls[acq_synch]
    else:
        timerable_ctrls = list(ctrls[acq_synch])

    return _filter_ctrls(timerable_ctrls, enabled, synchronizer)


def _get_timerable_channels(ctrls, acq_synch=None, enabled=None):
    timerable_ctrls = _get_timerable_ctrls(ctrls, acq_synch, enabled)
    timerable_channels = []
    for ctrl in timerable_ctrls:
        timerable_channels.extend(ctrl.get_channels(enabled))
    return timerable_channels


class ConfigurationItem(object):
    """Container of configuration attributes related to a given element.

    Wrap an element to pretend its API.
    Manage the element's configuration.
    Hold an information whether the element is enabled.
    By default it is enabled.

    .. note::
        The ConfigurationItem class has been included in Sardana
        on a provisional basis. Backwards incompatible changes
        (up to and including removal of the class) may occur if
        deemed necessary by the core developers.
    """

    def __init__(self, element: Any, attrs: Optional[Dict] = None) -> None:
        """Construct a wrapper around the element

        :param element: element to wrap
        :param: attrs: configuration attributes and their values
        """
        self._element = weakref.ref(element)
        self.enabled = True

        if attrs is not None:
            self.__dict__.update(attrs)

    def __getattr__(self, item):
        return getattr(self.element, item)

    def get_element(self):
        """Returns the element associated with this item"""
        return self._element()

    def set_element(self, element):
        """Sets the element for this item"""
        self._element = weakref.ref(element)

    element = property(get_element)


class ControllerConfiguration(ConfigurationItem):
    """Container of configuration attributes related to a given controller.

    Inherit behavior from
    :class:`~sardana.pool.poolmeasurementgroup.ConfigurationItem`
    and additionally hold information about its enabled/disabled channels.
    By default it is disabled.

    .. note::
        The ControllerConfiguration class has been included in Sardana
        on a provisional basis. Backwards incompatible changes
        (up to and including removal of the class) may occur if
        deemed necessary by the core developers.
    """

    def __init__(self, element, attrs=None):
        ConfigurationItem.__init__(self, element, attrs)
        self.enabled = False
        self._channels = []
        self._channels_enabled = []
        self._channels_disabled = []

    def add_channel(self, channel_item):
        """Aggregate a channel configuration item."""
        self._channels.append(channel_item)
        if channel_item.enabled:
            self.enabled = True
            if self._channels_enabled is None:
                self._channels_enabled = []
            self._channels_enabled.append(channel_item)
        else:
            if self._channels_disabled is None:
                self._channels_disabled = []
            self._channels_disabled.append(channel_item)

    def remove_channel(self, channel_item):
        """Remove a channel configuration item."""
        self._channels.remove(channel_item)
        if channel_item.enabled:
            self._channels_enabled.remove(channel_item)
            if len(self._channels_enabled) == 0:
                self.enabled = False
        else:
            self._channels_disabled.remove(channel_item)

    def update_state(self):
        """Update internal state based on the aggregated channels."""
        self.enabled = False
        self._channels_enabled = []
        self._channels_disabled = []
        for channel_item in self._channels:
            if channel_item.enabled:
                self.enabled = True
                self._channels_enabled.append(channel_item)
            else:
                self._channels_disabled.append(channel_item)

    def get_channels(self, enabled: Optional[bool] = None) -> List[Any]:
        """Return aggregated channels.

        :param enabled: which channels to return
         - True - only enabled
         - False - only disabled
         - None - all

        """
        if enabled is None:
            return list(self._channels)
        elif enabled:
            return list(self._channels_enabled)
        else:
            return list(self._channels_disabled)

    def validate(self):
        pass


class TimerableControllerConfiguration(ControllerConfiguration):
    """Container of configuration attributes related to a given
    timerable controller.

    Inherit behavior from
    :class:`~sardana.pool.poolmeasurementgroup.ControllerConfiguration`
    and additionally validate *timer* and *monitor* configuration.

    .. note::
        The TimerableControllerConfiguration class has been included in
        Sardana on a provisional basis. Backwards incompatible changes
        (up to and including removal of the class) may occur if
        deemed necessary by the core developers.
    """

    def update_timer(self):
        self._update_master("timer")

    def update_monitor(self):
        self._update_master("monitor")

    def _update_master(self, role):
        master = getattr(self, role, None)
        if master is None:
            idx = float("+inf")
            for channel in self._channels_enabled:
                if channel.index > idx:
                    continue
                master = channel
                idx = channel.index
        else:
            found = False
            for channel in self._channels:
                if channel.full_name == master:
                    master = channel
                    found = True
                    break
            if not found:
                master = None
        setattr(self, role, master)

    def validate(self):
        # validate if the timer and monitor are disabled if the
        # controller is enabled
        if self.enabled \
                and not self.timer.enabled \
                and not self.monitor.enabled:
            err_msg = 'channel {0} used as timer and channel ' \
                      '{1} used as monitor are disabled. One of them ' \
                      'must be enabled.'.format(self.timer.name,
                                                self.monitor.name)
            raise ValueError(err_msg)


class ExternalControllerConfiguration(ControllerConfiguration):
    """Container of configuration attributes related to a given
    external controller.

    Inherit behavior from
    :class:`~sardana.pool.poolmeasurementgroup.ControllerConfiguration`.

    .. note::
        The ExternalControllerConfiguration class has been included in
        Sardana on a provisional basis. Backwards incompatible changes
        (up to and including removal of the class) may occur if
        deemed necessary by the core developers.
    """

    def __init__(self, element, attrs=None):
        ControllerConfiguration.__init__(self, self, attrs)
        self.full_name = element


class ChannelConfiguration(ConfigurationItem):
    """Container of configuration attributes related to a given
    experimental channel.

    Inherit behavior from
    :class:`~sardana.pool.poolmeasurementgroup.ConfigurationItem`.

    .. note::
        The ChannelConfiguration class has been included in
        Sardana on a provisional basis. Backwards incompatible changes
        (up to and including removal of the class) may occur if
        deemed necessary by the core developers.
    """


class SynchronizerConfiguration(ConfigurationItem):
    """Container of configuration attributes related to a given
    synchronizer element.

    Inherit behavior from
    :class:`~sardana.pool.poolmeasurementgroup.ConfigurationItem`.
    By default it is disabled.

    .. note::
        The ChannelConfiguration class has been included in
        Sardana on a provisional basis. Backwards incompatible changes
        (up to and including removal of the class) may occur if
        deemed necessary by the core developers.
    """

    def __init__(self, element, attrs=None):
        ConfigurationItem.__init__(self, element, attrs)
        self.enabled = False


def build_measurement_configuration(user_elements):
    """Create a minimal measurement configuration data structure from the
    user_elements list.

    .. highlight:: none

    Minimal configuration data structure::

        dict <str, dict> with keys:
        - 'controllers' : where value is a dict<str, dict> where:
            - key: controller's full name
            - value: dict<str, dict> with keys:
                - 'channels' where value is a dict<str, obj> where:
                    - key: channel's full name
                    - value: dict<str, obj> with keys:
                        - 'index' : where value is the channel's index <int>

    .. highlight:: default

    .. note::
        The build_measurement_configuration function has been included in
        Sardana on a provisional basis. Backwards incompatible changes
        (up to and including removal of the function) may occur if
        deemed necessary by the core developers.
    """
    user_config = {}
    external_user_elements = []
    user_config["controllers"] = controllers = {}

    for index, element in enumerate(user_elements):
        elem_type = element.get_type()
        if elem_type == ElementType.External:
            external_user_elements.append((index, element))
            continue
        if elem_type == ElementType.TriggerGate:
            continue

        ctrl = element.controller
        ctrl_data = controllers.get(ctrl.full_name)

        if ctrl_data is None:
            controllers[ctrl.full_name] = ctrl_data = {}
            ctrl_data['channels'] = channels = {}
        else:
            channels = ctrl_data['channels']
        channels[element.full_name] = channel_data = {}
        channel_data['index'] = index

    if len(external_user_elements) > 0:
        controllers['__tango__'] = ctrl_data = {}
        ctrl_data['channels'] = channels = {}
        for index, element in external_user_elements:
            channels[element.full_name] = channel_data = {}
            channel_data['index'] = index
    return user_config


class MeasurementConfiguration(object):
    """Configuration of a measurement.

    Accepts import and export from/to a serializable data structure (based on
    dictionaries/lists and strings).
    Provides getter methods that facilitate extracting of information e.g.
    controllers of different types, master timers/monitors, etc.

    .. note::
        The build_measurement_configuration function has been included in
        Sardana on a provisional basis. Backwards incompatible changes
        (up to and including removal of the function) may occur if
        deemed necessary by the core developers.
    """

    DFT_DESC = 'General purpose measurement configuration'

    def __init__(self, parent=None):
        """Initialize measurement configuration object

        :param parent: (optional) object that this measurement configuration
        refers to (usually
         :class:`~sardana.pool.poolmeasurementgroup.PoolMeasurementGroup)`
        """
        self._parent = None
        if parent is not None:
            self._parent = weakref.proxy(parent)
        self._config = None
        # Structure to store the controllers and their channels
        self._timerable_ctrls = {}
        self._zerod_ctrls = []
        self._synch_ctrls = {}
        self._other_ctrls = []
        self._master_timer_sw = None
        self._master_monitor_sw = None
        self._master_timer_sw_start = None
        self._master_monitor_sw_start = None
        self._label = None
        self._description = None
        self._user_config = {}
        self._channel_acq_synch = {}
        self._ctrl_acq_synch = {}
        self.changed = False
        # provide back. compatibility for value_ref_{enabled,pattern}
        # config parameters created with Sardana < 3.
        self._value_ref_compat = False
        # provide back. compatibility for synchronizer, timer and monitor
        # config parameters set on external channels created with Sardana < 3.
        self._external_ctrl_compat = False

    def get_acq_synch_by_channel(self, channel: Union["sardana.pool.PoolBaseChannel", ChannelConfiguration]) -> sardana.pool.pooldefs.AcqSynch:
        """Return acquisition synchronization configured for this element.

        :param channel: channel to look for its acquisition synchronization
         or :class:`~sardana.pool.poolmeasurementgroup.ChannelConfiguration`
        :return: acquisition synchronization
        """
        if isinstance(channel, ChannelConfiguration):
            channel = channel.element
        return self._channel_acq_synch[channel]

    def get_acq_synch_by_controller(self, controller: Union[PoolController, ControllerConfiguration]) -> sardana.pool.pooldefs.AcqSynch:
        """Return acquisition synchronization configured for this controller.

        :param controller: controller to look for its acquisition
         synchronization
         or :class:`~sardana.pool.poolmeasurementgroup.ControllerConfiguration`
        :return: acquisition synchronization
        """
        if isinstance(controller, ConfigurationItem):
            controller = controller.element
        return self._ctrl_acq_synch[controller]

    def get_timerable_ctrls(self, acq_synch: Optional[sardana.pool.pooldefs.AcqSynch] = None, enabled: Optional[bool] = None, synchronizer: Optional[str] = None) -> List[ControllerConfiguration]:
        # noqa
        """Return timerable controllers.

        Allow to filter controllers based on acquisition synchronization or
        whether these are enabled/disabled.

        :param acq_synch: (optional) filter controller based on acquisition
         synchronization
        :param enabled: (optional) filter controllers whether these are
         enabled/disabled:

         - :obj:`True` - enabled only
         - :obj:`False` - disabled only
         - :obj:`None` - all

        :param synchronizer: (optional) filter controllers that their synchronizer
         name matches this parameter

        :return: timerable controllers that fulfils the filtering criteria
        """
        return _get_timerable_ctrls(self._timerable_ctrls, acq_synch, enabled, synchronizer)

    def get_timerable_channels(self, acq_synch: Optional[sardana.pool.pooldefs.AcqSynch] = None, enabled: Optional[bool] = None) -> List[ChannelConfiguration]:
        # noqa
        """Return timerable channels.

        Allow to filter channels based on acquisition synchronization or
        whether these are enabled/disabled.

        :param acq_synch: (optional) filter controller based on acquisition
         synchronization
        :param enabled: (optional) filter controllers whether these are
         enabled/disabled:

         - :obj:`True` - enabled only
         - :obj:`False` - disabled only
         - :obj:`None` - all

        :return: timerable channels that fulfils the filtering criteria
        """
        return _get_timerable_channels(self._timerable_ctrls, acq_synch,
                                       enabled)

    def get_zerod_ctrls(self, enabled: Optional[bool] = None) -> List[ControllerConfiguration]:
        # noqa
        """Return 0D controllers.

        Allow to filter controllers whether these are enabled/disabled.

        :param enabled: (optional) filter controllers whether these are
         enabled/disabled:

         - :obj:`True` - enabled only
         - :obj:`False` - disabled only
         - :obj:`None` - all

        :return: 0D controllers that fulfils the filtering criteria
        """
        return _filter_ctrls(self._zerod_ctrls, enabled)

    def get_synch_ctrls(self, enabled: Optional[bool] = None) -> List[ControllerConfiguration]:
        # noqa
        """Return synchronizer (currently only trigger/gate) controllers.

        Allow to filter controllers whether these are enabled/disabled.

        :param enabled: (optional) filter controllers whether these are
         enabled/disabled:

         - :obj:`True` - enabled only
         - :obj:`False` - disabled only
         - :obj:`None` - all

        :return: synchronizer controllers that fulfils the filtering criteria
        """
        return _filter_ctrls(self._synch_ctrls, enabled)

    def get_synchs(self, enabled: Optional[bool] = None) -> List[SynchronizerConfiguration]:
        # noqa
        """Return synchronizers (currently only trigger/gate).

        Allow to filter synchronizers whether these are enabled/disabled.

        :param enabled: (optional) filter synchronizers whether these are
         enabled/disabled:

         - :obj:`True` - enabled only
         - :obj:`False` - disabled only
         - :obj:`None` - all

        :return: synchronizers that fulfils the filtering criteria
        """
        synchs = []
        synch_ctrls = self.get_synch_ctrls(enabled)
        for ctrl in synch_ctrls:
            synchs.extend(ctrl.get_channels(enabled))
        return synchs

    def get_master_timer_software(self) -> ChannelConfiguration:
        # noqa
        """Return master timer in software acquisition.

        :return: master timer in software acquisition
        """
        return self._master_timer_sw

    def get_master_monitor_software(self) -> ChannelConfiguration:
        # noqa
        """Return master monitor in software acquisition.

        :return: master monitor in software acquisition
        """
        return self._master_monitor_sw

    def get_master_timer_software_start(self) -> ChannelConfiguration:
        # noqa
        """Return master timer in software start acquisition.

        :return: master timer in software start acquisition
        """
        return self._master_monitor_sw_start

    def get_master_monitor_software_start(self) -> ChannelConfiguration:
        # noqa
        """Return master monitor in software start acquisition.

        :return: master monitor in software start acquisition
        """
        return self._master_timer_sw_start

    def get_configuration_for_user(self):
        """Return measurement configuration serializable data structure."""
        return self._user_config

    def set_configuration_from_user(self, cfg):
        """Set measurement configuration from serializable data structure.

        Setting of the configuration includes the validation process. Setting
        of invalid configuration raises an exception and leaves the object
        as it was before the setting process. Thanks to that it is not
        necessary that the client application does the validation.

        The configuration parameters for given channels/controllers may differ
        depending on their types e.g. 0D channel does not support timer
        parameter while C/T does.

        .. todo::
            Raise exceptions when setting _Synchronization_ parameter for
            external channels, 0D and PSeudoCounters.
        """
        if not self._parent._is_online(cfg):
            self._parent.error("Some controllers of this measurement group are offline!")
            # Return because it won't be possible to know the controller types.
            # Before returning, assign "user configuration" to at least be able to
            # read it from the client (spock etc.).
            self._user_config = cfg
            return

        pool = self._parent.pool

        label = cfg.get('label', self._parent.name)
        description = cfg.get('description', self.DFT_DESC)

        timerable_ctrls = {AcqSynch.HardwareGate: [],
                           AcqSynch.HardwareStart: [],
                           AcqSynch.HardwareTrigger: [],
                           AcqSynch.SoftwareStart: [],
                           AcqSynch.SoftwareTrigger: [],
                           AcqSynch.SoftwareGate: []}
        zerod_ctrls = []
        synch_ctrls = []
        other_ctrls = []
        master_timer_sw = None
        master_monitor_sw = None
        master_timer_sw_start = None
        master_monitor_sw_start = None
        master_timer_idx_sw = float("+inf")
        master_monitor_idx_sw = float("+inf")
        master_timer_idx_sw_start = float("+inf")
        master_monitor_idx_sw_start = float("+inf")
        user_elem_ids = {}
        channel_acq_synch = {}
        ctrl_acq_synch = {}
        user_config = {}

        user_config['controllers'] = {}
        user_config['label'] = label
        user_config['description'] = description

        for ctrl_name, ctrl_data in list(cfg['controllers'].items()):
            # backwards compatibility for measurement groups created before
            # implementing feature-372:
            # https://sourceforge.net/p/sardana/tickets/372/
            # WARNING: this is one direction backwards compatibility - it just
            # reads channels from the units, but does not write channels to the
            # units back
            if 'units' in ctrl_data:
                ctrl_data = ctrl_data['units']['0']
            # discard controllers which don't have items (garbage)
            ch_count = len(ctrl_data['channels'])
            if ch_count == 0:
                continue

            external = ctrl_name in ['__tango__']

            if external:
                ctrl = ctrl_name
            else:
                ctrl = pool.get_element_by_full_name(ctrl_name)
                assert ctrl.get_type() == ElementType.Controller

            user_config['controllers'][ctrl_name] = user_config_ctrl = {}
            ctrl_conf = {}
            conf_synch = None

            # The external controllers should not have synchronizer

            if external:
                for parameter in ['synchronizer', 'timer', 'monitor']:
                    if parameter in ctrl_data:
                        if self._external_ctrl_compat:
                            msg = (
                                '{} is deprecated for external controllers '
                                'e.g. Tango, since 3.0.3. Re-apply configuration '
                                'in order to upgrade.'
                            ).format(parameter)
                            self._parent.warning(msg)
                        else:
                            raise ValueError(
                                'External controller does not allow '
                                'to have {}'.format(parameter))
            else:
                synchronizer = ctrl_data.get('synchronizer', 'software')
                if synchronizer is None or synchronizer == 'software':
                    ctrl_conf['synchronizer'] = 'software'
                    user_config_ctrl['synchronizer'] = 'software'
                else:
                    user_config_ctrl['synchronizer'] = synchronizer
                    pool_synch = pool.get_element_by_full_name(synchronizer)
                    pool_synch_ctrl = pool_synch.controller
                    conf_synch_ctrl = None
                    conf_synch = None
                    for conf_ctrl_created in synch_ctrls:
                        if pool_synch_ctrl == conf_ctrl_created.element:
                            conf_synch_ctrl = conf_ctrl_created
                            for conf_synch_created in \
                                    conf_ctrl_created.get_channels():
                                if pool_synch == conf_synch_created.element:
                                    conf_synch = conf_synch_created
                                    break
                            break

                    if conf_synch_ctrl is None:
                        conf_synch_ctrl = \
                            ControllerConfiguration(pool_synch_ctrl)
                        synch_ctrls.append(conf_synch_ctrl)

                    if conf_synch is None:
                        conf_synch = SynchronizerConfiguration(pool_synch)
                        conf_synch_ctrl.add_channel(conf_synch)

                    ctrl_conf['synchronizer'] = conf_synch
                try:
                    synchronization = ctrl_data['synchronization']
                except KeyError:
                    synchronization = AcqSynchType.Trigger
                ctrl_conf['synchronization'] = synchronization
                user_config_ctrl['synchronization'] = synchronization

            acq_synch = None
            if external:
                ctrl_item = ExternalControllerConfiguration(ctrl)
            elif ctrl.is_timerable():
                is_software = synchronizer == 'software'
                acq_synch = AcqSynch.from_synch_type(is_software,
                                                     synchronization)
                ctrl_acq_synch[ctrl] = acq_synch
                timer = ctrl_data.get("timer")
                ctrl_conf["timer"] = timer
                monitor = ctrl_data.get("monitor")
                ctrl_conf["monitor"] = monitor
                ctrl_item = TimerableControllerConfiguration(ctrl, ctrl_conf)
            else:
                ctrl_item = ControllerConfiguration(ctrl, ctrl_conf)

            ctrl_enabled = False
            if 'channels' in ctrl_data:
                user_config_ctrl['channels'] = user_config_channel = {}
            for ch_name, ch_data in list(ctrl_data['channels'].items()):
                if external:
                    validator = TangoAttributeNameValidator()
                    full_name = ch_data.get('full_name', ch_name)
                    params = validator.getUriGroups(full_name)
                    params['pool'] = pool
                    channel = PoolExternalObject(**params)
                else:
                    try:
                        channel = pool.get_element_by_full_name(ch_name)
                    except KeyError:
                        if not ch_data['enabled']:
                            user_config_channel[ch_name] = ch_data            
                            continue
                        raise ValueError(
                            '{} is not defined'.format(ch_data['name']))

                ch_data = self._fill_channel_data(channel, ch_data)
                user_config_channel[ch_name] = ch_data
                ch_item = ChannelConfiguration(channel, ch_data)
                ch_item.controller = ctrl_item
                ctrl_item.add_channel(ch_item)
                if ch_item.enabled:
                    if external:
                        id_ = channel.full_name
                    else:
                        id_ = channel.id
                    user_elem_ids[ch_item.index] = id_

                if ch_item.enabled:
                    ctrl_enabled = True

                if acq_synch is not None:
                    channel_acq_synch[channel] = acq_synch

            if not external and ctrl.is_timerable():
                ctrl_item.update_timer()
                ctrl_item.update_monitor()

                msg_error = ''
                if ctrl_item.timer is None:
                    timer_name = ctrl_data['timer']
                    ch_timer = pool.get_element_by_full_name(timer_name)
                    msg_error += 'Channel {0} is not present but used as ' \
                                 'timer. '.format(ch_timer.name)
                if ctrl_item.monitor is None:
                    monitor_name = ctrl_data['monitor']
                    ch_monitor = pool.get_element_by_full_name(monitor_name)
                    msg_error += 'Channel {0} is not present but used as ' \
                                 'monitor.'.format(ch_monitor.name)
                if len(msg_error) > 0:
                    raise ValueError(msg_error)

                if ctrl_item.enabled:
                    user_config_ctrl['timer'] = ctrl_item.timer.full_name
                    user_config_ctrl['monitor'] = ctrl_item.monitor.full_name
                else:                    
                    user_config_ctrl['timer'] = ctrl_data['timer']
                    user_config_ctrl['monitor'] = ctrl_data['monitor']

            # Update synchronizer state
            if ctrl_enabled and conf_synch is not None:
                conf_synch.enabled = True

            ctrl_item.validate()

            if external:
                other_ctrls.append(ctrl_item)
            elif ctrl.is_timerable():
                timerable_ctrls[acq_synch].append(ctrl_item)
                # Find master timer/monitor the system take the channel with
                # less index

                if not ctrl_item.enabled:
                    # Skip controllers disabled
                    pass
                elif acq_synch in (AcqSynch.SoftwareTrigger,
                                   AcqSynch.SoftwareGate):
                    if ctrl_item.timer.index < master_timer_idx_sw:
                        master_timer_sw = ctrl_item.timer
                        master_timer_idx_sw = ctrl_item.timer.index
                    if ctrl_item.monitor.index < master_monitor_idx_sw:
                        master_monitor_sw = ctrl_item.monitor
                        master_monitor_idx_sw = ctrl_item.monitor.index
                elif acq_synch == AcqSynch.SoftwareStart:
                    if ctrl_item.timer.index < master_timer_idx_sw_start:
                        master_timer_sw_start = ctrl_item.timer
                        master_timer_idx_sw_start = ctrl_item.timer.index
                    if ctrl_item.monitor.index < master_monitor_idx_sw_start:
                        master_monitor_sw_start = ctrl_item.monitor
                        master_monitor_idx_sw_start = ctrl_item.monitor.index
            elif ctrl.get_ctrl_types()[0] == ElementType.ZeroDExpChannel:
                zerod_ctrls.append(ctrl_item)

        # Update synchronizer controller states
        for conf_synch_ctrl in synch_ctrls:
            conf_synch_ctrl.update_state()

        mnt_grp_timer = cfg.get('timer')
        if mnt_grp_timer is not None:
            msg = ("global timer is deprecated since release 3.3.3 "
                   "Re-apply configuration in order to upgrade.")
            self._parent.warning(msg)

        mnt_grp_monitor = cfg.get('monitor')
        if mnt_grp_monitor is not None:
            msg = ("global monitor is deprecated since release 3.3.3 "
                   "Re-apply configuration in order to upgrade.")
            self._parent.warning(msg)

        # Update internals values
        self._label = label
        self._description = description
        self._timerable_ctrls = timerable_ctrls
        self._zerod_ctrls = zerod_ctrls
        self._synch_ctrls = synch_ctrls
        self._other_ctrls = other_ctrls
        self._master_timer_sw = master_timer_sw
        self._master_monitor_sw = master_monitor_sw
        self._master_timer_sw_start = master_timer_sw_start
        self._master_monitor_sw_start = master_monitor_sw_start
        self._user_config = user_config
        self._channel_acq_synch = channel_acq_synch
        self._ctrl_acq_synch = ctrl_acq_synch

        # sorted ids may not be consecutive (if a channel is disabled)
        indexes = sorted(user_elem_ids.keys())
        user_elem_ids_list = [user_elem_ids[idx] for idx in indexes]
        for conf_synch_ctrl in synch_ctrls:
            for conf_synch in conf_synch_ctrl.get_channels(enabled=True):
                user_elem_ids_list.append(conf_synch.id)
        self._parent.set_user_element_ids(user_elem_ids_list)
        # force assignment of user elements to the measurement group
        # in order to update the list of dependent elements (listeners)
        # of the element e.g. to prevent undefinition of an element added
        # to the measurement group.
        self._parent.get_user_elements()
        self.changed = True

    def _fill_channel_data(self, channel, channel_data):
        """Fill channel default values for the given channel dictionary"""
        name = channel.name
        ctype = channel.get_type()
        full_name = channel.full_name
        # choose ndim
        ndim = None
        if ctype == ElementType.CTExpChannel:
            ndim = 0
        elif ctype == ElementType.PseudoCounter:
            ndim = 0
        elif ctype == ElementType.ZeroDExpChannel:
            ndim = 0
        elif ctype == ElementType.OneDExpChannel:
            ndim = 1
        elif ctype == ElementType.TwoDExpChannel:
            ndim = 2
        elif ctype == ElementType.External:
            config = channel.get_config()
            if config is not None:
                ndim = int(config.data_format)
        elif ctype == ElementType.IORegister:
            ndim = 0

        if ctype != ElementType.External and channel.is_referable():
            value_ref_enabled = channel_data.get('value_ref_enabled', False)
            channel_data['value_ref_enabled'] = value_ref_enabled
            value_ref_pattern = channel_data.get('value_ref_pattern', '')
            channel_data['value_ref_pattern'] = value_ref_pattern
        elif 'value_ref_enabled' in channel_data or 'value_ref_pattern' in \
                channel_data:
            if self._value_ref_compat:
                msg = 'value_ref_pattern/value_ref_enabled is deprecated ' \
                      'for non-referable channels since 3.0.3. Re-apply ' \
                      'configuration in order to upgrade.'
                self._parent.warning(msg)
                channel_data.pop('value_ref_enabled', None)
                channel_data.pop('value_ref_pattern', None)
            else:
                msg = ('The channel {} is not referable. You can not set '
                       'the enabled and/or the pattern parameters.').format(
                        name)
                raise ValueError(msg)
        # Definitively should be initialized by measurement group
        # index MUST be here already (asserting this in the following line)
        channel_data['index'] = channel_data['index']
        channel_data['name'] = channel_data.get('name', name)
        channel_data['full_name'] = channel_data.get('full_name', full_name)
        channel_data['source'] = channel.get_source()
        channel_data['enabled'] = channel_data.get('enabled', True)
        channel_data['label'] = channel_data.get('label', channel_data['name'])
        channel_data['ndim'] = ndim
        # Probably should be initialized by measurement group
        channel_data['output'] = channel_data.get('output', True)

        # Perhaps should NOT be initialized by measurement group
        channel_data['plot_type'] = channel_data.get('plot_type', PlotType.No)
        channel_data['plot_axes'] = channel_data.get('plot_axes', [])
        channel_data['conditioning'] = channel_data.get('conditioning', '')
        channel_data['normalization'] = channel_data.get('normalization',
                                                         Normalization.No)
        # TODO: think of filling other keys: data_type, data_units, nexus_path
        #  here instead of feeling them on the Taurus extension level

        if ctype != ElementType.External:
            ctrl_name = channel.controller.full_name
            channel_data['_controller_name'] = channel_data.get(
                '_controller_name', ctrl_name)
        return channel_data


class PoolMeasurementGroup(PoolGroupElement):

    def __init__(self, **kwargs):
        self._state_lock = threading.Lock()
        self._monitor_count = None
        self._nb_starts = 1
        self._pending_starts = 0
        self._acquisition_mode = AcqMode.Timer
        self._config = MeasurementConfiguration(self)
        self._moveable = None
        self._moveable_obj = None
        # by default software synchronizer initial domain is set to Position
        self._software_synchronizer_initial_domain = SynchDomain.Position

        self._synch_description = MultiSynchDescription()

        kwargs['elem_type'] = ElementType.MeasurementGroup
        PoolGroupElement.__init__(self, **kwargs)
        configuration = kwargs.get("configuration")
        if configuration is None:
            user_elements = self.get_user_elements()
            configuration = build_measurement_configuration(user_elements)
        self.set_configuration_from_user(configuration)
    
    def init_attribute_values(self, attr_values: Optional[Dict[str, Any]] = None) -> None:
        """Initialize attributes with values.
        
        Set values to attributes as passed in `attr_values`.
        In lack of attribute value do nothing.

        :param attr_values: map of attribute names and values
        """
        super().init_attribute_values(attr_values)
        if attr_values is None:
            attr_values = {}
        attr_name = "Configuration"
        configuration = attr_values.pop(attr_name, None)
        if configuration is not None:
            self._config._value_ref_compat = True
            self._config._external_ctrl_compat = True
            try:
                self._config.set_configuration_from_user(configuration)
            except:
                self._failed_init_attrs.append(attr_name)
                self.debug(
                    "{} failed to init with {}".format(attr_name, configuration),
                    exc_info=True
                )
            finally:
                self._config._value_ref_compat = False
                self._config._external_ctrl_compat = False
        attrs = [
            "AcquisitionMode",
            "SoftwareSynchronizerInitialDomain",
            "Moveable"
        ]
        for attr_name in attrs:
            value = attr_values.pop(attr_name, None)
            if value is not None:
                prop_name = camel_to_snake(attr_name)
                try:
                    setattr(self, prop_name, value)
                except:
                    self._failed_init_attrs.append(attr_name)
                    self.debug(
                        "{} failed to init with {}".format(attr_name, value),
                        exc_info=True
                    )

    def _create_action_cache(self):
        acq_name = "%s.Acquisition" % self._name
        return PoolAcquisition(self, acq_name)

    def _calculate_states(self, state_info=None):
        state, status = PoolGroupElement._calculate_states(self, state_info)
        # check if software synchronizer is occupied
        synch_soft = self.acquisition._synch._synch_soft
        acq_sw = self.acquisition._sw_acq
        acq_sw_start = self.acquisition._sw_start_acq
        acq_0d = self.acquisition._0d_acq
        if (state in (State.On, State.Unknown)
            and (synch_soft.is_started()
                 or acq_sw._is_started()
                 or acq_sw_start._is_started()
                 or acq_0d._is_started())):
            state = State.Moving
            status += "\nSoftware synchronization is in progress"
        return state, status

    def on_element_changed(self, evt_src, evt_type, evt_value):
        name = evt_type.name
        if name == 'state':
            with self._state_lock:
                state, status = self._calculate_states()
                self.set_state(state, propagate=2)
                self.set_status(status)

    def get_pool_controllers(self):
        return self.get_acquisition().get_pool_controllers()

    def get_pool_controller_by_name(self, name):
        name = name.lower()
        for ctrl in self.get_pool_controllers():
            if ctrl.name.lower() == name or ctrl.full_name.lower() == name:
                return ctrl

    def add_user_element(self, element, index=None):
        '''Override the base behavior, so the TriggerGate elements are silently
        skipped if used multiple times in the group'''
        user_elements = self._user_elements
        if element in user_elements:
            # skipping TriggerGate element if already present
            if element.get_type() is ElementType.TriggerGate:
                return
        return PoolGroupElement.add_user_element(self, element, index)

    def rename_element(self, old_name: str, new_name: str, propagate: int = 1) -> None:
        """Rename element in the controller.

        :param old_name: old name of the element
        :param new_name: new name of the element
        :param propagate: 0 for not propagating, 1 to propagate,
               2 propagate with priority
        """
        self._config['label'] = new_name
        self.fire_event(EventType("configuration", priority=propagate),
                        self._config)

    # -------------------------------------------------------------------------
    # configuration
    # -------------------------------------------------------------------------

    def _is_internal_element(self, element_id):
        if self.pool.use_numeric_element_ids:
            return isinstance(element_id, int)
        try:
            # at this time all internal physical and pseudo elements
            # should be already created
            self.pool.get_element(id=element_id)
        except:
            return False
        return True


    def _is_managed_element(self, element):
        element_type = element.get_type()
        return (element_type in TYPE_EXP_CHANNEL_ELEMENTS or
                element_type is ElementType.TriggerGate)

    @property
    def configuration(self):
        return self._config

    # TODO: Check if it needed
    def set_configuration(self, config=None, propagate=1):
        self._config.configuration = config
        if not propagate:
            return
        self.fire_event(EventType("configuration", priority=propagate),
                        config)

    def set_configuration_from_user(self, cfg, propagate=1):
        old_ctrls = self.get_pool_controllers()
        self._config.set_configuration_from_user(cfg)
        new_ctrls = self.get_pool_controllers()
        if set(old_ctrls) != set(new_ctrls):
            self.fire_event(EventType("latencytime", priority=1),
                            self.latency_time)
        if not propagate:
            return
        self.fire_event(EventType("configuration", priority=propagate),
                        self._config.get_configuration_for_user())

    def get_user_configuration(self):
        return self._config.get_configuration_for_user()

    # -------------------------------------------------------------------------
    # integration time
    # -------------------------------------------------------------------------

    def get_integration_time(self):
        return self._synch_description.integration_time

    def set_integration_time(self, integration_time, propagate=1):
        total_time = integration_time + self.latency_time
        synch = [{SynchParam.Delay: {SynchDomain.Time: 0},
                  SynchParam.Active: {SynchDomain.Time: integration_time},
                  SynchParam.Total: {SynchDomain.Time: total_time},
                  SynchParam.Repeats: 1}]
        self.set_synch_description(synch, propagate)

    integration_time = property(get_integration_time, set_integration_time,
                                doc="the current integration time")

    # -------------------------------------------------------------------------
    # monitor count
    # -------------------------------------------------------------------------

    def get_monitor_count(self):
        return self._monitor_count

    def set_monitor_count(self, monitor_count, propagate=1):
        self._monitor_count = monitor_count
        if not propagate:
            return
        self.fire_event(EventType("monitor_count", priority=propagate),
                        monitor_count)

    monitor_count = property(get_monitor_count, set_monitor_count,
                             doc="the current monitor count")

    # -------------------------------------------------------------------------
    # acquisition mode
    # -------------------------------------------------------------------------

    def get_acquisition_mode(self):
        return self._acquisition_mode

    def set_acquisition_mode(self, acquisition_mode, propagate=1):
        self._acquisition_mode = acquisition_mode
        if not propagate:
            return
        self.fire_event(EventType("acquisition_mode", priority=propagate),
                        acquisition_mode)

    acquisition_mode = property(get_acquisition_mode, set_acquisition_mode,
                                doc="the current acquisition mode")

    # -------------------------------------------------------------------------
    # synch_description
    # -------------------------------------------------------------------------

    def _create_multi_synch_description(
            self,
            synch_description: Union[List[Dict],
                                     Dict[str, List[Dict]],
                                     SynchDescription,
                                     MultiSynchDescription]
            ) -> MultiSynchDescription:
        if isinstance(synch_description, dict):
            return MultiSynchDescription(synch_description)
        if not isinstance(synch_description, list):
            msg = "synch_description must be either a \
            MultiSynchDescription object, a dictionary or a list"
            raise TypeError(msg)

        # Create a new multiple synchronization description from a single synch description:
        # It will be a dictionary with all synchronizers in the measurement group as keys
        # and the same synchronization description for each synchronizer.
        synch_axes = self.configuration.get_synchs()
        synch_axes_name = [synch_axis.name for synch_axis in synch_axes]
        if self.configuration.get_master_timer_software() or \
           self.configuration.get_master_timer_software_start() or \
           self.configuration.get_zerod_ctrls():
            synch_axes_name.append("software")

        multi_synch_description = {synchronizer : synch_description for synchronizer in synch_axes_name}

        return MultiSynchDescription(multi_synch_description)

    def get_synch_description(self) -> MultiSynchDescription:
        return self._synch_description

    def set_synch_description(self, 
                              description: Union[List[Dict], 
                                                 Dict[str, List[Dict]], 
                                                 SynchDescription, 
                                                 MultiSynchDescription], 
                              propagate: Optional[int] = 1) -> None:
        """Set the current :ref:`synchronization description <sardana-measurementgroup-api-synchdescription>`  
        of the measurement group.

        :param description: Can be a :class:`~sardana.pool.poolsynchronization.SynchDescription` or the
          equivalent :class:`List` to set the same acquisition pattern to all elements.
          Can be a :class:`~sardana.pool.poolsynchronization.MultiSynchDescription` or the 
          equivalent :class:`Dict` to set a synchronization at synchronizer level.
        """
        self._synch_description = self._create_multi_synch_description(description)
        if not propagate:
            return
        try:
            integration_time = self._synch_description.integration_time
        except:
            integration_time = None
        self.fire_event(EventType("integration_time", priority=propagate),
                        integration_time)
        self.fire_event(EventType("synch_description", priority=propagate),
                        self._synch_description)

    synch_description = property(get_synch_description, set_synch_description,
                                 doc="the current synchronization description")

    # -------------------------------------------------------------------------
    # moveable
    # -------------------------------------------------------------------------

    def get_moveable(self):
        return self._moveable

    def set_moveable(self, moveable, propagate=1, to_fqdn=True):
        self._moveable = moveable
        if self._moveable is None:
            self._moveable_obj = None
        else:
            if to_fqdn:
                moveable = _to_fqdn(moveable, logger=self)
            self._moveable_obj = self.pool.get_element_by_full_name(moveable)
        self.fire_event(EventType("moveable", priority=propagate),
                        moveable)

    moveable = property(get_moveable, set_moveable,
                        doc="moveable source used in synchronization "
                            "description")

    # -------------------------------------------------------------------------
    # latency time
    # -------------------------------------------------------------------------

    def get_latency_time(self):
        latency_time = 0
        pool_ctrls = self.get_pool_controllers()
        for pool_ctrl in pool_ctrls:
            if not pool_ctrl.is_timerable():
                continue
            candidate = pool_ctrl.get_ctrl_par("latency_time")
            if candidate > latency_time:
                latency_time = candidate
        return latency_time

    latency_time = property(get_latency_time,
                            doc="latency time between two consecutive "
                                "acquisitions")

    # -------------------------------------------------------------------------
    # software synchronizer initial domain
    # -------------------------------------------------------------------------

    def get_software_synchronizer_initial_domain(self):
        return self._software_synchronizer_initial_domain

    def set_software_synchronizer_initial_domain(self, domain):
        self._software_synchronizer_initial_domain = domain

    software_synchronizer_initial_domain = property(
        get_software_synchronizer_initial_domain,
        set_software_synchronizer_initial_domain,
        doc="software synchronizer initial domain (SynchDomain.Time "
            "or SynchDomain.Position)"
    )

    # -------------------------------------------------------------------------
    # number of starts
    # -------------------------------------------------------------------------

    def get_nb_starts(self):
        return self._nb_starts

    def set_nb_starts(self, nb_starts, propagate=1):
        self._nb_starts = nb_starts
        if not propagate:
            return
        self.fire_event(EventType("nb_starts", priority=propagate),
                        nb_starts)

    nb_starts = property(get_nb_starts, set_nb_starts,
                         doc="current number of starts")

    # -------------------------------------------------------------------------
    # acquisition
    # -------------------------------------------------------------------------

    def prepare(self):
        """Prepare for measurement.

        Delegate measurement preparation to the acquisition action.
        """
        if len(self.get_user_elements()) == 0:
            # All channels were disabled
            raise RuntimeError('All channels in measurement group '
                               'are disabled.')

        if self._acquisition_mode == AcqMode.Timer:
            role = 'timer'
        elif self._acquisition_mode == AcqMode.Monitor:
            role = 'monitor'
        else:
            raise RuntimeError('acquisition mode must be either Timer '
                               'or Monitor')

        for ctrl in self._config.get_timerable_ctrls(enabled=True):
            master = getattr(ctrl, role, None)
            if master is None:
                msg = ('controller {0} does not have {1} '
                       'configured.').format(ctrl.name, role)
                raise RuntimeError(msg)
            if not master.enabled:
                msg = 'channel {0} used as {1} must be enabled'.format(
                    master.name, role)
                raise RuntimeError(msg)

        value = self._get_value()
        self._pending_starts = self.nb_starts

        self.acquisition.prepare(self.configuration,
                                 self.acquisition_mode,
                                 value,
                                 self._synch_description,
                                 self._moveable_obj,
                                 self.software_synchronizer_initial_domain,
                                 self.nb_starts)

    def start_acquisition(self, value=None):
        """Start measurement.

        Delegate start measurement to the acquisition action.
        Provide backwards compatibility for starts without previous prepare.
        """
        if self._pending_starts == 0:
            msg = "prepare is mandatory before starting acquisition"
            raise RuntimeError(msg)
        self._stopped = False
        self._aborted = False
        self._released = False
        self._pending_starts -= 1
        if not self._simulation_mode:
            self.acquisition.run()

    def _get_value(self):
        if self._acquisition_mode is AcqMode.Timer:
            software_synch_description = self._synch_description.get("software")
            if software_synch_description is not None:
                value = software_synch_description.integration_time
            else:
                value = None
        elif self.acquisition_mode is AcqMode.Monitor:
            value = self._monitor_count
        return value

    def set_acquisition(self, acq_cache):
        self.set_action_cache(acq_cache)

    def get_acquisition(self):
        return self.get_action_cache()

    acquisition = property(get_acquisition, doc="acquisition object")

    def stop(self):
        self._pending_starts = 0
        self.acquisition._synch._synch_soft.stop()
        PoolGroupElement.stop(self)

    def abort(self):
        self._pending_starts = 0
        self.acquisition._synch._synch_soft.abort()
        PoolGroupElement.abort(self)

    # -------------------------------------------------------------------------
    # utils
    # -------------------------------------------------------------------------

    def _is_online(self, cfg):
        pool = self.pool
        for ctrl_name in cfg['controllers']:
            external = ctrl_name in ['__tango__']
            if not external:
                ctrl = pool.get_element_by_full_name(ctrl_name)
                if not ctrl.is_online():
                    return False
        return True
    # --------------------------------------------------------------------------
    # release
    # --------------------------------------------------------------------------

    def release(self):
        # override PoolBaseElement.releaes() cause the PoolAcquisition action
        # is composed from many sub-actions and the default
        # PoolBaseElement.get_operation() is not able to get the top action
        operation = self.acquisition
        if not operation.is_running():
            self.warning("Operation is not running, can not release")
            return
        self._released = True
        self._state_event = None
        self.info("Release!")
        operation.release_action()
