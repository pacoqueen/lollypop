#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

# (ↄ)2018 Some changes made by Francisco José Rodríguez Bogado <bogado@qinn.es>

"""
Show lyrics for a single track in a view widget.
"""

from gettext import gettext as _
from gi.repository import Gio, GLib, Gtk
from lollypop.controllers import InfoController
from lollypop.define import App, Type, WindowSize
from lollypop.helper_task import TaskHelper
from lollypop.utils import escape, noaccents
from lollypop.view import View


# pylint: disable=too-many-instance-attributes
class LyricsView(View, InfoController):
    """
        Show lyrics for track
    """

    def __init__(self):
        """
            Init view
        """
        View.__init__(self)
        InfoController.__init__(self)
        self.__size_allocate_timeout_id = None
        self.__downloads_running = 0
        self.__lyrics_set = False
        self.__current_width = self.__current_height = 0
        self.__cancellable = Gio.Cancellable()
        builder = Gtk.Builder()
        builder.add_from_resource("/org/gnome/Lollypop/LyricsView.ui")
        builder.connect_signals(self)
        self._cover = builder.get_object("cover")
        self.__lyrics_label = builder.get_object("lyrics_label")
        self._buttonback = builder.get_object("button_back")
        self._buttonback.connect("clicked", self._close)
        self.add(builder.get_object("widget"))
        self.connect("size-allocate", self.__on_size_allocate)

    def populate(self):
        """
            Set lyrics
        """
        self.update_artwork(self.__current_width,
                            self.__current_height,
                            True)
        self.__lyrics_set = False
        self.__update_lyrics_style()
        self.__lyrics_label.set_text(_("Loading…"))
        self.__cancellable.cancel()
        self.__cancellable.reset()
        # First try to get lyrics from tags
        from lollypop.tagreader import TagReader
        lyrics = None
        reader = TagReader()
        try:
            info = reader.get_info(App().player.current_track.uri)
        # pylint: disable=broad-except,unused-variable
        except Exception as exceptinfo:
            info = None
        if info is not None:
            tags = info.get_tags()
            lyrics = reader.get_lyrics(tags)
        if lyrics:
            self.__lyrics_label.set_label(lyrics)
        elif App().settings.get_value("network-access"):
            self.__download_wikia_lyrics()
            self.__download_genius_lyrics()
        else:
            self.__lyrics_label.set_label(_("Network access disabled"))

##############
# PROTECTED  #
##############
    def _on_current_changed(self, player):
        """
            Update lyrics
            @param player as Player
        """
        self.populate()

    def _close(self, button=None):
        """Destroy lyrics widget, returning to previows view."""
        self.destroy()

############
# PRIVATE  #
############
    def __download_wikia_lyrics(self):
        """
            Downloas lyrics from wikia
        """
        self.__downloads_running += 1
        # Update lyrics
        task_helper = TaskHelper()
        if App().player.current_track.id == Type.RADIOS:
            split = App().player.current_track.name.split(" - ")
            if len(split) < 2:
                return
            artist = GLib.uri_escape_string(
                split[0],
                None,
                False)
            title = GLib.uri_escape_string(
                split[1],
                None,
                False)
        else:
            artist = GLib.uri_escape_string(
                App().player.current_track.artists[0],
                None,
                False)
            title = GLib.uri_escape_string(
                App().player.current_track.name,
                None,
                False)
        uri = "http://lyrics.wikia.com/wiki/%s:%s" % (artist, title)
        task_helper.load_uri_content(
            uri,
            self.__cancellable,
            self.__on_lyrics_downloaded,
            "lyricbox",
            "\n")

    def __download_genius_lyrics(self):
        """
            Download lyrics from genius
        """
        self.__downloads_running += 1
        # Update lyrics
        task_helper = TaskHelper()
        if App().player.current_track.id == Type.RADIOS:
            split = App().player.current_track.name.split(" - ")
            if len(split) < 2:
                return
            artist = split[0]
            title = split[1]
        else:
            artist = App().player.current_track.artists[0]
            title = App().player.current_track.name
        string = escape("%s %s" % (artist, title))
        string = noaccents(string)
        uri = "https://genius.com/%s-lyrics" % string.replace(" ", "-")
        task_helper.load_uri_content(
            uri,
            self.__cancellable,
            self.__on_lyrics_downloaded,
            "song_body-lyrics",
            "")

    def __update_lyrics_style(self):
        """
            Update lyrics style based on current view width
        """
        context = self.get_style_context()
        for cls in context.list_classes():
            context.remove_class(cls)
        context.add_class("lyrics")
        width = self.get_allocated_width()
        if width > WindowSize.XXLARGE:
            context.add_class("lyrics-x-large")
        elif width > WindowSize.MONSTER:
            context.add_class("lyrics-large")
        elif width > WindowSize.BIG:
            context.add_class("lyrics-medium")

    def __handle_size_allocation(self):
        """
            Update style and resize cover
        """
        self.__size_allocate_timeout_id = None
        self.__update_lyrics_style()
        self.update_artwork(self.__current_width,
                            self.__current_height,
                            True)

    # pylint: disable=unused-argument
    def __on_size_allocate(self, widget, allocation):
        """
            Update cover size
            @param widget as Gtk.Widget
            @param allocation as Gtk.Allocation
        """
        if (self.__current_width,
                self.__current_height) == (allocation.width,
                                           allocation.height):
            return
        (self.__current_width,
         self.__current_height) = (allocation.width,
                                   allocation.height)
        if self.__size_allocate_timeout_id is not None:
            GLib.source_remove(self.__size_allocate_timeout_id)
        self.__size_allocate_timeout_id = GLib.idle_add(
            self.__handle_size_allocation)

    # pylint: disable=too-many-arguments
    def __on_lyrics_downloaded(self, uri, status, data, cls, separator):
        """
            Show lyrics
            @param uri as str
            @param status as bool
            @param data as bytes
            @param cls as str
            @param separator as str
        """
        self.__downloads_running -= 1
        if self.__lyrics_set:
            return
        if status:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(data, 'html.parser')
            try:
                lyrics_text = soup.find_all(
                    "div", class_=cls)[0].get_text(separator=separator)
                self.__lyrics_label.set_text(lyrics_text)
                self.__lyrics_set = True
            # pylint: disable=broad-except,unused-variable
            except Exception as exceptiondl:
                pass
        if not self.__lyrics_set and self.__downloads_running == 0:
            self.__lyrics_label.set_text(_("No lyrics found ") + "😐")
