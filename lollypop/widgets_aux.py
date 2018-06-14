#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Auxiliary widgets.

Lollypop is a music player developed by Cedric Bellegarde.
I'm just scratching my own itch. Pull request considered "too geek" and
not accepted, so... fork!
"""

# Copyright (c) 2017 Francisco José Rodríguez Bogado <bogado@qinn.es>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, GLib, GObject


class HoldButton(Gtk.Button):
    """
    Based on https://stackoverflow.com/a/37386156/7002245
    """
    __gsignals__ = {'held': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())}

    def __init__(self, label=None, stock=None, use_underline=True):
        Gtk.Button.__init__(self, label, stock, use_underline)
        self.connect('pressed', HoldButton.h_pressed)
        self.connect('clicked', HoldButton.h_clicked)
        self.timeout_id = None

    def h_clicked(self):
        """
        Callback for clicked. It checks if "pressed" is still alive. If so,
        cancel the "held" signal. Otherwise, signal is terminated.
        """
        if self.timeout_id:
            GObject.source_remove(self.timeout_id)
            self.timeout_id = None
        else:
            self.stop_emission('clicked')

    def h_pressed(self):
        """
        When button is pressed, create a timeout to measure 750ms. If that
        time is reached, then the timeout callback will emit a new "held"
        signal.
        """
        self.timeout_id = GLib.timeout_add(750, HoldButton.h_timeout, self)

    def h_timeout(self):
        """
        Callback triggered after 750 ms. Emit "held" signal if not cancelled
        in "clicked" signal before reaches that time.
        """
        self.timeout_id = None
        self.emit('held')
        return False

    # pylint: disable=arguments-differ
    @classmethod
    def new_from_icon_name(cls, icon_name, size):
        """
        Wrapper for Button.new_from_icon_name because this:
        > HoldButton.new_from_icon_name("go-jump-symbolic", Gtk.IconSize.MENU)

        TypeError: Button constructor cannot be used to create instances of a
                    subclass HoldButton
        """
        button = cls()
        image = Gtk.Image()
        image.set_from_icon_name(icon_name, size)
        button.set_image(image)
        return button
