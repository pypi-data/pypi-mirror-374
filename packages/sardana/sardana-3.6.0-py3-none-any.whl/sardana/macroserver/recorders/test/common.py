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

"""This module contains common variables and functions for storage tests."""

from datetime import datetime
from sardana.macroserver.scan import ColumnDesc

COL1_NAME = "col1"

ENV = {
    "serialno": 0,
    "starttime": None,
    "scanstarttime": None,
    "title": "test",
    "user": "user",
    "datadesc": None,
    "estimatedtime": 1.0,
    "total_scan_intervals": 2,
    "ref_moveables": ["mot01"],
    "endtime": None
}


class RecordList(dict):

    def __init__(self, env):
        self._env = env

    def getEnviron(self):
        return self._env

    def getEnvironValue(self, name):
        return self._env[name]


class Record(object):

    def __init__(self, data, recordno=0):
        self.data = data
        self.recordno = recordno


def simulate_scan(recorder, shape, data, nb_records=1):
    data_desc = [
        ColumnDesc(name=COL1_NAME, label=COL1_NAME, dtype="float64",
                   shape=shape)
    ]
    environ = ENV.copy()
    environ["datadesc"] = data_desc

    # simulate sardana scan
    now = datetime.now()
    environ["starttime"] = now
    environ["scanstarttime"] = now
    record_list = RecordList(environ)
    recorder._startRecordList(record_list)
    for i in range(nb_records):
        record = Record({COL1_NAME: data}, i)
        recorder._writeRecord(record)
    environ["endtime"] = datetime.now()
    recorder._endRecordList(record_list)
    return environ
