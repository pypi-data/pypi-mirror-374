import pytest
from sardana import sardanacustomsettings

from sardana.macroserver.macros.test import (
    MacroExecutorFactory, 
    getMotors, 
    getIORs, 
    getCTs, 
    getControllers,
)


sar_demo_map = {
    "motctrl": getControllers,
    "mot": getMotors,
    "ct": getCTs,
    "ior": getIORs,
}

@pytest.fixture()
def macro_params(request):
    """
    .. note::
        The macro_params fixture has been included in Sardana
        on a provisional basis. Backwards incompatible changes
        (up to and including its removal) may occur if
        deemed necessary by the core developers.
    """
    macro_params = []
    raw_params = request.param
    for p in raw_params:
        name, suffix = p[:-2], p[-2:]
        try:
            nb = int(suffix)
        except ValueError:
            pass
        else:
            try:
                getter = sar_demo_map[name]
            except KeyError:
                pass
            else:
                p = getter()[nb]
        macro_params.append(p)
    return macro_params


@pytest.fixture()
def macro_executor():
    """
    .. note::
        The macro_executor fixture has been included in Sardana
        on a provisional basis. Backwards incompatible changes
        (up to and including its removal) may occur if
        deemed necessary by the core developers.
    """
    door_name = getattr(sardanacustomsettings, 'UNITTEST_DOOR_NAME')
    mefact = MacroExecutorFactory()
    me = mefact.getMacroExecutor(door_name)
    me.registerAll()
    yield me
    me.unregisterAll()
