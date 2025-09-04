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

"""
This module provides the sardana Command Line Interface

It is based on the click module to provide CLI utilities.

It defines a `sardana` command which can accept subcommands defined in
other sardana submodules or even in plugins.

To define a subcommand for sardana, you need to register it using the
`sardana_subcommands` entry point via setuptools.

.. todo:: add click link , add code snippet for plugins, etc.


"""

from .cli import main