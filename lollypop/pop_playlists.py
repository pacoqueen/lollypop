# Copyright (c) 2014-2018 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
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

from lollypop.loader import Loader
from lollypop.define import App
from lollypop.view_playlists import PlaylistsView


class PlaylistsPopover(Gtk.Popover):
    """
        Popover showing current albums
        @Warning: destroy it self on close
    """

    def __init__(self):
        """
            Init Popover
        """
        Gtk.Popover.__init__(self)
        self.set_position(Gtk.PositionType.BOTTOM)
        self.connect("map", self.__on_map)
        self.connect("unmap", self.__on_unmap)
        self._widget = PlaylistsView(App().player.get_playlist_ids(),
                                     False)
        self._widget.show()
        self.add(self._widget)

    def populate(self):
        """
            Populate view
        """
        def load():
            return [track.id for track in App().player.get_playlist_tracks()]
        loader = Loader(target=load, view=self._widget)
        loader.start()

#######################
# PRIVATE             #
#######################
    def __on_map(self, widget):
        """
            Connect signals, populate and resize
            @param widget as Gtk.Widget
        """
        self._stop = False
        self.populate()
        window_size = App().window.get_size()
        height = window_size[1]
        width = min(500, window_size[0])
        self.set_size_request(width, height * 0.7)

    def __on_unmap(self, widget):
        """
            Disconnect signals, clear view
            @param widget as Gtk.Widget
        """
        self._stop = True
        self.destroy()
