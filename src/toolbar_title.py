# Copyright (c) 2014-2017 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
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

from gi.repository import Gtk

from lollypop.controllers import ProgressController


class ToolbarTitle(Gtk.Bin, ProgressController):
    """
        Title toolbar
    """

    def __init__(self):
        """
            Init toolbar
        """
        Gtk.Bin.__init__(self)
        ProgressController.__init__(self)
        builder = Gtk.Builder()
        builder.add_from_resource("/org/gnome/Lollypop/ToolbarTitle.ui")
        builder.connect_signals(self)

        self.add(builder.get_object("title"))

        self._progress = builder.get_object("progress_scale")
        self._progress.set_sensitive(False)
        self._progress.set_hexpand(True)

        self._timelabel = builder.get_object("playback")
        self._total_time_label = builder.get_object("duration")

    def set_width(self, width):
        """
            Set Gtk.Scale progress width
            @param width as int
        """
        self.set_property("width_request", width)

    def show_hide_volume_control(self):
        """
            Show/Hide volume control
        """
        self._progress.clear_marks()
        self._show_volume_control = not self._show_volume_control
        self._update_state()

    def add_mark(self, position):
        """
            Add a mark at position
            @param position as float
        """
        if position > 0:
            self._progress.add_mark(position, Gtk.PositionType.BOTTOM, None)
#######################
# PRIVATE             #
#######################
