
.. _sardana-installing:

==========
Installing
==========

Installing with pip (platform-independent)
------------------------------------------

Sardana can be installed using pip. The following command will
automatically download and install the latest release of Sardana (see
pip3 --help for options)::

       pip3 install sardana

Note that for sardana > 3.4.0, this will only install the minimal dependencies.
To install all dependencies, use::

       pip3 install "sardana[all]"

If you only want dependencies to run :ref:`sardana-spock` and :ref:`sardana-taurus`::

       pip3 install "sardana[spock,qt]"

You can test the installation by running::

       python3 -c "import sardana; print(sardana.__version__)"

In sardana 3.6.0, the config tool was moved to its own `repository <https://gitlab.com/sardana-org/sardana-config>`_.
Install it with::

       pip3 install sardana-config

Note: Installing sardana with pip3 might require building some dependencies
like guiqwt or PyTango if no wheel is available for your platform.
You will need a compiler.
You could use :ref:`sardana-getting-started-installing-in-conda`
to avoid this. If you decide to continue with pip3, please refer to
`PyTango's installation guide <https://pytango.readthedocs.io/en/stable/start.html#pypi>`_.
On Debian this should work to prepare the build environment::

        apt-get install pkg-config libboost-python-dev libtango-dev

Linux (Debian-based)
--------------------

Sardana is part of the official repositories of Debian (and Ubuntu
and other Debian-based distros). You can install it and all its dependencies by
doing (as root)::

       apt-get install python3-sardana

Note: `python3-sardana` package is available starting from the Debian 11
(Bullseye) release. For previous releases you can use `python-sardana`
(compatible with Python 2 only).

.. _sardana-getting-started-installing-in-conda:

Installing in a conda environment (platform-independent)
--------------------------------------------------------

In a conda environment (we recommend creating one specifically for sardana)::

    conda install -c conda-forge sardana

Since version 3.4.0, `sardana` is a metapackage that will install sardana and all optional
dependencies. For minimal requirements, install `sardana-core` instead.
See `sardana-feedstock <https://github.com/conda-forge/sardana-feedstock>`_ for the up-to-date list of packages.

Working from Git source directly (in develop mode)
--------------------------------------------------
 
If you intend to do changes to Sardana itself, or want to try the latest
developments, it is convenient to work directly from the git source in
"develop" (aka "editable") mode, so that you do not need to re-install
on each change.

Start by cloning the sardana repository::

    git clone https://gitlab.com/sardana-org/sardana.git
    cd sardana


In a conda or python virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use a python virtual environment or a conda environment with the needed dependencies::

    # optional: if using a conda environment, pre-install dependencies with:
    conda install --only-deps -c conda-forge sardana-core sardana-config taurus-qt

    # install sardana in develop mode (inside the sardana repo)
    pip3 install -e ".[all]"  # <-- Note the -e !!

With pixi
~~~~~~~~~

Pixi_ is a package management tool for developers.
Its goal is to provide developers with a clean and simple command-line interface to manage their project.

Pixi hides the complexity of installing dependencies and allows to run simple tasks
whatever the operating system (Linux, Windows and macOS) using the conda ecosystem.

`Install pixi <https://pixi.sh/latest/#installation>`_ if you haven't already.

Pixi configuration is defined in the `pixi.toml` file at the root of the repository.
The required environment(s) will be created automatically when running a `pixi` command.

If you don't have a Tango Database server running, run::

  $ pixi run pydb
  ✨ Pixi task (pydb in pydb): PyDatabaseds 2
   Ready to accept request

This will start a PyTango Database Device server, which uses SQLite to store data, on port 10000.
The previous command will automatically create an environment to install `pytango-db` and run `PyDatabaseds 2`.
It will create the file `tango_database.db`, where the data is saved.

In another terminal, run::

  $ pixi run sar_demo
  ✨ Pixi task (sar_demo in default): sardanactl config load --write src/sardana/config/test/sar_demo.yaml

This will populate the database with the required Sardana instance and devices.
As long as you don't delete the `tango_database.db` file, you don't have to run this command again.

Once done, you can start Sardana::

  $ pixi run Sardana
  ✨ Pixi task (sardana in default): Sardana demo1

Sardana is now running. In another window, you can start spock. The first time it will create an ipython profile
under `.ipython` in the project directory. You'll have to select to which door to connect::

  $ pixi run spock
  MainThread     INFO     2025-04-23 16:59:27,145 TaurusRootLogger: Using PyQt5 (v5.15.10 with Qt 5.15.15 and Python 3.13.3)
  Profile 'spockdoor' does not exist. Do you want to create one now ([y]/n)? y
  Available Door devices from 127.0.0.1:10000 :
  MainThread     WARNING  2025-04-23 16:59:29,414 TaurusRootLogger: epics scheme not available: ModuleNotFoundError("No module named 'epics'")
  Door_demo1_1 (a.k.a. Door/demo1/1) (running)
  Door name from the list? Door_demo1_1
  Storing ipython_config.py in /Users/johndoe/Dev/Sardana/sardana/.ipython/profile_spockdoor... [DONE]
  Spock 3.5.3-alpha -- An interactive laboratory application.
  
  help      -> Spock's help system.
  object?   -> Details about 'object'. ?object also works, ?? prints more.
  
  IPython profile: spockdoor
  
  Connected to Door_demo1_1
  
  Door_demo1_1 [1]:

With docker
~~~~~~~~~~~

The sardana-docker_ repository provides docker images mainly used for continuous integration.
Those images can be used to run Sardana locally.
Refer to the repository `README.md <https://gitlab.com/sardana-org/sardana-docker/-/blob/main/README.md>`_ for more information.

.. _dependencies:

============
Dependencies
============

Sardana depends on PyTango_, Taurus_, lxml_, itango_ and click_.
However some Sardana features require additional dependencies. For example:

- Using the Sardana Qt_ widgets, requires either PyQt_ (v4 or v5)
  or PySide_ (v1 or v2).

- The macro plotting feature requires matplotlib_

- The showscan online widget requires pyqtgraph_

- The showscan offline widget requires PyMca5_

- The QtSpock widget requires qtconsole_

- The HDF5 NeXus recorder requires h5py_


.. _PyTango: http://pytango.readthedocs.io/
.. _Taurus: http://www.taurus-scada.org/
.. _lxml: http://lxml.de
.. _itango: https://pytango.readthedocs.io/en/stable/itango.html
.. _click: https://pypi.org/project/click/
.. _Qt: http://qt.nokia.com/products/
.. _PyQt: http://www.riverbankcomputing.co.uk/software/pyqt/
.. _PySide: https://wiki.qt.io/Qt_for_Python/
.. _matplotlib: https://matplotlib.org/
.. _pyqtgraph: http://www.pyqtgraph.org/
.. _PyMca5: http://pymca.sourceforge.net/
.. _h5py: https://www.h5py.org/
.. _spyder: http://pythonhosted.org/spyder/
.. _qtconsole: https://qtconsole.readthedocs.io/en/stable/
.. _sardana-docker: https://gitlab.com/sardana-org/sardana-docker
.. _Pixi: https://pixi.sh
