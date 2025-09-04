.. _ids:

==============
ids properties
==============

Sardana 3.4 comes with the possibility to use Sardana element names
instead of numeric identifiers when referring in the configuration between
the elements e.g. a motor ``mot01`` can refer to its controller by using
``motctrl01`` name instead of the numeric identifier ``1``.

The major benefits of this are:

- more self-descriptive configuration, both in the :ref:`sardana-configuration-format-and-tools`
  and in the Tango DB
- more self-descriptive runtime exception messages related to invalid configuration

The same release comes with the improved pseudo element controller properties.
First, the property name was unified between the pseudo motor and pseudo counter controllers,
from ``motor_role_ids`` and ``counter_role_ids`` to ``physical_roles``. Second, now its value
contains the physical role names together with the ids of the physical element. So, again it
offers a more self-descriptive configuration.

In Sardana 3.4 using the above explained features is optional and needs to be explicitly
enabled using :ref:`sardanacustomsettings`:

- `~sardana.sardanacustomsettings.USE_NUMERIC_ELEMENT_IDS`
- `~sardana.sardanacustomsettings.USE_PHYSICAL_ROLES_PROPERTY`

For newly created Sardana systems it is enough to enable these features. For existing,
systems before using Sardana element names instead of numeric identifiers,
you will need to perform a manual migration process. The new pseudo element controller
properties will be migrated automatically on the next server startup.

In Sardana 3.5, these features have been enabled by default (variables have been set respectively to `False` and `True`).

.. important::
    Both of these features are necessary to use the :ref:`sardana-configuration-format-and-tools`
    introduced by `SEP20 <https://gitlab.com/sardana-org/sardana/-/merge_requests/1749>`_.

Migrating existing systems
==========================

Backup
------

Before you migrate your system it is highly recommended that you perform the
Tango DB backup, at least of the Sardana system part. For example, you can use
directly the MySQL tools::

    mysqldump -u tango -p tango > backup.sql

or use the `dsconfig <https://pypi.org/project/dsconfig/>`_ tool (here ``demo1``
is the instance name of your servers)::

    python -m dsconfig.dump server:MacroServer/demo1 > backup_macroserver.json
    python -m dsconfig.dump server:Pool/demo1 > backup_pool.json

Run migration script
--------------------

The migration script is available here:
`upgrade_ids.py <https://gitlab.com/sardana-org/sardana/-/blob/develop/scripts/upgrade/upgrade_ids.py>`_.

.. important::
    You should not modify your Sardana system configuration during the migration process.

The order in which the script modifies the system is as follows:

1. Fix possible incorrect configuration from elements and motor_role_ids/counter_role_ids.
2. Remove pseudo_motor_role_ids and pseudo_counter_role_ids properties.
3. Remove elements property from pseudomotors and pseudocounters.
4. Update ctrl_id, elements and Instrument_id with alias instead of IDs.
5. Update roles (motor_role_ids, counter_role_ids, physical_roles) with alias instead of IDs.
6. Remove motorgroups.
7. Remove IDs from all devices.

The script has 3 modes of execution:

- fix_pseudos: Runs point 1 from the list above. As it only fixes incorrect configuration, it can be used either in version 3.3.x or in > 3.4.x. If this mode finds problems, it must write these changes to the DB for the rest of the script to run properly.
- cleanup: Runs point 1, 2 and 3 from the list above. It can only be run with version > 3.4, as it removes properties used in previous versions. Even if the system is still using IDs, it is recommended to run it to remove old properties no longer used.
- migrate: Runs all points from the list above. It can only be used with sardana > 3.4 and if the settings `~sardana.sardanacustomsettings.USE_NUMERIC_ELEMENT_IDS` are set to False.

All three modes will need the argument --write to actually write to the DB. First, it is a good idea to run it in dry-run mode (default)
so no changes will written to the Tango DB
(here ``demo1`` is the instance name of your servers)::

    python upgrade_ids.py --server=Pool/demo1 --mode=migrate
    python upgrade_ids.py --server=MacroServer/demo1 --mode=migrate    

Some existing systems may contain incomplete or broken configuration.
The script will detect such cases and report them on the output.
You will need to fix them manually and repeat the script execution
until all errors are fixed. The typical errors are:

- no alias defined for an element
- deleted physical element still referenced by a pseudo element controller

When all errors are fixed you can proceed to run the script so it
applies the modification in the Tango DB. We recommend
that you redirect the detailed output of the changes being performed
to a file and keep if for reference in case of any future problems.
These details are output on the standard error.

So, the full command to run the script to apply the changes and to redirect
its standard error is (here ``demo1`` is the instance name of your servers)::

    python upgrade_ids.py --server=Pool/demo1 --mode=migrate --write 2> upgrade_id_pool.log
    python upgrade_ids.py --server=MacroServer/demo1 --mode=migrate --write 2> upgrade_id_macroserver.log

In case of a successful execution of the script, you should enable
the new features using :ref:`sardanacustomsettings` as explained above
before re-starting the server(s).
    