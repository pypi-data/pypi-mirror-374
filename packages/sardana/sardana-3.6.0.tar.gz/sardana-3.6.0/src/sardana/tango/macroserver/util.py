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

import tango
from taurus.core.tango.tangovalidator import TangoDeviceNameValidator


def get_macroserver_for_door(door_name):
    """Returns the MacroServer device name in the same DeviceServer as the
    given door device"""
    name_validator = TangoDeviceNameValidator()
    _, door_name, _ = name_validator.getNames(door_name)
    db = tango.Database()
    door_name = door_name.lower()
    server_list = list(db.get_server_list('MacroServer/*'))
    server_list += list(db.get_server_list('Sardana/*'))
    server_devs = None
    for server in server_list:
        server_devs = db.get_device_class_list(server)
        devs, klasses = server_devs[0::2], server_devs[1::2]
        for dev in devs:
            if dev.lower() != door_name:
                continue
            for i, klass in enumerate(klasses):
                if klass != 'MacroServer':
                    continue
                full_name, _, _ = name_validator.getNames(devs[i])
                return full_name
    else:
        return None