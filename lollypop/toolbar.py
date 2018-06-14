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

from gi.repository import Gtk, Gst

from lollypop.define import App, WindowSize, LOLLYPOP_DATA_PATH
from lollypop.toolbar_playback import ToolbarPlayback
from lollypop.toolbar_info import ToolbarInfo
from lollypop.toolbar_title import ToolbarTitle
from lollypop.toolbar_end import ToolbarEnd
from lollypop.logger import Logger


class Toolbar(Gtk.HeaderBar):
    """
        Lollypop toolbar
    """

    def __init__(self):
        """
            Init toolbar
        """
        Gtk.HeaderBar.__init__(self)
        self.__width = WindowSize.SMALL
        self.set_title("Lollypop")
        self.__toolbar_playback = ToolbarPlayback()
        self.__toolbar_playback.show()
        self.__toolbar_info = ToolbarInfo()
        self.__toolbar_info.show()
        self.__toolbar_title = ToolbarTitle()
        self.__toolbar_title.show()
        self.__toolbar_end = ToolbarEnd()
        self.__toolbar_end.show()
        self.pack_start(self.__toolbar_playback)
        self.pack_start(self.__toolbar_info)
        self.set_custom_title(self.__toolbar_title)
        self.pack_end(self.__toolbar_end)

        App().player.connect("status-changed", self.__on_status_changed)
        App().player.connect("current-changed", self.__on_current_changed)
        App().player.connect("next-changed", self.__on_next_changed)
        App().player.connect("prev-changed", self.__on_prev_changed)

    def do_get_preferred_height(self):
        """
            Here, we calculate height based on:
            - playback toolbar if bigger
            - infos toolbar to adapt to font size then
        """
        style = self.get_style_context()
        padding = style.get_padding(style.get_state())
        info_height = self.__toolbar_info.get_preferred_height()
        if info_height[0] + padding.top + padding.bottom > 47:
            height = info_height[0] + padding.top + padding.bottom
        else:
            height = Gtk.HeaderBar.do_get_preferred_height(self)[0]
        return (height, height)

    def do_get_preferred_width(self):
        """
            Allow snapping for screen with width > 1400
            @return (int, int)
        """
        return (WindowSize.SMALL, self.__width)

    def set_content_width(self, window_width):
        """
            Calculate infos/title width
            @param window width as int
        """
        width = self.__toolbar_playback.get_preferred_width()[1]
        width += self.__toolbar_end.get_preferred_width()[1]
        window = self.get_window()
        if window is not None:
            available = window.get_width() - width
            if available > 0:
                if window_width >= WindowSize.MEDIUM:
                    title = available / 2
                else:
                    title = available
                self.__toolbar_title.set_width(title)
                self.__toolbar_info.set_width((available - title) / 2)
            self.__width = window.get_width()

    def update_position(self, value=None):
        """
            Update progress bar position
            @param value as int
        """
        if not self.__toolbar_title._show_volume_control:
            self.__toolbar_title._update_position(value)

    def setup_menu(self, menu):
        """
            Add an application menu to menu button
            @parma: menu as Gio.Menu
        """
        self.__toolbar_end.setup_menu(menu)

    def set_mark(self):
        """
            Mark toolbar with previously saved position
        """
        try:
            if App().settings.get_value("save-state"):
                from pickle import load
                position = load(open(LOLLYPOP_DATA_PATH + "/position.bin",
                                     "rb"))
                self.__toolbar_title.add_mark(position / Gst.SECOND)
        except Exception as e:
            Logger.error("Toolbar::restore_state(): %s" % e)

    @property
    def end(self):
        """
            Return end toolbar
            @return ToolbarEnd
        """
        return self.__toolbar_end

    @property
    def info(self):
        """
            Return info toolbar
            @return ToolbarInfo
        """
        return self.__toolbar_info

    @property
    def title(self):
        """
            Return title toolbar
            @return ToolbarTitle
        """
        return self.__toolbar_title

    @property
    def playback(self):
        """
            Return playback toolbar
            @return ToolbarPlayback
        """
        return self.__toolbar_playback

#######################
# PRIVATE             #
#######################
    def __on_current_changed(self, player):
        """
            Update toolbar
            @param player as Player
        """
        Logger.debug("Toolbar::_on_current_changed()")
        self.__toolbar_playback.on_current_changed(player)
        self.__toolbar_info.on_current_changed(player)
        self.__toolbar_title.on_current_changed(player)

    def __on_prev_changed(self, player):
        """
            Update toolbar
            @param player as Player
        """
        self.__toolbar_playback.on_prev_changed(player)

    def __on_next_changed(self, player):
        """
            Update toolbar
            @param player as Player
        """
        self.__toolbar_playback.on_next_changed(player)
        self.__toolbar_end.on_next_changed(player)

    def __on_status_changed(self, player):
        """
            Update buttons and progress bar
            @param player as Player
        """
        self.__toolbar_playback.on_status_changed(player)
        self.__toolbar_title.on_status_changed(player)
        self.__toolbar_end.on_status_changed(player)
