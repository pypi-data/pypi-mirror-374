.. _sardana-adding-elements:

====================
Adding real elements
====================

For the sake of demonstration, let's suppose you want to integrate a slit with
IcePAP-based motors into Sardana.

Before doing anything else you should check the
`Sardana plugins catalogue <https://gitlab.com/sardana-org/sardana-plugins>`_.
There's a high chance that somebody already wrote the plugin for your hardware.
If not, you can :ref:`write the plugin yourself <sardana-controller-howto>`.

Controllers
===========

The controller is a Sardana object that handles the communication with the
hardware (physical controller) or provides an abstraction layer (pseudo
controller).

Before creating the controller instance you need to load the controller
plugin class into the Sardana. To check if it is already loaded use the
:class:`~sardana.macroserver.macros.lists.lsctrllib` macro. If it is not, you will
need to configure the :ref:`controller plugin discovery path <sardana-configuration-pool>`
(``PoolPath`` property) and either restart the Sardana server or call the
:class:`~sardana.macroserver.macros.expert.addctrllib` macro::

  Pool_<ServerName>_<ServerNumber>.put_property({"PoolPath":["<Your controller dir path>"]})

  Example:
  Pool_demo1_1.put_property({"PoolPath":["/home/vagrant/controllers"]})

After that check again with the list macro if the controller class is present and if
yes let's continue...

To create a controller instance you can use
:class:`~sardana.macroserver.macros.expert.defctrl` macro::

  defctrl <class> <name> <roles/properties>

The ``<class>`` parameter is a class name for your controller to use and
``<name>`` is the name of the new controller instance. Roles and properties are
used to configure the controller.

For our IcePAP controller we will use two properties: ``Host`` and ``Port`` of
our IcePAP system::

  defctrl IcepapController ipap01 Host 10.0.0.30 Port 5000

.. note::
  In order to use the controller you must define also a motor and use the created controller as a parameter

.. hint::
  You can use the :class:`~sardana.macroserver.macros.expert.sar_info` macro to
  see the roles and properties available for a controller class.

.. note::
  To learn more about controllers see :ref:`sardana-controller-overview`.

Controller axes
===============

Since single motor controller can have multiple axes corresponding to multiple
motors, we will need to create the elements for these axes. This way the controller
will know which motor to move.

With the :class:`~sardana.macroserver.macros.expert.defelem` macro you can
create any type of controller axis, not only motors::

  defelem <name> <controller> <axis>

``<name>`` is the element name, ``<controller>`` is the controller instance on
which the element should be created and ``<axis>`` is the controller axis number.

Let's add an axis to our IcePAP controller::

  defelem mot01 ipap01 1

.. note::
  To learn more about different element types see the following sections:

  * :ref:`sardana-motor-overview`

  * :ref:`sardana-ior-overview`

  * :ref:`sardana-countertimer-overview`

  * :ref:`sardana-0d-overview`

  * :ref:`sardana-1d-overview`

  * :ref:`sardana-2d-overview`

  * :ref:`sardana-triggergate-overview`

Motors
======

For creating motors you can also use :class:`~sardana.macroserver.macros.expert.defm`
macro instead of :class:`~sardana.macroserver.macros.expert.defelem`.
Its invocation is the same, it's just a shortcut::

  defm mot02 ipap01 2

Pseudomotors
============

To use our slit with more abstract interface we can use the ``Slit`` pseudomotor
controller. To use it, just add the ``Slit`` controller with the
:class:`~sardana.macroserver.macros.expert.defctrl` macro::

  defctrl Slit s0ctrl sl2t=mot01 sl2b=mot02 Gap=s0gap Offset=s0off

For the ``Slit`` controller we use roles. There are two types of roles:

* physical roles - real motors, elements that already exist in Sardana

* pseudo roles - abstract motors that will be created by pseudo controller

The ``Slit`` controller defines two physical roles: ``sl2t`` and ``sl2b``, and
two pseudo roles: ``Gap`` and ``Offset``. Note the difference in syntax for passing
roles and properties to the :class:`~sardana.macroserver.macros.expert.defctrl` macro.

By this point your slit should be accesible from Sardana using real motors as well as
abstract pseudomotor interface.

.. note::
  To learn more about pseudo elements see :ref:`sardana-pseudomotor-overview` and
  :ref:`sardana-pseudocounter-overview`.

.. _sardana-adding-elements-configuration:

Elements configuration
======================

Your newly created elements are ready to be used. But, there are plenty
of additional configurations that will improve the usage experience.

Almost certainly you are using the Tango_ sardana server extension.
So, in continuation we will refer to the Tango features
and explain how to configure them.

Main attributes events
----------------------

Each element has at least one main attribute e.g. motor's position or
experimental channel's value.
These attributes asynchronously notifies the interested clients about the
value changes when an element is involved in a sardana action e.g. a motor
is being moved or an experimental channel is acquiring.
For that need sardana uses the `Tango event system`_.
In order to optimize the server - client communication, Tango will verify
if the value changed enough in order to send the notification, if not,
it will not send it. Note, that at the beginning and at the end of the
action there will be at least one event regardless of the verification result.
You can adjust the change criteria for each main attribute
using the Tango attribute property *abs_change* e.g. using Jive_:

.. image:: /_static/jive_event_abs_change.png
    :width: 680
    :align: center

Here is the list of the main attributes per element type:

===================================================== =======================
Element type                                          Attribute(s)    
===================================================== =======================
:ref:`Motor <sardana-motor-overview>`                 position, dial position
:ref:`PseudoMotor <sardana-pseudomotor-overview>`     position
:ref:`CTExpChannel <sardana-countertimer-overview>`   value
:ref:`ZeroDExpChannel <sardana-0d-overview>`          value
:ref:`PseudoCounter <sardana-pseudocounter-overview>` value
:ref:`IORegister <sardana-ior-overview>`              value
===================================================== =======================

.. important::

  If you don't configure the change criteria differently sardana will use
  default values which may not fit your use case. That's why it is important
  to apply your own configurations. The default values can be accessed
  in Jive_ the same way as for changing them (explained above).


Measurement groups
==================

To create a measurement group use :class:`~sardana.macroserver.macros.expert.defmeas`
macro::

  defmeas <name> <channel_list>

This macro takes the name for the new meaasurement group and the list of
experimetal channels as its arguments. The first channel must be a Sardana internal
channel and at least one of the channels must be a Counter/Timer.

Example::

  defmeas mntgrp01 ct01 ct02 ct03 ct04

.. note::
  To learn more about measurement groups see :ref:`sardana-measurementgroup-overview`.

Removing elements
=================

Each element can be removed using macro corresponding to the element type.
For controllers use :class:`~sardana.macroserver.macros.expert.udefctrl`.
For controller axes use :class:`~sardana.macroserver.macros.expert.udefelem`.
For measurement groups use :class:`~sardana.macroserver.macros.expert.udefmeas`.

Each of these macros takes the list of element names as the argument.

Remember that you cannot remove controllers with elements, so you must remove the
elements prior to removing the controller.

Useful lists
============

To create a controller it's useful to know which controller classes are available.
To do this use :class:`~sardana.macroserver.macros.lists.lsctrllib` macro.
To see the created controllers use :class:`~sardana.macroserver.macros.lists.lsctrl`.
For lists of motors and experimental channels use :class:`~sardana.macroserver.macros.lists.lsm`
and :class:`~sardana.macroserver.macros.lists.lsexp` respectively.
You can display all measurement groups with :class:`~sardana.macroserver.macros.lists.lsmeas`
macro.

Each of these macros accepts regexp filter as the optional argument.

.. seealso:: The path Sardana uses for loading controller classes can be configured.
             See the Configuration section for details.

.. TODO: Create proper link to the configuration description when it's ready

.. _Tango: http://www.tango-controls.org/
.. _Tango event system: https://tango-controls.readthedocs.io/en/latest/development/client-api/cpp-client-programmers-guide.html#events
.. _Jive: https://tango-controls.readthedocs.io/en/latest/tools-and-extensions/built-in/jive/index.html