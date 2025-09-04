###########
What's new?
###########

Below you will find the most relevant news that brings the Sardana releases.
For a complete list of changes consult the Sardana `CHANGELOG.md \
<https://gitlab.com/sardana-org/sardana/-/blob/develop/CHANGELOG.md>`_ file.

****************************
What's new in Sardana 3.6.0?
****************************

Date: 2025-09-04 (*Jul25* milestone)

Type: biannual stable release

It is backwards compatible and comes with new features, changes and bug fixes.

Added
=====

* Remove ``MotorGroup`` Tango devices on Pool and Sardana startup ``CLEANUP_MOTOR_GROUPS`` :ref:`sardana custom setting <sardanacustomsettings>` to eventually disable this behavior
* Measurement group core fixtures: ``mntgrp01`` and ``create_measurement_group``
* Improve storing MCA in FIO files and add MetadataScript support
* Add ScanID control on the :ref:`expconf <expconf_ui>`
* Add :ref:`showscan <showscan_ui>` inspector tool to display information of the data point under the mouse
* Remove caching of latency_time for measurement group device
* Add Pixi configuration
* Add Compatibility with IPython 9 and update minimum required version to 5.1
* Add macro com and introduce offset for pic cen com

Fixed
=====

* Allows using the pre-acq and post-acq hooks in the ``meshct``
* Handle error in ``defmeas`` macro
* Fix macro ``where``
* Fix ``GetMacroEnv()`` Door Tango device command
* :ref:`Sequencer <sequencer_ui>` parameter editor now displays macro default values correctly
* Force latency time reading instead to use cache value
* Fix default value reding for ParamRepeat on the sequencer
* Compatibility issues with IPython 9.x causing ``edmac`` macro to fail

Removed
=======

* ``sardanactl config`` entrypoint deleted. ``sardana-config`` was moved to its own `repo <https://gitlab.com/sardana-org/sardana-config>`_ and shall be installed separately

****************************
What's new in Sardana 3.5.2?
****************************

Date: 2025-04-04

Type: hotfix release


Fixed
=====

* IORegister widget creation in Taurus>=5.2 now correctly reads the 'Labels'
* Fix sphinx pytango reference and update reference link mapping
* Fix expstatus in Taurus>=5.2


****************************
What's new in Sardana 3.5.1?
****************************

Date: 2025-02-17

Type: hotfix release


Fixed
=====

* Fixed an error when reloading macros with mixed uppercase and lowercase names in Spock.
* Improved state handling for experimental channels by treating ``Running`` the same as ``Moving``.


**************************
What's new in Sardana 3.5?
**************************

Date: 2024-06-26 (*Jan24* milestone)

Type: biannual stable release

It is backwards compatible and comes with new features, changes and bug fixes.

Exceptionally, this release was not tested on Windows platform.

Added
=====
* :ref:`Experiment Status widget <expstatus_ui>`, a complete interface to monitor the status of the elements and running macros.
  It can be launched with `sardanactl expstatus` script.
* :ref:`Sardana Configuration Tool <sardana-configuration>`:

  * Now it is possible to split the configuration file into :ref:`multiple files <sardana-config-multiple-files>` for 
    easier management (added ``!include`` statement).
  * ``sardanactl config graph`` script to :ref:`generate a graph <sardana-config-graph>` with controllers and 
    elements to visualize the configuration from a YAML file.
  * Description field to document the purpose of the elements in the config file. This will map directly to the Tango device 
    description property.
  * ``sardanactl config validate`` now checks if required properties are declared in the config.

* Possibility to execute one point step scan by configuring ``starts`` equal to ``finals`` and ``nb_intervals = 0``
  (e.g. ``ascan mot01 1 1 0 .1``).
* :ref:`Showscan online <showscan-online>` widget enhancements (``showscan online``):
  
  * *Click-to-move* functionality to move a motor to a clicked position.
  * Pre-scaling of x-axis on scan start according to the scan's range.

* Possibility to execute `~sardana.macroserver.macros.scan.mesh`/`~sardana.macroserver.macros.scan.dmesh` scans without
  moving the second (slow) motor by setting the macro parameter ``m2_correct_drift`` to ``False`` or by setting this value 
  to the ``MeshM2CorrectDrift`` environment variable (so it will be used as default). See :ref:`documentation <meshm2correctdrift>`.
* Possibility to use characters from other encodings than Latin1 e.g. UTF-8 by changing
  `~sardana.sardanacustomsettings.LOG_MESSAGE_CODEC`
* :ref:`Diffractometer <sardana-diffractometer>` improvements:

  * New diffractometer HKL controller type ``Diffrac4Cp23``.
  * Added Ki and Kf attributes to diffractometer HKL controllers.

* Elements used (reserved) by running macros are now exposed on the Door device
* Compatibility with Python 3.12

Changed
=======
* Now Sardana uses by default non-numeric ids and physical roles properties. Custom setting `~sardana.sardanacustomsettings.USE_NUMERIC_ELEMENT_IDS`
  is now by default ``False`` and `~sardana.sardanacustomsettings.USE_PHYSICAL_ROLES_PROPERTY` is now by default ``True``.
  Old installations should migrate (:ref:`migration guide <ids>`) or, alternatively, force the old values.
* Sardana command-line interface tool renamed to ``sardanactl``

Fixed
=====
* Multiple fixes in :ref:`Sardana Configuration Tool <sardana-configuration>` to improve reliability and usability.
* Plotting of `~sardana.macroserver.macros.scan.timescan` in ``showscan online`` tool.
* Reload macro when the macro name is the same as the macro library name.
* :ref:`Deterministic scans <sardana-macros-scanframework-determscan>`:
  
  * `~sardana.macroserver.macros.scan.rscan`, `~sardana.macroserver.macros.scan.r2scan` and
    `~sardana.macroserver.macros.scan.r3scan` are now deterministic with number of points equal to the total points
    throughout all regions.
  * `~sardana.macroserver.macros.scan.fscan` is now deterministic if number of points is known and integration
    time is a scalar.

****************************
What's new in Sardana 3.4.4?
****************************

Date: 2024-03-20

Type: hotfix release


Fixed
=====

* Fixed scan velocity verification before to move the motor when the velocity
  of the motor is 0, in the case of the meshct it happens for the slow motor.

****************************
What's new in Sardana 3.4.4?
****************************

Date: 2024-03-20

Type: hotfix release


Fixed
=====

* Fixed scan velocity verification before to move the motor when the velocity
  of the motor is 0, in the case of the meshct it happens for the slow motor.



****************************
What's new in Sardana 3.4.3?
****************************

Date: 2023-11-15

Type: hotfix release

Added
=====

* Spock :ref:`documentation <sardana-coding-guide-spock>` for developers.

Fixed
=====

* Fix trigger/gate moveable_on_input in time synchronized measurement.
  See :ref:`documentation <sardana-triggergatecontroller-howto-output-id>` for more details.

****************************
What's new in Sardana 3.4.2?
****************************

Date: 2023-08-31

Type: hotfix release

Fixed
=====

* Build process of the sardana package when using setuptools < 40.1.0.

****************************
What's new in Sardana 3.4.1?
****************************

Date: 2023-08-30

Type: hotfix release

Added
=====

* Make installation of sardana extra dependencies optional for pip and conda.
  See :ref:`Installation instructions <sardana-installing>` for more details.

Fixed
=====

* Improve handling of motion errors and error reporting in continuous scans.
  This avoids confusion about the source of the error between acquisition and motion.
* Errors in continuous scan when motor velocities were using units.
* Restore compatibility with taurus < 5.1.4.

**************************
What's new in Sardana 3.4?
**************************

Date: 2023-04-06 (*Jan23* milestone)

Type: biannual stable release

It is backwards compatible and comes with new features, changes, deprecations and bug fixes.

Exceptionally, this release was not tested on Windows platform.

This release simplifies Tango DB configuration so Sardana does not rely on some properties
anymore. It is highly recommended that you cleanup your systems created prior to this release
using the `upgrade_ids.py <https://gitlab.com/sardana-org/sardana/-/blob/develop/scripts/upgrade/upgrade_ids.py>`_
script, using the following command: ``python upgrade_ids.py --server=Pool/sep20_example_pool --cleanup``.

Added
=====

* :ref:`Sardana configuration format and CLI tools <sardana-configuration-format-and-tools>`.
  The format is based on `YAML <https://yaml.org/>`_
  and covers all the Tango DB configuration points.
  The tools can be invoked with the ``sardana config`` script sub-commands
  (temporarily ``sardanacli config`` on Windows):
  
  * ``dump``
  * ``load``
  * ``diff``
  * ``update``
  * ``validate``

  Additionally, Sardana configuration was improved with the following features: 

  * Element names are used instead of numeric *ids*
    when referring to elements in configuration (including Tango DB configuration).
    To enable this feature you need to switch the 
    `~sardana.sardanacustomsettings.USE_NUMERIC_ELEMENT_IDS` flag
    and :ref:`migrate existing systems <ids>`.
    This feature is incompatible with renaming elements at runtime.
  * More self-descriptive configuration of pseudo controllers
    (``physical_roles`` property with role names and ids).
    To enable this feature you need to switch the
    `~sardana.sardanacustomsettings.USE_PHYSICAL_ROLES_PROPERTY` flag.

* Some of the previously existing standalone scripts were unified under one general
  script ``sardana`` (temporarily ``sardanacli`` on Windows) with sub-commands:

  * ``spock``
  * ``macroexecutor``
  * ``sequencer``
  * ``expconf``
  * ``showscan``
  * ``config``

* Scan :ref:`directory <scandir>` or :ref:`file <scanfile>`
  can be automatically changed on every new scan execution
  and its name can be parametrized with the :ref:`scanid`
  environment variable.
* New macros:

  * for configuring moveable limits:
    `~sardana.macroserver.macros.standard.set_user_lim`,
    `~sardana.macroserver.macros.standard.set_dial_lim`
    and `~sardana.macroserver.macros.standard.set_dial_pos`
  * stoppable/abortable `~sardana.macroserver.macros.standard.sleep` 
  * `~sardana.macroserver.macros.standard.set_step_per_unit`
    with an option to update limits

* Macros can be executed programmatically more easily with the new :term:`API` of
  `~sardana.macroserver.macro.Macro.runMacro()`

* Improved macro execution widgets:

  * Import/export history in :ref:`macroexecutor_ui`
  * Exceptions raised during macro execution are showed
    with a pop-up dialog in :ref:`macrobutton`

* Improved `~sardana.macroserver.macros.scan.scanstats` macro:

  * Can be executed independently right after the scan macro
  * N-dimensional scans are supported

* Continuous scans better validate:

  * scan velocity before moving to pre-start position
  * if pre-start move ended correctly

* *Default Pool* concept to macro server to disambiguate macro parameters when
  present in more than one pool. It is configurable with :ref:`defaultpool`
  environment variable.
* Generic data recorders (not file recorders) can be configured with
  :ref:`datarecorder` environment variable.
* :ref:`Scan points in step scans can be repeated based on an arbitrary condition <sardana-users-scan-step>`.
  Configurable with :ref:`generalcondition` environment variable.
* :ref:`Controller plugins tests can now be easily developed <howto-controller-testing>`
  thanks to the sardana core `pytest <pytest.org>`_ fixtures.
* It is now possible to not move certain motors in custom step scans
  developed with `~sardana.macroserver.scan.gscan.SScan`.
* Automatically test sardana with different python versions using `conda <https://conda.io/>`_.

Changed
=======

* :ref:`expconf_ui` measurement group tab by default starts with a simplified view
  instead of showing all the possible configuration options.
* ``showscan`` magic command (in Spock) shows the :ref:`showscan-online`
  instead of :ref:`showscan-offline`

Deprecated
==========

* Some of the standalone scripts:

  * ``spock``
  * ``macroexeutor``
  * ``sequencer``
  * ``showscan``

  in favor of ``sardana`` (temporarily ``sardanacli`` on Windows) script with sub-commands.

* ``showscan online`` magic command (in Spock) in favor of ``showscan`` magic command
* `~sardana.macroserver.macros.standard.set_lim`,
  `~sardana.macroserver.macros.standard.set_lm`
  and `~sardana.macroserver.macros.standard.set_pos` macros in favor of 
  `~sardana.macroserver.macros.standard.set_user_lim`,
  `~sardana.macroserver.macros.standard.set_dial_lim`
  and `~sardana.macroserver.macros.standard.set_dial_pos` macros

Fixed
=====

* Compatibility with Python 3.11.
* Make Spock prompt always visible at the bottom in the secondary session
  (when macros are executed from outside of this Spock session). 
* Pseudo counters with complex hierarchy.
* Changes of controller (plugins) default properties and attribute values
  are now correctly applied.
* :ref:`macrobutton` state correctly reflects exceptions
  raised during macro execution.
* Remove Taurus deprecation warnings

****************************
What's new in Sardana 3.3.8?
****************************

Date: 2022-01-09

Type: hotfix release

Fixed
=====

* Properly stop/abort macros which call other macros when the interrupt
  request was sent while the internal macro was executing either of:

  * *pre-cleanup* and *post-cleanup* hooks
  * macro's `do_backup()` and `do_restore()`

****************************
What's new in Sardana 3.3.7?
****************************

Date: 2022-12-23

Type: hotfix release

Fixed
=====

* Protect against exceptions in hardware acquisition and synchronization
  action starting procedure (exception raised in controller's methods like:
  `StartAll()`, `StartOne()`, etc.). Such exceptions were impeding further
  executions of these actions.


****************************
What's new in Sardana 3.3.6?
****************************

Date: 2022-10-05

Type: hotfix release

Fixed
=====

* Regression introduced in version 3.3.0 causing final padding up to
  `nb_points` after interrupting a `timescan`.

****************************
What's new in Sardana 3.3.5?
****************************

Date: 2022-09-21

Type: hotfix release

Fixed
=====

* Regression introduced in version 3.3.3 causing attributes with
  memorization `MemorizedNoInit` to restore their
  memorized values on the server startup and the `reconfig` execution.
* Allow to reduce size of the `expconf` widget by making the *mode* warning label
  wrap its text when there is not enough space.

****************************
What's new in Sardana 3.3.4?
****************************

Date: 2022-09-06

Type: hotfix release

Fixed
=====

* Regression introduced in version 3.2.1 causing deadlocks in
  macros which use disposable `taurus.Device()` objects.
* `macroexecutor` and `sequencer` widget compatibility with Python 3.10

****************************
What's new in Sardana 3.3.3?
****************************

Date: 2022-08-10 (*Jul22* milestone)

Type: biannual stable release

It is backwards compatible and comes with new features, changes and bug fixes.

Added
=====

* *View* and *Edit* alternative use modes of :ref:`expconf_ui`. These modes let
  avoid annoying pop-ups with external changes e.g. when experiment configuration was
  changed programmatically by a macro.
* Allow to **not acquire** the last point in :ref:`sardana-users-scan-continuous`
  (by specifying negative value of ``nr_interv`` macro parameters e.g.
  ``ascanct mot01 0 3 -3 1`` will acquire only 3 scan points).
  This enables scans composed from only one scan point and does not extend the motion
  range beyond the point that was requested as the final position plus the necessary
  deceleration range.
* `~sardana.macroserver.macros.scan.rscanct` macro - continuous scan with multiple regions.
* `~sardana.macroserver.macros.expert.reconfig` macro - reconfigure a single axis element
  or the whole controller. Reconfiguration consists of the element initialization
  and application of memorized attribute values.
* Recalculate and set software limits in the
  `~sardana.macroserver.macros.standard.set_user_pos` macro.
* Fully stop :ref:`macro sequences in Spock <sardana-spock-sequences>`
  (*multiline input* macro execution) with ``Ctrl+c`` by propagating
  `KeyboardInterrupt` exception.
* Possibility to use spectrum attributes in :ref:`sardana-users-scan-snapshot`
  in SPEC recorder.
* Improved *instruments* usage experience:

  * Show NeXus class in the `~sardana.macroserver.macros.lists.lsi` macro
  * Add `~sardana.macroserver.macros.expert.definstr` macro for defining new instruments

* Fix order of :ref:`sardana-controller-howto-controller-memorized`.
* :ref:`Trigger/gate coupled and multiplexor modes in position domain <sardana-triggergatecontroller-howto-output-id>`.
* Allow to load :ref:`sardanacustomsettings` from `.ini` configuration files.

Changed
=======

* `~sardana.macroserver.macros.scan.timescan` first parameter from ``nr_interv``
  to ``nb_points`` what results in one acquisition less during the scan.
* Allow to execute new macros during :ref:`sardana-macro-handling-macro-stop-and-abort`.
* `~sardana.pool.controller.TriggerGateController` API: `~sardana.pool.controller.Synchronizer.PreSynchOne()`
  and `~sardana.pool.controller.Synchronizer.SynchOne()` receive
  synchronization description in position domain in :term:`dial position` instead of
  :term:`user position`. The old way was maintained for backwards compatibility but is
  **deprecated**.

Fixed
=====

* Corruption of move targets leading to wrong movements, especially affecting
  motor groups - some motors were erroneously sent to 0.
* Decouple attribute default values from memorized values i.e. changes of the
  attribute default values in the controller code will take effect.
* Issues with aborting :ref:`sardana-users-scan-continuous`.
* Avoid hung :ref:`sardana-acquisition-measgrp` with hardware synchronization
  when working with extended timeout.

Removed
=======

* *Hard links* in NXscan HDF5 files ``measurement`` group pointing to 
  ``measurement/pre_scan_snapshot`` items. Optionally could be re-introduced as
  *soft links* using `~sardana.sardanacustomsettings.NXSCANH5_RECORDER_LINK_PRE_SCAN_SNAPSHOT`.
* *Auto-update* mode in :ref:`expconf_ui` in favor of the *View* mode.
* Master timer/monitor from measurement group configuration. Measurement group
  configurations with master timer/monitor are still supported but are **deprecated**.

****************************
What's new in Sardana 3.2.1?
****************************

Date: 2022-03-21

Type: hotfix release

Fixed
=====

* Make Sardana compatible with Python 3.10.
* Regression introduced in Sardana 3.2.0 causing hangs on motion/acquisition start.
* Macro plotting for matplotlib < 3.

  
**************************
What's new in Sardana 3.2?
**************************

Date: 2022-01-31 (*Jul21* milestone)

Type: biannual stable release

It is backwards compatible and comes with new features, changes and bug fixes.

Added
=====

* Possibility to *release* hung operations e.g. motion or acquisition hung due to a hung hardware
  controller. Such a release could be issued, for example, from Spock using further 
  :kbd:`Control+c` in the process of :ref:`sardana-spock-stopping`.
* `~sardana.macroserver.macros.scan.rscan`, `~sardana.macroserver.macros.scan.r2scan`
  and `~sardana.macroserver.macros.scan.r3scan` scan macros (formerly available as examples
  under different names `regscan`, `reg2scan` and `reg3scan`). These macros were enahnced with
  the standard scan *hooks* and *scan data* support and fixed so the `region_nr_intervals`
  macro parameter type is now an `int` and the `integ_time` macro parameter was moved to the end.
* Possibility to disable overshoot correction in continuous scans using the
  :ref:`scanovershootcorrection` environment variable.
* Print in form of a table relevant motion parameters: acceleration, velocity, etc. used during
  continuous scans before the scan starts.
* `macro_start_time` dataset in `NXscan` (HDF5, NeXus) data file which contains the scan macro
  execution start timestamp in addition to already existing `start_time` dataset which contains
  the scan measurement start timestamp.
* Possibility to change *custom data* format e.g.: `#UVAR`, `#C`, etc. in the SPEC data file
* `~sardana.macroserver.macros.lists.lsp` macro to list Pools the MacroServer is connected to
* Improve error handling for state read in `~sardana.macroserver.macros.standard.mv` family macros
  and step scan macros.
* History log of motor attributes (sign, offset and step_per_unit) changes.
* Validate new limit values before applying them in `~sardana.macroserver.macros.standard.set_lim`
  and `~sardana.macroserver.macros.standard.set_lm` macros.

Changed
=======

* Execute `post-scan` hooks also in case an exception occurs during the scan execution.
* Default SPEC recorder *custom data* format: `#C` -> `#UVAR`

Fixed
=====

* *Memory leaks* in scans.
* Deletion of Pool element now checks if dependent elements exists. For example, if you delete 
  a motor it will be checked if any pseudo motor depends on it and eventually it will prevent
  the deletion.
* Several issues with stopping macros:

  * Remove annoying info messages of stopping instruments when stopping macros  
  * Stop motion only once in scans
  * Stop/abort element in `~sardana.macroserver.macros.standard.ct` macro when used directly
    with a channel instead of a measurement group
  * Allow aborting macros without prior stopping of them

* Allow to recreate measurement group with the same name but other channels at runtime.
* :ref:`showscan-offline` widget is again usable.
* Avoid problems with duplicated entries in :ref:`sardana-users-scan-snapshot`
* Spock prompt informs when the Door is offline i.e. MacroServer server is not running.
* Make MeasurementGroup state readout evaluate states of the involved elements
* Prevent start of operation e.g. motion or acquisition when the element is not ready.
* Fix restoring velocity in software (`~sardana.macroserver.macros.scan.ascanc`) continuous scans.
* Ensure controller, element and group state are set to Fault and details are reported in the status
  whenever plugin code i.e. controller library, is missing.  
* Hang of IPython when :ref:`sardana-macro-input` gives timeout
* Allow running Spock without an X-session on Linux.
* `~sardana.macroserver.macros.scan.amultiscan` macro parameters interpretation
* Respect measurement group `enabled` configuration  in `~sardana.macroserver.macros.standard.uct` macro
* `~sardana.macroserver.macros.expconf.set_meas_conf` macro when setting *plot axes* on all channels
* :ref:`sequencer_ui` widget action buttons (new, save and play) state (enabled/disabled)
* Make :ref:`pmtv` relative move combobox accept only positive numbers.
* `post_mortem` Spock's magic command which is useful for debugging problems.


****************************
What's new in Sardana 3.1.3?
****************************

Date: 2021-09-17

Type: hotfix release

Fixed
=====

- Regression introduced in Sardana 3.0.3 affecting grouped move/scan of pseudo
  motors proceeding from the same controller e.g. slit's gap and offset, HKL pseudo motors.
  Such a grouped move was only sending set possition to the first pseudo motor.
- Regression introduced in Sardana 3.1.2 affecting custom continuous scans composed from
  waypoints with non-homogeneous number of points. Such scans were producing erroneuous
  number of points due to an error in the final padding logic.

****************************
What's new in Sardana 3.1.2?
****************************

Date: 2021-08-02

Type: hotfix release

Fixed
=====

- Avoid *memory leak* in continuous scans (``ascanct``, ``meshct``, etc.).
  The MacroServer process memory was growing on each scan execution by the
  amount corresponding to storing in the memory the scan data.

****************************
What's new in Sardana 3.1.1?
****************************

Date: 2021-06-11

Type: hotfix release

Fixed
=====

- Correctly handle stop/abort of macros e.g. ``Ctrl+c`` in Spock in case
  the macro was executing another hooked macros e.g. a scan executing a general
  hook.

**************************
What's new in Sardana 3.1?
**************************

Date: 2021-05-17 (*Jan21* milestone)

Type: biannual stable release

It is backwards compatible and comes with new features, changes and bug fixes.

.. note::

    This release, in comparison to the previous ones, brings significant
    user experience improvements when used on Windows.

Added
=====

- *HDF5 write session*, in order to avoid the file locking problems and to introduce
  the SWMR mode support. It enables safe introspection e.g.: using data
  analysis tools like PyMCA or silx, custom scripts, etc. of the scan data files
  written in the `HDF5 data format <https://www.hdfgroup.org/solutions/hdf5/>`_
  while scanning.
  You can control the session using e.g.:
  `~sardana.macroserver.macros.h5storage.h5_start_session` and
  `~sardana.macroserver.macros.h5storage.h5_end_session` macros
  or the `~sardana.macroserver.macros.h5storage.h5_write_session`
  context manager.
  More information in the :ref:`NXscanH5_FileRecorder documentation \
  <sardana-users-scan-data-storage-nxscanh5_filerecorder>`
- *scan information* and *scan point* forms to the *showscan online* widget.
  See example in the :ref:`showscan online screenshot \
  <showscan-online-infopanels-figure>`.
- Handle `pre-move` and `post-move` hooks by: `mv`, `mvr`, `umv`, `umvr`,
  `br` and `ubr` macros.
  You may use `~sardana.sardanacustomsettings.PRE_POST_MOVE_HOOK_IN_MV`
  for disabling these hooks.
- Include trigger/gate (synchronizer) elements in the per-measurement preparation.
  This enables possible dead time optimization in hardware synchronized step scans.
  More information in the :ref:`How to write a trigger/gate controller documentation \
  <sardana-TriggerGateController-howto-prepare>`.
- :ref:`scanuser` environment variable.
- Support to `PosFormat` :ref:`ViewOption <sardana-spock-viewoptions>` in `umv` macro.
- Avoid double printing of user units in :ref:`pmtv`: read widget and
  units widget.
- Print of allowed :ref:`sardana-macros-hooks` when :ref:`sardana-spock-gettinghelp`
  on macros in Spock.
- Documentation:

    - :ref:`sardana-1dcontroller-howto` and :ref:`sardana-2dcontroller-howto`
    - :ref:`sardana-countertimercontroller` now contains the `SEP18 \
      <http://www.sardana-controls.org/sep/?SEP18.md>`_ concepts.
    - Properly :ref:`sardana-macro-exception-handling` in macros in order
      to not interfere with macro stopping/aborting
    - :ref:`faq_how_to_access_tango_from_macros_and_controllers`
    - Update :ref:`Installation instructions <sardana-installing>`

Changed
=======

- Experimental channel's shape is now considered as a result of the configuration
  e.g. RoI, binning, etc. and not part of the measurement group configuration:

  - Added :ref:`shape controller axis parameter (plugin) <sardana-2dcontroller-general-guide-shape>`,
    `shape` experimental channel attribute (kernel)
    and `Shape` Tango attribute to the experimental channels
  - **Removed** the *shape* column from the measurement group's configuration panel
    in :ref:`expconf_ui`.

Fixed
=====

- Sardana server (standalone) startup is more robust.
- Storing string values in *datasets*, *pre-scan snapshot* and *custom data*
  in :ref:`sardana-users-scan-data-storage-nxscanh5_filerecorder`.
- Stopping/aborting grouped movement when backlash correction would be applied.
- Randomly swapping target positions in grouped motion when moveables proceed
  from various Device Pool's.
- Enables possible dead time optimization in `mesh` scan macro by executing
  :ref:`per measurement preparation <sardana-macros-scanframework-determscan>`.
- Continuously read experimental channel's value references in hardware
  synchronized acquisition instead of reading only once at the end.
- Problems when :ref:`sardana-controller-howto-change-default-interface` of standard attributes
  in controllers e.g. shape of the pseudo counter's Value attribute.
- :ref:`sequencer_ui` related bugs:

    * Fill Macro's `parent_macro` in case of executing XML hooks in sequencer
    * Problems with macro id's when executing sequences loaded from *plain text* files with spock syntax
    * Loading of sequences using macro functions from *plain text* files with spock syntax
- Apply position formatting (configured with `PosFormat`
  :ref:`ViewOption <sardana-spock-viewoptions>`) to the limits in the `wm` macro.
