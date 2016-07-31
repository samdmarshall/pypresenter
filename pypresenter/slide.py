# Copyright (c) 2016, Samantha Marshall (http://pewpewthespells.com)
# All rights reserved.
#
# https://github.com/samdmarshall/pypresenter
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# 3. Neither the name of Samantha Marshall nor the names of its contributors may
# be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

import blessings

def NumLinesInText(columns, text):
    number_of_newlines = text.count('\n')
    number_of_wrapped_lines = (len(text) / columns) + 1
    return number_of_newlines + number_of_wrapped_lines

def NumTextLines(window, text):
    rows = window.height
    cols = window.width
    text_lines = NumLinesInText(cols, text)
    text_lines = max(text_lines - rows, text_lines)
    return text_lines

def FormatText(text, rows, cols, add_hyphen):
    formatted_lines = list()
    for unformatted_line in text.split('\n'):
        start_index = 0
        end_index = 0
        formatted_text = ''
        is_iterating = True
        while is_iterating:
            remaining_length = len(unformatted_line[start_index:])
            if remaining_length < cols:
                is_iterating = False
            length = min(remaining_length, cols-1)
            end_index = length + start_index
            formatted_text += unformatted_line[start_index:end_index]
            start_index += length
            if end_index < len(unformatted_line) and add_hyphen:
                formatted_text += '-'
        formatted_lines.append(formatted_text)
    return formatted_lines

def center_x(dimension, content):
    return ((int(dimension) / 2) - (content / 2))

def center_y(dimension, content, offset):
    return ((int(dimension) / 2) - ((content / 2) - offset))

def left_x(dimension, content):
    return 0

def left_y(dimension, content, offset):
    return 0 + offset

def DisplayText(window, line, newline_count, line_index, func_x, func_y):
    rows = window.height
    cols = window.width
    text_length = min(len(line), cols)
    x = func_x(cols, text_length)
    y = func_y(rows, newline_count, line_index)
    with window.location(x=x,y=y):
        print(line)

def LeftText(window, text, scroll_offset):
    rows = window.height
    cols = window.width
    text_lines = FormatText(text, rows, cols, False)
    newlines = len(text_lines)
    line_index = 0
    for line in text_lines[scroll_offset:]:
        if line_index < rows -1:
            DisplayText(window, line, newlines, line_index, left_x, left_y)
        line_index += 1

def CenterText(window, text, scroll_offset):
    rows = window.height
    cols = window.width
    text_lines = FormatText(text, rows, cols, True)
    newlines = len(text_lines)
    line_index = 0
    for line in text_lines[scroll_offset:]:
        if line_index < newlines:
            DisplayText(window, line, newlines, line_index, center_x, center_y)
        line_index += 1

kDrawingMethods = {
    'center': CenterText,
    'left':   LeftText,
}

class slide(object):
    def __init__(self, draw_method):
        self.scroll_position = 0
        self.drawMethod = kDrawingMethods[draw_method]
    def draw(self, window):
        raise Exception("Subclass this type to implement a slide")
    def content(self):
        raise Exception("Subclass this type to implement a slide")
    @property
    def scroll_position(self):
        return self._scroll_position
    @scroll_position.setter
    def scroll_position(self, scroll_position):
        self._scroll_position = scroll_position

# ---

    def displayText(self, window, text):
        print(window.clear())
        self.drawMethod(window, text, self.scroll_position)
        print(window.refresh())

    def numLinesInText(self, columns, text):
        return NumLinesInText(columns, text)

    def numTextLines(self, window, text):
        return NumTextLines(window, text)

    def scrollUp(self, window):
        text = self.content(window)
        lines = len(text.split('\n'))
        if lines > window.height:
            if self.scroll_position > 0:
                self.scroll_position = self.scroll_position - 1
                self.displayText(window, text)
            else:
                window.flash()

    def scrollDown(self, window):
        text = self.content(window)
        lines = len(text.split('\n'))
        if lines - self.scroll_position > window.height:
            if self.scroll_position + 1 < lines:
                self.scroll_position = self.scroll_position + 1
                self.displayText(window, text)
            else:
                window.flash()
