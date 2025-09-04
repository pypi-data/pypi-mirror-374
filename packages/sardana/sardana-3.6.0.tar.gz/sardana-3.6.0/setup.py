#!/usr/bin/env python

##############################################################################
##
# This file is part of Sardana
##
# http://www.sardana-controls.org/
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Sardana is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Sardana is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

import os
import sys
import importlib.util
from setuptools import setup



# Create new function find_namespace_packages to be compatible with
# setuptools < 40.1.0 (required for Debian 9).
# Remove this chunk of code and import find_namespace_packages from
# setuptools once we require setuptools >= 40.1.0
try:
    from setuptools import find_namespace_packages
except ImportError:
    from setuptools import PackageFinder

    class PEP420PackageFinder(PackageFinder):
        @staticmethod
        def _looks_like_package(path):
            return True

    find_namespace_packages = PEP420PackageFinder.find

def get_release_info():
    name = "release"
    setup_dir = os.path.dirname(os.path.abspath(__file__))
    release_dir = os.path.join(setup_dir, "src", "sardana", "release.py")
    spec = importlib.util.spec_from_file_location(name, release_dir)
    release = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(release)
    return release

release = get_release_info()

package_dir = {"": "src"}
package_data = {"": ["*"]}

# Exclude sardana.config package until removed (already moved to its own repo)
packages = find_namespace_packages(where="src", exclude=('sardana.config*',))

provides = [
    'sardana',
    # 'sardana.pool',
    # 'sardana.macroserver',
    # 'sardana.spock',
    # 'sardana.tango',
]

install_requires = [
    'PyTango>=9.2.5',  # could be moved to extras_require["tango"] if needed
    'taurus >=5.1.4',
    'lxml>=2.3',
    'click',
    'packaging'
]

extras_require_spock = [
    "ipython>=5.1",
    "itango>=0.1.6",
]

extras_require_qt = [
    "taurus[taurus-qt]",
]

extras_require_all = (
    extras_require_spock
    + extras_require_qt
)

extras_require = {
    "spock": extras_require_spock,
    "qt": extras_require_qt,
    "all": extras_require_all
}

console_scripts = [
    "sardanactl = sardana.cli:main",
    "MacroServer = sardana.tango.macroserver:main",
    "Pool = sardana.tango.pool:main",
    "Sardana = sardana.tango:main",
    "spock = sardana.spock:main",
    "diffractometeralignment = sardana.taurus.qt.qtgui.extra_hkl.diffractometeralignment:main",
    "hklscan = sardana.taurus.qt.qtgui.extra_hkl.hklscan:main",
    "macroexecutor = sardana.taurus.qt.qtgui.extra_macroexecutor.macroexecutor:_main",
    "sequencer = sardana.taurus.qt.qtgui.extra_macroexecutor.sequenceeditor:_main",
    "ubmatrix = sardana.taurus.qt.qtgui.extra_hkl.ubmatrix:main",
    "showscan = sardana.taurus.qt.qtgui.extra_sardana.showscanonline:_main",
]

sardana_subcommands = [
    "expconf = sardana.taurus.qt.qtgui.extra_sardana.expdescription:expconf_cmd",
    "macroexecutor = sardana.taurus.qt.qtgui.extra_macroexecutor.macroexecutor:macroexecutor_cmd",
    "sequencer = sardana.taurus.qt.qtgui.extra_macroexecutor.sequenceeditor.sequenceeditor:sequencer_cmd",
    "showscan = sardana.taurus.qt.qtgui.extra_sardana.showscanonline:showscan_cmd",
    "spock = sardana.spock:spock_cmd",
    "expstatus = sardana.taurus.qt.qtgui.expstatus.expstatus:expstatus_cmd",
]

form_factories = [
    "sardana.pool = sardana.taurus.qt.qtgui.extra_pool.formitemfactory:pool_item_factory"  # noqa
]

pytest_plugins = [
    "sardana_pool_plugins = sardana.pool.test.util"
]

entry_points = {
    'console_scripts': console_scripts,
    'sardana.cli.subcommands': sardana_subcommands,
    'taurus.form.item_factories': form_factories,
    'pytest11': pytest_plugins
}

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Environment :: No Input/Output (Daemon)',
    'Environment :: Win32 (MS Windows)',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Unix',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.5',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development :: Libraries',
]

setup(name='sardana',
      version=release.version,
      description=release.description,
      long_description=release.long_description,
      author=release.authors['Tiago_et_al'][0],
      maintainer=release.authors['Community'][0],
      maintainer_email=release.authors['Community'][1],
      url=release.url,
      download_url=release.download_url,
      platforms=release.platforms,
      license=release.license,
      keywords=release.keywords,
      packages=packages,
      package_dir=package_dir,
      package_data=package_data,
      classifiers=classifiers,
      entry_points=entry_points,
      provides=provides,
      install_requires=install_requires,
      extras_require=extras_require,
      )
