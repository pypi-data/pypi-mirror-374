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

import unittest
import pytest

from sardana.pool.test import (FakePool, createPoolController,
                               dummyPoolCTCtrlConf01)
from sardana.pool.poolcontroller import PoolController


class PoolControllerTestCase(unittest.TestCase):
    """Unittest of PoolController Class"""

    def setUp(self):
        """Instantiate a fake Pool and create a Controller"""
        pool = FakePool()
        self.pc = createPoolController(pool, dummyPoolCTCtrlConf01)

    def test_init(self):
        """Verify that the created Controller is an instance of
        PoolController"""
        msg = 'PoolController constructor does not create ' +\
              'PoolController instance'
        self.assertIsInstance(self.pc, PoolController, msg)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.pc = None


def test_default_property(motctrl01):
    assert motctrl01.ctrl.Prop2 == 531


@pytest.mark.kwargs({"motctrl01": {"properties": {"Prop1": "foo"}}})
def test_property(motctrl01):
    assert motctrl01.ctrl.Prop1 == "foo"


def test_init_attribute_values_default(motctrl01):
    motctrl01.init_attribute_values()
    assert motctrl01.get_ctrl_attr("LowerLimitSwitch") == -9999.9999


def test_init_attribute_values(motctrl01):
    import logging
    motctrl01.init_attribute_values({
        "LogLevel": logging.DEBUG,
        "LowerLimitSwitch": 123.456
    })
    assert motctrl01.log_level == logging.DEBUG
    assert motctrl01.get_ctrl_attr("LowerLimitSwitch") == 123.456

@pytest.mark.attribute_values({"motctrl01": {"LowerLimitSwitch": -100},
                               "mot01": {"Power": False}})
def test_dummy_motor_controller(mot01):
    assert mot01.controller.get_ctrl_attr("LowerLimitSwitch") == -100
    assert mot01.get_extra_par("Power") == False