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

__all__ = ["AttributeListener", "ActionEvent", "get_marker_attrs",
           "get_marker_attribute_values", "get_marker_kwargs", "mot",
           "set_obj_attrs"]

import sys
import numpy
import pytest
import threading
from functools import partial

from sardana import State
from sardana.pool.pool import Pool


def set_obj_attrs(obj, attrs):
    """Set multiple attributes to an object using `setattr`"""
    for name, value in attrs.items():
        setattr(obj, name, value)

def get_marker_attrs(request):
    """Return python attr values corresponding to the fixture.

    Must be called from within the fixture code.

    Python attrs must be passed using `pytest` marker e.g.::

        @pytest.mark.attrs({"pool": {"drift_correction": False}})
        def test_pool(pool):
            assert pool.drift_correction = False
    """
    marker = request.node.get_closest_marker("attrs")
    if marker is None:
        attrs = {}
    else:
        attrs = marker.args[0].get(request.fixturename, {})
    return attrs


def get_marker_attribute_values(request):
    """Return attribute values corresponding to the fixture.

    Must be called from within the fixture code.

    Attribute values must be passed using `pytest` marker e.g.::

        @pytest.mark.attribute_values({"mot01": {"Offset": 1.23}})
        def test_motor(mot01):
            assert mot01.offset = 1.23
    """
    marker = request.node.get_closest_marker("attribute_values")
    if marker is None:
        attrs = {}
    else:
        attrs = marker.args[0].get(request.fixturename, {})
    return attrs

def get_marker_kwargs(request):
    """Return creation kwargs corresponding to the fixture.

    Must be called from within the fixture code.

    Attribute values must be passed using `pytest` marker e.g.::

        @pytest.mark.kwargs({"motctrl01" {"properties": {"Prop2": 123}}}})
        def test_motctrl(motctrl01):
            assert motctrl01.ctrl.Prop2 == 123
    """
    marker = request.node.get_closest_marker("kwargs")
    if marker is None:
        kwargs = {}
    else:
        kwargs = marker.args[0].get(request.fixturename, {})
    return kwargs


@pytest.fixture
def create_pool():
    """"Factory as fixture" for creating `~sardana.pool.pool.Pool` objects.
    
    Can be used to create fixtures or directly from tests::

        def test_pool(create_pool):
            pool = create_pool()
            pool.pool_path = "/path/to/tour/controller/classes"

    """
    def _create_pool(kwargs=None):
        _kwargs = {
            "full_name": "pool",
            "name": "pool"
        }
        if kwargs is not None:
            _kwargs.update(kwargs)
        pool = Pool(**_kwargs)
        return pool
    return _create_pool


@pytest.fixture
def pool(create_pool, request):
    """Return a `~sardana.pool.pool.Pool` object.

    By default it is loaded with built-in controller plugins.
    Can be customized with `attrs` and `kwargs` markers.
    """
    pool = create_pool()
    set_obj_attrs(pool, get_marker_attrs(request))
    if len(pool.pool_path) == 0:
        pool.pool_path = []
    return pool


@pytest.fixture
def create_ctrl(pool):
    """"Factory as fixture" for creating
    `~sardana.pool.poolcontroller.PoolController` objects.

    Can be used to create fixtures or directly from tests::

        def test_ctrl(create_ctrl):
            kwargs = {
                "name": "motctrl01",
                "klass": "TangoAttrMotorController",
                "library": "TangoAttrMotorCtrl.py"
                "type": "Motor",
                "properties": {}
            }
            ctrl = create_ctrl(kwargs)
            assert ctrl.is_online() == True
    
    """
    def _create_ctrl(kwargs):
        if "full_name" not in kwargs:
            kwargs["full_name"] = kwargs["name"]
        return pool.create_controller(**kwargs)        
    return _create_ctrl


@pytest.fixture
def create_motor_ctrl(create_ctrl):
    """"Factory as fixture" for creating
    `~sardana.pool.poolcontroller.PoolController` objects of
    motor type.

    Can be used to create fixtures or directly from tests::

        def test_motor_ctrl(create_motor_ctrl):
            kwargs = {              
                "klass": "TangoAttrMotorController",
                "library": "TangoAttrMotorCtrl.py"                
            }
            ctrl = create_motor_ctrl(kwargs)
            assert ctrl.is_online() == True

    """
    def _create_motor_ctrl(kwargs=None):
        _kwargs = {
            "name": "motctrl01",
            "klass": "DummyMotorController",
            "library": "DummyMotorController.py",
            "type": "Motor",
            "properties": {}
        }
        if kwargs is not None:
            _kwargs.update(kwargs)
        return create_ctrl(_kwargs)
    return _create_motor_ctrl


@pytest.fixture()
def motctrl01(create_motor_ctrl, request):
    """Return a `~sardana.pool.poolcontroller.PoolController` object
    of motor type.
    By default it uses the dummy controller plugin.
    It resides in the pool object returned by the `pool` fixture.
    """
    ctrl = create_motor_ctrl(get_marker_kwargs(request))
    set_obj_attrs(ctrl, get_marker_attrs(request))
    ctrl.init_attribute_values(get_marker_attribute_values(request))
    return ctrl


@pytest.fixture
def create_counter_timer_ctrl(create_ctrl):
    """"Factory as fixture" for creating
    `~sardana.pool.poolcontroller.PoolController` objects of
    counter/timer type.

    Can be used to create fixtures or directly from tests::

        def test_counter_timer_ctrl(create_counter_timer_ctrl):
            kwargs = {
                "klass": "TangoAttrCTController",
                "library": "TangoAttrCTCtrl.py"
            }
            ctrl = create_counter_timer_ctrl(kwargs)
            assert ctrl.is_online() == True

    """
    def _create_counter_timer_ctrl(kwargs=None):
        _kwargs = {
            "name": "ctctrl01",
            "klass": "DummyCounterTimerController",
            "library": "DummyCounterTimerController.py",
            "type": "CTExpChannel",
            "properties": {}
        }
        if kwargs is not None:
            _kwargs.update(kwargs)
        return create_ctrl(_kwargs)
    return _create_counter_timer_ctrl


@pytest.fixture()
def ctctrl01(create_counter_timer_ctrl, request):
    """Return a `~sardana.pool.poolcontroller.PoolController` object
    of counter/timer type.
    By default it uses the dummy controller plugin.
    It resides in the pool object returned by the `pool` fixture.
    """
    ctrl = create_counter_timer_ctrl(get_marker_kwargs(request))
    set_obj_attrs(ctrl, get_marker_attrs(request))
    ctrl.init_attribute_values(get_marker_attribute_values(request))
    return ctrl


@pytest.fixture
def create_zerod_ctrl(create_ctrl):
    """"Factory as fixture" for creating
    `~sardana.pool.poolcontroller.PoolController` objects of
    0D experimental channel type.

    Can be used to create fixtures or directly from tests::

        def test_zerod_ctrl(create_zerod_ctrl):
            kwargs = {
                "klass": "TangoAttrZeroDController",
                "library": "TangoAttrZeroDCtrl.py"
            }
            ctrl = create_zerod_ctrl(kwargs)
            assert ctrl.is_online() == True

    """
    def _create_zerod_ctrl(kwargs=None):
        _kwargs = {
            "name": "zerodctrl01",
            "klass": "DummyZeroDController",
            "library": "DummyZeroDController.py",
            "type": "ZeroDExpChannel",
            "properties": {}
        }
        if kwargs is not None:
            _kwargs.update(kwargs)
        return create_ctrl(_kwargs)
    return _create_zerod_ctrl


@pytest.fixture()
def zerodctrl01(create_zerod_ctrl, request):
    """Return a `~sardana.pool.poolcontroller.PoolController` object
    of 0D experimental channel type.
    By default it uses the dummy controller plugin.
    It resides in the pool object returned by the `pool` fixture.
    """
    ctrl = create_zerod_ctrl(get_marker_kwargs(request))
    set_obj_attrs(ctrl, get_marker_attrs(request))
    ctrl.init_attribute_values(get_marker_attribute_values(request))
    return ctrl

@pytest.fixture
def create_oned_ctrl(create_ctrl):
    """"Factory as fixture" for creating
    `~sardana.pool.poolcontroller.PoolController` objects of
    1D experimental channel type.

    Can be used to create fixtures or directly from tests::

        def test_oned_ctrl(create_oned_ctrl):
            kwargs = {
                "klass": "OneDController",
                "library": "OneDCtrl.py"
            }
            ctrl = create_oned_ctrl(kwargs)
            assert ctrl.is_online() == True

    """
    def _create_oned_ctrl(kwargs=None):
        _kwargs = {
            "name": "onedctrl01",
            "klass": "DummyOneDController",
            "library": "DummyOneDController.py",
            "type": "OneDExpChannel",
            "properties": {}
        }
        if kwargs is not None:
            _kwargs.update(kwargs)
        return create_ctrl(_kwargs)
    return _create_oned_ctrl


@pytest.fixture()
def onedctrl01(create_oned_ctrl, request):
    """Return a `~sardana.pool.poolcontroller.PoolController` object
    of 1D experimental channel type.
    By default it uses the dummy controller plugin.
    It resides in the pool object returned by the `pool` fixture.
    """
    ctrl = create_oned_ctrl(get_marker_kwargs(request))
    set_obj_attrs(ctrl, get_marker_attrs(request))
    ctrl.init_attribute_values(get_marker_attribute_values(request))
    return ctrl

@pytest.fixture
def create_twod_ctrl(create_ctrl):
    """"Factory as fixture" for creating
    `~sardana.pool.poolcontroller.PoolController` objects of
    2D experimental channel type.

    Can be used to create fixtures or directly from tests::

        def test_twod_ctrl(create_twod_ctrl):
            kwargs = {
                "klass": "TwoDController",
                "library": "TwoDCtrl.py"
            }
            ctrl = create_twod_ctrl(kwargs)
            assert ctrl.is_online() == True

    """
    def _create_twod_ctrl(kwargs=None):
        _kwargs = {
            "name": "twodctrl01",
            "klass": "DummyTwoDController",
            "library": "DummyTwoDController.py",
            "type": "TwoDExpChannel",
            "properties": {}
        }
        if kwargs is not None:
            _kwargs.update(kwargs)
        return create_ctrl(_kwargs)
    return _create_twod_ctrl


@pytest.fixture()
def twodctrl01(create_twod_ctrl, request):
    """Return a `~sardana.pool.poolcontroller.PoolController` object
    of 2D experimental channel type.
    By default it uses the dummy controller plugin.
    It resides in the pool object returned by the `pool` fixture.
    """
    ctrl = create_twod_ctrl(get_marker_kwargs(request))
    set_obj_attrs(ctrl, get_marker_attrs(request))
    ctrl.init_attribute_values(get_marker_attribute_values(request))
    return ctrl

@pytest.fixture
def create_ior_ctrl(create_ctrl):
    """"Factory as fixture" for creating
    `~sardana.pool.poolcontroller.PoolController` objects of
    IORegister type.

    Can be used to create fixtures or directly from tests::

        def test_ior_ctrl(create_ior_ctrl):
            kwargs = {
                "klass": "TangoAttrIORController",
                "library": "TangoAttrIORCtrl.py"
            }
            ctrl = create_ior_ctrl(kwargs)
            assert ctrl.is_online() == True

    """
    def _create_ior_ctrl(kwargs=None):
        _kwargs = {
            "name": "iorctrl01",
            "klass": "DummyIORController",
            "library": "DummyIORController.py",
            "type": "IORegister",
            "properties": {}
        }
        if kwargs is not None:
            _kwargs.update(kwargs)
        return create_ctrl(_kwargs)
    return _create_ior_ctrl


@pytest.fixture()
def iorctrl01(create_ior_ctrl, request):
    """Return a `~sardana.pool.poolcontroller.PoolController` object
    of IORegister type.
    By default it uses the dummy controller plugin.
    It resides in the pool object returned by the `pool` fixture.
    """
    ctrl = create_ior_ctrl(get_marker_kwargs(request))
    set_obj_attrs(ctrl, get_marker_attrs(request))
    ctrl.init_attribute_values(get_marker_attribute_values(request))
    return ctrl


@pytest.fixture
def create_tg_ctrl(create_ctrl):
    """"Factory as fixture" for creating
    `~sardana.pool.poolcontroller.PoolController` objects of
    TriggerGate type.

    Can be used to create fixtures or directly from tests::

        def test_tg_ctrl(create_tg_ctrl):
            kwargs = {
                "klass": "TriggerGateController",
                "library": "TriggerGateCtrl.py"
            }
            ctrl = create_tg_ctrl(kwargs)
            assert ctrl.is_online() == True

    """
    def _create_tg_ctrl(kwargs=None):
        _kwargs = {
            "name": "tgctrl01",
            "klass": "DummyTriggerGateController",
            "library": "DummyTriggerGateController.py",
            "type": "TriggerGate",
            "properties": {}
        }
        if kwargs is not None:
            _kwargs.update(kwargs)
        return create_ctrl(_kwargs)
    return _create_tg_ctrl


@pytest.fixture()
def tgctrl01(create_tg_ctrl, request):
    """Return a `~sardana.pool.poolcontroller.PoolController` object
    of TriggerGate type.
    By default it uses the dummy controller plugin.
    It resides in the pool object returned by the `pool` fixture.
    """
    ctrl = create_tg_ctrl(get_marker_kwargs(request))
    set_obj_attrs(ctrl, get_marker_attrs(request))
    ctrl.init_attribute_values(get_marker_attribute_values(request))
    return ctrl


@pytest.fixture
def create_element(request):
    """"Factory as fixture" for creating
    `~sardana.pool.poolelement.PoolElement` objects.

    Can be used to create fixtures or directly from tests::

        def test_element(motctrl01, create_element):
            kwargs = {
                "type": "Motor",
                "name": "mot01",
                "ctrl_id": motctrl01.id,
                "axis": 1
            }
            element = create_element(kwargs)
            assert element.state == State.On
    """
    def _create_element(ctrl, kwargs):
        pool = ctrl.pool
        if "full_name" not in kwargs:
            kwargs["full_name"] = kwargs["name"]
        elem = pool.create_element(**kwargs)
        # In some complex cases of dependent elements
        # pool.delete_element() fails because pytest
        # keeps reference to the fixtures making it impossible
        # to delete the objects from the finalizer.
        # At least call ctrl.remove_element() to ensure call of DeleteDevice()
        # for physical element controllers.
        request.addfinalizer(lambda: ctrl.remove_element(elem))
        return elem
    return _create_element


@pytest.fixture
def create_motor(create_element):
    """"Factory as fixture" for creating
    `~sardana.pool.poolmotor.PoolMotor` objects.

    Can be used to create fixtures or directly from tests::

        def test_motor(motctrl01, create_motor):
            motor = create_motor(motctrl01, axis=6)
            assert motor.state == State.On
    """
    def _create_motor(motctrl, axis=None, kwargs=None):        
        assert axis is not None or kwargs is not None
        _kwargs = {
            "type": "Motor",
            "ctrl_id": motctrl.id,
        }
        if axis is not None:
            _kwargs["axis"] = axis
            name = "mot{:02d}".format(axis)
            _kwargs["name"] = name
        if kwargs is not None:
            _kwargs.update(kwargs)
        return create_element(motctrl, _kwargs)
    return _create_motor


def mot(create_motor, motctrl01, request):
    """Return a `~sardana.pool.poolmotor.PoolMotor` object which axis
    number is determined from the last two digits of the fixture
    name. It is handled by the controller object returned by
    the `motctrl01` fixture.
    """
    axis = int(request.fixturename[-2:])
    mot = create_motor(motctrl01, axis, get_marker_kwargs(request))
    set_obj_attrs(mot, get_marker_attrs(request))
    mot.init_attribute_values(get_marker_attribute_values(request))
    return mot


for axis in range(1, 5):
    fixture_name = "mot{:02d}".format(axis)
    fixture = pytest.fixture(mot, name=fixture_name)
    setattr(sys.modules[__name__], fixture_name, fixture)


@pytest.fixture
def create_counter_timer(create_element):
    """"Factory as fixture" for creating
    `~sardana.pool.poolcountertimer.PoolCounterTimer` objects.

    Can be used to create fixtures or directly from tests::

        def test_counter_timer(ctctrl01, create_counter_timer):
            ct = create_counter_timer(ctctrl01, axis=1)
            assert ct.state == State.On
    """
    def _create_counter_timer(ctctrl, axis=None, kwargs=None):
        assert axis is not None or kwargs is not None
        _kwargs = {
            "type": "CTExpChannel",
            "ctrl_id": ctctrl.id,
        }
        if axis is not None:
            _kwargs["axis"] = axis
            name = "ct{:02d}".format(axis)
            _kwargs["name"] = name
        if kwargs is not None:
            _kwargs.update(kwargs)
        return create_element(ctctrl, _kwargs)
    return _create_counter_timer


def ct(create_counter_timer, ctctrl01, request):
    """Return a `~sardana.pool.poolacqusition.PoolCounterTimer` object
    which axis number is determined from the last two digits of the fixture
    name. It is handled by the controller object returned by
    the `ctctrl01` fixture.
    """
    axis = int(request.fixturename[-2:])
    ct = create_counter_timer(ctctrl01, axis, get_marker_kwargs(request))
    set_obj_attrs(ct, get_marker_attrs(request))
    ct.init_attribute_values(get_marker_attribute_values(request))
    return ct


for axis in range(1, 5):
    fixture_name = "ct{:02d}".format(axis)
    fixture = pytest.fixture(ct, name=fixture_name)
    setattr(sys.modules[__name__], fixture_name, fixture)

@pytest.fixture
def create_zerod(create_element):
    """"Factory as fixture" for creating
    `~sardana.pool.poolzerodexpchannel.Pool0DExpChannel` objects.

    Can be used to create fixtures or directly from tests::

        def test_zerod(zerodctrl01, create_zerod):
            zerod = create_zerod(zerodctrl01, axis=1)
            assert zerod.state == State.On
    """
    def _create_zerod(zerodctrl, axis=None, kwargs=None):
        assert axis is not None or kwargs is not None
        _kwargs = {
            "type": "ZeroDExpChannel",
            "ctrl_id": zerodctrl.id,
        }
        if axis is not None:
            _kwargs["axis"] = axis
            name = "zerod{:02d}".format(axis)
            _kwargs["name"] = name
        if kwargs is not None:
            _kwargs.update(kwargs)
        return create_element(zerodctrl, _kwargs)
    return _create_zerod


def zerod(create_zerod, zerodctrl01, request):
    """Return a `~sardana.pool.poolzerodexpchannel.Pool0DExpChannel` object
    which axis number is determined from the last two digits of the fixture
    name. It is handled by the controller object returned by
    the `zerodctrl01` fixture.
    """
    axis = int(request.fixturename[-2:])
    zerod = create_zerod(zerodctrl01, axis, get_marker_kwargs(request))
    set_obj_attrs(zerod, get_marker_attrs(request))
    zerod.init_attribute_values(get_marker_attribute_values(request))
    return zerod


for axis in range(1, 5):
    fixture_name = "zerod{:02d}".format(axis)
    fixture = pytest.fixture(zerod, name=fixture_name)
    setattr(sys.modules[__name__], fixture_name, fixture)


@pytest.fixture
def create_oned(create_element):
    """"Factory as fixture" for creating
    `~sardana.pool.poolonedexpchannel.Pool1DExpChannel` objects.

    Can be used to create fixtures or directly from tests::

        def test_oned(onedctrl01, create_oned):
            oned = create_oned(onedctrl01, axis=1)
            assert oned.state == State.On
    """
    def _create_oned(onedctrl, axis=None, kwargs=None):
        assert axis is not None or kwargs is not None
        _kwargs = {
            "type": "OneDExpChannel",
            "ctrl_id": onedctrl.id,
        }
        if axis is not None:
            _kwargs["axis"] = axis
            name = "oned{:02d}".format(axis)
            _kwargs["name"] = name
        if kwargs is not None:
            _kwargs.update(kwargs)
        return create_element(onedctrl, _kwargs)
    return _create_oned


def oned(create_oned, onedctrl01, request):
    """Return a `~sardana.pool.poolonedexpchannel.Pool1DExpChannel` object
    which axis number is determined from the last two digits of the fixture
    name. It is handled by the controller object returned by
    the `onedctrl01` fixture.
    """
    axis = int(request.fixturename[-2:])
    oned = create_oned(onedctrl01, axis, get_marker_kwargs(request))
    set_obj_attrs(oned, get_marker_attrs(request))
    oned.init_attribute_values(get_marker_attribute_values(request))
    return oned


fixture_name = "oned01"
fixture = pytest.fixture(oned, name=fixture_name)
setattr(sys.modules[__name__], fixture_name, fixture)


@pytest.fixture
def create_twod(create_element):
    """"Factory as fixture" for creating
    `~sardana.pool.poolonedexpchannel.Pool2DExpChannel` objects.

    Can be used to create fixtures or directly from tests::

        def test_twod(twodctrl01, create_twod):
            twod = create_twod(twodctrl01, axis=1)
            assert twod.state == State.On
    """
    def _create_twod(twodctrl, axis=None, kwargs=None):
        assert axis is not None or kwargs is not None
        _kwargs = {
            "type": "TwoDExpChannel",
            "ctrl_id": twodctrl.id,
        }
        if axis is not None:
            _kwargs["axis"] = axis
            name = "twod{:02d}".format(axis)
            _kwargs["name"] = name
        if kwargs is not None:
            _kwargs.update(kwargs)
        return create_element(twodctrl, _kwargs)
    return _create_twod


def twod(create_twod, twodctrl01, request):
    """Return a `~sardana.pool.poolonedexpchannel.Pool2DExpChannel` object
    which axis number is determined from the last two digits of the fixture
    name. It is handled by the controller object returned by
    the `twodctrl01` fixture.
    """
    axis = int(request.fixturename[-2:])
    twod = create_twod(twodctrl01, axis, get_marker_kwargs(request))
    set_obj_attrs(twod, get_marker_attrs(request))
    twod.init_attribute_values(get_marker_attribute_values(request))
    return twod


fixture_name = "twod01"
fixture = pytest.fixture(twod, name=fixture_name)
setattr(sys.modules[__name__], fixture_name, fixture)


@pytest.fixture
def create_ior(create_element):
    """"Factory as fixture" for creating
    `~sardana.pool.poolioregister.PoolIORegister` objects.

    Can be used to create fixtures or directly from tests::

        def test_ior(iorctrl01, create_ior):
            ior = create_ior(iorctrl01, axis=1)
            assert ior.state == State.On
    """
    def _create_ior(iorctrl, axis=None, kwargs=None):
        assert axis is not None or kwargs is not None
        _kwargs = {
            "type": "IORegister",
            "ctrl_id": iorctrl.id,
        }
        if axis is not None:
            _kwargs["axis"] = axis
            name = "ior{:02d}".format(axis)
            _kwargs["name"] = name
        if kwargs is not None:
            _kwargs.update(kwargs)
        return create_element(iorctrl, _kwargs)
    return _create_ior


def ior(create_ior, iorctrl01, request):
    """Return a `~sardana.pool.poolioregister.PoolIORegister` object
    which axis number is determined from the last two digits of the fixture
    name. It is handled by the controller object returned by
    the `iorctrl01` fixture.
    """
    axis = int(request.fixturename[-2:])
    ior = create_ior(iorctrl01, axis, get_marker_kwargs(request))
    set_obj_attrs(ior, get_marker_attrs(request))
    ior.init_attribute_values(get_marker_attribute_values(request))
    return ior


for axis in range(1, 3):
    fixture_name = "ior{:02d}".format(axis)
    fixture = pytest.fixture(ior, name=fixture_name)
    setattr(sys.modules[__name__], fixture_name, fixture)


@pytest.fixture
def create_tg(create_element):
    """"Factory as fixture" for creating
    `~sardana.pool.pooltriggergate.PoolTriggerGate` objects.

    Can be used to create fixtures or directly from tests::

        def test_tg(tgctrl01, create_ior):
            tg = create_tg(tgctrl01, axis=1)
            assert tg.state == State.On
    """
    def _create_tg(tgctrl, axis=None, kwargs=None):
        assert axis is not None or kwargs is not None
        _kwargs = {
            "type": "TriggerGate",
            "ctrl_id": tgctrl.id,
        }
        if axis is not None:
            _kwargs["axis"] = axis
            name = "tg{:02d}".format(axis)
            _kwargs["name"] = name
        if kwargs is not None:
            _kwargs.update(kwargs)
        return create_element(tgctrl, _kwargs)
    return _create_tg


def tg(create_tg, tgctrl01, request):
    """Return a `~sardana.pool.pooltriggergate.PoolTriggerGate` object
    which axis number is determined from the last two digits of the fixture
    name. It is handled by the controller object returned by
    the `tgctrl01` fixture.
    """
    axis = int(request.fixturename[-2:])
    tg = create_tg(tgctrl01, axis, get_marker_kwargs(request))
    set_obj_attrs(tg, get_marker_attrs(request))
    tg.init_attribute_values(get_marker_attribute_values(request))
    return tg

for axis in range(1, 3):
    fixture_name = "tg0{}".format(axis)
    fixture = pytest.fixture(tg, name=fixture_name)
    setattr(sys.modules[__name__], fixture_name, fixture)


@pytest.fixture
def create_pseudo_motor_ctrl(create_ctrl):
    """"Factory as fixture" for creating
    `~sardana.pool.poolcontroller.PoolPseudoMotorController` objects.

    Can be used to create fixtures or directly from tests::

        def test_pseudo_motor_ctrl(create_pseudo_motor_ctrl):
            kwargs = {              
                "klass": "CustomSlit",
                "library": "CustomSlit.py"                
            }
            ctrl = create_pseudo_motor_ctrl(kwargs)
            assert ctrl.is_online() == True

    """
    def _create_pseudo_motor_ctrl(motors, kwargs=None):
        _kwargs = {
            "name": "slitctrl01",
            "full_name": "slitctrl01",
            "klass": "Slit",
            "library": "Slit.py",
            "type": "PseudoMotor",
            "properties": {},
            "role_ids": [mot.id for mot in motors]
        }
        if kwargs is not None:
            _kwargs.update(kwargs)
        return create_ctrl(_kwargs)
    return _create_pseudo_motor_ctrl


@pytest.fixture()
def slitctrl01(create_pseudo_motor_ctrl, mot01, mot02, request):
    """Return a `~sardana.pool.poolcontroller.PoolPseudoMotorController`
    object. By default it uses the slit controller plugin.
    It resides in the pool object returned by the `pool` fixture.
    """
    ctrl = create_pseudo_motor_ctrl([mot01, mot02], get_marker_kwargs(request))
    set_obj_attrs(ctrl, get_marker_attrs(request))
    ctrl.init_attribute_values(get_marker_attribute_values(request))
    return ctrl


@pytest.fixture
def create_pseudo_motor(create_element):
    """"Factory as fixture" for creating
    `~sardana.pool.poolelement.PoolPseudoMotor` objects.

    Can be used to create fixtures or directly from tests::

        def test_element(slitctrl01, create_pseudo_motor):
            kwargs = {
                "name": "gap01",
                "axis": 1
            }
            gap01 = create_pseudo_motor(kwargs)
            assert gap01.state == State.On
    """
    def _create_pseudo_motor(ctrl, kwargs=None):
        _kwargs = {
            "type": "PseudoMotor",
            "ctrl_id": ctrl.id,
            "user_elements": ctrl._motor_ids
        }
        if kwargs is not None:
            _kwargs.update(kwargs)
        return create_element(ctrl, _kwargs)
    return _create_pseudo_motor


@pytest.fixture()
def gap01(create_pseudo_motor, slitctrl01, request):
    """Return a `~sardana.pool.poolpseudomotor.PoolPseudoMotor` object
    corresponding to the Gap role. It is handled by the controller object
    returned by the `slitctrl01` fixture.
    """
    kwargs = {
        "axis": 1,
        "name": "gap01",
    }
    kwargs.update(get_marker_kwargs(request))
    gap = create_pseudo_motor(slitctrl01, kwargs)
    set_obj_attrs(gap, get_marker_attrs(request))
    gap.init_attribute_values(get_marker_attribute_values(request))
    return gap


@pytest.fixture()
def offset01(create_pseudo_motor, slitctrl01, request):
    """Return a `~sardana.pool.poolpseudomotor.PoolPseudoMotor` object
    corresponding to the Offset role. It is handled by the controller object
    returned by the `slitctrl01` fixture.
    """
    kwargs = {
        "axis": 2,
        "name": "offset01",
    }
    kwargs.update(get_marker_kwargs(request))
    offset = create_pseudo_motor(slitctrl01, kwargs)
    set_obj_attrs(offset, get_marker_attrs(request))
    offset.init_attribute_values(get_marker_attribute_values(request))
    return offset


@pytest.fixture
def create_motor_group():
    """"Factory as fixture" for creating
    `~sardana.pool.poolmotorgroup.PoolMotorGroup` objects.

    Can be used to create fixtures or directly from tests::

        def test_motor_group(create_motor_group, mot01, mot02):
            motgrp = create_motor_group([mot01, mot02]])
            assert motgrp.state == State.On

    """
    def _create_motor_group(motors, kwargs=None):
        pool = motors[0].pool
        _kwargs = {
            "name": "motgrp",
            "user_elements": [m.id for m in motors],
        }
        if kwargs is not None:
            _kwargs.update(kwargs)
        if "full_name" not in _kwargs:
            _kwargs["full_name"] = _kwargs["name"]
        return pool.create_motor_group(**_kwargs)
    return _create_motor_group


@pytest.fixture()
def motgrp0102(create_motor_group, mot01, mot02, request):
    """Return a `~sardana.pool.poolmotorgroup.PoolMotorGroup` object
    handling motors returned by the `mot01` and `mot02` fixtures.
    It resides in the pool object returned by the `pool` fixture.
    """
    kwargs = {"name": "motgrp0102"}
    kwargs.update(get_marker_kwargs(request))
    motgrp = create_motor_group([mot01, mot02], kwargs)
    set_obj_attrs(motgrp, get_marker_attrs(request))
    return motgrp


@pytest.fixture
def create_measurement_group():
    """"Factory as fixture" for creating
    `~sardana.pool.poolmeasurementgroup.PoolMeasurementGroup` objects.

    Can be used to create fixtures or directly from tests::

        def test_measurement_group(create_measurement_group, ct01, ct02):
            mntgrp = create_measurement_group([ct01, ct02]])
            assert mntgrp.state == State.On

    """
    def _create_measurement_group(channels, kwargs=None):
        pool = channels[0].pool
        _kwargs = {
            "name": "mntgrp",
            "user_elements": [m.id for m in channels],
        }
        if kwargs is not None:
            _kwargs.update(kwargs)
        if "full_name" not in _kwargs:
            _kwargs["full_name"] = _kwargs["name"]
        return pool.create_measurement_group(**_kwargs)
    return _create_measurement_group


@pytest.fixture()
def mntgrp01(create_measurement_group, ct01, ct02, ct03, ct04, request):
    """Return a `~sardana.pool.poolmeasurementgroup.PoolMeasurementGroup` object
    containing four CounterTimer channels returned by the `ct01`, `ct02`, `ct03`
    and `ct04` fixtures.
    It resides in the pool object returned by the `pool` fixture.
    """
    kwargs = {"name": "mntgrp01"}
    kwargs.update(get_marker_kwargs(request))
    mntgrp = create_measurement_group([ct01, ct02, ct03, ct04], kwargs)
    set_obj_attrs(mntgrp, get_marker_attrs(request))
    mntgrp.init_attribute_values(get_marker_attribute_values(request))
    return mntgrp


class ActionEvent:
    """Helper class for synchronizing tests with background actions.
    
    Can be used for synchronizing actions start and finish events::

        def test_motor_motion(mot01):
            motion_event = ActionEvent(mot01)
            mot01.position = 10
            motion_event.started.wait(1)
            # here you could do some stuff
            motion_event.done.wait(1)
            assert mot01.position.value == 10
    """

    def __init__(self, element):
        self._element = element
        self.started = threading.Event()
        self.done = threading.Event()
        self._element.add_listener(self.on_element_changed)

    def on_element_changed(self, event_source, event_type, event_value):
        name = event_type.name.lower()
        if name == "state":
            if event_value == State.Moving:
                self.started.set()
            if event_value == State.On:
                self.done.set()


class AttributeListener(object):

    def __init__(self, dtype=object, attr_name="valuebuffer"):
        self.data = {}
        self.dtype = dtype
        self.attr_name = attr_name
        self.data_lock = threading.RLock()

    def event_received(self, *args, **kwargs):
        # s - type: sardana.sardanavalue.SardanaValue
        # t - type: sardana.sardanaevent.EventType
        # v - type: sardana.sardanaattribute.SardanaAttribute e.g.
        #           sardana.pool.poolbasechannel.Value
        s, t, v = args
        if t.name.lower() != self.attr_name:
            return
        # obtaining sardana element e.g. exp. channel (the attribute owner)
        obj_name = s.name
        # obtaining the SardanaValue(s) either from the value_chunk (in case
        # of buffered attributes) or from the value in case of normal
        # attributes
        chunk = v
        idx = list(chunk.keys())
        value = [sardana_value.value for sardana_value in list(chunk.values())]
        # filling the measurement records
        with self.data_lock:
            channel_data = self.data.get(obj_name, [])
            expected_idx = len(channel_data)
            pad = [None] * (idx[0] - expected_idx)
            channel_data.extend(pad + value)
            self.data[obj_name] = channel_data

    def get_table(self):
        '''Construct a table-like array with padded  channel data as columns.
        Return the '''
        with self.data_lock:
            max_len = max([len(d) for d in list(self.data.values())])
            dtype_spec = []
            table = []
            for k in sorted(self.data.keys()):
                v = self.data[k]
                v.extend([None] * (max_len - len(v)))
                table.append(v)
                dtype_spec.append((k, self.dtype))
            a = numpy.array(list(zip(*table)), dtype=dtype_spec)
            return a
