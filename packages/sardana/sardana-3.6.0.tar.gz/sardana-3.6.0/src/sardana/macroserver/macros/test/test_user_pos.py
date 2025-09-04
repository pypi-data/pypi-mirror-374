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

"""Tests for set_user_pos macro"""

import pytest
import functools
import tango
from sardana.macroserver.macros.test import MacroTester, getMotors

Device = functools.lru_cache(maxsize=1024)(tango.DeviceProxy)

@pytest.fixture()
def motor():
    MOT_NAME = getMotors()[0]
    proxy = Device(MOT_NAME)
    pos_config = proxy.get_attribute_config('Position')
    pos_config.max_value = '5.0'
    pos_config.min_value = '-2.0'
    proxy.set_attribute_config(pos_config)
    proxy.Offset = 1 
    proxy.DefinePosition(1)
    return proxy

@pytest.mark.parametrize("update_limits,expected_limits", 
    [
        (True, (3.0, -4.0)),
        (False, (5.0, -2.0)),
    ]
)
def test_user_pos_update_limit(
    create_sar_demo, macro_executor, motor,
    update_limits, expected_limits
    ):
    tester = MacroTester(macro_executor)
    motor_name = motor.alias()
    tester.macro_runs("set_user_pos", [motor_name, "-1", str(update_limits)])
    
    pos_config = motor.get_attribute_config('Position')
    high_limit = pos_config.max_value
    low_limit = pos_config.min_value
    msg = 'Motor software limit does not equal the expected value'
    expected_high_limit, expected_low_limit = expected_limits
    assert str(expected_high_limit) == high_limit, msg
    assert str(expected_low_limit) == low_limit, msg
