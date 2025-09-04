# -*- coding: utf-8 -*-

##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
##
## Copyright 2019 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

import re
import math
import html

from taurus.external.qt import Qt
from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.display.tauruslabel import TaurusLabelController


class ResponsiveTaurusLabelController(TaurusLabelController):
    def __init__(self, label):
        TaurusLabelController.__init__(self, label)
        self._maxCharsText = False

    def _updateForeground(self, label):
        fgRole, value = label.fgRole, ""

        # handle special cases (that are not covered with fragment)
        if fgRole.lower() == "state":
            try:
                value = self.state().name
            except AttributeError:
                pass  # protect against calls with state not instantiated
        elif fgRole.lower() in ("", "none"):
            pass
        else:
            value = label.getDisplayValue(fragmentName=fgRole)
        self._text = text = label.prefixText + value + label.suffixText

        # trims the text to the specified max characters.
        self._maxCharsText, text = self._calculateMaxChars(label, text)

        # Checks that the display fits in the widget and sets it to "..." if
        # it does not fit the widget
        self._trimmedText, text = self._shouldTrim(label, text)
        
        if self._maxCharsText or self._trimmedText:
            text = html.escape(text)
            text = text.replace('\n', '<br/>')
            text = "<a href='...'>" + text + "</a>"
        label.setText_(text)

    def _shouldTrim(self, label, text):
        if not label.autoTrim:
            return False
        #text = re.sub(self._trimPattern, "", text)
        text = text.replace('\n\n', '\n')
        size = label.size().width()
        text_split = text.split("\n")
        font_metrics = Qt.QFontMetrics(label.font())
        
        after_wrap_lines = 0
        trimmed_text = ""
        for line in text_split:
            line_size = font_metrics.width(line)
            actual_lines = math.ceil((line_size+8)/size)
            after_wrap_lines += actual_lines

            if after_wrap_lines > label.maxLines:
                lines_still_fit = label.maxLines-(after_wrap_lines-actual_lines)
                trim_chars =int(len(line)/actual_lines*lines_still_fit)
                trimmed_text+=line[0:trim_chars]
                label.setMinimumHeight(16*label.maxLines)

                return True, f'{trimmed_text[0:-24]} ...'
            
            trimmed_text+=line+"\n"
        else:
            label.setMinimumHeight(16*after_wrap_lines)
            return False, text

    def _calculateMaxChars(self, label, text):
        n_maxChars = label.maxChars
        if n_maxChars < 0:
            return False, text

        n_textChars = len(text)
        if n_textChars < n_maxChars:
            return False, text
        return True, text[:n_maxChars-3]+"..."


class ResponsiveTaurusLabel(TaurusLabel):
    DefaultMaxChars = -1
    DefaultMaxLines = 5

    def __init__(self, *args):
        self._maxChars = self.DefaultMaxChars
        self._maxLines = self.DefaultMaxLines
        TaurusLabel.__init__(self, *args)
        self.setMinimumHeight(16*self._maxLines)

    def _calculate_controller_class(self):
        return ResponsiveTaurusLabelController

    def setMaxChars(self, n=-1):
        """Set the maximum number of characters that should appear in the text of
         TaurusLabel.

         :param n:
         :type n: int
         """
        self._maxChars = n
        self.controllerUpdate()

    def getMaxChars(self):
        """
        Return the number of characters to display on the TaurusLabel text

        :return:
        :rtype: int
        """
        return self._maxChars

    def resetMaxChars(self):
        """Reset maximum characters to its default value"""
        self.setMaxChars(self.DefaultMaxChars)

    def setMaxLines(self, n):
        """Set the maximum number of lines that should appear in the text of
         TaurusLabel.

         :param n:
         :type n: int
         """
        self._maxLines = n
        self.setMaximumHeight(16*self._maxLines)
        self.controllerUpdate()

    def getMaxLines(self):
        """
        Return the number of lines to display on the TaurusLabel text

        :return:
        :rtype: int
        """
        return self._maxLines

    def resetMaxLines(self):
        """Reset maximum lines to its default value"""
        self.setMaxLines(self.DefaultMaxLines)

    #: Specified the number of maximum characters the text will have, regardless
    #: of the available space
    #:
    #: **Access functions:**
    #:
    #:      * :meth:`TaurusLabel.getMaxChars`
    #:      * :meth:`TaurusLabel.setMaxChars`
    #:      * :meth:`TaurusLabel.resetMaxChars`
    maxChars = Qt.pyqtProperty(
        "int", getMaxChars, setMaxChars, resetMaxChars,
        doc="Maximum characters in label"
    )

    #: Specified the number of maximum lines the text will have
    #:
    #: **Access functions:**
    #:
    #:      * :meth:`TaurusLabel.getMaxLines`
    #:      * :meth:`TaurusLabel.setMaxLines`
    #:      * :meth:`TaurusLabel.resetMaxLines`
    maxLines = Qt.pyqtProperty(
        "int", getMaxLines, setMaxLines, resetMaxLines,
        doc="Maximum lines in label"
    )
