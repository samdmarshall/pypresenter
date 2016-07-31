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
import imp
import sys
import tty
import glob
import curses
import termios
import blessings
from .Switch    import Switch
from .          import slide

class _Getch:
    def __call__(self):
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(3)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

class console(object):

    def __init__(self, slides_path):
        self.slides_directory = slides_path
        self.term = None
        self.input = _Getch()
        self.slides = dict()
        self.slide_index = 1
        self._cached_slide = None
        self._cached_slide_name = None
        if os.path.exists(self.slides_directory):
            self.setup()
            self.load()
            self.run()
        else:
            print('Unable to find a slide deck at "%s" :(' % self.slides_directory)

    def setup(self):
        self.term = blessings.Terminal()
        self.term.enter_fullscreen()
        self.term.stream.write(self.term.hide_cursor)

    def load(self):
        working_dir = os.getcwd()
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
        os.chdir(working_dir)

    def flash(self):
        print('\a')
        print(self.term.move(0,0))

    def next(self):
        new_slide = False
        if self.slide_index + 1 <= len(self.slides):
            self.slide_index += 1
            new_slide = True
        else:
            self.flash()
        return new_slide

    def back(self):
        new_slide = False
        if self.slide_index - 1 >= 1:
            self.slide_index -= 1
            new_slide = True
        else:
            self.flash()
        return new_slide

    def scrollUp(self):
        self.currentSlide().scrollUp(self.term)

    def scrollDown(self):
        self.currentSlide().scrollDown(self.term)

    def currentSlide(self):
        slide_name = 'slide'+str(self.slide_index)
        if self._cached_slide_name != slide_name:
            self._cached_slide_name = slide_name
            self._cached_slide = getattr(self.slides[slide_name], slide_name)()
        return self._cached_slide

    def separator(self):
        separator_bar = '=' * (self.term.width - 2)
        separator_string = '@'+separator_bar+'@'
        return separator_string
        
    def run(self):
        new_slide = True
        should_run = True
        while should_run:
            if new_slide:
                new_slide = False
                print(self.term.clear())
                print(self.separator())
                print(self.term.clear())
                current_slide = self.currentSlide()
                self.term.move(0,0)
                current_slide.draw(self.term)
            key = self.input()
            for case in Switch(key):
                if case('\x1b[D'):
                    new_slide = self.back()
                    break
                if case('\x1b[C'):
                    new_slide = self.next()
                    break
                if case('\x1b[A'):
                    self.scrollUp()
                    break
                if case('\x1b[B'):
                    self.scrollDown()
                    break
                if case('qqq'): # the letter Q
                    should_run = False
                    break
                if case():
                    break
        self.exit()

    def exit(self):
        print(self.term.clear())
        self.term.stream.write(self.term.normal_cursor)
        self.term.exit_fullscreen()
        cruft = os.path.join(self.slides_directory, '*.pyc')
        [os.remove(pyc_file) for pyc_file in glob.glob(cruft)]
