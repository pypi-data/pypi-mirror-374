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

"""Tests for scan macros"""
import pytest
from sardana.macroserver.macros.test import (MacroTester, getMotors)


def parsing_log_output(log_output):
    """A helper method to parse log output of an executed scan macro.
    :params log_output: (seq<str>) Result of macro_executor.getLog('output')
    (see description in :class:`.BaseMacroExecutor`).

    :return: (seq<number>) The numeric data of a scan.
    """
    first_data_line = 1
    scan_index = 0
    data = []
    for line, in log_output[first_data_line:]:
        # Get a list of elements without white spaces between them
        l = line.split()
        # Cast all elements of the scan line (l) to float
        l = [float(scan_elem) for scan_elem in l]
        # Cast index of scan to int (the first element of the list)
        l[scan_index] = int(l[scan_index])
        data.append(l)
    return data


def test_ascan_positions(create_sar_demo, macro_executor):
    """Test ascan result using double checking, with log output
    and data from the macro:

        - The motor initial and final positions of the scan are the
            ones given as input.

        - Intervals in terms of motor position between one point and
            the next one are equidistant.
    """
    tester = MacroTester(macro_executor)
    macro_params=[getMotors()[0], "0", "5", "4", ".1"]
    tester.macro_runs(
        macro_name="ascan",
        macro_params=macro_params,
        wait_timeout=30.0
    )

    mot_name = macro_params[0]
    expected_init_pos = float(macro_params[1])
    expected_final_pos = float(macro_params[2])
    steps = int(macro_params[-2])
    interval = abs(expected_final_pos - expected_init_pos) / steps

    # Test data from macro (macro_executor.getData())
    data = tester.macro_executor.getData()
    mot_init_pos = data[min(data.keys())].data[mot_name]
    mot_final_pos = data[max(data.keys())].data[mot_name]
    pre = mot_init_pos

    for step in range(1, max(data.keys()) + 1):
        assert pytest.approx(abs(pre - data[step].data[mot_name])) == interval, \
            "Step interval differs for more than expected (using getData)"
        pre = data[step].data[mot_name]

    assert pytest.approx(mot_init_pos) == expected_init_pos, \
        "Initial possition differs from set value (using getData)"
    assert pytest.approx(mot_final_pos) == expected_final_pos, \
        "Final possition differs from set value (using getData)"

    # Test data from log_output (macro_executor.getLog('output'))
    log_output = tester.macro_executor.getLog('output')
    data = parsing_log_output(log_output)
    init_pos = 0
    last_pos = -1
    value = 1
    pre = data[init_pos]
    for step in data[1:]:
        assert pytest.approx(abs(pre[value] - step[value])) == interval, \
            "Step interval differs for more than expected (using getData)"
        pre = step

    assert pytest.approx(data[init_pos][value]) == expected_init_pos, \
        "Initial possition differs from set value (using getLog)"
    assert pytest.approx(data[last_pos][value]) == expected_final_pos, \
        "Final possition differs from set value (using getLog)"


def test_ascan_onepoint(create_sar_demo, macro_executor):
    """Test ascan result using double checking, with log output
    and data from the macro:

        - The motor initial and final positions of the scan are the
            ones given as input.

    """
    tester = MacroTester(macro_executor)
    macro_params = [getMotors()[0], "6", "6", "0", ".1"]
    tester.macro_runs(
        macro_name="ascan",
        macro_params=macro_params,
        wait_timeout=30.0
    )

    mot_name = macro_params[0]
    expected_init_pos = float(macro_params[1])
    expected_final_pos = float(macro_params[2])

    # Test data from macro (macro_executor.getData())
    data = tester.macro_executor.getData()
    mot_init_pos = data[min(data.keys())].data[mot_name]
    mot_final_pos = data[max(data.keys())].data[mot_name]

    assert pytest.approx(mot_init_pos) == expected_init_pos, \
        "Initial possition differs from set value (using getData)"
    assert pytest.approx(mot_final_pos) == expected_final_pos, \
        "Final possition differs from set value (using getData)"

    # Test data from log_output (macro_executor.getLog('output'))
    log_output = tester.macro_executor.getLog('output')
    data = parsing_log_output(log_output)
    init_pos = 0
    value = 1

    assert pytest.approx(data[init_pos][value]) == expected_init_pos, \
        "Initial possition differs from set value (using getLog)"
