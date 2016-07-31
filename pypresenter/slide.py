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

def FormatText(text, rows, cols):
    formatted_text = ''
    start_index = 0
    end_index = 0
    is_iterating = True
    while is_iterating:
        remaining_length = len(text[start_index:])
        if remaining_length < cols:
            is_iterating = False
        length = min(remaining_length, cols - 1) 
        end_index = length + start_index
        formatted_text += text[start_index:end_index]
        if end_index < len(text):
            formatted_text += '-'
        start_index += length
    return formatted_text

def CenterText(window, text):
    rows = window.height
    cols = window.width
    text = FormatText(text, rows, cols)
    # fix this :(
    newlines = text.count('\n')
    text_length = min(len(text), cols)
    x = ((int(cols) / 2) - (text_length / 2))
    y = ((int(rows) / 2) - (newlines / 2))
    with window.location(x=x,y=y):
        print(text)

class slide(object):
    def draw(self, window):
        raise Exception("Subclass this type to implement a slide")
    def content(self):
        raise Exception("Subclass this type to implement a slide")

# ---

    def numLinesInText(self, columns, text):
        return NumLinesInText(columns, text)

    def numTextLines(self, window, text):
        return NumTextLines(window, text)

    def centerText(self, window, text):
        CenterText(window, text)
