.. currentmodule:: sardana.taurus.qt.qtgui.extra_sardana

.. _sardanaeditor_ui:


==========================
Sardana Editor's interface
==========================

.. warning::

    Sardana editor is no more maintained and was removed from the code base in
    `!1716 <https://gitlab.com/sardana-org/sardana/-/merge_requests/1716>`_.
    This decission was motivated by its low popularity 
    (see `Sardana Users Questionnaire 2020 <https://gitlab.com/sardana-org/sardana-questionnaire>`_)
    and lack of resources to maintain it. If you are interested in this widget please contact us via the project
    issue tracker.

.. contents::

Sardana editor is an :term:`IDE` for developing sardana plugins such as
:ref:`macros <sardana-macro-howto>` or :ref:`controllers <sardana-controller-howto>`.
It is based on the `Spyder <https://www.spyder-ide.org/>`_ project.

.. image:: /_static/sardanaeditor.png

Some features of the sardana editor are:

* plugins modules navigation
* reload of the plugin code on the server

At the time of writing this document there is no script to directly start the editor
but you can launch it with the following command specifying the door to which you
want to connect::

    python -m sardana.taurus.qt.qtgui.extra_sardana.sardanaeditor <door_name>
    
.. warning::
    Sardana editor is still under development. If you find a bug please check the
    `project issues <www.gitlab.com/sardana-org/sardana/-/issues>`_ if it was already
    reported and if not report it or directly propose a fix.

 
