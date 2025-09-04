.. currentmodule:: sardana.pool.test.util

.. _howto-controller-testing:

==============================
How to test controller plugins
==============================

For third-party controller plugin projects it is recommended to
develop their integration tests with the pool, for example,
during the TDD process or for their later use in the CI process.

We recommend developing tests with `pytest`_
and sardana built-in fixtures defined in `sardana.pool.test`.

We believe that the approach of integration testing together with
the use of pytest is good because:

- The `sardana.pool.controller` API was optimized for 
  multi-axes commands and queries, frequently making the plugin methods
  like: :func:`~sardana.pool.controller.Startable.PreStartAll`,
  :func:`~sardana.pool.controller.Startable.PreStartOne`,
  :func:`~sardana.pool.controller.Startable.StartOne`,
  :func:`~sardana.pool.controller.Startable.StartAll` not maintaining
  the class invariants, hence not really suitable for unit testing.
- Some controller plugin classes, during complex actions like motion
  or acquisition, may even not maintain the class invariants in between
  the series of calls to *state* and *read* methods what is again
  not really suitable for unit testing.
- For the above reasons the most efficient way of testing would be
  to replicate the call algorithms from the pool. But since sardana
  is an evolving project, the integration testing strategy with
  actually using the pool algorithms, could early discover eventual
  incompatibilities between the plugins and newer versions of sardana.
- pytest is the most complete and widespread python testing framework,
  which in contrary to unittest, which follows the xUnit testing
  patterns, provides more pythonic and modular way of developing tests.
- With the sardana built-in fixtures, which require minimal configuration,
  you could directly focus on writing your tests without carrying too much
  about the setup and tear down. For example, they take care of executing
  the calls to methods like
  :func:`~sardana.pool.controller.Controller.AddDevice` and
  :func:`~sardana.pool.controller.Controller.DeleteDevice`, etc.

You will need to either fine tune the fixtures using markers
e.g. `kwargs` or create custom fixtures using "Factory as fixture"
e.g. `create_motor_ctrl`.

Until SEP19_ gets implemented, the first thing that you will need
to do is to tell the pool where to look for your controller plugins i.e.
set the `pool_path`, by either:

- changing the behavior of the `pool`
  fixture using the `attrs` marker e.g. for the whole test module by
  setting the `pytestmark` module attribute::

    pytestmark = [pytest.mark.attrs({"pool": {"pool_path": ["/path/to/your/controller/classes"]}})]

- or, creating your own ``pool`` fixture using the `create_pool`
  "Factory as fixture"::

    @pytest.fixture
    def pool(create_pool):
        pool = create_pool()
        pool.pool_path = ["/path/to/your/controller/classes"]
        return pool

Next, you will need a controller object driven by your controller
plugin. Here you can either:

- change the behavior of the `motctrl01` fixture::

    pytestmark = pytest.mark.kwargs({
        "motctrl01": {
            "klass": "MyMotorController",
            "library": "MyMotorCtrl.py"
        }
    })


- or, create your own ``motctrl01`` fixture using the `create_motor_ctrl` 
  "Factory as fixture"::

    @pytest.fixture
    def motctrl01(create_motor_ctrl):
        kwargs = {        
            "klass": "MyMotorController",
            "library": "MyMotorCtrl.py"
        }
        return create_motor_ctrl(kwargs)

.. important::

    In case you create your own fixtures, it is recommended
    to follow naming convention of the fixtures defined in
    the `sardana.pool.test` module, as in the above example.
    This way you will be able to reuse the built-in dependent fixtures
    e.g. by creating controller fixture called ``motctrl01`` you
    can reuse `mot01` built-in fixture. These fixtures could be
    further fine tuned with markers.

So, now you could already start testing your controller::

    def test_init(motctrl01):
        assert motctrl01.is_online() == True

or axis::

    def test_get_state(mot01):
        assert mot01.state == State.On

Built-in controller elements fixtures are limited to the low axis numbers.
For higher axis numbers you will need to define your own fixtures. For this, 
you could use the `sardana.pool.test.util.mot()` helper function e.g.::

    mot99 = pytest.fixture(mot)

.. hint::

    You could get some inspiration on writing controller tests from the sardana-tango_ project.


.. _pytest: pytest.org
.. _SEP19: https://github.com/reszelaz/sardana/blob/sep19/doc/source/sep/SEP19.md
.. _sardana-tango: https://github.com/ALBA-Synchrotron/sardana-tango