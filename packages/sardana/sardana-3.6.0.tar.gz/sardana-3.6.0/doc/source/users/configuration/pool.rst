.. _sardana-configuration-pool:

Pool
====

Device Pool is easily extendable by means of controller plugins. Device Pool
discovers them in directories configurable via
:ref:`sardana-pool-api-poolpath` attribute. In case Sardana is used with
Tango this configuration is accessible via the ``PoolPath``
:class:`~sardana.tango.pool.Pool.Pool` device property.

Your controller plugins may need to access to third party Python modules. One
can configure the directory where to look for them via
:ref:`sardana-pool-api-pythonpath` attribute. In case Sardana is
used with Tango this configuration is accessible via the ``PythonPath``
:class:`~sardana.tango.pool.Pool.Pool` device property.

Device Pool implements a controlled way of performing
:ref:`sardana-users-motion` and :ref:`sardana-acquisition`.
These actions consists of performing a high frequency polling loops
over the involved elements in order to control and update the
states and the principal attributes i.e. ``Position`` for
a :ref:`motor <sardana-motor-overview>` or ``Value`` for an experimental channel
e.g. :ref:`Counter/timer <sardana-countertimer-overview>`. The default
frequency of these polling loops can be controlled with the following
:class:`~sardana.tango.pool.Pool.Pool` device properties:

- ``MotionLoop_SleepTime`` - sleep time in the motion loop
  between the state reads in ms (default: 10 ms)
- ``MotionLoop_StatesPerPosition`` - number of state reads done
  before doing a position read in the motion loop (default: 10)
- ``AcqLoop_SleepTime`` - sleep time in the acquisition loop
  between the state queries in ms (default: 10 ms)
- ``AcqLoop_StatesPerValue``- number of state reads done
  before doing a value read in the acquisition loop (default: 10)
            
Device Pool integrates natively with the
`Elastic Stack <http://www.elastic.co>`_ and may send logs to the a Logstash
instance. In case Sardana is used with Tango this configuration is
accessible via the ``LogstashHost`` and ``LogstashPort``
:class:`~sardana.tango.pool.Pool.Pool` device properties.
You can use the intermediate SQLite cache database configured with
``LogstashCacheDbPath`` property, however this is discouraged due to logging
performance problems.


.. todo::
    Document RemoteLog, DriftCorrection, InstrumentList
