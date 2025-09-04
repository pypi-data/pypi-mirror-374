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

"""Tests for wm macros"""

from sardana.macroserver.macros.test import MacroTester, getMotors


def test_wm_output(create_sar_demo, macro_executor):
    """Testing the execution of the 'wm' macro and verify that the log
       'output' exists.
    """
    tester = MacroTester(macro_executor)
    tester.macro_runs(
        macro_name="wm",
        macro_params=[getMotors()[0]],
        wait_timeout=5
    )

    log_output = tester.macro_executor.getLog("output")
    msg = "wm macro did not return any data."
    assert len(log_output) > 0, msg
