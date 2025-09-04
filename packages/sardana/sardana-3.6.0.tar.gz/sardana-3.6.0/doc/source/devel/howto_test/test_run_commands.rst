
.. currentmodule:: sardana.test.

.. _sardana-test-run-commands:

===========================
Run tests from command line
===========================

Run test suite
--------------

We recommend using pytest to run Sardana tests. Please refer to
`pytest documentation <https://docs.pytest.org/en/latest/usage.html>`_
on how to execute tests. You may find a good example on how run Sardana
tests in its `CI pipelines <https://gitlab.com/sardana-org/sardana/-/blob/develop/.gitlab-ci.yml>`_.

.. note::
  Some tests may require optional :ref:`dependencies` to be installed.

.. note::
  Currently the majority of the Sardana tests are written using unittest.
  We plan to gradually migrate them to pytest.
