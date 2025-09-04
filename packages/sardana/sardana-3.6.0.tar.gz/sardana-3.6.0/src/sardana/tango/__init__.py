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

""" Tango_ attributes/ command interface does not accept certain python
types e.g. `dict`. For these cases we recommend using `~tango.DevEncoded`
or `~tango.DevString` types (the later one when you need a memorized
attribute). For coding/ decoding of data we recommend using Taurus codec
utilities: `~taurus.core.util.codecs.CodecFactory`. 

Apart from using Tango as middleware, sardana uses some of Tango features:

- serialization monitor
- limits protection (partially, a part of it is re-implemented in the core)
- attribute configuration
- state machine (partially, a part of it is re-implemented in the core)
- Tango DB:

  - for storing persistent configuration (but MacroServer environment)
  - naming service / broker

.. note::
    `SEP20 <https://gitlab.com/sardana-org/sardana/-/merge_requests/1749>`_
    propose to use YAML configuration files for storing persistent configuration
"""

__docformat__ = 'restructuredtext'

SERVER_NAME = "Sardana"


def prepare_sardana(util):
    from . import pool
    from . import macroserver
    pool.prepare_pool(util)
    macroserver.prepare_macroserver(util)


def main_sardana(args=None, start_time=None, mode=None):
    from .core import util
    # pass server name so the scripts generated with setuptools work on Windows
    return util.run(prepare_sardana, args=args, start_time=start_time,
                    mode=mode, name=SERVER_NAME)

run = main_sardana


def main():
    import datetime
    run(start_time=datetime.datetime.now())
