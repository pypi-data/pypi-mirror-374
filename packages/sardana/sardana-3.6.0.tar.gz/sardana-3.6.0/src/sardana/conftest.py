import logging
import os
import pytest

import PyTango
from taurus.core.util import whichexecutable
from taurus.core.tango.starter import ProcessStarter

from sardana import sardanacustomsettings
from sardana.tango.macroserver.MacroServer import MacroServerClass
from sardana.macroserver.macros.test import MacroExecutorFactory
from sardana.tango.core.util import (get_free_server, get_free_device,
                                     get_free_alias)


@pytest.fixture(scope="session")
def create_tango_pool():
    """
    .. note::
        The create_tango_pool fixture has been included
        in Sardana on a provisional basis. Backwards incompatible changes
        (up to and including its removal) may occur if
        deemed necessary by the core developers.
    """
    pool_ds_name = getattr(sardanacustomsettings, 'UNITTEST_POOL_DS_NAME')
    pool_name = getattr(sardanacustomsettings, 'UNITTEST_POOL_NAME')
    properties = {}
    # Create Pool    
    db = PyTango.Database()
    # Discover the Pool launcher script
    poolExec = whichexecutable.whichfile("Pool")
    # register Pool server
    pool_ds_name = "Pool/" + pool_ds_name
    pool_free_ds_name = get_free_server(PyTango.Database(),
                                        pool_ds_name)
    _starter = ProcessStarter(poolExec, pool_free_ds_name)
    # register Pool device
    dev_name_parts = pool_name.split('/')
    prefix = '/'.join(dev_name_parts[0:2])
    start_from = int(dev_name_parts[2])
    pool_name = get_free_device(db, prefix, start_from)
    _starter.addNewDevice(pool_name, klass='Pool')
    # Add properties
    if properties:
        for key, values in list(properties.items()):
            db.put_device_property(pool_name,
                                    {key: values})
    # start Pool server
    _starter.startDs(wait_seconds=20)
    
    yield pool_name
    _starter.cleanDb(force=True)
    
        

@pytest.fixture(scope="session")
def create_tango_macroserver(create_tango_pool):
    """
    .. note::
        The create_tango_macroexecutor fixture has been included
        in Sardana on a provisional basis. Backwards incompatible changes
        (up to and including its removal) may occur if
        deemed necessary by the core developers.
    """
    ms_ds_name = getattr(sardanacustomsettings, 'UNITTEST_MS_DS_NAME',
                    "unittest1")
    ms_name = getattr(sardanacustomsettings, 'UNITTEST_MS_NAME',
                "macroserver/demo1/1")
    door_name = getattr(sardanacustomsettings, 'UNITTEST_DOOR_NAME', "door/demo1/1")

    pool_name = create_tango_pool
    properties = {'PoolNames': pool_name}
    
    # Create Macroserver    
    db = PyTango.Database()
    # Discover the MS launcher script
    msExec = whichexecutable.whichfile("MacroServer")
    # register MS server
    ms_ds_name_base = "MacroServer/" + ms_ds_name
    ms_ds_name = get_free_server(db, ms_ds_name_base)
    _msstarter = ProcessStarter(msExec, ms_ds_name)
    # register MS device
    dev_name_parts = ms_name.split('/')
    prefix = '/'.join(dev_name_parts[0:2])
    start_from = int(dev_name_parts[2])
    ms_name = get_free_device(
        db, prefix, start_from)
    _msstarter.addNewDevice(ms_name, klass='MacroServer')
    # register Door device
    dev_name_parts = door_name.split('/')
    prefix = '/'.join(dev_name_parts[0:2])    
    start_from = int(dev_name_parts[2])
    door_name = get_free_device(db, prefix, start_from)
    _msstarter.addNewDevice(door_name, klass='Door')
    setattr(sardanacustomsettings, 'UNITTEST_DOOR_NAME', door_name)    
    # Add properties
    if properties:
        for key, values in list(properties.items()):
            db.put_device_property(ms_name,
                                    {key: values})
    # start MS server
    _msstarter.startDs(wait_seconds=20)
    door = PyTango.DeviceProxy(door_name)
    
    yield door_name

    _msstarter.cleanDb(force=True)

    db = PyTango.Database()
    prop = db.get_device_property(ms_name, "EnvironmentDb")
    ms_properties = prop["EnvironmentDb"]
    if not ms_properties:
        dft_ms_properties = os.path.join(
            MacroServerClass.DefaultEnvBaseDir,
            MacroServerClass.DefaultEnvRelDir)
        ds_inst_name = ms_ds_name.split("/")[1]
        ms_properties = dft_ms_properties % {
            "ds_exec_name": "MacroServer",
            "ds_inst_name": ds_inst_name}
    ms_properties = os.path.normpath(ms_properties)
    extensions = [".bak", ".dat", ".dir"]
    for ext in extensions:
        name = ms_properties + ext
        if not os.path.exists(name):
            continue
        try:
            os.remove(name)
        except Exception as e:
            msg = "Not possible to remove macroserver environment file"
            logging.log(msg)
            logging.log(("Details: %s" % e))
            
@pytest.fixture(scope="session")
def create_sar_demo(create_tango_macroserver):
    """
    .. note::
        The create_sar_demo fixture has been included
        in Sardana on a provisional basis. Backwards incompatible changes
        (up to and including its removal) may occur if
        deemed necessary by the core developers.
    """
    door_name = create_tango_macroserver
    mefact = MacroExecutorFactory()
    macro_executor = mefact.getMacroExecutor(door_name)
    
    macro_executor.run(macro_name='sar_demo')
    