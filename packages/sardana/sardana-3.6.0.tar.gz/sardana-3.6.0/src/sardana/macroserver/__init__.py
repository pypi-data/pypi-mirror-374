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

"""MacroServer part of the kernel consist of one
`~sardana.macroserver.macroserver.MacroServer` object which acts as:

- container (inherits from `~sardana.sardanacontainer.SardanaContainer`) of:

 - macro parameter types managed by `~sardana.macroserver.mstypemanager.TypeManager`
 - macros managed by `~sardana.macroserver.msmacromanager.MacroManager`
 - objects managed by `~sardana.pool.pool.Pool` instances it is connected to (can be multiple of them)

- facade (implements `Facade pattern <https://en.wikipedia.org/wiki/Facade_pattern>`_) to:

  - `~sardana.macroserver.msmacromanager.MacroManager`
  - `~sardana.macroserver.msrecordermanager.RecorderManager`
  - `~sardana.macroserver.msenvmanager.EnvironmentManager`

The objects currently under `~sardana.macroserver.macroserver.MacroServer` management are
communicated to the clients with the `Elements` attribute.

`~sardana.macroserver.msdoor.Door` is just a thin layer in macro execution process
where the principal role plays `~sardana.macroserver.msmacromanager.MacroExecutor` - one
instance per `~sardana.macroserver.msdoor.Door`.

Macros are executed asynchronously using threads by one
`~taurus.core.util.threadpool.ThreadPool` with just one worker thread per
`~sardana.macroserver.msmacromanager.MacroExecutor`.

.. note::

  `sardana-jupyter <https://gitlab.com/sardana-org/sardana-jupyter>`_ executes
  macros synchronously.

Macro execution consists of:

- user inputs macro parameters
- composing of XML document with macro execution information e.g. parameters
  parsing in Spock
- execution of `RunMacro()` command on Door Tango Device
- parameters decoding and validation by
  `~sardana.macroserver.msmacromanager.MacroManager` and
  `~sardana.macroserver.msparameter.ParamDecoder`
- creation of macro object from its meta equivalent
  `~sardana.macroserver.msmacromanager.MacroManager`
- macro execution using `~sardana.macroserver.msmacromanager.MacroExecutor`

Macro execution can be stopped, aborted or released, and the following sketch
demonstrate different activity flows depending on where the macro was
interrupted:

.. figure:: /_static/macro_interruption_flow.jpeg
    :align: center

    Activity diagram showing different execution flows of interrupting a macro


While Device Pool controllers are long-lived objects, recorders and macros are
short-lived objects created on demand and destroyed when not needed anymore.

.. figure:: /_static/macros_recorders_software_layers.png
    :align: center

    Main software layers of sardana on example of MacroServer
    macros and recorders
"""

__docformat__ = 'restructuredtext'
