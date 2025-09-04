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

"""This module contains tests for HDF5 recorders."""

import os
import sys
import tempfile
import contextlib
import multiprocessing
from datetime import datetime
from typing import Iterator

import h5py
import numpy
import pytest
from unittest import TestCase, mock

from sardana.macroserver.scan import ColumnDesc
from sardana.macroserver.recorders.h5storage import NXscanH5_FileRecorder
from sardana.macroserver.recorders.h5util import _h5_file_handler
from .common import COL1_NAME, ENV, simulate_scan, Record, RecordList


@contextlib.contextmanager
def h5_write_session(fname: str, swmr_mode: bool = False) -> Iterator[h5py.File]:
    """Context manager for HDF5 file write session.

    Maintains HDF5 file opened for the context lifetime.
    It optionally can open the file as SWRM writer.

    :param fname: Path of the file to be opened
    :param swmr_mode: Use SWMR write mode
    """
    fd = _h5_file_handler.open_file(fname, swmr_mode)
    try:
        yield fd
    finally:
        _h5_file_handler.close_file(fname)


@pytest.fixture
def recorder(tmpdir):
    path = str(tmpdir / "file.h5")
    return NXscanH5_FileRecorder(filename=path)


def test_dtype_float64(recorder):
    """Test creation of dataset with float64 data type"""
    # simulate sardana scan
    nb_records = 1
    simulate_scan(recorder, tuple(), 0.1, nb_records)
    # assert if reading datasets from the sardana file access to the
    # dataset of the partial files
    file_ = h5py.File(recorder.filename)
    for i in range(nb_records):
        expected_data = 0.1
        data = file_["entry0"]["measurement"][COL1_NAME][i]
        msg = "data does not match"
        assert data == expected_data, msg


@pytest.mark.parametrize(
    "shape, expected_data",
    [
        (tuple(), 0.3),
        ((1,), numpy.array([1.0])),
        ((2,), numpy.array([0.2, 12.0])),
        ((2, 1), numpy.array([[0.1], [1.0]])),
    ],
)
def test_shape(recorder, shape, expected_data):
    """Test creation of dataset with different shapes"""
    # simulate sardana scan
    nb_records = 1
    simulate_scan(recorder, shape, expected_data, nb_records)
    # assert if the data is identical
    file_ = h5py.File(recorder.filename)
    for i in range(nb_records):
        data = file_["entry0"]["measurement"][COL1_NAME][i]
        numpy.testing.assert_array_equal(data, expected_data)


def test_value_ref(recorder):
    """Test creation of dataset with str data type"""
    nb_records = 1
    # create description of channel data
    data_desc = [
        ColumnDesc(name=COL1_NAME, label=COL1_NAME, dtype="float64",
                   shape=(1024, 1024), value_ref_enabled=True)
    ]
    environ = ENV.copy()
    environ["datadesc"] = data_desc

    # simulate sardana scan
    environ["starttime"] = datetime.now()
    environ["scanstarttime"] = datetime.now()
    record_list = RecordList(environ)
    recorder._startRecordList(record_list)
    for i in range(nb_records):
        record = Record({COL1_NAME: "file:///tmp/test.edf"}, i)
        recorder._writeRecord(record)
    environ["endtime"] = datetime.now()
    recorder._endRecordList(record_list)

    # assert if reading datasets from the sardana file access to the
    # dataset of the partial files
    file_ = h5py.File(recorder.filename)
    for i in range(nb_records):
        expected_data = "file:///tmp/test.edf"
        try:
            dataset = file_["entry0"]["measurement"][COL1_NAME].asstr()
        except AttributeError:
            # h5py < 3
            dataset = file_["entry0"]["measurement"][COL1_NAME]
        data = dataset[i]
        msg = "data does not match"
        assert data == expected_data, msg


@pytest.mark.xfail(os.name == "nt", reason="VDS are buggy on Windows")
@pytest.mark.skipif(not hasattr(h5py, "VirtualLayout"),
                    reason="VDS not available in this version of h5py")
def test_VDS(recorder):
    """Test creation of VDS when channel reports URIs (str) of h5file
    scheme in a simulated sardana scan (3 points).
    """
    nb_records = 3
    # create partial files
    part_file_name_pattern = "test_vds_part{0}.h5"
    part_file_paths = []
    for i in range(nb_records):
        path = os.path.join(os.path.dirname(recorder.filename),
                            part_file_name_pattern.format(i))
        part_file_paths.append(path)
        part_file = h5py.File(path, "w")
        img = numpy.array([[i, i], [i, i]])
        dataset = "dataset"
        part_file.create_dataset(dataset, data=img)
        part_file.flush()
        part_file.close()
    try:
        # create description of channel data
        data_desc = [
            ColumnDesc(name=COL1_NAME, label=COL1_NAME, dtype="float64",
                       shape=(2, 2), value_ref_enabled=True)
        ]
        environ = ENV.copy()
        environ["datadesc"] = data_desc

        # simulate sardana scan
        environ["starttime"] = datetime.now()
        environ["scanstarttime"] = datetime.now()
        record_list = RecordList(environ)
        recorder._startRecordList(record_list)
        for i in range(nb_records):
            ref = "h5file://" + part_file_paths[i] + "::" + dataset
            record = Record({COL1_NAME: ref}, i)
            recorder._writeRecord(record)
        environ["endtime"] = datetime.now()
        recorder._endRecordList(record_list)

        # assert if reading datasets from the sardana file access to the
        # dataset of the partial files
        file_ = h5py.File(recorder.filename)
        for i in range(nb_records):
            expected_img = numpy.array([[i, i], [i, i]])
            img = file_["entry0"]["measurement"][COL1_NAME][i]
            msg = "VDS extracted image does not match"
            # TODO: check if this assert works well
            numpy.testing.assert_array_equal(img, expected_img, msg)
    finally:
        # remove partial files
        for path in part_file_paths:
            os.remove(path)


@pytest.mark.parametrize("custom_data", [8, True])
def test_addCustomData(recorder, custom_data):
    name = "custom_data_name"
    recorder.addCustomData(custom_data, name)
    with h5py.File(recorder.filename) as fd:
        assert fd["entry"]["custom_data"][name][()] == custom_data


def test_addCustomData_str(recorder):
    name = "custom_data_name"
    custom_data = "str_custom_data"
    recorder.addCustomData(custom_data, name)
    with h5py.File(recorder.filename) as fd:
        try:
            dset = fd["entry"]["custom_data"][name].asstr()
        except AttributeError:
            dset = fd["entry"]["custom_data"][name]
        assert dset[()] == custom_data


def test_addCustomData_postScan(recorder):
    simulate_scan(recorder, tuple(), 0.1, 1)
    msg = "when fd status is {}".format(recorder.fd)
    name = "custom_data_name"
    custom_data = 8
    recorder.addCustomData(custom_data, name)
    with h5py.File(recorder.filename) as fd:
        assert fd["entry0"]["custom_data"][name][()] == custom_data, msg


@pytest.mark.parametrize("fd_status", ["None", "Opened", "Closed"])
def test_addCustomData_fdCheck(recorder, fd_status):
    name = "custom_data_name"
    custom_data = 8
    if fd_status == "None":
        pass
    elif fd_status == "Opened":
        recorder.fd = recorder._openFile(recorder.filename)
    elif fd_status == "Closed":
        recorder.fd = recorder._openFile(recorder.filename)
        recorder.fd.close()

    msg = "when fd is {}".format(recorder.fd)
    recorder.addCustomData(custom_data, name)
    with h5py.File(recorder.filename) as fd:
        assert fd["entry"]["custom_data"][name][()] == custom_data, msg


def _scan(path, serialno=0):
    env = ENV.copy()
    env["serialno"] = serialno
    record_list = RecordList(env)
    nb_records = 2
    # create description of channel data
    data_desc = [
        ColumnDesc(name=COL1_NAME,
                   label=COL1_NAME,
                   dtype="float64",
                   shape=())
    ]
    env["datadesc"] = data_desc
    # simulate sardana scan
    recorder = NXscanH5_FileRecorder(filename=path)
    env["starttime"] = datetime.now()
    env["scanstarttime"] = datetime.now()
    recorder._startRecordList(record_list)
    for i in range(nb_records):
        record = Record({COL1_NAME: 0.1}, i)
        recorder._writeRecord(record)
    env["endtime"] = datetime.now()
    recorder._endRecordList(record_list)


def read_file(path, ready, done):
    with h5py.File(path, mode="r"):
        ready.set()
        done.wait()


@pytest.mark.skipif(
    sys.platform == "win32"
        and h5py.version.version_tuple >= (3, 4, 0),
    reason="hangs on windows with h5py >= 3.4 (see #1722)"
)
def test_swmr_with_h5_session(tmpdir):
    path = str(tmpdir / "file.h5")
    reader_is_ready = multiprocessing.Event()
    writer_is_done = multiprocessing.Event()
    reader = multiprocessing.Process(
        target=read_file, args=(path, reader_is_ready, writer_is_done)
    )
    with h5_write_session(path):
        _scan(path, serialno=0)
        reader.start()
        reader_is_ready.wait()
        try:
            _scan(path, serialno=1)
        finally:
            writer_is_done.set()
            reader.join()


def read_file_without_file_locking(path, ready, done):
    with h5py.File(path, mode="r", locking=False):
        ready.set()
        done.wait()

@pytest.mark.skipif(
    condition=(
        h5py.version.hdf5_version_tuple < (1, 12, 1)
        or h5py.version.version_tuple < (3, 5, 0)
    ),
    reason=("locking argument not supported by hdf5<1.12.1 "
            "and h5py<3.5")
)
def test_swmr_without_h5_session(tmpdir):
    path = str(tmpdir / "file.h5")
    reader_is_ready = multiprocessing.Event()
    writer_is_done = multiprocessing.Event()
    reader = multiprocessing.Process(
        target=read_file_without_file_locking,
        args=(path, reader_is_ready, writer_is_done)
    )

    _scan(path, serialno=0)
    reader.start()
    reader_is_ready.wait()
    try:
        _scan(path, serialno=1)
    finally:
        writer_is_done.set()
        reader.join()
