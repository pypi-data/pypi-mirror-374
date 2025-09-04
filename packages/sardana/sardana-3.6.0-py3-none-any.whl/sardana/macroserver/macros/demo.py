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

"""This is the demo macro module"""



__all__ = ["sar_demo", "clear_sar_demo", "sar_demo_hkl", "clear_sar_demo_hkl"]

import PyTango

from sardana.macroserver.macro import macro, Type
from sardana.macroserver.msexception import UnknownEnv
from sardana.macroserver.msparameter import WrongParam
from copy import deepcopy

_ENV = "_SAR_DEMO"

_ENV_HKL = "_SAR_DEMO_HKL"


def get_free_names(db, prefix, nb, start_at=1):
    ret = []
    i = start_at
    failed = 96
    while len(ret) < nb and failed > 0:
        name = "%s%02d" % (prefix, i)
        try:
            db.get_device_alias(name)
            failed -= 1
        except:
            ret.append(name)
        i += 1
    if len(ret) < nb or failed == 0:
        raise Exception("Too many sardana demos registered on this system.\n"
                        "Please try using a different tango system")
    return ret


@macro()
def clear_sar_demo(self):
    """Undoes changes done with sar_demo"""
    try:
        SAR_DEMO = self.getEnv(_ENV)
    except:
        self.error("No demo has been prepared yet on this sardana!")
        return

    try:
        _ActiveMntGrp = self.getEnv("ActiveMntGrp")
    except UnknownEnv:
        _ActiveMntGrp = None

    self.print("Removing measurement groups...")

    for mg in deepcopy(SAR_DEMO.get("measurement_groups", ())):
        try:
            self.udefmeas(mg)
            if mg == _ActiveMntGrp:
                self.print("Unsetting ActiveMntGrp (was: %s)" % _ActiveMntGrp)
                self.unsetEnv("ActiveMntGrp")
            SAR_DEMO["measurement_groups"].remove(mg)
        except WrongParam as e:
            self.info("Element {} does not exist so it cannot be removed, skipping. Error message: {}".format(mg, e))
            SAR_DEMO["measurement_groups"].remove(mg)
        except Exception as e:
            self.error("Error occurred when deleting element {}: {}".format(mg, e))

    self.print("Removing elements...")
    for elem in deepcopy(SAR_DEMO.get("elements", ())):
        try:
            self.udefelem(elem)
            SAR_DEMO["elements"].remove(elem)
        except WrongParam as e:
            self.info("Element {} does not exist so it cannot be removed, skipping. Error message: {}".format(elem, e))
            SAR_DEMO["elements"].remove(elem)
        except Exception as e:
            self.error("Error occurred when deleting element {}: {}".format(elem, e))

    self.print("Removing controllers...")
    for ctrl in deepcopy(SAR_DEMO.get("controllers", ())):
        try:
            self.udefctrl(ctrl)
            SAR_DEMO["controllers"].remove(ctrl)
        except WrongParam as e:
            self.info("Controller {} does not exist so it cannot be removed, skipping. Error message: {}".format(ctrl, e))
            SAR_DEMO["controllers"].remove(ctrl)
        except Exception as e:
            self.error("Error occurred when deleting controller {}: {}".format(ctrl, e))

    self.print("Removing instruments...")
    pool = self.getPools()[0]
    for instrument in deepcopy(SAR_DEMO.get("instruments", ())):
        try:
            pool.DeleteElement(instrument)
            SAR_DEMO["instruments"].remove(instrument)
        except Exception as e:
            self.error("Error occurred when deleting instrument {}: {}".format(instrument, e))

    if any(SAR_DEMO.values()):
        self.warning("Some sar_demo elements cannot be removed! Check the error and try again")
    else:
        self.unsetEnv(_ENV)

    self.print("DONE!")

# Default sar_demo's elements quantity
default_elements_quant = {
    "motor": 4,
    "ctexpchannel": 4,
    "zerodexpchannel": 4,
    "onedexpchannel": 1,
    "twodexpchannel": 1,
    "triggergate": 2,
    "iorregister": 2
}

@macro([ 
    ["elements",[
        ["elem_type", Type.String, None, "Element type"],
        ["elem_quant", Type.Integer, 0, "Element quantity"], 
        {'min': 0, 'max': None}
    ], None, "Number of elements to be created per type"]
])
def sar_demo(self, elements):
    """Sets up a demo environment. It creates many elements for testing"""

    try:
        SAR_DEMO = self.getEnv(_ENV)
        self.error("A demo has already been prepared on this sardana")
        return
    except:
        pass

    db = PyTango.Database()

    elements_quant = default_elements_quant.copy()
    for elem_type, elem_quant in elements:
        elem_type_lower = elem_type.lower()
        if elem_type_lower not in elements_quant:
            raise ValueError(
                "element type '{}' is not recognised (allowed types: {})".format(
                    elem_type, list(elements_quant.keys())))
        # Replace the default quantity with the configured one
        elements_quant[elem_type_lower] = elem_quant

    mot_ctrl_name = get_free_names(db, "motctrl", 1)[0]
    ct_ctrl_name = get_free_names(db, "ctctrl", 1)[0]
    zerod_ctrl_name = get_free_names(db, "zerodctrl", 1)[0]
    oned_ctrl_name = get_free_names(db, "onedctrl", 1)[0]
    twod_ctrl_name = get_free_names(db, "twodctrl", 1)[0]
    tg_ctrl_name = get_free_names(db, "tgctrl", 1)[0]
    slit_ctrl_name = get_free_names(db, "slitctrl", 1)[0]
    discrete_pm_ctrl_name = get_free_names(db, "dpmctrl", 1)[0]
    pc_ctrl_name = get_free_names(db, "ioveri0ctrl", 1)[0]
    ior_ctrl_name = get_free_names(db, "iorctrl", 1)[0]

    motor_names = get_free_names(db, "mot", elements_quant["motor"])
    ct_names = get_free_names(db, "ct", elements_quant["ctexpchannel"])
    zerod_names = get_free_names(db, "zerod", elements_quant["zerodexpchannel"])
    oned_names = get_free_names(db, "oned", elements_quant["onedexpchannel"])
    twod_names = get_free_names(db, "twod", elements_quant["twodexpchannel"])
    tg_names = get_free_names(db, "tg", elements_quant["triggergate"])
    gap, offset = get_free_names(db, "gap", 1) + \
        get_free_names(db, "offset", 1)
    discrete_pm = get_free_names(db, "discretepm", 1)[0]
    ioveri0 = get_free_names(db, "ioveri0", 1)[0]
    ior_names = get_free_names(db, "ior", elements_quant["iorregister"])
    mg_name = get_free_names(db, "mntgrp", 1)[0]

    pools = self.getPools()
    if not len(pools):
        self.error('This is not a valid sardana demonstration system.\n'
                   'Sardana demonstration systems must be connect to at least '
                   'one Pool')
        return
    pool = pools[0]

    d = dict(controllers=[], elements=[],
             measurement_groups=[], instruments=[])

    try:
        self.print("Creating motor controller", mot_ctrl_name, "...")
        self.defctrl("DummyMotorController", mot_ctrl_name)
        for axis, motor_name in enumerate(motor_names, 1):
            self.print("Creating motor", motor_name, "...")
            self.defelem(motor_name, mot_ctrl_name, axis)
        d["controllers"].append(mot_ctrl_name)
        d["elements"].extend(motor_names)

        self.print("Creating counter controller", ct_ctrl_name, "...")
        self.defctrl("DummyCounterTimerController", ct_ctrl_name)
        for axis, ct_name in enumerate(ct_names, 1):
            self.print("Creating counter channel", ct_name, "...")
            self.defelem(ct_name, ct_ctrl_name, axis)
        d["controllers"].append(ct_ctrl_name)
        d["elements"].extend(ct_names)

        self.print("Creating 0D controller", zerod_ctrl_name, "...")
        self.defctrl("DummyZeroDController", zerod_ctrl_name)
        for axis, zerod_name in enumerate(zerod_names, 1):
            self.print("Creating 0D channel", zerod_name, "...")
            self.defelem(zerod_name, zerod_ctrl_name, axis)
        d["controllers"].append(zerod_ctrl_name)
        d["elements"].extend(zerod_names)

        self.print("Creating 1D controller", oned_ctrl_name, "...")
        self.defctrl("DummyOneDController", oned_ctrl_name)
        for axis, oned_name in enumerate(oned_names, 1):
            self.print("Creating 1D channel", oned_name, "...")
            self.defelem(oned_name, oned_ctrl_name, axis)
        d["controllers"].append(oned_ctrl_name)
        d["elements"].extend(oned_names)

        self.print("Creating 2D controller", twod_ctrl_name, "...")
        self.defctrl("DummyTwoDController", twod_ctrl_name)
        for axis, twod_name in enumerate(twod_names, 1):
            self.print("Creating 2D channel", twod_name, "...")
            self.defelem(twod_name, twod_ctrl_name, axis)
        d["controllers"].append(twod_ctrl_name)
        d["elements"].extend(twod_names)

        self.print("Creating Slit", slit_ctrl_name, "with", gap, ",", offset, "...")
        sl2t, sl2b = motor_names[:2]
        self.defctrl("Slit", slit_ctrl_name, ["sl2t=" + sl2t, "sl2b=" + sl2b,
                                            "Gap=" + gap, "Offset=" + offset])
        d["controllers"].append(slit_ctrl_name)
        d["elements"].insert(0, gap)
        d["elements"].insert(0, offset)

        self.print("Creating Discrete PseudoMotor controller", discrete_pm_ctrl_name, "with", discrete_pm, "...")
        cont_mot = motor_names[2]
        self.defctrl("DiscretePseudoMotorController", discrete_pm_ctrl_name,
                     ["ContinuousMoveable=" + cont_mot, "DiscreteMoveable=" + discrete_pm])
        d["controllers"].append(discrete_pm_ctrl_name)
        d["elements"].insert(0, discrete_pm)
        self.def_discr_pos(discrete_pm, "in", -1, -3, -.5, .5)
        self.def_discr_pos(discrete_pm, "out", 1, 3, -.5, .5)

        self.print("Creating IoverI0", pc_ctrl_name, "with", ioveri0, "...")
        i, i0 = ct_names[:2]
        self.defctrl("IoverI0", pc_ctrl_name, ["I=" + i, "I0=" + i0,
                                            "IoverI0=" + ioveri0])
        d["controllers"].append(pc_ctrl_name)
        d["elements"].insert(0, ioveri0)

        self.print("Creating trigger controller", tg_ctrl_name, "...")
        self.defctrl("DummyTriggerGateController", tg_ctrl_name)
        for axis, tg_name in enumerate(tg_names, 1):
            self.print("Creating trigger element", tg_name, "...")
            self.defelem(tg_name, tg_ctrl_name, axis)
        d["controllers"].append(tg_ctrl_name)
        d["elements"].extend(tg_names)

        ct_ctrl = self.getController(ct_ctrl_name)
        ct_ctrl.getAttribute("synchronizer").write(tg_name)
        self.print("Connecting trigger/gate element", tg_name,
                   "with counter/timer controller", ct_ctrl_name)

        self.print("Creating IORegister controller", ior_ctrl_name, "...")
        self.defctrl("DummyIORController", ior_ctrl_name)
        for axis, ior_name in enumerate(ior_names, 1):
            self.print("Creating IORegister", ior_name, "...")
            self.defelem(ior_name, ior_ctrl_name, axis)
        d["controllers"].append(ior_ctrl_name)
        d["elements"].extend(ior_names)

        self.print("Creating measurement group", mg_name, "...")
        self.defmeas(mg_name, ct_names)
        d["measurement_groups"].append(mg_name)

        try:
            self.getEnv("ActiveMntGrp")
        except UnknownEnv:
            self.print("Setting %s as ActiveMntGrp" % mg_name)
            self.setEnv("ActiveMntGrp", mg_name)

        self.print("Creating instruments: /slit, /mirror and /monitor ...")
        pool.createInstrument('/slit', 'NXcollimator')
        pool.createInstrument('/mirror', 'NXmirror')
        pool.createInstrument('/monitor', 'NXmonitor')
        d["instruments"].extend(["/slit", "/mirror", "/monitor"])

        self.print("Assigning elements to instruments...")
        self.getMotor(motor_names[0]).setInstrumentName('/slit')
        self.getMotor(motor_names[1]).setInstrumentName('/slit')
        self.getPseudoMotor(gap).setInstrumentName('/slit')
        self.getPseudoMotor(offset).setInstrumentName('/slit')
        self.getMotor(motor_names[2]).setInstrumentName('/mirror')
        self.getMotor(motor_names[3]).setInstrumentName('/mirror')
        self.getCounterTimer(ct_names[1]).setInstrumentName('/monitor')
    except Exception as e:
        self.error("Error while running sar_demo macro. Some elements might be missing! Error raised: {}".format(e))

    if any(d.values()):
        self.setEnv(_ENV, d)
        self.print("DONE!")
    else:
        self.warning("No elements created")


@macro()
def clear_sar_demo_hkl(self):
    """Undoes changes done with sar_demo"""
    try:
        SAR_DEMO_HKL = self.getEnv(_ENV_HKL)
    except:
        self.error("No hkl demo has been prepared yet on this sardana!")
        return

    self.print("Removing hkl demo elements...")
    for elem in SAR_DEMO_HKL.get("elements", ()):
        self.udefelem(elem)

    self.print("Removing hkl demo controllers...")
    for ctrl in SAR_DEMO_HKL.get("controllers", ()):
        self.udefctrl(ctrl)

    self.unsetEnv(_ENV_HKL)

    self.clear_sar_demo()

    self.print("DONE!")


@macro()
def sar_demo_hkl(self):
    """Sets up a demo environment. It creates many elements for testing"""

    self.sar_demo()

    try:
        SAR_DEMO_HKL = self.getEnv(_ENV_HKL)
        self.error("An hkl demo has already been prepared on this sardana")
        return
    except:
        pass

    db = PyTango.Database()

    motor_ctrl_name = get_free_names(db, "motctrl", 1)[0]
    hkl_ctrl_name = get_free_names(db, "hklctrl", 1)[0]

    motor_names = []
    for motor in ["mu", "omega", "chi", "phi", "gamma", "delta"]:
        motor_names += get_free_names(db, motor, 1)

    pseudo_names = []
    for pseudo in ["h", "k", "l",
                   "psi",
                   "q", "alpha",
                   "qper", "qpar"]:
        pseudo_names += get_free_names(db, pseudo, 1)

    pools = self.getPools()
    if not len(pools):
        self.error('This is not a valid sardana demonstration system.\n'
                   'Sardana demonstration systems must be connect to at least '
                   'one Pool')
        return
    pool = pools[0]

    self.print("Creating motor controller", motor_ctrl_name, "...")
    self.defctrl("DummyMotorController", motor_ctrl_name)
    for axis, motor_name in enumerate(motor_names, 1):
        self.print("Creating motor", motor_name, "...")
        self.defelem(motor_name, motor_ctrl_name, axis)

    self.print("Creating hkl controller", hkl_ctrl_name, "...")
    self.defctrl("DiffracE6C", hkl_ctrl_name,
                 ["mu=" + motor_names[0],  # motor role
                  "omega=" + motor_names[1],
                  "chi=" + motor_names[2],
                  "phi=" + motor_names[3],
                  "gamma=" + motor_names[4],
                  "delta=" + motor_names[5],
                  "h=" + pseudo_names[0],  # pseudo role
                  "k=" + pseudo_names[1],
                  "l=" + pseudo_names[2],
                  "psi=" + pseudo_names[3],
                  "q=" + pseudo_names[4],
                  "alpha=" + pseudo_names[5],
                  "qper=" + pseudo_names[6],
                  "qpar=" + pseudo_names[7],
                  "diffractometertype", "E6C"])

    controllers = motor_ctrl_name, hkl_ctrl_name
    elements = pseudo_names + motor_names
    d = dict(controllers=controllers, elements=elements)
    self.setEnv(_ENV_HKL, d)

    self.print("DONE!")
