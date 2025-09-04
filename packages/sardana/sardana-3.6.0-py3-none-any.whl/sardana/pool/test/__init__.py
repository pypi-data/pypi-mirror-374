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

"""Utilities for testing pool and third-party controller plugins.

For third-party controller plugins projects it is recommended to
develop their integration tests with the pool.
From the other hand, the pool core features can be easily tested
using the dummy controller plugins.
This module contains fixtures and test utilities applicable for
both these use cases.

The `~sardana.pool.test.util` module comes with a set of fixtures
providing you the most common pool elements e.g. those created by
the `~sardana.macroserver.macros.demo.sar_demo` macro e.g.
`mot01`, `ct01`, `motctrl01`, etc. You can use them directly in your tests
without even importing them, this is because sardana installs them
as pytest plugins.

For example, to test that the calculation of the user position works
you could write the following test::

    def test_motor_user_pos_after_set_sign(mot01):
        mot01.define_position(3)
        mot01.sign = -1
        assert mot01.position.value == -3

You can customize the fixtures with the following markers:

- `kwargs` for customizing the object creation e.g.::

    @pytest.mark.kwargs({"motctrl01": {"properties": {"Prop1": "foo"}}})
    def test_property(motctrl01):
        assert motctrl01.ctrl.Prop1 == "foo"

- `attribute_values` for setting attribute values::

    @pytest.mark.attribute_values({"mot01": {"Offset": -1},
                                   "mot02": {"Offset": 1}})
    def test_motor_group_get_position(motgrp0102):
        assert motgrp0102.position == [-1, 1]

- `attrs` for setting python object attributes (using `setattr`)::

    @pytest.mark.attrs({"pool": {"drift_correction": False},
    def test_dummy_motor_controller(pool):
        assert pool.drift_correction == False

This may be specially useful when you use fixtures of higher level elements
and you would like to change the behavior of the lower level elements
indirectly requested as fixtures.    

The above introduced markers are good for minor and occasional modifications
of fixtures. For more demanding use cases it is better that you use the
factory fixtures e.g. `~sardana.pool.test.util.create_motor`.

You can parametrize your test with multiple fixtures using `parametrize`
marker and `request.getfixturevalue()`. This will automatically create
one test per parameterize option::

    @pytest.mark.parametrize("moveable", ["mot01", "gap01"])
    def test_get_moveable_position(moveable, request):
        moveable = request.getfixturevalue(moveable)
        assert moveable.position.value == 0

For synchronizing your tests execution with execution of background actions it
is very handy to use the `~sardana.pool.test.util.ActionEvent` class.
"""

from .fake import *  # NOQA
from .helper import *  # NOQA
from .util import *  # NOQA
from .dummyconfs import *  # NOQA
from .base import *  # NOQA
from .test_acquisition import *  # NOQA
from .test_ctacquisition import *  # NOQA
from .test_measurementgroup import *  # NOQA
from .test_poolcontroller import *  # NOQA
from .test_poolcontrollermanager import *  # NOQA
from .test_poolcountertimer import *  # NOQA
from .test_poolsynchronization import *  # NOQA
from .test_synchronization import *  # NOQA
from .test_poolmotion import *  # NOQA
