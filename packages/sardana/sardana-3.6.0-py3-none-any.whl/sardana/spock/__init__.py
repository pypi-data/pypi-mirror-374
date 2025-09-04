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

"""Spock is basically an IPython extension.

It implements the `load_ipython_extension()` hook function where it exposes some
variables and magic commands to the IPython namespace on startup.

There are two different groups of variables and magics: the built-in ones
and the custom ones.

The built-in ones are exposed directly by the `load_ipython_extension()`
function and are common to all Sardana systems and Spock sessions
e.g. `www` and `edmac` magics or `MACRO_SERVER` and `DOOR` variables.

The custom ones are exposed by the MacroServer's *elements* attribute listener
as explained in the next paragraph.

Spock implements its own Taurus extensions for MacroServer and Door devices in
`SpockMacroServer` and `SpockDoor` classes. This extenstion enhances the standard
:ref:`Taurus extensions for Sardana devices<sardana-taurus-api>`
in the following way. In case of the MacroServer, when the
`SpockMacroServer` receives the *elements* attribute event it exposes
the current Device Pool elements as variables
e.g. `mot01`, `mntgrp01`, and macros as magics 
e.g. `sar_demo`, `mv`, `ct`. On Spock startup, when the `SpockMacroServer` object
is created, it will expose at once all variables corresponding
to all elements proceding from all Device Pools the MacroServer is connected to
and magics corresponding to all macros present in the MacroServer.
In case of the Door, when the macro magics are executed the `SpockDoor` extensions
executes them in synchronous way i.e. holds the Spock prompt until the macro has
finished, and handles `KeyboardInterrupt` exceptions (``Ctrl+C``) to interrupt
the macro execution.
"""

import click
from .genutils import (load_ipython_extension, unload_ipython_extension,  # noqa
    load_config, run)  # noqa


def main():
    import taurus
    taurus.setLogLevel(getattr(taurus, "Warning"))
    run()


@click.command("spock")
@click.option("--profile", 
              help=("use custom IPython profile, for example, "
                    "to connect to your Door."))
def spock_cmd(*args, **kwargs):
    """CLI for executing macros and general control.
    
    For full list of arguments and options check IPython's help:
    `ipython --help`
    """
    import sys
    import taurus
    # taurus.setLogLevel(getattr(taurus, "Warning"))
    sys.argv = sys.argv[sys.argv.index("spock"):]  # necessary for IPython to work
    run()

# in order to click not intercept and complain about
# arguments/options passed to IPython
spock_cmd.allow_extra_args=True
spock_cmd.ignore_unknown_options=True
