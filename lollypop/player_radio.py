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

from gi.repository import TotemPlParser, Gst, Gio

from lollypop.radios import Radios
from lollypop.player_base import BasePlayer
from lollypop.logger import Logger
from lollypop.define import App


class RadioPlayer(BasePlayer):
    """
        Radio player
        This class neeed the parent object to be a BinPlayer
        We keep a version of available radios (set_radios()) because we
        need to be in sync with current/last view and not with db (popularity
        changes)
    """

    def __init__(self):
        """
            Init radio player
        """
        BasePlayer.__init__(self)
        self.__current = None

    def load(self, track, play=True):
        """
            Load radio at uri
            @param track as Track
            @param play as bool
        """
        if Gio.NetworkMonitor.get_default().get_network_available():
            try:
                if not App().scanner.is_locked():
                    App().window.container.pulse(True)
                self.__current = track
                parser = TotemPlParser.Parser.new()
                parser.connect("entry-parsed", self.__on_entry_parsed,
                               track, play)
                parser.parse_async(track.uri, True,
                                   None, self.__on_parse_finished,
                                   track, play)
            except Exception as e:
                Logger.error("RadioPlayer::load(): %s" % e)
            if self.is_party:
                self.set_party(False)

#######################
# PROTECTED           #
#######################

#######################
# PRIVATE             #
#######################
    def __start_playback(self, track, play):
        """
            Start playing track
            @param track as Track
            @param play as bool
        """
        self._plugins.volume.props.volume = 1.0
        self._playbin.set_state(Gst.State.NULL)
        self._playbin.set_property("uri", track.uri)
        Radios().set_more_popular(track.album_artists[0])
        self._current_track = track
        self.__current = None
        if play:
            self._playbin.set_state(Gst.State.PLAYING)
            self.emit("status-changed")
        else:
            self.emit("current-changed")
            App().window.container.pulse(False)

    def __on_parse_finished(self, parser, result, track, play):
        """
            Play stream
            @param parser as TotemPlParser.Parser
            @param result as Gio.AsyncResult
            @param track as Track
            @param play as bool
        """
        # Only start playing if context always True
        if self.__current == track:
            self.__start_playback(track, play)
            App().window.container.pulse(False)

    def __on_entry_parsed(self, parser, uri, metadata, track, play):
        """
            Play stream
            @param parser as TotemPlParser.Parser
            @param track uri as str
            @param metadata as GLib.HastTable
            @param track as Track
            @param play as bool
        """
        # Only start playing if context always True
        if self.__current == track:
            track.set_radio(track.album_artists[0], uri)
