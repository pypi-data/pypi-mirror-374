.. _pmtv:

PoolMotorTV User’s Interface
-----------------------------

Sardana provides a widget to display and operate any Sardana moveables.
As all Taurus widget it needs at least a model, but several can be given
to this widget,
The widget exports the Sardana moveable models as Taurus attributes.

The :class:`~sardana.taurus.qt.qtgui.extra_pool.poolmotor.PoolMotorTV`
allows:

    - Move relative/absolute any moveable to a set point
    - Abort a movement
    - or simply monitor the moveables

.. image:: /_static/pmtv.png
    :align: center

Moreover, this widget allows you to access to the moveable configuration via a
context menu (right-click over the moveable name) See the image bellow. Also you
can enable the ``expert mode`` option in the same context menu. This option
add new buttons under the line edit of the setting point. These buttons allows
you to move the moveable to their limits (with just one click) or move it
in a direction when the button is pressed but **only** if limits have
been configured.

.. image:: /_static/pmtv_attr_editor.png
    :align: center


Limits
^^^^^^

Moveables may have physical limits - physical motor usually have them, or
software limits - defined by the user and verified by sardana software at runtime.

PoolMotorTV try to summarize state of limits in as compact and possible way
using just two icons.

.. image:: /_static/pmtv_limits.png
    :align: center

The above form presents all the possible states of the limit icons
(analysis refers to negative limits):

- mot01 is a physical motor and its negative limit is active.
  At the first look it can not be distinguished which limit is active
  (software, hardware or both) and one needs to access the tooltip to get this detail.
- mot02 is a physical motor with none of the limits active. At the first look
  it can not be determined if the software limit is defined and one needs to access
  the tooltip to get this detail. But the limit icon is enabled since physical motors
  usually have hardware limits.
- gap01 is a pseudo motor and its negative limit is active. It must be the software
  limit because pseudo motors can not have hardware limits.
- offset01 is a pseudo motor with negative software limit defined but not active.
- alpha01 is a pseudo motor without negative software limit defined.
