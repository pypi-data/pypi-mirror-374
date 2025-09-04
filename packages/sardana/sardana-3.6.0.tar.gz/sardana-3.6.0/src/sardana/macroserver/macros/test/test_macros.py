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

import pytest
from typing import Sequence

from sardana.macroserver.macros.test import MacroTester


@pytest.mark.parametrize(
    "macro_name,macro_params,wait_timeout",
    [
        ("read_ioreg", ["ior01"], 1),
        ("write_ioreg", ["ior01", "1"], 1),
        ("mstate", ["mot01"], 1),
        ("report", ["blabla"], 1),
        ("set_user_lim", ["mot01", "-100", "100"], 1),
        ("set_dial_lim", ["mot01", "-1000", "1000"], 1),
        ("set_dial_pos", ["mot01", "0"], 1),
        ("set_user_pos", ["mot01", "0"], 1),
        ("mv", ["mot01", "1"], 3),
        ("umv", ["mot01", "0"], 3),
        ("mvr", ["mot01", "1"], 3),
        ("umvr", ["mot01", "-1"], 3),
        ("dumpenv", [], 1),
        ("lsvo", [], 1),
        ("setvo", ["PosFormat", "3"], 1),
        ("usetvo", ["PosFormat"], 1),
        ("lsenv", [], 1),
        ("lsenv", ["ascan"], 1),
        ("lsenv", ["ascan", "dscan"], 1),
        ("senv", ["MyEnvVar", "test.dat"], 1),
        ("usenv", ["MyEnvVar"], 1),
        ("lsgh", [], 1),
        ("defgh", ["lsm", "pre-acq"], 1),
        ("defgh", ["lsm mot.*", "pre-acq"], 1),
        ("udefgh", [], 1),
        ("lsdef", [], 1),
        ("lsdef", ["w.*"], 1),
        ("lsctrllib", [], 1),
        ("lsctrllib", ["Dummy.*"], 1),
        ("lsi", [], 1),
        ("lsi", ["mot.*"], 1),
        ("lsa", [], 1),
        ("lsa", ["mot.*"], 1),
        ("lsmeas", [], 1),
        ("lsmeas", ["mot.*"], 1),
        ("lsmac", [], 1),
        ("lsmac", ["w.*"], 1),
        ("lsmaclib", [], 1),
        ("lsmaclib", ["s.*"], 1),
        ("prdef", ["wa"], 1),
        ("relmaclib", ["standard"], 1),
        ("relmac", ["wa"], 1),
        ("sar_info", ["wa"], 1),
        ("sar_info", ["motctrl01"], 1),
        ("sar_info", ["ct01"], 1),
        ("ct", ['.1'], 2.5),
        ("ct", ['.3'], 2.5),
        ("uct", ['.1'], 2),
        ("uct", ['.3'], 2),
        ("mesh", ["mot01", "-1", "1", "3", "mot02", "-1", "0", "2", ".1"], 30),
        ("mesh", ["mot01", "-2", "2", "3", "mot02", "-2", "-1", "2", ".1"], 40),
        ("timescan", ["10", "0.1"], 10),
        ("fscan", ["'x=[1,2]'", "0.1", "mot01", "x**2"], 5),
        ("dscan", ["mot01", "-1", "1", "2", ".1"], 30),
    ],
    indirect=["macro_params"])
def test_macro_runs(create_sar_demo,
                    macro_executor,
                    macro_name: str,
                    macro_params: Sequence[str],
                    wait_timeout: float,
                    data: object = MacroTester.DATA_NOT_PASSED):
    """A helper method to create tests that check if the macro can be
    successfully executed for the given input parameters. It may also
    optionally perform checks on the outputs from the execution.

    :param macro_name: macro name (takes precedence over macro_name
                            class member)
    :param macro_params: parameters for running the macro.
                            If passed, they must be given as a sequence of
                            their string representations.
    :param wait_timeout: maximum allowed time (in s) for the macro
                            to finish. By default infinite timeout is
                            used (None).
    :param data:  If passed, the macro data after the
                    execution is tested to be equal to this.
    """
    tester = MacroTester(macro_executor)
    tester.macro_runs(
        macro_name=macro_name,
        macro_params=macro_params,
        wait_timeout=wait_timeout,
        data=data,
    )


@pytest.mark.parametrize(
    "macro_name,macro_params,stop_delay,wait_timeout",
    [
        ("ct", ['1'], .1, 3.5),        
        ("uct", ['1'], .1, 3),
        ("mesh", ["mot01", "-3", "0", "3", "mot02", "-3", "0", "2", ".1"], 1, 1),
        ("fscan", ["'x=[1,2]'", "0.1", "mot01", "x**2"], 0.1, 1),
        ("ascan", ["mot01", "0", "5", "3", ".1"], 0.1, 1),
        ("dscan", ["mot01", "1", "-1", "3", ".1"], 0.1, 1),
    ],
    indirect=["macro_params"]
)
def test_macro_stops(create_sar_demo,
                     macro_executor,
                     macro_name: str,
                     macro_params: Sequence[str],
                     wait_timeout: float,
                     stop_delay: float
                     ):
    """A helper method to create tests that check if the macro can be
    successfully executed for the given input parameters. It may also
    optionally perform checks on the outputs from the execution.

    :param macro_name: macro name (takes precedence over macro_name
                            class member)
    :param macro_params: parameters for running the macro.
                            If passed, they must be given as a sequence of
                            their string representations.
    :param wait_timeout: maximum allowed time (in s) for the macro
                            to finish. By default infinite timeout is
                            used (None).
    """
    tester = MacroTester(macro_executor)
    tester.macro_stops(
        macro_name=macro_name,
        macro_params=macro_params,
        wait_timeout=wait_timeout,
        stop_delay=stop_delay
    )

# TODO: these tests randomly causes segfaults. fix it!
# @testRun(macro_name="wu", wait_timeout=1)
# @testRun(macro_name="wa", wait_timeout=1)
# @testRun(macro_name="wa", macro_params=["mot.*"], wait_timeout=1)
# @testRun(macro_name="pwa", wait_timeout=1)
# @testRun(macro_name="wm", macro_params=[MOT_NAME1], wait_timeout=1)
# @testRun(macro_name="wm", macro_params=[MOT_NAME1, MOT_NAME2], wait_timeout=1)
# @testRun(macro_name="wum", macro_params=[MOT_NAME1], wait_timeout=1)
# @testRun(macro_name="wum", macro_params=[MOT_NAME1, MOT_NAME2], wait_timeout=1)
# @testRun(macro_name="pwm", macro_params=[MOT_NAME1], wait_timeout=1)
# @testRun(macro_name="pwm", macro_params=[MOT_NAME1, MOT_NAME2], wait_timeout=1)
# class WhereTest(RunMacroTestCase, unittest.TestCase):
#     """Test case for where macros
#     """
#     pass
