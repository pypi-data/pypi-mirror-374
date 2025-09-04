.. _sardanacustomsettings:

=======================
Sardana custom settings
=======================


Sardana provides a module located at its root directory called
`~sardana.sardanacustomsettings` which exposes global configuration options.

It can be accessed programmatically at run time for setting options
for the current execution.

System and user settings files
------------------------------

If one wants to permanently modify options for all applications, the
recommended way is to do it by declaring them in the system-wide or
user-specific configuration files (which are loaded automatically when
importing `~sardana.sardanacustomsettings`).

The default location of the system-wide and user-specific configuration
files is set in `~sardana.sardanacustomsettings.SYSTEM_CFG_FILE` and
`~sardana.sardanacustomsettings.USER_CFG_FILE`, respectively. The values are
platform-dependent:

- on posix systems we use: ``/etc/sardana/sardana.ini``
  for system and ``~/.sardana/sardana.ini`` for user.
- on windows machines we use ``%PROGRAMDATA%\sardana\sardana.ini`` for system
  and ``%APPDATA%\sardana\sardana.ini`` for user

In case of conflict, the user settings take precedence over the system
settings.

Custom setting file locations
-----------------------------

One can also programmatically call the `~sardana.sardanacustomsettings.load_configs()`
function at any point to load other configuration files.

In both cases, the values of existing variables in `~sardana.sardanacustomsettings`
are overwritten in case of conflict).

Format of the settings files
----------------------------

The settings files are plain-text .ini files of the form::

    [sardana]
    FOO = "bar"
    BAR = [1, 2, 3]
    baz = False

The keys, which are **key-sensitive**, are exposed as `~sardana.sardanacustomsettings`
variables and their **values are parsed as python literals** (e.g., in the above example,
`sardanacustomsettings.FOO` would be the `bar` string,
`sardanacustomsettings.BAR` would be a list and `sardanacustomsettings.baz`
would be a boolean).

Note that all key-values must be declared within a `[sardana]` section.

.. automodule:: sardana.sardanacustomsettings
   :members:
   :undoc-members:
