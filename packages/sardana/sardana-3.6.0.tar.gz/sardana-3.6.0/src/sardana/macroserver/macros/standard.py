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

"""This is the standard macro module"""

__all__ = ["ct", "mstate", "mv", "mvr", "pwa", "pwm", "repeat", "set_user_lim",
           "set_dial_lim", "set_lim", "set_lm", "set_dial_pos", "set_pos",
           "set_user_pos", "set_step_per_unit", "sleep", "uct", "umv", "umvr",
           "wa", "wm", "tw", "logmacro", "newfile", "plotselect", "pic", "cen",
           "com", "where"]


__docformat__ = 'restructuredtext'

import datetime
import os
import re
import time

import numpy as np
from taurus import Device
from taurus.console.table import Table
import PyTango
from PyTango import DevState

from sardana.macroserver.macro import Macro, macro, Type, ViewOption, \
    iMacro, Hookable
from sardana.macroserver.msexception import StopException, UnknownEnv
from sardana.macroserver.scan.scandata import Record
from sardana.macroserver.macro import Optional
from sardana import sardanacustomsettings

##########################################################################
#
# Motion related macros
#
##########################################################################


class _wm(Macro):
    """Show motor positions"""

    param_def = [
        ['motor_list', [['motor', Type.Moveable, None, 'Motor to move']],
         None, 'List of motor to show'],
    ]

    def run(self, motor_list):
        show_dial = self.getViewOption(ViewOption.ShowDial)
        show_ctrlaxis = self.getViewOption(ViewOption.ShowCtrlAxis)
        pos_format = self.getViewOption(ViewOption.PosFormat)
        motor_width = 9
        motors = {}  # dict(motor name: motor obj)
        requests = {}  # dict(motor name: request id)
        data = {}  # dict(motor name: list of motor data)
        # sending asynchronous requests: neither Taurus nor Sardana extensions
        # allow asynchronous requests - use PyTango asynchronous request model
        for motor in motor_list:
            name = motor.getName()
            motors[name] = motor
            args = ('position',)
            if show_dial:
                args += ('dialposition',)
            _id = motor.read_attributes_asynch(args)
            requests[name] = _id
            motor_width = max(motor_width, len(name))
            data[name] = []
        # get additional motor information (ctrl name & axis)
        if show_ctrlaxis:
            for name, motor in motors.items():
                ctrl_name = self.getController(motor.controller).name
                axis_nb = str(getattr(motor, "axis"))
                data[name].extend((ctrl_name, axis_nb))
                motor_width = max(motor_width, len(ctrl_name), len(axis_nb))
        # collect asynchronous replies
        while len(requests) > 0:
            req2delete = []
            for name, _id in requests.items():
                motor = motors[name]
                try:
                    attrs = motor.read_attributes_reply(_id)
                    for attr in attrs:
                        value = attr.value
                        if value is None:
                            value = float('NaN')
                            if attr.name == 'dialposition':
                                value = motor.getDialPosition()
                                if value is None:
                                    value = float('NaN')
                        data[name].append(value)
                    req2delete.append(name)
                except PyTango.AsynReplyNotArrived:
                    continue
                except PyTango.DevFailed:
                    data[name].append(float('NaN'))
                    if show_dial:
                        data[name].append(float('NaN'))
                    req2delete.append(name)
                    self.debug('Error when reading %s position(s)' % name)
                    self.debug('Details:', exc_info=1)
                    continue
            # removing motors which alredy replied
            for name in req2delete:
                requests.pop(name)
        # define format for numerical values
        fmt = '%c*.%df' % ('%', motor_width - 5)
        if pos_format > -1:
            fmt = '%c*.%df' % ('%', int(pos_format))
        # prepare row headers and formats
        row_headers = []
        t_format = []
        if show_ctrlaxis:
            row_headers += ['Ctrl', 'Axis']
            t_format += ['%*s', '%*s']
        row_headers.append('User')
        t_format.append(fmt)
        if show_dial:
            row_headers.append('Dial')
            t_format.append(fmt)
        # sort the data dict by keys
        col_headers = []
        values = []
        for mot_name, mot_values in sorted(data.items()):
            col_headers.append([mot_name])  # convert name to list
            values.append(mot_values)
        # create and print table
        table = Table(values, elem_fmt=t_format,
                      col_head_str=col_headers, col_head_width=motor_width,
                      row_head_str=row_headers)
        for line in table.genOutput():
            self.output(line)


class _wum(Macro):
    """Show user motor positions"""

    param_def = [
        ['motor_list', [['motor', Type.Moveable, None, 'Motor to move']],
         None, 'List of motor to show'],
    ]

    def prepare(self, motor_list, **opts):
        self.table_opts = {}

    def run(self, motor_list):
        motor_width = 9
        motor_names = []
        motor_pos = []
        motor_list = sorted(motor_list)
        pos_format = self.getViewOption(ViewOption.PosFormat)
        for motor in motor_list:
            name = motor.getName()
            motor_names.append([name])
            pos = motor.getPosition(force=True)
            if pos is None:
                pos = float('NAN')
            motor_pos.append((pos,))
            motor_width = max(motor_width, len(name))

        fmt = '%c*.%df' % ('%', motor_width - 5)
        if pos_format > -1:
            fmt = '%c*.%df' % ('%', int(pos_format))

        table = Table(motor_pos, elem_fmt=[fmt],
                      col_head_str=motor_names, col_head_width=motor_width,
                      **self.table_opts)
        for line in table.genOutput():
            self.output(line)


class wu(Macro):
    """Show all user motor positions"""

    def prepare(self, **opts):
        self.all_motors = self.findObjs('.*', type_class=Type.Moveable, reserve=False)
        self.table_opts = {}

    def run(self):
        nr_motors = len(self.all_motors)
        if nr_motors == 0:
            self.output('No motor defined')
            return

        self.output('Current positions (user) on %s' %
                    datetime.datetime.now().isoformat(' '))
        self.output('')

        self.execMacro('_wum', self.all_motors, **self.table_opts)


class wa(Macro):
    """Show all motor positions"""

    # TODO: duplication of the default value definition is a workaround
    # for #427. See commit message cc3331a for more details.
    param_def = [
        ['filter', [['filter', Type.String, '.*',
                     'a regular expression filter'], {'min': 1}],
         ['.*'], 'a regular expression filter'],
    ]

    def prepare(self, filter, **opts):
        self.all_motors = self.findObjs(filter, type_class=Type.Moveable, reserve=False)
        self.table_opts = {}

    def run(self, filter):
        nr_motors = len(self.all_motors)
        if nr_motors == 0:
            self.output('No motor defined')
            return

        show_dial = self.getViewOption(ViewOption.ShowDial)
        if show_dial:
            self.output('Current positions (user, dial) on %s' %
                        datetime.datetime.now().isoformat(' '))
        else:
            self.output('Current positions (user) on %s' %
                        datetime.datetime.now().isoformat(' '))
        self.output('')
        self.execMacro('_wm', self.all_motors, **self.table_opts)


class pwa(Macro):
    """Show all motor positions in a pretty table"""

    # TODO: duplication of the default value definition is a workaround
    # for #427. See commit message cc3331a for more details.
    param_def = [
        ['filter', [['filter', Type.String, '.*',
                     'a regular expression filter'], {'min': 1}],
         ['.*'], 'a regular expression filter'],
    ]

    def run(self, filter):
        self.execMacro('wa', filter, **Table.PrettyOpts)


class set_user_lim(Macro):
    """Sets the user limits on the specified motor"""

    param_def = [
        ["motor", Type.Moveable, None, "Motor name"],
        ["low", Type.Float, None, "lower user limit"],
        ["high", Type.Float, None, "upper user limit"],
    ]

    def run(self, motor, low, high):
        name = motor.getName()
        self.debug("Setting user limits for %s" % name)
        if low > high:
            raise ValueError("lower limit must be lower than the upper limit")
        motor.getPositionObj().setLimits(low, high)
        self.output(
            "%s limits set to %.4f %.4f (user units)" % (name, low, high)
            )


class set_dial_lim(Macro):
    """Sets the dial limits on the specified motor"""

    param_def = [
        ["motor", Type.Motor, None, "Motor name"],
        ["low", Type.Float, None, "lower dial limit"],
        ["high", Type.Float, None, "upper dial limit"],
    ]

    def run(self, motor, low, high):
        name = motor.getName()
        self.debug("Setting dial limits for %s" % name)
        if low > high:
            raise Exception("lower limit must be lower than the upper limit")
        motor.getDialPositionObj().setLimits(low, high)
        self.output(
            "%s limits set to %.4f %.4f (dial units)" % (name, low, high)
            )


class set_lim(set_user_lim):
    """Deprecated: Sets the user limits on the specified motor"""

    def prepare(self, motor, low, high):
        self.warning('Deprecation warning: you should use '
                     '"set_user_lim" instead of "set_lim"')


class set_lm(set_dial_lim):
    """Deprecated: Sets the dial limits on the specified motor"""

    def prepare(self, motor, low, high):
        self.warning('Deprecation warning: you should use '
                     '"set_dial_lim" instead of "set_lm"')


class set_dial_pos(Macro):
    """Sets the USER position of the motor to the specified value
    (by changing DIAL and keeping OFFSET).
    """

    param_def = [
        ['motor', Type.Motor, None, 'Motor name'],
        ['pos',   Type.Float, None, 'Position to move to']
    ]

    def run(self, motor, pos):
        name = motor.getName()
        old_pos = motor.getPosition(force=True)
        motor.definePosition(pos)
        self.output("%s reset from %.4f to %.4f" % (name, old_pos, pos))


class set_pos(set_dial_pos):
    """Deprecated: Sets the dial position on the specified motor"""

    def prepare(self, motor, pos):
        self.warning('Deprecation warning: you should use '
                     '"set_dial_pos" instead of "set_pos"')


class set_user_pos(Macro):
    """Sets the USER position of the motor to the specified value (by
    changing OFFSET and keeping DIAL) and recalculates the USER limits
    (can be disabled with the `update_limit` parameter)."""

    param_def = [
        ['motor', Type.Motor, None, 'Motor name'],
        ['pos',   Type.Float, None, 'Position to move to'],
        ['update_limit', Type.Boolean, True,
         'Update the software limit, enabled by default']
    ]

    def run(self, motor, pos, update_limit):
        name = motor.getName()
        old_pos = motor.getPosition(force=True)
        offset_attr = motor.getAttribute('Offset')
        old_offset = offset_attr.read().rvalue.magnitude
        new_offset = pos - (old_pos - old_offset)
        offset_attr.write(new_offset)

        if update_limit is True:
            posObj = motor.getPositionObj()
            new_high = self.calculate_limit(posObj, pos, old_pos, 'high')
            new_low = self.calculate_limit(posObj, pos, old_pos, 'low')
            self.set_user_lim(motor, new_low, new_high)

        msg = "%s reset from %.4f (offset %.4f) to %.4f (offset %.4f)" % (
            name, old_pos, old_offset, pos, new_offset)
        self.output(msg)

    def calculate_limit(self, posObj, new_pos, old_pos, limit):
        if limit == 'high':
            old_limit = posObj.getMaxRange().magnitude
        elif limit == 'low':
            old_limit = posObj.getMinRange().magnitude
        else:
            raise Exception("the limit specification is invalid")
        new_limit = new_pos - (old_pos - old_limit)
        return new_limit


class set_step_per_unit(Macro):
    """Set the step_per_unit defined by user. Macro allows to update 
    limits (user and dial) depending on update_limits value.
    """
    
    param_def = [
        ['motor', Type.Moveable, None, 'Motor to update steps_per_unit.'],
        ['step_per_unit', Type.Float, None,'New step per unit to be applied.'],
        ['update_limits', Type.Boolean, False, 'Update limits.']
    ]

    def run(self, motor, step_per_unit, update_limits):

        try:
            old_step_per_unit = motor.getStepPerUnit()
            motor.setStepPerUnit(step_per_unit)
        except Exception as e:
            raise RuntimeError(
                "We can not update step_per_unit in {}".format(motor)) from e

        if not update_limits:
            return
        try:
            factor = self.calculate_conversion_factor(old_step_per_unit,
                                                      step_per_unit)

            user_upper_limit, user_lower_limit = self.calculate_limits(
                motor.getPositionObj(), factor)
            dial_upper_limit, dial_lower_limit = self.calculate_limits(
                motor.getDialPositionObj(), factor)

            self.set_user_lim(motor, user_lower_limit, user_upper_limit)   
            self.set_dial_lim(motor, dial_lower_limit, dial_upper_limit)
        
        except Exception as e:
            raise RuntimeError(
                "We can not update limits in {}".format(motor)) from e    
           
    def calculate_conversion_factor(self, old_step_per_unit, new_step_per_unit):
        try:
            factor = new_step_per_unit / old_step_per_unit
        
        except Exception as e:
            raise ValueError("We can not calculate conversion factor") from e

        return factor

    def get_new_limit(self, actual_software_limit, factor):
        try:
            new_limit = actual_software_limit / factor

        except Exception as e:
            raise ValueError("We can not calculate new limit") from e

        return new_limit
    
    def calculate_limits(self, positionObj, factor):
        try:
            actual_upper_limit = positionObj.getMaxRange().magnitude
            actual_lower_limit = positionObj.getMinRange().magnitude
            new_upper_limit = self.get_new_limit(actual_upper_limit, factor)
            new_lower_limit = self.get_new_limit(actual_lower_limit, factor)
        
        except Exception as e:
            txt = positionObj.getSimpleName()
            
            raise ValueError(
                "We can not calculate new {} limits.".format(txt)) from e

        return new_upper_limit, new_lower_limit


class wm(Macro):
    """Show the position of the specified motors."""

    param_def = [
        ['motor_list', [['motor', Type.Moveable, None,
                         'Motor to see where it is']],
         None, 'List of motor to show'],
    ]

    @staticmethod
    def format_value(fmt, str_fmt, value):
        """
        Formats given value following the fmt and/or str_fmt rules.

        Parameters
        ----------
        fmt : str
            The value format.

        str_fmt : str
            The string format.

        value : float
            The value to be formatted.

        Returns
        -------
        str
            The string formatted value.
        """

        if fmt is not None:
            fmt_value = fmt % value
            fmt_value = str_fmt % fmt_value
        else:
            fmt_value = str_fmt % value

        return fmt_value

    def prepare(self, motor_list, **opts):
        self.table_opts = {}

    def run(self, motor_list):
        motor_width = 10
        motor_names = []
        motor_pos = []

        show_dial = self.getViewOption(ViewOption.ShowDial)
        show_ctrlaxis = self.getViewOption(ViewOption.ShowCtrlAxis)
        pos_format = self.getViewOption(ViewOption.PosFormat)

        for motor in motor_list:

            max_len = 0
            if show_ctrlaxis:
                axis_nb = getattr(motor, "axis")
                ctrl_name = self.getController(motor.controller).name
                max_len = max(max_len, len(ctrl_name), len(str(axis_nb)))
            name = motor.getName()
            max_len = max(max_len, len(name))

            max_len = max_len + 5
            if max_len < 14:
                max_len = 14  # Length of 'Not specified'

            str_fmt = "%c%ds" % ('%', int(max_len))

            name = str_fmt % name

            motor_names.append([name])
            posObj = motor.getPositionObj()
            if pos_format > -1:
                fmt = '%c.%df' % ('%', int(pos_format))
            else:
                fmt = None

            val1 = motor.getPosition(force=True)
            val1 = self.format_value(fmt, str_fmt, val1)

            val2 = posObj.getMaxRange().magnitude
            val2 = self.format_value(fmt, str_fmt, val2)

            val3 = posObj.getMinRange().magnitude
            val3 = self.format_value(fmt, str_fmt, val3)

            if show_ctrlaxis:
                valctrl = str_fmt % (ctrl_name)
                valaxis = str_fmt % str(axis_nb)
                upos = list(map(str, [valctrl, valaxis, ' ', val2, val1,
                                      val3]))
            else:
                upos = list(map(str, ['', val2, val1, val3]))
            pos_data = upos
            if show_dial:
                try:
                    val1 = fmt % motor.getDialPosition(force=True)
                    val1 = str_fmt % val1
                except Exception:
                    val1 = str_fmt % motor.getDialPosition(force=True)

                dPosObj = motor.getDialPositionObj()
                val2 = str_fmt % dPosObj.getMaxRange().magnitude
                val3 = str_fmt % dPosObj.getMinRange().magnitude

                dpos = list(map(str, [val2, val1, val3]))
                pos_data += [''] + dpos

            motor_pos.append(pos_data)

        elem_fmt = (['%*s'] + ['%*s'] * 5) * 2
        row_head_str = []
        if show_ctrlaxis:
            row_head_str += ['Ctrl', 'Axis']
        row_head_str += ['User', ' High', ' Current', ' Low']
        if show_dial:
            row_head_str += ['Dial', ' High', ' Current', ' Low']
        table = Table(motor_pos, elem_fmt=elem_fmt, row_head_str=row_head_str,
                      col_head_str=motor_names, col_head_width=motor_width,
                      **self.table_opts)
        for line in table.genOutput():
            self.output(line)


class wum(Macro):
    """Show the user position of the specified motors."""

    param_def = [
        ['motor_list', [['motor', Type.Moveable, None,
                         'Motor to see where it is']],
         None, 'List of motor to show'],
    ]

    def prepare(self, motor_list, **opts):
        self.table_opts = {}

    def run(self, motor_list):
        motor_width = 10
        motor_names = []
        motor_pos = []

        for motor in motor_list:
            name = motor.getName()
            motor_names.append([name])
            posObj = motor.getPositionObj()
            upos = list(map(str, [posObj.getMaxRange().magnitude,
                                  motor.getPosition(force=True),
                                  posObj.getMinRange().magnitude]))
            pos_data = [''] + upos

            motor_pos.append(pos_data)

        elem_fmt = (['%*s'] + ['%*s'] * 3) * 2
        row_head_str = ['User', ' High', ' Current', ' Low', ]
        table = Table(motor_pos, elem_fmt=elem_fmt, row_head_str=row_head_str,
                      col_head_str=motor_names, col_head_width=motor_width,
                      **self.table_opts)
        for line in table.genOutput():
            self.output(line)


class pwm(Macro):
    """Show the position of the specified motors in a pretty table"""

    param_def = [
        ['motor_list', [['motor', Type.Moveable, None, 'Motor to move']],
         None, 'List of motor to show'],
    ]

    def run(self, motor_list):
        self.execMacro('wm', motor_list, **Table.PrettyOpts)


class mv(Macro, Hookable):
    """Move motor(s) to the specified position(s)"""

    hints = {'allowsHooks': ('pre-move', 'post-move')}
    param_def = [
        ['motor_pos_list',
         [['motor', Type.Moveable, None, 'Motor to move'],
          ['pos',   Type.Float, None, 'Position to move to']],
         None, 'List of motor/position pairs'],
    ]

    def run(self, motor_pos_list):
        self.motors, positions = [], []
        for m, p in motor_pos_list:
            self.motors.append(m)
            positions.append(p)

        enable_hooks = getattr(sardanacustomsettings,
                               'PRE_POST_MOVE_HOOK_IN_MV',
                               True)

        if enable_hooks:
            for preMoveHook in self.getHooks('pre-move'):
                preMoveHook()

        for m, p in zip(self.motors, positions):
            self.debug("Starting %s movement to %s", m.getName(), p)

        motion = self.getMotion(self.motors)
        try:
            state, pos = motion.move(positions)
        except Exception as e:
            self.warning("Motion failed due to: {}".format(e))
            self._log_information()
            raise e
        if state != DevState.ON:
            self.warning("Motion ended in %s", state.name)
            self._log_information()

        if enable_hooks:
            for postMoveHook in self.getHooks('post-move'):
                postMoveHook()

    def _log_information(self):
        msg = []
        for motor in self.motors:
            msg.append(motor.information())
        self.info("\n".join(msg))


class mstate(Macro):
    """Prints the state of a motor"""

    param_def = [['motor', Type.Moveable, None, 'Motor to check state']]

    def run(self, motor):
        self.info("Motor %s" % str(motor.stateObj.read().rvalue))


class umv(Macro, Hookable):
    """Move motor(s) to the specified position(s) and update"""

    hints = {'allowsHooks': ('pre-move', 'post-move')}
    param_def = mv.param_def

    def prepare(self, motor_pos_list, **opts):
        self.all_names = []
        self.all_pos = []
        self.motors = []
        self.print_pos = False
        for motor, pos in motor_pos_list:
            self.all_names.append([motor.getName()])
            self.motors.append(motor)
            pos, posObj = motor.getPosition(force=True), motor.getPositionObj()
            self.all_pos.append([pos])
            posObj.subscribeEvent(self.positionChanged, motor)

    def run(self, motor_pos_list):
        self.print_pos = True
        try:
            mv, _ = self.createMacro('mv', motor_pos_list)
            mv._setHooks(self.hooks)
            self.runMacro(mv)
        finally:
            self.finish()

    def finish(self):
        self._clean()

    def _clean(self):
        for motor, pos in self.getParameters()[0]:
            posObj = motor.getPositionObj()
            try:
                posObj.unsubscribeEvent(self.positionChanged, motor)
            except Exception as e:
                print(str(e))
                raise e

    def positionChanged(self, motor, position):
        idx = self.all_names.index([motor.getName()])
        self.all_pos[idx] = [position]
        if self.print_pos:
            self.printAllPos()

    def printAllPos(self):
        motor_width = 10
        pos_format = self.getViewOption(ViewOption.PosFormat)
        fmt = '%*.4f'
        if pos_format > -1:
            fmt = '%c*.%df' % ('%', int(pos_format))
        table = Table(self.all_pos, elem_fmt=[fmt],
                      col_head_str=self.all_names, col_head_width=motor_width)
        self.outputBlock(table.genOutput())
        self.flushOutput()


class mvr(Macro, Hookable):
    """Move motor(s) relative to the current position(s)"""

    hints = {'allowsHooks': ('pre-move', 'post-move')}
    param_def = [
        ['motor_disp_list',
         [['motor', Type.Moveable, None, 'Motor to move'],
          ['disp',  Type.Float, None, 'Relative displacement']],
         None, 'List of motor/displacement pairs'],
    ]

    def run(self, motor_disp_list):
        self.motors, motor_pos_list = [], []
        for motor, disp in motor_disp_list:
            pos = motor.getPosition(force=True)
            self.motors.append(motor)
            if pos is None:
                self.error("Cannot get %s position" % motor.getName())
                return
            else:
                pos += disp
            motor_pos_list.append([motor, pos])
        mv, _ = self.createMacro('mv', motor_pos_list)
        mv._setHooks(self.hooks)
        self.runMacro(mv)


class umvr(Macro, Hookable):
    """Move motor(s) relative to the current position(s) and update"""

    hints = {'allowsHooks': ('pre-move', 'post-move')}
    param_def = mvr.param_def

    def run(self, motor_disp_list):
        self.motors, motor_pos_list = [], []
        for motor, disp in motor_disp_list:
            pos = motor.getPosition(force=True)
            self.motors.append(motor)
            if pos is None:
                self.error("Cannot get %s position" % motor.getName())
                return
            else:
                pos += disp
            motor_pos_list.append([motor, pos])
        umv, _ = self.createMacro('umv', motor_pos_list)
        umv._setHooks(self.hooks)
        self.runMacro(umv)

# TODO: implement tw macro with param repeats in order to be able to pass
# multiple motors and multiple deltas. Also allow to pass the integration time
# in order to execute the measurement group acquisition after each move and
# print the results. Basically follow the SPEC's API:
# https://certif.com/spec_help/tw.html


class tw(iMacro):
    """Tweak motor by variable delta"""

    param_def = [
        ['motor', Type.Moveable, "test", 'Motor to move'],
        ['delta',   Type.Float, None, 'Amount to tweak']
    ]

    def run(self, motor, delta):
        self.output(
            "Indicate direction with + (or p) or - (or n) or enter")
        self.output(
            "new step size. Type something else (or ctrl-C) to quit.")
        self.output("")
        if np.sign(delta) == -1:
            a = "-"
        if np.sign(delta) == 1:
            a = "+"
        while a in ('+', '-', 'p', 'n'):
            pos = motor.position
            a = self.input("%s = %s, which way? " % (
                motor, pos), default_value=a, data_type=Type.String)
            try:
                # check if the input is a new delta
                delta = float(a)
                # obtain the sign of the new delta
                if np.sign(delta) == -1:
                    a = "-"
                else:
                    a = "+"
            except:
                # convert to the common sign
                if a == "p":
                    a = "+"
                # convert to the common sign
                elif a == "n":
                    a = "-"
                # the sign is already correct, just continue
                elif a in ("+", "-"):
                    pass
                else:
                    msg = "Typing '%s' caused 'tw' macro to stop." % a
                    self.info(msg)
                    raise StopException()
                # invert the delta if necessary
                if (a == "+" and np.sign(delta) < 0) or \
                   (a == "-" and np.sign(delta) > 0):
                    delta = -delta
            pos += delta
            self.mv(motor, pos)


##########################################################################
#
# Data acquisition related macros
#
##########################################################################


def _value_to_repr(data):
    if data is None:
        return "<nodata>"
    elif np.ndim(data) > 0:
        return list(np.shape(data))
    else:
        return data


class _ct:

    def dump_information(self, elements):
        msg = ["Elements ended acquisition with:"]
        for element in elements:
            msg.append(element.information())
        self.info("\n".join(msg))

    def _getElements(self):
        if self.countable_elem.type == Type.MeasurementGroup:
            names = self.countable_elem.ElementList
            if names is None:
                elements = []
            else:
                elements = [self.getObj(name) for name in names]
        else:    
            elements = [self.countable_elem]
        return elements


class ct(Macro, Hookable, _ct):
    """Count for the specified time on the measurement group
       or experimental channel given as second argument
       (if not given the active measurement group is used)"""

    hints = {'allowsHooks': ('pre-acq', 'post-acq')}
    param_def = [
        ['integ_time', Type.Float, 1.0, 'Integration time'],
        ['countable_elem', Type.Countable, Optional,
         'Countable element e.g. MeasurementGroup or ExpChannel']
    ]



    def run(self, integ_time, countable_elem):
        if countable_elem is None:
            try:
                self.countable_elem_name = self.getEnv('ActiveMntGrp')
            except UnknownEnv:
                msg = ('No countable element. Use macro parameter or set'
                   ' ActiveMntGrp environment variable.')
                raise RuntimeError(msg)
        else:
            self.countable_elem_name = countable_elem.name
        self.countable_elem = self.getObj(self.countable_elem_name)
        if self.countable_elem is None:
            msg = ('ActiveMntGrp is referencing a nonexistent countable element.')
            raise RuntimeError(msg)

        # integration time has to be accessible from with in the hooks
        self.integ_time = integ_time
        self.debug("Counting for %s sec", integ_time)
        self.outputDate()
        self.output('')
        self.flushOutput()

        for preAcqHook in self.getHooks('pre-acq'):
            preAcqHook()

        try:
            state, data = self.countable_elem.count(integ_time)
        except Exception:
            self.dump_information(self._getElements())
            raise
        if state != DevState.ON:
            self.dump_information(self._getElements())
            raise ValueError("Acquisition ended with {}".format(
                state.name.capitalize()))

        for postAcqHook in self.getHooks('post-acq'):
            postAcqHook()

        names, counts = [], []
        if self.countable_elem.type == Type.MeasurementGroup:
            meas_grp = self.countable_elem
            for ch_info in meas_grp.getChannelsEnabledInfo():
                names.append('  %s' % ch_info.label)
                ch_data = data.get(ch_info.full_name)
                counts.append(_value_to_repr(ch_data))
        else:
            channel = self.countable_elem
            names.append("  %s" % channel.name)
            counts.append(_value_to_repr(data))
            # to be compatible with measurement group count
            data = {channel.full_name: data}
        self.setData(Record(data))
        table = Table([counts], row_head_str=names, row_head_fmt='%*s',
                      col_sep='  =  ')
        for line in table.genOutput():
            self.output(line)


class uct(Macro, _ct):
    """Count on the active measurement group and update"""

    param_def = [
        ['integ_time', Type.Float, 1.0, 'Integration time'],
        ['countable_elem', Type.Countable, Optional,
         'Countable element e.g. MeasurementGroup or ExpChannel']
    ]

    def prepare(self, integ_time, countable_elem, **opts):

        self.print_value = False

        if countable_elem is None:
            try:
                self.countable_elem_name = self.getEnv('ActiveMntGrp')
            except UnknownEnv:
                msg = ('No countable element. Use macro parameter or set'
                   ' ActiveMntGrp environment variable.')
                raise RuntimeError(msg)
        else:
            self.countable_elem_name = countable_elem.name
        
        self.countable_elem = self.getObj(self.countable_elem_name)

        if self.countable_elem is None:
            msg = ('ActiveMntGrp is referencing a nonexistent countable element.')
            raise RuntimeError(msg)

        self.channels = []
        self.values = []
        names = []
        if self.countable_elem.type == Type.MeasurementGroup:
            meas_grp = self.countable_elem
            for channel_info in meas_grp.getChannelsEnabledInfo():
                names.append(channel_info.label)
            self.names = [[n] for n in names]
            for channel_info in meas_grp.getChannelsEnabledInfo():
                full_name = channel_info.full_name
                channel = Device(full_name)
                self.channels.append(channel)
                value = channel.getValue(force=True)
                self.values.append([value])
                valueObj = channel.getValueObj_()
                valueObj.subscribeEvent(self.counterChanged, channel)
        else:
            channel = self.countable_elem
            self.names = [[channel.getName()]]
            channel = Device(channel.full_name)
            self.channels.append(channel)
            value = channel.getValue(force=True)
            self.values.append([value])
            valueObj = channel.getValueObj_()
            valueObj.subscribeEvent(self.counterChanged, channel)

    def run(self, integ_time, countable_elem):
        self.print_value = True
        try:
            state, data = self.countable_elem.count(integ_time)
        except Exception:
            self.dump_information(self._getElements())
            raise
        finally:
            self.finish()
        if state != DevState.ON:
            self.dump_information(self._getElements())
            raise ValueError("Acquisition ended with {}".format(
                state.name.capitalize()))
        self.setData(Record(data))
        self.printAllValues()

    def finish(self):
        self._clean()

    def _clean(self):
        for channel in self.channels:
            valueObj = channel.getValueObj_()
            valueObj.unsubscribeEvent(self.counterChanged, channel)

    def counterChanged(self, channel, value):
        idx = self.names.index([channel.getName()])
        self.values[idx] = [value]
        if self.print_value and not self.isStopped():
            self.printAllValues()

    def printAllValues(self):
        ch_width = 10
        table = Table(self.values, elem_fmt=['%*.4f'], col_head_str=self.names,
                      col_head_width=ch_width)
        self.outputBlock(table.genOutput())
        self.flushOutput()


@macro([['message', [['message_item', Type.String, None,
                      'message item to be reported']], None,
         'message to be reported']])
def report(self, message):
    """Logs a new record into the message report system (if active)"""
    self.report(' '.join(message))


class logmacro(Macro):
    """ Turn on/off logging of the spock output.

    .. note::
        The logmacro class has been included in Sardana
        on a provisional basis. Backwards incompatible changes
        (up to and including its removal) may occur if
        deemed necessary by the core developers
    """

    param_def = [
        ['offon', Type.Boolean, None, 'Unset/Set logging'],
        ['mode', Type.Integer, -1, 'Mode: 0 append, 1 new file'],
    ]

    def run(self, offon, mode):
        if offon:
            if mode == 1:
                self.setEnv('LogMacroMode', True)
            elif mode == 0:
                self.setEnv('LogMacroMode', False)
            self.setEnv('LogMacro', True)
        else:
            self.setEnv('LogMacro', False)


class repeat(Hookable, Macro):
    """This macro executes as many repetitions of a set of macros as
    specified by nr parameter. The macros to be repeated can be
    given as parameters or as body hooks.
    If both are given first will be executed the ones given as
    parameters and then the ones given as body hooks.
    If nr has negative value, repetitions will be executed until you
    stop repeat macro.

    .. note::
        The repeat macro has been included in Sardana
        on a provisional basis. Backwards incompatible changes
        (up to and including removal of the macro) may occur if
        deemed necessary by the core developers."""

    hints = {'allowsHooks': ('body',)}

    param_def = [
        ['nr', Type.Integer, None, 'Nr of iterations'],
        ['macro_name_params', [
                ['token', Type.String,
                 None, 'Macro name and parameters (if any)'],
                {'min': 0}
            ],
            None, "List with macro name and parameters (if any)"]
    ]

    def prepare(self, nr, macro_name_params):
        self.bodyHooks = self.getHooks("body")
        self.macro_name_params = macro_name_params

    def __loop(self):
        self.checkPoint()
        if len(self.macro_name_params) > 0:
            for macro_cmd in self.macro_name_params:
                self.execMacro(macro_cmd)
        for bodyHook in self.bodyHooks:
            bodyHook()

    def run(self, nr, macro_name_params):
        if nr < 0:
            while True:
                self.__loop()
        else:
            for i in range(nr):
                self.__loop()
                progress = ((i + 1) / nr) * 100
                yield progress


class sleep(Macro):
    """
    This macro waits for a time amount specified by dtime parameter (in seconds).
    In contrary to Python ``time.sleep(dtime)`` this macro execution can
    by interrupted (stopped or aborted).
    """

    param_def = [
       ['dtime', Type.Float, 0, 'Sleep time in seconds']
    ]

    def run(self, dtime):
        while dtime > 0:
            self.checkPoint()

            if dtime > 1:
                time.sleep(1)
                dtime = dtime - 1
            else:
                time.sleep(dtime)
                dtime = 0


class newfile(Hookable, Macro):
    """ Sets the ScanDir and ScanFile as well as ScanID in the environment.

    If ScanFilePath is only a file name, the ScanDir must be set externally
    via `senv ScanDir <PathToScanFile>` or using the %expconf. Otherwise,
    the path in ScanFilePath must be absolute and existing on the
    MacroServer host.

    The ScanID should be set to the value before the upcoming scan number.
    Default value is 0.
    """

    hints = {'allowsHooks': ('post-newfile', )}

    param_def = [
        ['ScanFilePath_list',
         [['ScanFilePath', Type.String, None, '(ScanDir/)ScanFile']],
         None, 'List of (ScanDir/)ScanFile'],
        ['ScanID', Type.Integer, 0, 'Scan ID'],
    ]

    def run(self, ScanFilePath_list, ScanID):
        path_list = []
        fileName_list = []
        # traverse the repeat parameters for the ScanFilePath_list
        for i, ScanFilePath in enumerate(ScanFilePath_list):
            path = os.path.dirname(ScanFilePath)
            fileName = os.path.basename(ScanFilePath)
            if not path and i == 0:
                # first entry and no given ScanDir: check if ScanDir exists
                try:
                    ScanDir = self.getEnv('ScanDir')
                except UnknownEnv:
                    ScanDir = ''
                if not (isinstance(ScanDir, str) and len(ScanDir) > 0):
                    msg = ('Data is not stored until ScanDir is correctly '
                           'set! Provide ScanDir with newfile macro: '
                           '`newfile [<ScanDir>/<ScanFile>] <ScanID>` '
                           'or `senv ScanDir <ScanDir>` or with %expconf')
                    self.error(msg)
                    return
                else:
                    path = ScanDir
            elif not path and i > 0:
                # not first entry and no given path: use path of last iteration
                path = path_list[i-1]
            elif not os.path.isabs(path):
                # relative path
                self.error('Only absolute path are allowed!')
                return
            else:
                # absolute path
                path = os.path.normpath(path)

            if i > 0 and (path not in path_list):
                # check if paths are equal
                self.error('Multiple paths to the data files are not allowed')
                return
            elif not os.path.exists(path) and not re.match(r'.*{.*}.*', path):
                # check if folder exists or is dynamic e.g. {ScanID}
                self.error('Path %s does not exists on the host of the '
                           'MacroServer and has to be created in '
                           'advance.' % path)
                return
            else:
                self.debug('Path %s appended.' % path)
                path_list.append(path)

            if not fileName:
                self.error('No filename is given.')
                return
            elif fileName in fileName_list:
                self.error('Duplicate filename %s is not allowed.' % fileName)
                return
            else:
                self.debug('Filename is %s.' % fileName)
                fileName_list.append(fileName)

        if ScanID < 1:
            ScanID = 0

        self.setEnv('ScanFile', fileName_list)
        self.setEnv('ScanDir', path_list[0])
        self.setEnv('ScanID', ScanID)

        self.output('ScanDir is\t: %s', path_list[0])
        for i, ScanFile in enumerate(fileName_list):
            if i == 0:
                self.output('ScanFile set to\t: %s', ScanFile)
            else:
                self.output('\t\t  %s', ScanFile)
        self.output('Next scan is\t: #%d', ScanID+1)

        for postNewfileHook in self.getHooks('post-newfile'):
            postNewfileHook()


class plotselect(Macro):
    """select channels for plotting in the active measurement group"""

    env = ("ActiveMntGrp", )
    param_def = [
          ['channel',
           [['channel', Type.ExpChannel, 'None', ""], {'min': 0}],
           None,
           "List of channels to plot"],
     ]

    def run(self, channel):
        active_meas_grp = self.getEnv('ActiveMntGrp')
        meas_grp = self.getMeasurementGroup(active_meas_grp)
        self.output("Active measurement group: {}".format(meas_grp.name))

        plot_channels_ok = []
        enabled_channels = meas_grp.getEnabled()
        # check channels first
        for chan in channel:
            enabled = enabled_channels.get(chan.name)
            if enabled is None:
                self.warning("{} not in {}".format(chan.name, meas_grp.name))
            else:
                plot_channels_ok.append(chan.name)
                if not enabled:
                    self.warning("{} is disabled".format(chan.name))
                else:
                    self.output("{} selected for plotting".format(chan.name))
        # set the plot type and plot axis in the meas_group
        meas_grp.setPlotType("No", apply=False)
        meas_grp.setPlotType("Spectrum", *plot_channels_ok, apply=False)
        meas_grp.setPlotAxes(["<mov>"], *plot_channels_ok)


class _movetostatspos(Macro):
    """This macro does the logic for pic, cen and com"""

    env = ("ScanStats", )

    param_def = [
        ['channel', Type.ExpChannel, Optional, 'name of channel'],
        ['motor', Type.Moveable, Optional, 'name of motor'],
        ['caller', Type.String, None, 'caller (pic, cen or com)'],
        ['offset', Type.Float, 0.0, 'move offset']
    ]

    def run(self, channel, motor, caller, offset):
        stats = self.getEnv('ScanStats', door_name=self.getDoorName())

        if motor is None:
            # use first motor in stats
            motor_name = next(iter(stats['Motors']))
        else:
            if motor.name in stats['Motors']:
                motor_name = motor.name
            else:
                raise Exception("motor {} not present in ScanStats".format(
                                motor.name))

        if channel is None:
            # use first channel in stats
            channel = next(iter(stats['Stats'][motor_name]))
        else:
            if channel.name in stats['Stats'][motor_name]:
                channel = channel.name
            else:
                raise Exception("channel {} not present in ScanStats".format(
                                channel.name))

        if caller == 'pic':
            stats_value = 'maxpos'
            stats_str = 'PIC'
        elif caller == 'cen':
            stats_value = 'cen'
            stats_str = 'CEN'
        elif caller == 'com':
            stats_value = 'com'
            stats_str = 'COM'              
        else:
            raise Exception("caller {} is unknown".format(caller))

        motor = self.getMotion([motor_name])
        current_pos = motor.readPosition()[0]
        pos = stats['Stats'][motor_name][channel][stats_value] + offset

        self.info("move motor {:s} from current position\nat {:.4f}\n"
                  "to {:s} of counter {:s}\nat {:.4f}".format(motor_name,
                                                              current_pos,
                                                              stats_str,
                                                              channel,
                                                              pos))
        motor.move(pos)


class pic(Macro):
    """This macro moves a motor of the last scan to its PEAK position for a
    given channel. If no channel is given, it selects the first channel from
    the ScanStats env variable. If no motor is given, it selects the first/only
    motor from the ScanStats env variable.
    """

    param_def = [
        ['channel', Type.ExpChannel, Optional, 'name of channel'],
        ['motor', Type.Moveable, Optional, 'name of motor'],
        ['offset', Type.Float, 0.0, 'move offset']
    ]

    def run(self, channel, motor, offset):
        self.execMacro('_movetostatspos', channel, motor, 'pic', offset)


class cen(Macro):
    """This macro moves a motor of the last scan to its CEN position for a
    given channel. If no channel is given, it selects the first channel from
    the ScanStats env variable. If no motor is given, it selects the first/only
    motor from the ScanStats env variable.
    """

    param_def = [
        ['channel', Type.ExpChannel, Optional, 'name of channel'],
        ['motor', Type.Moveable, Optional, 'name of motor'],
        ['offset', Type.Float, 0.0, 'move offset']
    ]

    def run(self, channel, motor, offset):
        self.execMacro('_movetostatspos', channel, motor, 'cen', offset)


class com(Macro):
    """This macro moves a motor of the last scan to its COM position for a
    given channel. If no channel is given, it selects the first channel from
    the ScanStats env variable. If no motor is given, it selects the first/only
    motor from the ScanStats env variable.
    """

    param_def = [
        ['channel', Type.ExpChannel, Optional, 'name of channel'],
        ['motor', Type.Moveable, Optional, 'name of motor'],
        ['offset', Type.Float, 0.0, 'move offset']
    ]

    def run(self, channel, motor, offset):
        self.execMacro('_movetostatspos', channel, motor, 'com', offset)


class where(Macro):
    """This macro shows the current position of the last scanned motor.
    If no motor is given, it selects the first/only motor from the ScanStats
    env variable.
    """

    env = ("ScanStats", )

    param_def = [
        ['motor', Type.Moveable, Optional, 'name of motor']
    ]    

    def run(self, motor):
        stats = self.getEnv('ScanStats', door_name=self.getDoorName())

        if motor is None:
            # use first motor in stats
            motor_name = next(iter(stats['Motors']))
        else:
            if motor.name in stats['Motors']:
                motor_name = motor.name
            else:
                raise Exception("motor {} not present in ScanStats".format(
                                motor.name))        
        motor = self.getMoveable(motor_name)
        self.info("motor {:s} is\nat {:.4f}".format(motor_name,
                                                    motor.getPosition()))
