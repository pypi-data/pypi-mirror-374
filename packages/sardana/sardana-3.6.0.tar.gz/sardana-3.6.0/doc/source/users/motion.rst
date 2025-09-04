.. _sardana-users-motion:

======
Motion
======

Sardana provides advanced solutions for motion. By motion we understand
a controlled process of changing any set point, which could be, a physical motor's position,
temperature set point of a temperature controller or a voltage of a power supplier, etc.

In this chapter we just want to list all the features related to motion
and eventually point you to more detailed information. It is not necessary to
understand them if you follow the order of this documentation guide - you will
step by them sooner or later.

We call a sardana element involved in the motion process a :ref:`motor <sardana-motor-overview>`.
Motors can be intergrated into sardana by means of :ref:`MotorController <sardana-motorcontroller-howto-basics>`
plugin classes.

Some times you need to control the motion by means of an interface which
is more meaningful to you, for example, your physical motor acts on a
linear to angular translation and you would like to act on the motor in the
angular dimension. This is solved in sardana by a :ref:`pseudo motor <sardana-pseudomotor-overview>`.
Pseudo motors calculations can be intergrated into sardana by means of :ref:`PseudoMotorController <sardana-pseudomotorcontroller-howto-basics>` plugin classes.

Other motion features:

* :term:`user position` to/from :term:`dial position` conversion
* :ref:`synchronized start of multiple axes motion <sardana-motorcontroller-howto-mutiple-motion>`
* emergency break
* physical motor backlash correction
* :ref:`pseudo motor drift correction <sardana-pseudomotor-api-driftcorrection>`

.. _sardana-users-motion-discr:

Discrete Motion
---------------

Some times you would like to operate your :term:`moveable` by means of
sending it to some discrete positions. For example, discrete positions
of a linear translation of a mirror could be used to select a given mirror
coating stripe. Furthermore each coating stripe spans
over a limited range of linear translation displacement, so any of the
positions within a given range should indicate which stripe is currently
selected.

Sardana comes with a built-in controller plugin:
``DiscretePseudoMotorController`` that you could use to translate
a continuous displacement of a :term:`moveable` into a discrete
displacement using a :ref:`pseudo motor <sardana-pseudomotor-overview>`.

You could use the following macros:
:class:`~sardana.macroserver.macros.discrete.def_discr_pos`
:class:`~sardana.macroserver.macros.discrete.udef_discr_pos`
and :class:`~sardana.macroserver.macros.discrete.prdef_discr`
to change the configuration of the discrete pseudo motor at runtime.

.. note::
    
    Previously to adding discrete motion into Sardana 
    the preferred way of implementing it was using
    `TangoAttrIORController <https://github.com/ALBA-Synchrotron/sardana-tango/blob/master/sardana_tango/ctrl/TangoAttrIORCtrl.py>`_.
    However the :ref:`sardana-ior-overview` solution does not control the process of
    changing between the discrete positions.
    The discrete motion solution overcomes this limitation and
    should be used now.


