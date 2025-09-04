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

"""Tests for expert macros"""

from sardana import sardanacustomsettings
from sardana.macroserver.macros.test import MacroTester, getCTs


def test_expert_macros(create_sar_demo, macro_executor):
    tester = MacroTester(macro_executor)
    CTRL_NAME = "unittestmotctrl01"
    MOT_NAME1 = "unittestmot01"
    MOT_NAME2 = "unittestmot02"
    try:
        tester.macro_runs(macro_name="defctrl",
                          macro_params=["DummyMotorController", CTRL_NAME],
                          wait_timeout=1)
        tester.macro_runs(macro_name="defelem",
                          macro_params=[MOT_NAME1, CTRL_NAME, "1"],
                          wait_timeout=1)
        if getattr(sardanacustomsettings, "USE_NUMERIC_ELEMENT_IDS", False):
            tester.macro_runs(macro_name="renameelem",
                              macro_params=[MOT_NAME1, MOT_NAME2],
                              wait_timeout=1)
            tester.macro_runs(macro_name="defm",
                              macro_params=[MOT_NAME1, CTRL_NAME, "2"],
                              wait_timeout=1)
        else:
            tester.macro_runs(macro_name="defm",
                              macro_params=[MOT_NAME2, CTRL_NAME, "2"],
                              wait_timeout=1)
        tester.macro_runs(macro_name="udefelem",
                          macro_params=[MOT_NAME1, MOT_NAME2],
                          wait_timeout=1)
        tester.macro_runs(macro_name="udefctrl",
                          macro_params=[CTRL_NAME],
                          wait_timeout=1)
    except Exception as e:
        import taurus
        taurus.warning("Your system may stay dirty due to an unexpected"
                        " exception during the test.")
        raise e


def test_meas(create_sar_demo, macro_executor):
    tester = MacroTester(macro_executor)
    """Test case for measurement group related expert macros."""
    MNTGRP_NAME = "unittestmntgrp01"
    CT_NAME1, CT_NAME2 = getCTs()[:2]
    try:
        tester.macro_runs(macro_name="defmeas",
                          macro_params=[MNTGRP_NAME, CT_NAME1, CT_NAME2])
        tester.macro_runs(macro_name="udefmeas",
                          macro_params=[MNTGRP_NAME])
    except Exception as e:
        import taurus
        taurus.warning("Your system may stay dirty due to an unexpected"
                        " exception during the test.")
        raise e

# TODO: improve this test: not all sardana controller implement SendToCtrl
# @testRun(macro_params=[CTRL_NAME1, "blabla"], wait_timeout=1)
# class Send2ctrlTest(RunMacroTestCase, unittest.TestCase):
#     """Test case for send2ctrl macro.
#     """
#     macro_name = "send2ctrl"


# This is a known failure until bug-472 is fixed:
# https://sourceforge.net/p/sardana/tickets/472/
# @testRun(macro_params=["DummyMotorController"])
# class EdctrlTest(RunMacroTestCase, unittest.TestCase):
#     """Test case for edctrl macro.
#     """
#     macro_name = "edctrl"
