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

import pkg_resources
import click
import taurus
import sardana

@click.group('sardana')
@click.option('--log-level',
              type=click.Choice(['critical', 'error', 'warning', 'info',
                                 'debug', 'trace']),
              default='error', show_default=True,
              help='Show only logs with priority LEVEL or above')
@click.version_option(version=sardana.__version__)
def sardana_cmd(log_level):
    """The main sardana command"""

    taurus.setLogLevel(getattr(taurus, log_level.capitalize()))


def main():
    # set the log level to WARNING avoid spamming the CLI while loading
    # subcommands
    # it will be restored to the desired one first thing in sardana_cmd()
    taurus.setLogLevel(taurus.Warning)

    # Add subcommands from the sardana_subcommands entry point
    for ep in pkg_resources.iter_entry_points('sardana.cli.subcommands'):
        try:
            subcommand = ep.load()
            sardana_cmd.add_command(subcommand)
        except Exception as e:
            # -----------------------------------------------------------
            taurus.warning('Cannot add "%s" subcommand to sardana. Reason: %r',
                 ep.name, e)

    # launch the sardana command
    sardana_cmd()


if __name__ == '__main__':
    main()