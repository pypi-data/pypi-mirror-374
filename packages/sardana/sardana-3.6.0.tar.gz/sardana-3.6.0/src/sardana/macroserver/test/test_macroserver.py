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
import os.path
import tempfile

import pytest

from sardana.macroserver import macro
from sardana.macroserver.msmetamacro import (
    MacroFunction,
    MacroClass,
    MacroLibrary
)
from sardana.macroserver.msmetarecorder import (
    RecorderClass,
    RecorderLibrary
)
from sardana.macroserver.macroserver import MacroServer
from sardana.macroserver.msenvmanager import UnknownEnv


class ElementsChangedCb:

    def __init__(self):
        self.reset()
    
    def reset(self):
        self.new_elements = []
        self.changed_elements = []
        self.deleted_elements = []

    def on_elements_changed(self, source, type_, value):
        if type_.name == "ElementsChanged":
            self.new_elements = value["new"]
            self.changed_elements = value["change"]
            self.deleted_elements = value["del"]


def assert_elements(elements, allowed_types, elem_name):
    elem_found = False
    for elem in elements:
        assert (
            isinstance(elem, allowed_types)
        ), "element of unexpected type"
        if elem.name == elem_name:
            elem_found = True
    assert elem_found, "element {} not found"


def test_set_macro_path():                    
    ms = MacroServer("test")
    cb = ElementsChangedCb()
    ms.add_listener(cb.on_elements_changed)
    ms.set_macro_path([])

    assert len(cb.new_elements) > 0, \
        "no 'new' elements in 'ElementsChanged' event"
    assert len(cb.changed_elements) == 0, \
        "unexpected 'changed' elements in 'ElementsChanged' event"
    assert len(cb.deleted_elements) == 0, \
        "unexpected 'changed' elements in 'ElementsChanged' event"
    allowed_types = (MacroFunction, MacroClass, MacroLibrary)
    assert_elements(
        elements=cb.new_elements,
        allowed_types=allowed_types,
        elem_name="sar_info"
    )

    expected_changed_elements = len(cb.new_elements)
    
    cb.reset()
    ms.set_macro_path([])

    assert len(cb.new_elements) == 0, \
        "unexpected 'new' elements in 'ElementsChanged' event"
    assert len(cb.changed_elements) == expected_changed_elements, \
        "wrong number of 'changed' elements in 'ElementsChanged' event"
    assert len(cb.deleted_elements) == 0, \
        "unexpected 'changed' elements in 'ElementsChanged' event"

    assert_elements(
        elements=cb.changed_elements,
        allowed_types=allowed_types,
        elem_name="sar_info"
    )


def test_set_recorder_path():                    
    ms = MacroServer("test")
    cb = ElementsChangedCb()
    ms.add_listener(cb.on_elements_changed)
    ms.set_recorder_path([])

    assert len(cb.new_elements) > 0, \
        "no 'new' elements in 'ElementsChanged' event"
    assert len(cb.changed_elements) == 0, \
        "unexpected 'changed' elements in 'ElementsChanged' event"
    assert len(cb.deleted_elements) == 0, \
        "unexpected 'changed' elements in 'ElementsChanged' event"
    
    assert_elements(
        elements=cb.new_elements,
        allowed_types=(RecorderClass, RecorderLibrary),
        elem_name="NXscanH5_FileRecorder"
    )

    expected_changed_elements = len(cb.new_elements)

    ms.set_recorder_path([])

    assert len(cb.new_elements) == 0, \
        "unexpected 'new' elements in 'ElementsChanged' event"
    assert len(cb.changed_elements) == expected_changed_elements, \
        "wrong number of 'changed' elements in 'ElementsChanged' event"
    assert len(cb.deleted_elements) == 0, \
        "unexpected 'changed' elements in 'ElementsChanged' event"

    assert_elements(
        cb.changed_elements,
        allowed_types=(RecorderClass, RecorderLibrary),
        elem_name="NXscanH5_FileRecorder"
    )


def test_reload_macro_lib():
    ms = MacroServer("test")
    cb = ElementsChangedCb()
    ms.set_macro_path([])
    ms.add_listener(cb.on_elements_changed)
    ms.reload_macro_lib("expert")

    assert len(cb.new_elements) == 0, \
        "unexpected 'new' elements in 'ElementsChanged' event"
    assert len(cb.deleted_elements) == 0, \
        "unexpected 'del' elements in 'ElementsChanged' event"
    assert_elements(
        elements=cb.changed_elements,
        allowed_types=(MacroFunction, MacroClass, MacroLibrary),
        elem_name="sar_info"
    )


class TestEnvironmentManager:

    @pytest.fixture
    def env_manager(self):
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            ms = MacroServer("test")
            ms.set_environment_db(os.path.join(tmp_dir_name, "testenv"))
            yield ms.environment_manager
            ms.environment_manager.cleanUp()

    @pytest.mark.parametrize(
        "value, expected",
        [
            ("self", "self"),
            ("__builtins__", "__builtins__"),
            ("k", "k"),
            ("v", "v"),
            ("d", "d"),
        ],
    )
    def test_set_get_env_does_not_access_locals_or_globals(self, env_manager, value, expected):
        env_manager.setEnv("key", value)
        assert env_manager.getEnv("key") == expected

    @pytest.mark.parametrize(
        "value, expected",
        [
            (123, 123),
            (12.5, 12.5),
            ("123", 123),
            ("12.5", 12.5),
            (True, True),
            ("True", True),
            ("true", True),
            ("faLSE", False),
            ({"a": 1, "b": {"c": 2}}, {"a": 1, "b": {"c": 2}}),
            ("{'a': 1, 'b': {'c': 2}}", {"a": 1, "b": {"c": 2}}),
            (("real", "tuple"), ("real", "tuple")),
            ('("str", "tuple")', ("str", "tuple")),
            (["real", "list"], ["real", "list"]),
            ('["str", "list"]', ["str", "list"]),
            ("['not a', 'list", "['not a', 'list"),
        ],
    )
    def test_set_get_env_works_with_normal_inputs(self, env_manager, value, expected):
        env_manager.setEnv("key", value)
        assert env_manager.getEnv("key") == expected

    def test_get_env_raises_on_none_value(self, env_manager):
        env_manager.setEnv("key", None)
        with pytest.raises(UnknownEnv):
            env_manager.getEnv("key")

    def test_get_env_raises_on_unknown_key(self, env_manager):
        with pytest.raises(UnknownEnv):
            env_manager.getEnv("never-set")

    def test_get_env_raises_after_key_unset(self, env_manager):
        env_manager.setEnv("key", "abc")
        assert env_manager.getEnv("key") == "abc"
        env_manager.unsetEnv("key")
        with pytest.raises(UnknownEnv):
            env_manager.getEnv("key")

    def test_set_env_overwrites_previous(self, env_manager):
        env_manager.setEnv("key", "old")
        assert env_manager.getEnv("key") == "old"
        env_manager.setEnv("key", "new")
        assert env_manager.getEnv("key") == "new"
