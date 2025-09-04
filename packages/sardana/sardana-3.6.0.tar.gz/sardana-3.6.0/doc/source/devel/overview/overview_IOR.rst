.. currentmodule:: sardana.pool

.. _sardana-ior-overview:

=======================
I/O register overview
=======================

The IOR is a generic element which allows to write/read from a given hardware
register a value. This value type may be one of: :class:`int`,
:class:`float`, :class:`bool` but the hardware usually expects a fixed type
for a given register.

In contrary to the writing of the :ref:`motor's <sardana-motor-overview>`
position attribute the writing of the IOR's value attribute is an instant
operation.

.. note::
    
    Previously to adding :ref:`sardana-users-motion-discr` into Sardana 
    the preferred way of implementing it was using
    `TangoAttrIORController <https://github.com/ALBA-Synchrotron/sardana-tango/blob/master/sardana_tango/ctrl/TangoAttrIORCtrl.py>`_.
    However the IOR solution does not control the process of
    changing between the discrete positions.
    The discrete motion solution overcomes this limitation and
    should be used now.

The IOR has a very wide range of applications, for example it can serve to
control the :term:`PLC` registers.

.. seealso::

    :ref:`sardana-ior-api`
        the I/O register :term:`API` 

    :class:`~sardana.tango.pool.IORegister.IORegister`
        the I/O register tango device :term:`API`
