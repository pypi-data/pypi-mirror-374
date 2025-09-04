.. _macro-environment:

=================
Macro Environment
=================

The sardana server provides a global space to store variables, called
*Macro Environment*. It is a store of *variable - value* pairs,
which can be accessed during macro execution at any time.
One of its common use case is to share  configuration
(or even small data) between different macros.

The macro environment is stored persistently, so if the sardana
server is restarted the environment is properly restored.

The most common way of accessing environment variables is using
:ref:`sardana-environment-macros`:

.. sourcecode:: spock

    LAB-01-D01 [1]: senv Foo Bar
    Foo = Bar
    
    LAB-01-D01 [1]: genv Foo
    Foo = 
    'Bar'

.. important::
    Environment variable names are case sensitive. So, variable ``Foo`` is
    a different variable than ``foo``.


Sardana built-in macros use a set of standard environment variables listed in
:ref:`environment-variable-catalog`. You can also define your own environment variables.

.. _sardana-macro-environment_types:

Environment Variables Types
---------------------------

Environment variables can be of different Python literal types: string, numbers, collections, etc.
The type interpreation is based on Python's
`ast.literal_eval() <https://docs.python.org/3/library/ast.html#ast.literal_eval>`_ function.
So, all the values not evaluating into Python literal structures are interpreted as strings.

For example, you can define a dictionary value in the following way:

.. sourcecode:: spock

    LAB-01-D01 [1]: senv Foo '{"Bar": "Baz"}'
    Foo = {'Bar': 'Baz'}

Environment Variables Scope
---------------------------

An environment variable can be set on different scope:

* global (default)
* door
* macro

In order to set a variable for a specific scope you must preceed its name with the scope name
separated by ``.`` (dot(s)).

For example to define a variable on a specific Door scope:

.. sourcecode:: spock

    LAB-01-D01 [1]: senv LAB/01/D02.Foo Bar
    LAB/01/D02.Foo = Bar

This way the ``Foo`` variable will be known only to the macros
running on ``LAB/01/D02`` door and will override the ``Foo`` variable
defined on the global scope.

.. important::

    Remember to use Door device name for defining variables on the door scope.
    Currently you can not use the Door alias.

Furthermore, the door and the macro scope can be mixed together, so an environment variable could
only apply to a specific macro executed on a specific door.

For example to define a variable that apply only to the ``foo`` macro
when run on a specific door:

.. sourcecode:: spock

    LAB-01-D01 [1]: senv LAB/01/D02.foo.Bar Baz
    LAB/01/D02.foo.Bar = Baz

.. seealso::

    Apart of the :ref:`sardana-environment-macros` you have other
    :term:`API` for accessing environment.
    
    :ref:`sardana-macro-api`
        the Macro :term:`API`
    
    :ref:`sardana-taurus-macroserver-api`
        the Taurus Extension :term:`API` to MacroServer and Door Tango devices
    
    :class:`~sardana.tango.macroserver.Door.Door`
        the Door Tango device :term:`API`
    
    :class:`~sardana.tango.macroserver.MacroServer.MacroServer`
        the MacroServer Tango device :term:`API`