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

"""This is the main macro server module"""

__all__ = ["AttributeLogHandler", "AttributeBufferedLogHandler"]

__docformat__ = 'restructuredtext'

import logging
import weakref
import operator

from taurus.core.util.containers import LIFO
from taurus.core.util.codecs import CodecFactory
import collections
from sardana import sardanacustomsettings

class AttributeLogHandler(logging.Handler):

    def __init__(self, dev, attr_name, level=logging.NOTSET, max_buff_size=0):
        logging.Handler.__init__(self, level)
        self._attr_name = attr_name
        self._level = level
        self._max_buff_size = max_buff_size
        self._dev = weakref.ref(dev)
        self._attr = dev.get_device_attr().get_attr_by_name(attr_name)
        self._buff = LIFO(max_buff_size)

    def emit(self, record):
        output = self.getRecordMessage(record)
        self.appendBuffer(output)
        self.sendText(output)

    def getRecordMessage(self, record):
        message = self.format(record).split('\n')
        # Tango DevString attributes are transferred in Latin1 encoding.
        # To allow characters/glyphs which are not covered by Latin1, we
        # encode the message first into `bytes`, then decode it using
        # the Latin1 character encoding. After transfer, the client does
        # the same but backwards: encodes into Latin1, then decodes it
        # with the desired codec (which must be the same as set in the
        # server), using the LOG_MESSAGE_CODEC config option.
        codecname = getattr(
            sardanacustomsettings, "LOG_MESSAGE_CODEC", None
        )
        if codecname is not None:
            cf = CodecFactory()
            codec = cf.getCodec(codecname)
            if isinstance(message, str):
                # a single line
                message = [message]
            message_encoded = [
                codec.encode(('', line))[1].decode('latin1')
                for line in message
            ]
            return message_encoded
        else:
            return message

    def sendText(self, output):
        dev = self._dev()
        attr = self._attr
        if attr is None or dev is None:
            return
        dev.set_attribute(attr, output)

    def read(self, attr):
        """Read from the buffer and assign to the attribute value"""
        attr.set_value(self._buff.getCopy())

    def clearBuffer(self):
        self._buff.clear()

    def appendBuffer(self, d):
        if isinstance(d, collections.abc.Sequence):
            if isinstance(d, str):
                self._buff.append(d)
            else:
                self._buff.extend(d)
        else:
            self._buff.append(str(d))

    def sync(self):
        pass

    def finish(self):
        pass

AttributeBufferedLogHandler = AttributeLogHandler
