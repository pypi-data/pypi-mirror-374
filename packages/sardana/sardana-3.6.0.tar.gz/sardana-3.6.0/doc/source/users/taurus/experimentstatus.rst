.. currentmodule:: sardana.taurus.qt.qtgui.expstatus

.. _expstatus_ui:


=======================================
Experiment Status user interface
=======================================

.. contents::

Experiment Status widget a.k.a. ``expstatus`` is a complete interface to view the status of the elements
and running macros. It consists of two main panels:

* Door status and macro stack (left panel)

* Elements status and information (right panel)

The widget can be used in either *only reserved elements* (default mode) and *view all elements*.

In the only reserved elements mode the elements shown are the ones currently being used by a macro.
It is useful when a macro is stuck and you want to release the elements being used.

In the view all elements mode the elements shown are all the available ones. It is useful when you want
to have an overview of all the elements, along with their status and values.

Both modes allow you to *stop*, *abort*, *release* and *reconfig* the elements.


.. _expstatus_ui_startingwidget:

Starting the widget
-------------------
The widget is used by running ``sardanactl expstatus``. A dialog will show up allowing you to choose the
MacroServer and the Pool you wish to connect to.

.. figure:: /_static/expstatus_pick_dialog.png
   :width: 50%
   :figwidth: 100%
   :align: center

   Door dialog



Alternatively, you may use parameters to skip this dialog:

.. sourcecode:: bash

    Usage: sardanactl expstatus [OPTIONS] [DOOR_NAME]

    Experiment status widget GUI.

    Provides a view of elements reserved by a running macro, allowing to stop them if they are stuck.

    Options:
      -a, --all / --no-all  Show all elements or only the ones currently being
                            used.
      --help                Show this message and exit.

An example on how to run the widget using parameters would be like so:
``sardanactl expstatus door/demo1/1 -a``. Notice how by giving the *Door* as an argument, it will
automatically launch the widget, instead of showing the dialog to pick a *Door*.
At the same time, using *-a* as argument, modifies the default behaviour and shows
all the elements from start.



.. _expstatus_ui_usingwidget:

Using the widget
-------------------
Once the widget is started, it will look similar to this picture.


.. figure:: /_static/expstatus_main_window.png
   :width: 100%
   :figwidth: 100%
   :align: center

   Main window

Keep in mind that the previous image is showing all the available elements. The default behaviour will
only show elements currently being used by a macro, and thus will be empty if no macro is running.


.. _expstatus_ui_usingwidget_typycalusage:

Typical usage
~~~~~~~~~~~~~

When a macro gets stuck, or you don't know what it is doing, then open the expstatus widget and show macro elements. If you think that something is wrong, then try to interrupt the macro first (you can do it from your macro execution client e.g. spock) or from the expstatus widget: stop, abort and eventually release (you may need to exeute the release more than once). Second, try to reconfig the element(s) that are not ready to use (in Fault or Moving state).


.. _expstatus_ui_usingwidget_leftpanel:

Left panel
~~~~~~~~~~

This panel shows you a brief summary of the current Door status along with buttons to conrol it:

* Button *Show macro elements* - will regenerate the right panel showing only the elements currently
  being used by a macro.
* Button *Show all elements* - will regenerate the right panel showing all the elements.
* Door status - shows the status, along with the macrostack.
* Button *STOP* - will stop the macro and under the hood send the *stop* command to all the elements being used by the current macro.
* Button *ABORT* - will abort the macro and under the hood send the *abort* command to all the elements being used by the current macro.
* Button *RELEASE* - will release the macro and under the hood send the *release* command to all the elements being used by the current macro. Note: you should use this option only if it is not possible to stop/abort.


.. _expstatus_ui_usingwidget_rightpanel:

Right panel
~~~~~~~~~~~

This panel shows a list of the elements. As already mentioned, it may show all the elements or only
the ones currently being used by a macro. They are grouped by type in collapsable sublists.

The featured values for each element are:

* Element name
* State
* Status
* Attribute
* Actions:
    - RECONFIG
    - STOP
    - ABORT
    - RELEASE

Additionally, there is a search bar at the top to filter by the element name.