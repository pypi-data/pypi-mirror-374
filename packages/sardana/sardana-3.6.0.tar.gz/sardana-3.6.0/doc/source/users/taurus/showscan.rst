.. _showscan_ui:

========
Showscan
========

Sardana provides widgets for plotting scans either *online* or *offline*.
Currently there are two different widgets for providing these features.
These widgets can be used in your GUI or
:ref:`launched from spock <sardana-spock-showscan>`.

.. _showscan-online:

---------------
Showscan online
---------------

Showscan online is a simplified Taurus application which provides live scan
plots. The number of plots and their configuration depends on the
:ref:`measurement group plotting configuration <expconf_ui_measurementgroup>`.

It can be launched from Spock using the :class:`~sardana.spock.magic.showscan`
command:

.. sourcecode:: spock

    LAB-01-D01 [1]: showscan

or with the console command: ``sardanactl showscan``.

When started it gets populated with empty plots of the
:ref:`active measurement group <activemntgrp>`. As soon as you start
scanning the curves and the legend will start to appear. Even if you change
the active measurement group or you change the plotting configuration the
plots will not get recreated until you start another scan. The purpose of this
behavior is to keep the plotted data available for inspection after the scan
execution.

.. figure:: /_static/showscan-online.png

    Showscan online plotting one physical counter against the motor's
    position.

Another interesting feature of this widget is its multi plot organization when
you ask for plotting multiple curves. You can choose between having a separate
plot per curve or group curves by the selected x axis using the ``--group=single|x-axis``
command line parameter. The option is not available when starting showscan from spock.

.. figure:: /_static/showscan-online-multi.png

    Showscan online plotting three physical counters against the motor's
    position on separate plots (using ``--group=single``).

All axes support *click-to-move*, when the scan is over a motor coordinate, and
the *Plot Axis* is set to ``<mov>`` in the :ref:`measurement group plotting configuration <expconf_ui_measurementgroup>`.
A single left-click into the plot will open a dialog that asks for confirmation
before moving the motor to the position clicked.

.. figure:: /_static/showscan-online-clicktomove.png

    Dialog prompt asking for confirmation before moving the motor to clicked position.

Finally, the *scan point* and the *scan information* panels are available
and offer online updates on the channel values of the current scan point
and some general scan information e.g. scan file, start and end time, etc.
respectively.

.. _showscan-online-infopanels-figure:

.. figure:: /_static/showscan-online-infopanels.png

    Showscan online plotting with separate plots and information panels.

.. _showscan-offline:

----------------
Showscan offline
----------------

Showscan is basically a simple HDF5 viewer application. It can be launched from
Spock using the :func:`showscan offline <sardana.spock.magic.showscan>` command. Without
further arguments, it will show you the result of the last scan in a :term:`GUI`:

.. figure:: /_static/spock_snapshot02.png
    :height: 600

    Scan data viewer in action

:func:`showscan offline <sardana.spock.magic.showscan>` *scan_number* will display
data for the given scan number.

.. note::
	The :func:`showscan offline <sardana.spock.magic.showscan>` application can only read scans
	saved in the HDF5 format.

The scan files are saved on the Sardana server machine, however
:func:`showscan offline <sardana.spock.magic.showscan>` is running on the client one. If it's not
the same machine, you will need to share the scan files between machines, for
example with NFS.

.. note::
	If the path to the file on the server is different than on the client, you
	should use :ref:`directorymap` environment variable to map server paths	to
	client paths.

In order to use the :func:`showscan offline <sardana.spock.magic.showscan>` widget while
scanning, you will need to use the :ref:`HDF5 write session <sardana-users-scan-data-storage-nxscanh5_filerecorder>`
in the SWMR mode, for example:
    
.. sourcecode:: spock

    LAB-01-D01 [1]: newfile /tmp/scans.h5
    ScanDir is      : /tmp
    ScanFile set to : scans.h5
    Next scan is    : #1

    LAB-01-D01 [2]: h5_start_session True
    H5 session open for '/tmp/scans.h5'
            SWMR mode: True
            HDF5 version compatibility: ('v110', 'v110')
    
    LAB-01-D01 [3]: showscan
    Trying to open local scan file /tmp/scans.h5...

    LAB-01-D01 [4]: # now you can execute scans without the need to close the showscan

Otherwise, you will need to close the :func:`showscan offline <sardana.spock.magic.showscan>` for every new scan execution.