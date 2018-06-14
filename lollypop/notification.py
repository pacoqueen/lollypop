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

from gi.repository import Gdk, GLib, Gio
from gettext import gettext as _

from lollypop.define import App, ArtSize, Type
from lollypop.utils import is_gnome


class NotificationManager:
    """
        Freedesktop notification support
    """

    def __init__(self):
        """
            Init notification object with lollypop infos
        """
        self.__notification_handler_id = None
        self.__disable_all_notifications = True
        self.__is_gnome = is_gnome()
        self.__notification = Gio.Notification.new("")
        self.__action = Gio.Notification.new("")
        self.__action.add_button_with_target(
            _("Previous"),
            "app.shortcut",
            GLib.Variant("s", "prev"))
        self.__action.add_button_with_target(
            _("Next"),
            "app.shortcut",
            GLib.Variant("s", "next"))
        self.__on_notifications_settings_changed()

        App().settings.connect(
            "changed::disable-song-notifications",
            self.__on_notifications_settings_changed,
        )

        App().settings.connect(
            "changed::disable-notifications",
            self.__on_notifications_settings_changed,
        )

    def send(self, title, body=""):
        """
            Send message to user
            @param title as str
            @param body as str
        """

        if self.__disable_all_notifications:
            return
        self.__notification.set_title(title)
        if body:
            self.__notification.set_body(body)
        App().send_notification("send-message", self.__notification)

#######################
# PRIVATE             #
#######################
    def __on_current_changed(self, player):
        """
            Send notification with track_id infos
            @param player Player
        """
        state = App().window.get_window().get_state()
        if player.current_track.id is None or\
                state & Gdk.WindowState.FOCUSED or\
                App().is_fullscreen():
            return

        if player.current_track.id == Type.RADIOS:
            cover_path = App().art.get_radio_cache_path(
                player.current_track.album_artists[0], ArtSize.BIG)
        else:
            cover_path = App().art.get_album_cache_path(
                player.current_track.album, ArtSize.BIG)
        if cover_path is None:
            icon = Gio.Icon.new_for_string("org.gnome.Lollypop-symbolic")
        else:
            f = Gio.File.new_for_path(cover_path)
            icon = Gio.FileIcon.new(f)
        self.__action.set_icon(icon)
        self.__action.set_title(player.current_track.title)
        if player.current_track.album.name == "":
            self.__action.set_body(
                # TRANSLATORS: by refers to the artist,
                _("by %s") %
                ", ".join(player.current_track.artists))
        else:
            self.__action.set_body(
                # TRANSLATORS: by refers to the artist,
                # from to the album
                _("by %s, from %s") %
                (", ".join(player.current_track.artists),
                 player.current_track.album.name))
        App().send_notification("current-changed", self.__action)

    def __on_notifications_settings_changed(self, *ignore):
        self.__disable_all_notifications = App().settings.get_value(
            "disable-notifications",
        )

        disable_song_notifications = App().settings.get_value(
            "disable-song-notifications",
        )

        if self.__notification_handler_id:
            App().player.disconnect(self.__notification_handler_id)
            self.__notification_handler_id = None

        if (not self.__disable_all_notifications and not
                disable_song_notifications):
            self.__notification_handler_id = App().player.connect(
                "current-changed",
                self.__on_current_changed,
            )
