#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""In general, sardana was designed for using it with `client-server
architecture <https://en.wikipedia.org/wiki/Client%E2%80%93server_model>`_.
Where all the business logic resides on the server side
and client side is just a thin layer to enable control and monitoring.

One of the fundamental principle in sardana design is its clear
separation between the core and the middleware.
The sardana kernel is composed from objects of the core classes which are
then exposed to the clients via server extensions.

Sardana kernel objects communicates using `publisher-subscriber pattern
<https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern>`_
in which messages are exchanged by means of synchronous invocation of
callbacks.
A class inheriting from `~sardana.sardanaevent.EventGenerator` acts as
publisher and a class inheriting from `~sardana.sardanaevent.EventReceiver`
as subscriber e.g. `~sardana.pool.poolmotor.PoolMotor` and
`~sardana.pool.poolpseudomotor.PoolPseudoMotor` respectively or
`~sardana.pool.poolmotor.Position` and `~sardana.pool.poolmotor.PoolMotor`
respectively.
Moreover this mechanism is used for notifying server extension about
sardana kernel events e.g. element's state change.

Major core classes have `state` attribute which value is one of the
`~sardana.sardanadefs.State` enum values.

Sardana uses threads for concurrency. More precise using
`Thread pool <https://en.wikipedia.org/wiki/Thread_pool>`_ pattern
implemented in  `~taurus.core.util.threadpool.ThreadPool` and different
instances of such thread pools exist within a kernel.

.. important::
    Due to the use of Tango sardana `~taurus.core.util.threadpool.ThreadPool`
    instances must use special worker threads which execute jobs within
    `~tango.EnsureOmniThread` context manager.

Logging infrastructure is initialized on server startup using
`~sardana.tango.core.util.prepare_logging()`.
Most of the Sardana classes inherit from `~taurus.Logger`
and you can directly invoke their logging methods
e.g. `~taurus.Logger.debug()`, `~taurus.Logger.error()`, etc..
For consistency we recommend to use Taurus logging utilities -
`taurus.core.util.log`.
"""

from . import release as __release


class Release:
    pass


for attr, value in __release.__dict__.items():
    setattr(Release, attr, value)
Release.__doc__ = __release.__doc__

__version__ = Release.version

from .sardanadefs import *
from .sardanavalue import SardanaValue
