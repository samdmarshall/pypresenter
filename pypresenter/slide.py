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

def FormatText(text, cols, add_hyphen):
    column_width = cols - 1
    formatted_lines = list()
    for unformatted_line in text.split('\n'):
        line_length = len(unformatted_line)
        if line_length > column_width:
            split_line = list()
            start_index = 0
            end_index = cols
            while start_index < line_length:
                end_index = min(column_width, (line_length - start_index))
                end_index += start_index
                string_value = unformatted_line[start_index:end_index]
                if end_index < line_length and add_hyphen:
                    string_value += '-'
                split_line.append(string_value)
                start_index = end_index
            formatted_lines.extend(split_line)
        else:
            formatted_lines.append(unformatted_line)
    return formatted_lines

def center_x(dimension, content):
    return ((int(dimension) / 2) - (content / 2))

def center_y(dimension, content, offset):
    return ((int(dimension) / 2) - ((content / 2) - offset))

def left_x(dimension, content):
    return 0

def left_y(dimension, content, offset):
    return offset

def DisplayText(window, line, line_index, total_line_count, func_x, func_y, character_index, formatting):
    rows = window.height
    cols = window.width
    row_offset = min(total_line_count, rows)
    column_offset = min(len(line), cols)
    x = func_x(cols, len(line))
    y = func_y(rows, row_offset, line_index)
    with window.location(x=x,y=y):
        line_text = ''
        for letter in line:
            formatting_values = formatting.get(str(character_index), [])
            for format_value in formatting_values:
                line_text += getattr(window, format_value)
            line_text += letter
            character_index += 1
        print(line_text)
    return character_index

def LeftText(window, text, scroll_offset, formatting):
    rows = window.height
    cols = window.width
    text_lines = FormatText(text, cols, False)
    line_index = 0
    index_offset = scroll_offset
    character_index = sum([len(line) for line in text_lines[:line_index+index_offset]])
    while line_index < (rows - 2) and line_index+index_offset < len(text_lines):
        character_index = DisplayText(window, text_lines[line_index+index_offset], line_index, len(text_lines), left_x, left_y, character_index, formatting)
        line_index += 1

def CenterText(window, text, scroll_offset, formatting):
    rows = window.height
    cols = window.width
    text_lines = FormatText(text, cols, True)
    line_index = 0
    index_offset = scroll_offset
    character_index = sum([len(line) for line in text_lines[:line_index+index_offset]])
    while line_index < (rows - 2) and line_index < len(text_lines):
        character_index = DisplayText(window, text_lines[line_index+index_offset], line_index, len(text_lines), center_x, center_y, character_index, formatting)
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
        raise Exception("Subclass this type to implement a slide rendering")
    def content(self):
        raise Exception("Subclass this type to implement a slide content")
    def formatting(self):
        return {}
    @property
    def scroll_position(self):
        return self._scroll_position
    @scroll_position.setter
    def scroll_position(self, scroll_position):
        self._scroll_position = scroll_position

# ---

    def displayText(self, window, text):
        print(window.clear())
        self.drawMethod(window, text, self.scroll_position, self.formatting())
        print(window.refresh())

    def scrollUp(self, window):
        text = self.content(window)
        line_count = len(text.split('\n'))
        if line_count >= window.height - 2:
            if self.scroll_position > 0:
                self.scroll_position = self.scroll_position - 1
                self.displayText(window, text)

    def scrollDown(self, window):
        text = self.content(window)
        line_count = len(text.split('\n'))
        if line_count >= window.height - 2:
            self.scroll_position = self.scroll_position + 1
            self.displayText(window, text)
