    Title: Sardana Configuration Tool
    SEP: 20
    State: DRAFT
    Date: 2022-04-06
    Drivers: Johan Forsberg <johan.forsberg@maxiv.lu.se>, Zbigniew Reszela <zreszela@cells.es>
    URL: https://gitlab.com/sardana-org/sardana/-/blob/sep20/doc/source/sep/SEP20.md
    License: http://www.jclark.com/xml/copying.txt
    Abstract:
     Sardana does not provide any standard configuration tool, just the
     configuration macros e.g. `defelem`, `set_lim` and bases its
     configuration on Tango DB.
     Different institutes developed their more or less specific tools.
     Here we evaluate the existing tools in the context of requirements
     and develop a standard configuration tool for Sardana.

# Vocabulary

- **Sardana System (System)** - typically composed from servers 
  (Pool, MacroServer and Sardana servers) and clients (Spock, TaurusGUI, 
  macroexecutor) TODO#1
- Personas:
    - **Sardana System Administrator (Administrator)** - typically a Control
      Engineer giving controls support to the laboratory
    - **Sardana System Manager (Manager)** - typically a scientist working
      permanently in the laboratory
    - **Sardana User (User)** - typically a visiting scientist accessing
      the laboratory for an experiment 
- **Sardana System Configuration (Configuration)** - all Elements Definitions
  and Configuration Parameters organized in a hierarchy
    - **Element Definition** - element e.g. motor, measurement group
      definition i.e. name, identifier, etc.
    - **Configuration Parameter** - an atomic part of Sardana System
      Configuration e.g. Configuration Attribute e.g. motor offset,
      velocity, position limit or Configuration Property e.g. controller host
      and port
- **Runtime Sardana System Configuration (Runtime Configuration)** - 
  both Element Definitions and Configuration Parameters, hence the whole
  Sardana System Configuration, have their runtime equivalents e.g. motor,
  measurement group definitions or motor offset or velocity. They are
  not persistently stored and will not be preserved between executions.

# Vision Statement

For Administrators and Managers who need to configure a System,
the Sardana Configuration Tool makes it easy and intuitive to edit
and browse the System Configuration and track historical changes.
Unlike the Tango Database together with the Jive application (which is a very
powerful and generic combination), our solution is specific, simple and transparent.

# Objectives

- Reduce the time of configuring a new System e.g. a new beamline or laboratory.
- Reduce the time of adding/removing/editing elements e.g. adding a new controller, 
  axis, measurement group, etc.
- Increase the participation of Managers in System administration tasks which were
  previously executed by Administrators only.
- Reduce the time of debugging problems caused by a wrong Configuration.
- Smooth the Sardana learning curve.
  
# Requirements

## User Stories

### General

- **GEN01**: As an Administrator/Manager/User, I want clear and intuitive view
  of the Configuration, so it will be easy to browse and find
  what I look for.
- GEN02: (excluded from MVP on sardana follow-up 12/01/2023) As an Administrator/Manager, I want to label different versions
  of Configuration with date&time and optional description,
  so it will be easier to find it afterwards.
- GEN03: As an Administrator/Manager I want to restrict edition of some part
  of the Configuration in order to avoid accidental misconfiguration.
- GEN04: As an Administrator/Manager I want to restrict view
  of some part of the Configuration (expert view) in order to show
  a simpler and more comprehensive view.
- **GEN05**: As an Administrator/Manager/User I want to run a Configuration validation
  procedure so it early discovers mistakes/bugs 
  - before Runtime Configuration dump
  - on server startup
  - on request

### Configuration

- CONF01: As an Administrator, I want to create a new empty Configuration,
  so I could start populating it with elements.
- CONF02: As an Administrator, I want to create a new Configuration from a template,
  so I could continue populating it with elements.
  - Institutes could have their templates that would help in unifying names 
    e.g. Iring vs. sr_current, etc.
- CONF03: As an Administrator/Manager, I want to create new Elements from a template,
  so I could get the System ready for operation.
  - Complex instruments e.g. Detectors, Diffractometers could have their 
    templates that would speed add creating their elements
- CONF04: As an Administrator/Manager, I want to configure Elements and Parameters,
  so I could get the System ready for operation.

### Operation

- **OPER01**: As a Manager/User, I want to store the Runtime Configuration (on request, 
  on server shutdown, periodically) or a part of it, so it becomes the 
  System Configuration
- OPER02: As a Manager/User, I want to apply a Configuration to a part of the System
  e.g. an Element, at runtime, so I avoid to restart the whole System.
- **OPER03**: As an Administrator/Manager/User, I want to start the System
  with a given version of the Configuration, in order to use the System as I need it.

### Debugging

- DBG01: As an Administrator/Manager, I want to browse the history of Configuration
  changes so I could correlate it with other events and debug problems.
- DBG02: As an Administrator/Manager, I want to compare the Configuration
  or parts of it between two points in time so I could debug problems.
- DBG03: As a Administrator/Manager/User, I want to compare the Configuration
  or part of it with its Runtime equivalent so I could debug problems.

## System Requirements

- SYS01: Must run on Linux and Windows.
- SYS02: Should be possible to reuse it in Tango-independent Sardana Systems.

## MVP

Design and development of the solution will start from building Minimum Viable Product (MVP).

Institutes voted on the above listed requirements and, based on the popularity, for MVP was selected:
GEN01, GEN05, OPER01 and OPER03.

# Sardana Configuration prior to SEP20

## Sardana library

[sardanacustomsettings](https://sardana-controls.org/users/configuration/sardanacustomsettings.html)
[!1733](https://gitlab.com/sardana-org/sardana/-/merge_requests/1733)
## Server side

### Tango DB

- Server definitions
- Device definitions
- Device properties
- Attribute properties

![Tango DB](res/sep20/tango_db.jpg)

Memorized attributes:

- Controller
    - LogLevel

- Motor
    - Acceleration
    - Deceleration
    - Base_rate
    - Velocity
    - Offset
    - DialPosition (customly applied)
    - Step_per_unit
    - Backlash
    - Sign

- IORegister
    - Value (customly applied)

- CTExpChannel
    - Timer

- OneDExpChannel
    - Timer

- TwoDExpChannel
    - Timer

- ZeroDExpChannel
    - AccumulationType

- MeasurementGroup
    - AcquisitionMode
    - Configuration
    - Moveable
    - SoftwareSynchronizerInitialDomain
### Environment Variables

[Environment Variable Catalog](https://sardana-controls.org/users/environment_variable_catalog.html)

## Client side

- Spock profile
- Taurus GUI configuration files (XML, Qt ini files)

# Existing Sardana Configuration Tools

1. Sardana configuration format based on XML and tool developed and used at DESY
2. Sardana configuration format based on Excel sheets and
   a tool called sardanasheets developed by MAXIV and used at MAXIV and SOLARIS
   (using dsconfig behind the scene).
3. Sardana configuration format based on Excel sheets and a set of tools developed
   at ALBA and used at ALBA for creation of beamlines of phase I (2011-2013)
   - see sardana/tools/config/README.md
4. Built-in expert macros (can be used only at runtime) e.g. `defctrl`, `defelem`, ...

# Design

Neither of the existing formats: XML, Excel and pure dsconfig (JSON) will be taken
as base of this enhancement. None of them is at the same time:
- human readable
- easy to handle in Python
- flexible and scalable

Sardana configuration format based on YAML was agreed and is documented in:
`sardana/config/test/sar_demo.yaml`

The idea is to reuse dsconfig as an intermediate format for taking a profit
of its integration with Tango DB.

The configuration tools should not require the Sardana system to be running and
it should be enough to work with a Tango DB

# Implementation

The implementation part of this enhancement is focused only on the requirements
selected for the MVP and requires Python 3.7 or higher.

All the configuration tools implementation was placed in `sardana.config` module.

Two modules responsible for translating between the Sardana configuration format
(YAML) and dsconfig (JSON) are: `dsconfig2yaml` and `yaml2dsconfig`.

Roundtripping (maintaining comments, order, etc.) is implemented using `ruamel.yaml`
third-party module.

Format scheme validation is implemented using `pydentic` third-party module

All the actions: 
- dump
- load
- validate
- diff
- merge

are implemented in the modules of the same name.

The CLI tools are implemented using `click` third-party module (see 
discussion on the CLI tools design in [#1823](<https://gitlab.com/sardana-org/sardana/-/issues/1823>))

# Documentation 

General discussion on this SEP took place on [!1749](https://gitlab.com/sardana-org/sardana/-/merge_requests/1749) MR.

All tools document their usage in the docstring which is accessible
to the users with the `--help` option.

Higher level documentation was placed in `Documentation -> User's Guide -> Configuration`.

# Changes

- 2022-04-06 [reszelaz][]. DRAFT
- 2023-02-27 [reszelaz][]. DRAFT -> CANDIDATE
