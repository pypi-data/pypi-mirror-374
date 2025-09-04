.. currentmodule:: sardana.pool.pooltriggergate

.. _sardana-triggergate-api:

=============================
Trigger/Gate API reference
=============================

The trigger/gate element represents synchronization devices like for example
the digital trigger and/or gate generators that are used to synchronize the
experimental channels.

Trigger or gate characteristics could be described in either the time and/or
the position configuration domains.

Time domain
-----------

In the time domain, elements are configured in time units (seconds) and
generation of the synchronization signals is based on passing time.

Position domain
---------------

The concept of position domain is based on the relation between
the trigger/gate and the moveable element. In the position domain,
elements are configured in distance units of the moveable element configured as
the feedback source (this could be mm, mrad, degrees, etc.). In this case
generation of the synchronization signals is based on receiving updates from
the source.

There exist different types of hardware capable to synchronize in position
domain by means of processing encoder signals and generating synchronization signals:

- Motion controllers e.g. IcePAP, Pmac, etc.
- *Versatile* controllers e.g. Pandabox, PiLC, etc.

These devices consist of set of inputs (encoders signals) and outputs
(synchronization signals) and usually can work in two modes, where:

- *coupled mode* - one input is coupled to one output
- *multiplexor mode* - many inputs may produce synchronization signals on many outputs

Each trigger/gate element supporting position domain must be configured with ``moveable_on_input``
attribute which value should reflect the hardware connection between the moveable feedback signal 
(encoder) and the trigger/gate input id.

Attributes
----------

A trigger/gate has a ``state``, and a ``index`` attributes. The state
indicates at any time if the trigger/gate is stopped, in alarm or moving.
The index, indicates the current trigger/gate index.

Trigger/gate elements will also have:

**moveable_on_input**

Its value differs depending on the supported mode of a given trigger/gate element:

- for the coupled mode it is a name or full name (:obj:`str`) of the moveable
  which encoder is connected to the input
- for the multiplexor mode it is a :obj:`dict` mapping names or full names (:obj:`str`)
  of moveables which encoders are connected on inputs to the inputs' IDs (:obj:`int`)

.. seealso::

    :ref:`sardana-triggergate-overview`
        the trigger/gate overview 

    :class:`~sardana.tango.pool.TriggerGate.TriggerGate`
        the trigger/gate tango device :term:`API`

    :class:`~sardana.pool.pooltriggergate.PoolTriggerGate`
        the trigger/gate class :term:`API`
