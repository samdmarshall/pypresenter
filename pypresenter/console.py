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

from __future__ import print_function
import os
import sys
import curses
import imp
from .Switch    import Switch

def linesInText(columns, text):
    number_of_newlines = text.count('\n')
    number_of_wrapped_lines = (len(text) / columns) + 1
    return number_of_newlines + number_of_wrapped_lines

class console(object):

    def __init__(self, slides_path):
        self.slides_directory = slides_path
        self.window = None
        self.text_pad = None
        self.slides = dict()
        self.slide_index = 1
        self.scroll_position = 1
        if os.path.exists(self.slides_directory):
            self.setup()
            self.load()
            self.run()
        else:
            print('Unable to find a slide deck at "%s" :(' % self.slides_directory)

    def setup(self):
        self.window = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.window.keypad(1)
        self.window.scrollok(True)

    def load(self):
        os.chdir(self.slides_directory)
        slide_files = list()
        for fileref in os.listdir(self.slides_directory):
            name, extension = os.path.splitext(fileref)
            if name != '__init__' and extension == '.py':
                slide_files.append(fileref)
        for slide in slide_files:
            slide_path = os.path.join(self.slides_directory, slide)
            name, _ = os.path.splitext(slide)
            self.slides[name] = imp.load_source(name, slide_path)

    def next(self):
        new_slide = False
        if self.slide_index + 1 <= len(self.slides):
            self.slide_index += 1
            new_slide = True
        else:
            curses.flash()
        return new_slide

    def back(self):
        new_slide = False
        if self.slide_index - 1 >= 1:
            self.slide_index -= 1
            new_slide = True
        else:
            curses.flash()
        return new_slide

    def scrollup(self):
        if self.scroll_position > 1:
            self.scroll_position -= 1
            self.window.scroll(-1)
        else:
            curses.flash()

    def scrolldown(self, lines):
        if self.scroll_position + 1 < lines:
            self.scroll_position += 1
            self.window.scroll(1)
        else:
            curses.flash()

    def currentSlide(self):
        slide_name = 'slide'+str(self.slide_index)
        return getattr(self.slides[slide_name], slide_name)()

    def run(self):
        new_slide = True
        should_run = True
        y = 0
        x = 0
        text_lines = 0
        while should_run:
            if new_slide:
                self.window.erase()
                current_slide = self.currentSlide()
                y, cols = self.window.getmaxyx()
                text_lines = linesInText(cols, current_slide.content())
                text_lines = max(text_lines - y, text_lines)
                lines = max(y, text_lines)
                current_slide.draw(self.window)
                new_slide = False
            self.window.refresh()
            key = self.window.getch()
            for case in Switch(key):
                if case(curses.KEY_LEFT):
                    new_slide = self.back()
                    break
                if case(curses.KEY_RIGHT):
                    new_slide = self.next()
                    break
                if case(curses.KEY_UP):
                    self.scrollup()
                    break
                if case(curses.KEY_DOWN):
                    self.scrolldown(text_lines)
                    break
                if case(113): # the letter Q
                    should_run = False
                    break
                if case():
                    break
        self.exit()

    def exit(self):
        curses.nocbreak()
        curses.echo()
        self.window.keypad(0)
        curses.endwin()
