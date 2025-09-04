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
# the Free Software Fo.undation, either version 3 of the License, or.
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

"""Device Pool part of the kernel consist of one `~sardana.pool.pool.Pool` 
object which acts as:

- container (inherits from `~sardana.sardanacontainer.SardanaContainer`) of
  objects of specific classes inheriting from `~sardana.pool.poolobject.PoolObject`
- facade (implements `Facade pattern <https://en.wikipedia.org/wiki/Facade_pattern>`_)
  to `~sardana.pool.poolcontrollermanager.ControllerManager`

Main categories of objects managed by Device Pool:

- controller e.g. `~sardana.pool.poolcontroller.PoolController`
  or `~sardana.pool.poolcontroller.PoolPseudoMotorController`
- axis element e.g. `~sardana.pool.poolmotor.PoolMotor`
  or `~sardana.pool.poolcountertimer.PoolCounterTimer`
- pseudo axis element e.g. `~sardana.pool.poolpseudomotor.PoolPseudoMotor`
- group e.g. `~sardana.pool.poolmotorgroup.PoolMotorGroup`
- instrument - `~sardana.pool.poolinstrument.PoolInstrument`

.. mermaid::
    :align: center
    :caption: Class diagram of motion related main classes

    classDiagram
        PoolObject <|-- PoolBaseElement
        PoolBaseElement <|-- PoolBaseController
        Controller <|-- MotorController
        MotorController <|-- MyCustomController
        PoolBaseController <|-- PoolController
        PoolBaseController "1" *-- Controller
        PoolController <|-- PoolPseudoMotorController
        PoolBaseController "0..*" *-- PoolElement
        PoolBaseElement <|-- PoolElement
        PoolElement <|-- PoolMotor
        PoolBaseGroup <|-- PoolPseudoMotor
        PoolBaseGroup "1..*" o-- PoolElement
        PoolElement <|-- PoolPseudoMotor
        PoolBaseGroup <|-- PoolGroupElement
        PoolBaseElement <|-- PoolGroupElement
        PoolGroupElement <|-- PoolMotorGroup

        cssClass "Controller,MotorController,MyCustomController" pluginNode
        cssClass "PoolObject,PoolBaseElement,PoolBaseController" coreNode
        cssClass "PoolController,PoolPseudoMotorController" coreNode
        cssClass "PoolBaseElement,PoolElement,PoolMotor" coreNode
        cssClass "PoolPseudoMotor,PoolBaseGroup,PoolGroupElement" coreNode
        cssClass "PoolMotorGroup" coreNode

.. note::
    - the most specific common base class is
      `~sardana.pool.poolbaseelement.PoolBaseElement` 
    - pseudo axis element e.g. `~sardana.pool.poolpseudomotor.PoolPseudoMotor`
      are of axis element and group nature due to multiple inheritance
      from `~sardana.pool.poolelement.PoolElement`
      and `~sardana.pool.poolbasegroup.PoolBaseGroup`   
    - controller is composed from axis elements
    - controller is composed from a plugin
      `~sardana.pool.controller.Controller`
    - group aggregates axis elements

The objects currently under `~sardana.pool.pool.Pool` management
are communicated to the clients with the `Elements` attribute.

`state` of pseudo axis elements or groups is composed from `state`'s of their
associated elements e.g.

- group `state` turns `~sardana.sardanadefs.State.Moving` when one of its
  associated elements reports `~sardana.sardanadefs.State.Moving`
- group `state` turns `~sardana.sardanadefs.State.On` when all of its
  associated elements reports `~sardana.sardanadefs.State.On`

State changes are notified with the publisher-subscriber implementation. 

Motion and acquisition are handled with `~sardana.pool.poolmotion.PoolMotion`
and `~sardana.pool.poolacquisition.PoolAcquisition` respectively
(the latter one is composed from specific sub-actions).
Each axis elements and pseudo axis elements aggregates one action instance
for exclusive use during an independent motion or acquisition.
Groups aggregate a different action instance for grouped motion or acquisition
which involves all elements associated to the group.
"""

__all__ = ["ControllerAPI", "AcqTriggerType", "AcqSynch", "AcqSynchType",
           "AcqMode", "PoolUtil"]

__docformat__ = 'restructuredtext'

from .pooldefs import (ControllerAPI, AcqTriggerType, AcqMode, AcqSynch,
                       AcqSynchType, SynchDomain, SynchParam)
from .poolutil import PoolUtil
from .poolobject import PoolObject
from .poolbaseelement import PoolBaseElement
