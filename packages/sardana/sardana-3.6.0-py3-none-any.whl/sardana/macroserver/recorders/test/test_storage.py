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

"""This module contains tests for SPEC and FIO recorders."""


import numpy
import pytest
import tango
from datetime import datetime
from pathlib import Path

from sardana.macroserver.scan import ColumnDesc
from sardana.macroserver.recorders.storage import SPEC_FileRecorder, FIO_FileRecorder
from .common import ENV, simulate_scan, Record, RecordList


@pytest.fixture
def spec_recorder(tmpdir):
    path = str(tmpdir / "file.spec")
    return SPEC_FileRecorder(filename=path)


@pytest.fixture
def fio_recorder(tmpdir):
    path = str(tmpdir / "file.fio")
    return FIO_FileRecorder(filename=path)


@pytest.fixture
def create_alias():
    dev_info = tango.DbDevInfo()
    dev_info.name = "sys/foo/bar"
    dev_info._class = "Foo"
    dev_info.server = "MyServer/foo"
    db = tango.Database()
    db.add_device(dev_info)
    alias = "bar01"
    db.put_device_alias(dev_info.name, alias)
    yield (dev_info.name, alias)
    db.delete_device_alias(alias)
    db.delete_device_alias(dev_info.name)


def check_lines(filename, expected_lines):
    with open(filename, "r") as f:
        for index, line in enumerate(f):
            assert line.strip() == expected_lines[index]


@pytest.mark.parametrize(
    "shape, expected_data",
    [
        (tuple(), 0.3),
        ((1,), numpy.array([1.0])),
    ],
)
def test_spec_recorder_no_mca(spec_recorder, shape, expected_data):
    """Test creation of spec file with one column"""
    environ = simulate_scan(spec_recorder, shape, expected_data)
    # assert if the data is identical
    EXPECTED_LINES = [
        "#S 0 test",
        "#U user",
        "#D {}".format(environ["starttime"].strftime("%a %b %d %H:%M:%S %Y")),
        "#C Acquisition started at {}".format(environ["scanstarttime"].ctime()),
        "#N 1",
        "#L col1",
        str(expected_data),
        "#C Acquisition ended at {}".format(environ["endtime"].ctime()),
    ]
    check_lines(spec_recorder.filename, EXPECTED_LINES)


def test_spec_recorder_mca(spec_recorder):
    """Test creation of spec file an array"""
    environ = simulate_scan(spec_recorder, (2,), numpy.array([0.2, 12.0]))
    # assert if the data is identical
    EXPECTED_LINES = [
        "#S 0 test",
        "#U user",
        "#D {}".format(environ["starttime"].strftime("%a %b %d %H:%M:%S %Y")),
        "#C Acquisition started at {}".format(environ["scanstarttime"].ctime()),
        "#N 0",
        "#@MCA 2C",
        "#@CHANN 2 0 1 1",
        "#@MCA_NB 1",
        "#@DET_0 col1",
        "#L",
        "@A 0.2 12.0",
        "",
        "#C Acquisition ended at {}".format(environ["endtime"].ctime()),
    ]
    check_lines(spec_recorder.filename, EXPECTED_LINES)


@pytest.mark.parametrize(
    "shape, expected_data",
    [
        (tuple(), 0.3),
        ((1,), 1.0),
    ],
)
def test_fio_recorder_no_mca(fio_recorder, shape, expected_data):
    """Test creation of fio file with one column"""
    environ = simulate_scan(fio_recorder, shape, expected_data)
    # assert if the data is identical
    EXPECTED_LINES = [
        "!",
        "! Comments",
        "!",
        "%c",
        "test",
        "user user Acquisition started at {}".format(environ["scanstarttime"].ctime()),
        "!",
        "! Parameter",
        "!",
        "%p",
        "!",
        "! Data",
        "!",
        "%d",
        "Col 1 col1 DOUBLE",
        "Col 2 timestamp DOUBLE",
        "{} nan".format(expected_data),
        "! Acquisition ended at {}".format(environ["endtime"].ctime()),
    ]
    check_lines(fio_recorder.filename, EXPECTED_LINES)


def test_fio_recorder_mca(fio_recorder, create_alias):
    """Test creation of fio file with an array"""
    name, alias = create_alias
    full_name = "tango://machine:10000/{}".format(name)
    data_desc = [
        ColumnDesc(name=full_name, label="oned01", dtype="float64", shape=(2,))
    ]
    environ = ENV.copy()
    environ["datadesc"] = data_desc
    # simulate sardana scan
    today = datetime.now()
    environ["starttime"] = today
    environ["scanstarttime"] = today
    environ["ScanFile"] = "file"
    record_list = RecordList(environ)
    # We have to set fio_recorder.recordlist before calling _startRecordList
    fio_recorder.recordlist = record_list
    fio_recorder._startRecordList(record_list)
    data = numpy.array([10.0, 20.0])
    record = Record({full_name: data, "mot01": 1.0, "point_nb": 0}, 0)
    fio_recorder._writeRecord(record)
    environ["endtime"] = datetime.now()
    fio_recorder._endRecordList(record_list)
    # assert if the data is identical
    EXPECTED_LINES = [
        "!",
        "! Comments",
        "!",
        "%c",
        "test",
        "user user Acquisition started at {}".format(environ["scanstarttime"].ctime()),
        "!",
        "! Parameter",
        "!",
        "%p",
        "!",
        "! Data",
        "!",
        "%d",
        "Col 1 timestamp DOUBLE",
        "nan",
        "! Acquisition ended at {}".format(environ["endtime"].ctime()),
    ]
    check_lines(fio_recorder.filename, EXPECTED_LINES)
    mca_file = Path(fio_recorder.mcaDirName) / "file_00000_mca_s1.fio"
    assert mca_file.exists()
    EXPECTED_MCA_LINES = [
        "!",
        "! Comments",
        "!",
        "%c",
        "Position 1, Index 0",
        "!",
        "! Parameter",
        "%p",
        "Sample_time = 0.333333",
        "!",
        "! Data",
        "%d",
        "Col 1 bar01 FLOAT",
        "10.0",
        "20.0",
    ]
    check_lines(str(mca_file), EXPECTED_MCA_LINES)
