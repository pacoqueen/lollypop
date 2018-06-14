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
Widgets for context menu.
"""

from gettext import gettext as _
from gi.repository import Gtk, GLib
from lollypop.widgets_rating import RatingWidget
from lollypop.widgets_loved import LovedWidget
from lollypop.objects import Album, Track, Disc
from lollypop.define import App, TAG_EDITORS
from lollypop.logger import Logger
from lollypop.helper_dbus import DBusHelper


class ContextWidget(Gtk.EventBox):
    """
        Context widget
    """

    # pylint: disable=too-many-branches,too-many-locals,too-many-statements
    def __init__(self, objeto, button):
        """
            Init widget
            @param objeto as Track/Album
            @param button as Gtk.Button
        """
        Gtk.EventBox.__init__(self)
        self.__object = objeto
        self.__button = button

        self.connect("button-release-event", self.__on_button_release_event)

        grid = Gtk.Grid()
        grid.show()

        # Search for available tag editors
        self.__tag_editor = App().settings.get_value("tag-editor").get_string()
        if not self.__tag_editor:
            for tag_editor in TAG_EDITORS:
                if GLib.find_program_in_path(tag_editor) is not None:
                    self.__tag_editor = tag_editor
                    break

        if not isinstance(objeto, Disc):
            edit_button = Gtk.Button.new_from_icon_name(
                "document-properties-symbolic",
                Gtk.IconSize.BUTTON)
            edit_button.connect("clicked", self.__on_edit_button_clicked)
            edit_button.get_style_context().add_class("dim-button")
            edit_button.set_tooltip_text(_("Modify information"))
            edit_button.set_margin_end(2)
            grid.add(edit_button)
            # Check portal for tag editor
            dbus_helper = DBusHelper()
            dbus_helper.call("CanLaunchTagEditor",
                             GLib.Variant("(s)", (self.__tag_editor,)),
                             self.__on_can_launch_tag_editor, edit_button)
            # Open directory
            opendir_button = Gtk.Button.new_from_icon_name('document-open',
                                                           Gtk.IconSize.BUTTON)
            opendir_button.connect("clicked", self.__on_opendir_button_clicked)
            opendir_button.get_style_context().add_class("dim-button")
            opendir_button.set_tooltip_text(_("Open directory"))
            grid.add(opendir_button)
            opendir_button.show()
        if isinstance(objeto, Track):
            add_to_queue = True
            string = _("Add to queue")
            icon = "zoom-in-symbolic"
            if App().player.track_in_queue(self.__object):
                add_to_queue = False
                string = _("Remove from queue")
                icon = "zoom-out-symbolic"
            queue_button = Gtk.Button.new_from_icon_name(icon,
                                                         Gtk.IconSize.BUTTON)
            queue_button.connect("clicked",
                                 self.__on_queue_button_clicked,
                                 add_to_queue)
            queue_button.get_style_context().add_class("dim-button")
            queue_button.set_tooltip_text(string)
            queue_button.set_margin_end(2)
            queue_button.show()
            grid.add(queue_button)
        else:
            add_to_playback = True
            string = _("Add to current playlist")
            icon = "list-add-symbolic"
            # Search album in player
            if isinstance(objeto, Disc):
                album = objeto.album
            else:
                album = objeto
            player_album = None
            for _album in App().player.albums:
                if album.id == _album.id:
                    player_album = _album
                    break
            if player_album is not None:
                if player_album.track_ids.sort() == objeto.track_ids.sort():
                    add_to_playback = False
                    string = _("Remove from current playlist")
                    icon = "list-remove-symbolic"
            playback_button = Gtk.Button.new_from_icon_name(
                icon,
                Gtk.IconSize.BUTTON)
            playback_button.connect("clicked",
                                    self.__on_playback_button_clicked,
                                    add_to_playback)
            playback_button.get_style_context().add_class("dim-button")
            playback_button.set_tooltip_text(string)
            playback_button.set_margin_end(2)
            playback_button.show()
            grid.add(playback_button)

        playlist_button = Gtk.Button.new_from_icon_name("view-list-symbolic",
                                                        Gtk.IconSize.BUTTON)
        playlist_button.connect("clicked", self.__on_playlist_button_clicked)
        playlist_button.get_style_context().add_class("dim-button")
        playlist_button.set_tooltip_text(_("Add to playlist"))
        playlist_button.show()
        grid.add(playlist_button)

        if isinstance(self.__object, Track):
            rating = RatingWidget(objeto)
            rating.set_margin_end(2)
            rating.set_property("halign", Gtk.Align.END)
            rating.set_property("hexpand", True)
            rating.show()
            loved = LovedWidget(objeto)
            loved.set_margin_end(2)
            loved.show()
            grid.add(rating)
            grid.add(loved)
        self.add(grid)

#######################
# PRIVATE             #
#######################
    # pylint: disable=no-self-use,unused-argument
    def __on_button_release_event(self, widget, event):
        """
            Block signal
            @param widget as Gtk.Widget
            @param event as Gdk.Event
        """
        return True

    def __on_queue_button_clicked(self, button, add_to_queue):
        """
            Add or remove track to/from queue
            @param button as Gtk.Button
            @param add_to_queue as bool
        """
        if isinstance(self.__object, Album):
            for track_id in self.__object.track_ids:
                if add_to_queue:
                    App().player.append_to_queue(track_id, False)
                else:
                    App().player.del_from_queue(track_id, False)
        elif isinstance(self.__object, Track):
            if add_to_queue:
                App().player.append_to_queue(self.__object.id, False)
            else:
                App().player.del_from_queue(self.__object.id, False)
        App().player.emit("queue-changed")
        self.hide()

    def __on_playback_button_clicked(self, button, add_to_playback):
        """
            Add to/remove from current playback
            @param button as Gtk.Button
            @param add_to_playback as bool
        """
        if isinstance(self.__object, Disc):
            album = self.__object.album
        else:
            album = self.__object
        if add_to_playback:
            App().player.add_album(album)
        else:
            App().player.remove_album(album)
        self.hide()

    def __on_edit_button_clicked(self, button):
        """
            Run tags editor
            @param button as Gtk.Button
        """
        path = GLib.filename_from_uri(self.__object.uri)[0]
        dbus_helper = DBusHelper()
        dbus_helper.call("LaunchTagEditor",
                         GLib.Variant("(ss)", (self.__tag_editor, path)),
                         None, None)
        self.hide()

    def __on_opendir_button_clicked(self, button):
        """
            Run tags editor
            @param button as Gtk.Button
        """
        path = GLib.filename_from_uri(self.__object.uri)[0]
        dbus_helper = DBusHelper()
        dbus_helper.call("LaunchFileManager",
                         GLib.Variant("(s)", (path, )),
                         None, None)
        self.hide()

    def __on_playlist_button_clicked(self, button):
        """
            Show playlist_button manager
            @param button as Gtk.Button
        """
        App().window.container.show_playlist_manager(self.__object)
        self.hide()

    def __on_can_launch_tag_editor(self, source, result, button):
        """
            Add action if launchable
            @param source as GObject.Object
            @param result as Gio.AsyncResult
            @param button as Gtk.Button
        """
        try:
            source_result = source.call_finish(result)
            if source_result is not None and source_result[0]:
                button.show()
        # pylint: disable=broad-except
        except Exception as exception:
            Logger.error("ContextWidget::__on_can_launch_tag_editor(): {}"
                         "".format(exception))
