.. _sardana-coding-guide:

==============================
Sardana development guidelines
==============================

Overview
--------

This document describes Sardana from the perspective of developers. Most 
importantly, it gives information for people who want to contribute code to the 
development of Sardana. So if you want to help out, read on!

How to contribute to Sardana
----------------------------

Sardana development is managed with the `Sardana GitLab project
<https://gitlab.com/sardana-org/sardana>`_. 

Apart from directly contributing code, you can contribute to Sardana in many
ways, such as reporting bugs or proposing new features. In all cases you will
probably need a GitLab.com account and you are strongly encouraged to subscribe to the
`sardana-devel and sardana-users mailing lists <https://sourceforge.net/p/sardana/mailman/>`_.

We also invite you to join the regular project `follow-up meetings <https://gitlab.com/sardana-org/sardana-followup>`_.
These are announced on the previously mentioned mailing list.

Detailed instructions on how to contribute to code or documentation can be found in
`CONTRIBUTING.md <https://gitlab.com/sardana-org/sardana/-/blob/develop/CONTRIBUTING.md>`_.

General design
--------------

.. automodule:: sardana
   :noindex:

Software layers
---------------

The main software layers of sardana are:

- client: `sardana.taurus` and `sardana.spock`
- server extension: `sardana.tango`
- core a.k.a. kernel: `sardana.pool` and `sardana.macroserver`
- plugins: built-in (`sardana.pool.poolcontrollers` and
  `sardana.macroserver.macros`) and third-party (sardana-extras_)

.. figure:: /_static/software_layers.png
    :align: center
    
    Main software layers of sardana on example of Device Pool
    (including controller and axis element)

In continuation we point you to more detailed information about each of them.

Client
^^^^^^
In the wide range of built-in sardana clients we include:

- PyQt_ based GUI widgets e.g. :ref:`macroexecutor_ui`, :ref:`expconf_ui`, etc.
- IPython_ based CLI called :ref:`sardana-spock`
- MacroServer which is a client of Device Pool objects

All of them underneath use Taurus_ library and one of these model extensions:

- Sardana-Taurus model API `sardana.taurus.core.tango.sardana`
- Sardana-Taurus Qt model API `sardana.taurus.qt.qtcore.tango.sardana`

Sardana background activities e.g. motion and acquisition actions or macro execution
send Tango_ event notifications about the state changes. Clients then synchronize
with these events using `~taurus.core.util.event.AttributeEventWait` class.

.. _sardana-coding-guide-spock:

Spock
"""""

.. automodule:: sardana.spock
   :noindex:

Server extension
^^^^^^^^^^^^^^^^

At the time of writing of this documentation, the only one production ready
server extension is implemented using Tango_, hence the remaining part of
this guideline will refer to it.
Nevertheless it was proofed that sardana could be used with a different
middleware e.g. sardana-jupyter_ project shows how to run MacroServer
within JupyterLab_.

Server extension is a thin layer which principal responsibilities are:

- instantiation of core classes based on the configuration and keeping their
  references
- redirecting requests to kernel objects
- propagating events from the kernel objects

.. automodule:: sardana.tango
  :noindex:

Sardana kernel
--------------

Within sardana kernel resides objects of the sardana core classes. There are two principal
objects:

- MacroServer - macro execution engine
- Device Pool - repository of hardware elements

Pool
^^^^

.. automodule:: sardana.pool
   :noindex:

MacroServer
^^^^^^^^^^^

.. automodule:: sardana.macroserver
  :noindex:

Plugins
-------

In sardana we distinguish the following plugin types:

- macros
- recorders
- controllers

Manager classes e.g. `~sardana.pool.poolcontrollermanager.ControllerManager` or
`~sardana.macroserver.msmacromanager.MacroManager` are mainly responsible for:

- discovery and reloading
- act as container of plugins
- factory of plugin instances

Plugins are represented by meta classes e.g. `~sardana.pool.poolmetacontroller.ControllerClass`
or `~sardana.macroserver.msmetamacro.MacroClass`.

Sardana plugins discovery is based on directory scanning and python modules introspection.
The scanning process looks for classes inheriting from a certain base class
e.g. `~sardana.pool.controller.MotorController` or specially decorated functions
e.g. `~sardana.macroserver.macro.macro` and if found they are loaded into the kernel
and available for instantiation. Plugins discovery takes place on the server startup
and can be executed on user request at runtime.

Sardana comes with a catalogue of built-in plugins and allows for overriding of plugins
based on the name. By means of configuration you define which directories
and in which order (relevant for the overriding mechanism) will be scanned.

.. note::
    SEP19_ proposes to add a new way of registering plugins based on `setuptools` Entry Points.


.. _Tango: http://www.tango-controls.org/
.. _sardana-extras: https://gitlab.com/sardana-org/sardana-extras
.. _Taurus: http://taurus-scada.org/
.. _PyQt: https://riverbankcomputing.com/software/pyqt
.. _IPython: http://ipython.org/
.. _JupyterLab: https://jupyter.org/
.. _sardana-jupyter: https://gitlab.com/sardana-org/sardana-jupyter
.. _SEP19: https://gitlab.com/sardana-org/sardana/-/merge_requests/1328
