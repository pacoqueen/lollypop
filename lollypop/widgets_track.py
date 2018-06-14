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

from gi.repository import GObject, Gtk, Gdk, Pango, GLib, Gst

from lollypop.define import App, ArtSize, Type, ResponsiveType
from lollypop.pop_menu import TrackMenuPopover, TrackMenu
from lollypop.widgets_indicator import IndicatorWidget
from lollypop.widgets_context import ContextWidget
from lollypop.utils import seconds_to_string
from lollypop.objects import Track
from lollypop.logger import Logger


class Row(Gtk.ListBoxRow):
    """
        A row
    """
    __gsignals__ = {
        "album-moved": (GObject.SignalFlags.RUN_FIRST, None, (str, bool)),
        "track-moved": (GObject.SignalFlags.RUN_FIRST, None, (str, str, bool))
    }

    def __init__(self, track, responsive_type):
        """
            Init row widgets
            @param track as Track
            @param responsive_type as ResponsiveType
        """
        # We do not use Gtk.Builder for speed reasons
        Gtk.ListBoxRow.__init__(self)
        self._artists_label = None
        self._track = track
        self.__preview_timeout_id = None
        self.__context_timeout_id = None
        self.__context = None
        self._indicator = IndicatorWidget(
            self._track,
            self if responsive_type == ResponsiveType.DND else None)
        self.set_indicator(App().player.current_track.id == self._track.id,
                           self._track.loved)
        self._row_widget = Gtk.EventBox()
        self._row_widget.connect("button-release-event",
                                 self.__on_button_release_event)
        self._row_widget.connect("enter-notify-event",
                                 self.__on_enter_notify_event)
        self._row_widget.connect("leave-notify-event",
                                 self.__on_leave_notify_event)
        self._grid = Gtk.Grid()
        self._grid.set_column_spacing(5)
        self._row_widget.add(self._grid)
        self._title_label = Gtk.Label.new(self._track.name)
        self._title_label.set_property("has-tooltip", True)
        self._title_label.connect("query-tooltip",
                                  self.__on_query_tooltip)
        self._title_label.set_property("hexpand", True)
        self._title_label.set_property("halign", Gtk.Align.START)
        self._title_label.set_ellipsize(Pango.EllipsizeMode.END)
        featuring_artist_ids = track.featuring_artist_ids
        if featuring_artist_ids:
            artists = []
            for artist_id in featuring_artist_ids:
                artists.append(App().artists.get_name(artist_id))
            self._artists_label = Gtk.Label.new(GLib.markup_escape_text(
                ", ".join(artists)))
            self._artists_label.set_use_markup(True)
            self._artists_label.set_property("has-tooltip", True)
            self._artists_label.connect("query-tooltip",
                                        self.__on_query_tooltip)
            self._artists_label.set_property("hexpand", True)
            self._artists_label.set_property("halign", Gtk.Align.END)
            self._artists_label.set_ellipsize(Pango.EllipsizeMode.END)
            self._artists_label.set_opacity(0.3)
            self._artists_label.set_margin_end(5)
            self._artists_label.show()
        self._duration_label = Gtk.Label.new(
            seconds_to_string(self._track.duration))
        self._duration_label.get_style_context().add_class("dim-label")
        self._num_label = Gtk.Label()
        self._num_label.set_ellipsize(Pango.EllipsizeMode.END)
        self._num_label.set_property("valign", Gtk.Align.CENTER)
        self._num_label.set_width_chars(4)
        self._num_label.get_style_context().add_class("dim-label")
        self.update_num_label()
        self.__menu_button = Gtk.Button.new()
        self.__menu_button.set_relief(Gtk.ReliefStyle.NONE)
        self.__menu_button.get_style_context().add_class("menu-button")
        self.__menu_button.get_style_context().add_class("track-menu-button")
        self._grid.add(self._num_label)
        self._grid.add(self._title_label)
        if self._artists_label is not None:
            self._grid.add(self._artists_label)
        self._grid.add(self._duration_label)
        self._grid.add(self.__menu_button)
        self.add(self._row_widget)
        self.get_style_context().add_class("trackrow")

    def show_spinner(self):
        """
            Show spinner
        """
        self._indicator.show_spinner()

    def set_indicator(self, playing, loved):
        """
            Show indicator
            @param widget name as str
            @param playing as bool
            @param loved as bool
        """
        self._indicator.clear()
        if playing:
            self.get_style_context().remove_class("trackrow")
            self.get_style_context().add_class("trackrowplaying")
            if loved:
                self._indicator.play_loved()
            else:
                self._indicator.play()
        else:
            self.get_style_context().remove_class("trackrowplaying")
            self.get_style_context().add_class("trackrow")
            if loved and self.__context is None:
                self._indicator.loved()
            else:
                self._indicator.empty()

    def update_duration(self):
        """
            Update duration for row
        """
        # Get a new track to get new duration (cache)
        track = Track(self._track.id)
        self._duration_label.set_text(seconds_to_string(track.duration))

    def update_num_label(self):
        """
            Update position label for row
        """
        if App().player.track_in_queue(self._track):
            self._num_label.get_style_context().add_class("queued")
            pos = App().player.get_track_position(self._track.id)
            self._num_label.set_text(str(pos))
        elif self._track.number > 0:
            self._num_label.get_style_context().remove_class("queued")
            self._num_label.set_text(str(self._track.number))
        else:
            self._num_label.get_style_context().remove_class("queued")
            self._num_label.set_text("")

    @property
    def track(self):
        """
            Get row track
            @return Track
        """
        return self._track

#######################
# PROTECTED           #
#######################
    def _get_menu(self):
        """
            Return TrackMenu
        """
        return TrackMenu(self._track)

#######################
# PRIVATE             #
#######################
    def __play_preview(self):
        """
            Play track
            @param widget as Gtk.Widget
        """
        App().player.preview.set_property("uri", self._track.uri)
        App().player.preview.set_state(Gst.State.PLAYING)
        self.set_indicator(True, False)
        self.__preview_timeout_id = None

    def __popup_menu(self, widget, xcoordinate=None, ycoordinate=None):
        """
            Popup menu for track
            @param widget as Gtk.Button
            @param xcoordinate as int (or None)
            @param ycoordinate as int (or None)
        """
        popover = TrackMenuPopover(self._track, self._get_menu())
        if xcoordinate is not None and ycoordinate is not None:
            rect = widget.get_allocation()
            rect.x = xcoordinate
            rect.y = ycoordinate
            rect.width = rect.height = 1
        popover.set_relative_to(widget)
        popover.set_pointing_to(rect)
        popover.connect("closed", self.__on_closed)
        self.get_style_context().add_class("track-menu-selected")
        popover.show()

    def __on_map(self, widget):
        """
            Fix for Gtk < 3.18,
            if we are in a popover, do not show menu button
        """
        widget = self.get_parent()
        while widget is not None:
            if isinstance(widget, Gtk.Popover):
                break
            widget = widget.get_parent()
        if widget is None:
            self._grid.add(self.__menu_button)
            self.__menu_button.show()

    def __on_artist_button_press(self, eventbox, event):
        """
            Go to artist page
            @param eventbox as Gtk.EventBox
            @param event as Gdk.EventButton
        """
        App().window.container.show_artists_albums(self._album.artist_ids)
        return True

    def __on_enter_notify_event(self, widget, event):
        """
            Set image on buttons now, speed reason
            @param widget as Gtk.Widget
            @param event as Gdk.Event
        """
        if self.__context_timeout_id is not None:
            GLib.source_remove(self.__context_timeout_id)
            self.__context_timeout_id = None
        if App().settings.get_value("preview-output").get_string() != "":
            self.__preview_timeout_id = GLib.timeout_add(500,
                                                         self.__play_preview)
        if self.__menu_button.get_image() is None:
            image = Gtk.Image.new_from_icon_name("go-previous-symbolic",
                                                 Gtk.IconSize.MENU)
            self.__menu_button.set_image(image)
            self.__menu_button.connect(
                "button-release-event",
                self.__on_indicator_button_release_event)
            self._indicator.update_button()

    def __on_leave_notify_event(self, widget, event):
        """
            Stop preview
            @param widget as Gtk.Widget
            @param event as Gdk.Event
        """
        def close_indicator():
            """
                Simulate a release event
            """
            self.__on_indicator_button_release_event(self.__menu_button,
                                                     event)
        allocation = widget.get_allocation()
        if event.x <= 0 or\
           event.x >= allocation.width or\
           event.y <= 0 or\
           event.y >= allocation.height:
            if self.__context is not None and\
                    self.__context_timeout_id is None:
                self.__context_timeout_id = GLib.timeout_add(
                    1000,
                    close_indicator)
            if App().settings.get_value("preview-output").get_string() != "":
                if self.__preview_timeout_id is not None:
                    GLib.source_remove(self.__preview_timeout_id)
                    self.__preview_timeout_id = None
                self.set_indicator(
                    App().player.current_track.id == self._track.id,
                    self._track.loved)
                App().player.preview.set_state(Gst.State.NULL)

    def __on_button_release_event(self, widget, event):
        """
            Handle button press event:
                |_ 1 => activate
                |_ 2 => queue
                |_ 3 => menu
            @param widget as Gtk.Widget
            @param event as Gdk.EventButton
        """
        if event.button == 3:
            window = widget.get_window()
            if window == event.window:
                self.__popup_menu(widget, event.x, event.y)
            # Happens when pressing button over menu btn
            else:
                self.__on_indicator_button_release_event(self.__menu_button,
                                                         event)
        elif event.button == 2:
            if self._track.id in App().player.queue:
                App().player.del_from_queue(self._track.id)
            else:
                App().player.append_to_queue(self._track.id)
        else:
            self.activate()
        return True

    def __on_indicator_button_release_event(self, button, event):
        """
            Popup menu for track relative to button
            @param button as Gtk.Button
            @param event as Gdk.EventButton
        """
        def on_hide(widget):
            self.__on_indicator_button_release_event(button, event)
        self.__context_timeout_id = None
        image = self.__menu_button.get_image()
        if self.__context is None:
            image.set_from_icon_name("go-next-symbolic",
                                     Gtk.IconSize.MENU)
            self.__context = ContextWidget(self._track, button)
            self.__context.connect("hide", on_hide)
            self.__context.set_property("halign", Gtk.Align.END)
            self.__context.show()
            self._duration_label.hide()
            self._grid.insert_next_to(button, Gtk.PositionType.LEFT)
            self._grid.attach_next_to(self.__context, button,
                                      Gtk.PositionType.LEFT, 1, 1)
            self.set_indicator(App().player.current_track.id == self._track.id,
                               False)
        else:
            image.set_from_icon_name("go-previous-symbolic",
                                     Gtk.IconSize.MENU)
            self.__context.destroy()
            self._duration_label.show()
            self.__context = None
            self.set_indicator(App().player.current_track.id == self._track.id,
                               self._track.loved)
        return True

    def __on_closed(self, widget):
        """
            Remove selected style
            @param widget as Gtk.Popover
        """
        self.get_style_context().remove_class("track-menu-selected")

    def __on_query_tooltip(self, widget, x, y, keyboard, tooltip):
        """
            Show tooltip if needed
            @param widget as Gtk.Widget
            @param x as int
            @param y as int
            @param keyboard as bool
            @param tooltip as Gtk.Tooltip
        """
        text = ""
        layout = widget.get_layout()
        label = widget.get_text()
        if layout.is_ellipsized():
            text = "%s" % (GLib.markup_escape_text(label))
        widget.set_tooltip_markup(text)


class PlaylistRow(Row):
    """
        A track row with album cover
    """

    def __init__(self, track, show_headers):
        """
            Init row widget
            @param track as Track
            @param show headers as bool
        """
        Row.__init__(self, track, ResponsiveType.DND)
        self.__parent_filter = False
        self.__show_headers = show_headers
        self._grid.insert_row(0)
        self._grid.insert_column(0)
        self._grid.insert_column(1)
        self._grid.attach(self._indicator, 1, 1, 1, 2)
        self.__cover = Gtk.Image()
        self.__cover.set_property("halign", Gtk.Align.CENTER)
        self.__cover.set_property("valign", Gtk.Align.CENTER)
        self.__cover.get_style_context().add_class("small-cover-frame")
        self.__cover.set_no_show_all(True)
        # We force width with a Box
        box = Gtk.Box()
        box.set_homogeneous(True)
        box.add(self.__cover)
        box.set_property("width-request", ArtSize.MEDIUM + 2)
        self._grid.attach(box, 0, 0, 1, 2)
        self.show_all()
        self.__header = Gtk.Grid()
        self.__header.set_column_spacing(5)
        if self._track.album.artist_ids[0] != Type.COMPILATIONS:
            self.__album_artist_label = Gtk.Label()
            self.__album_artist_label.set_markup(
                "<b>" +
                GLib.markup_escape_text(
                    ", ".join(self._track.album.artists)) +
                "</b>")
            self.__album_artist_label.set_ellipsize(Pango.EllipsizeMode.END)
            self.__album_artist_label.get_style_context().add_class(
                "dim-label")
            self.__header.add(self.__album_artist_label)
        self.__album_label = Gtk.Label.new(self._track.album.name)
        self.__album_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.__album_label.get_style_context().add_class("dim-label")
        self.__album_label.set_hexpand(True)
        self.__album_label.set_property("halign", Gtk.Align.END)
        self.__header.add(self.__album_label)
        if self._artists_label is not None:
            self._grid.attach(self.__header, 1, 0, 5, 1)
        else:
            self._grid.attach(self.__header, 1, 0, 4, 1)
        self.set_indicator(App().player.current_track.id == self._track.id,
                           self._track.loved)
        self.show_headers(self.__show_headers)
        self.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [],
                             Gdk.DragAction.MOVE)
        self.drag_source_add_text_targets()
        self.drag_dest_set(Gtk.DestDefaults.DROP,
                           [], Gdk.DragAction.MOVE)
        self.drag_dest_add_text_targets()
        self.connect("drag-begin", self.__on_drag_begin)
        self.connect("drag-data-get", self.__on_drag_data_get)
        self.connect("drag-data-received", self.__on_drag_data_received)

    @property
    def filter(self):
        """
            @return str
        """
        return " ".join(self._track.album.artists +
                        self._track.artists +
                        [self._track.name] +
                        [self._track.album.name])

    def set_filtered(self, b):
        """
            Set widget filtered
        """
        self.__parent_filter = b

    @property
    def filtered(self):
        """
            True if filtered by parent
        """
        return self.__parent_filter

    def show_headers(self, show):
        """
            Show header
            @param show as bool
        """
        if not self.get_sensitive():
            return
        if self.__header.is_visible() == show:
            return
        self.__show_headers = show
        if show:
            self.__cover.set_tooltip_text(self._track.album.name)
            surface = App().art.get_album_artwork(
                self._track.album,
                ArtSize.MEDIUM,
                self.get_scale_factor())
            self.__cover.set_from_surface(surface)
            self.__cover.show()
            self.__header.show_all()
        else:
            self.__cover.set_tooltip_text("")
            self.__cover.clear()
            self.__cover.hide()
            self.__header.hide()

#######################
# PROTECTED           #
#######################
    def _get_menu(self):
        """
            Return TrackMenu
        """
        return TrackMenu(self._track, True)

#######################
# PRIVATE             #
#######################
    def __on_drag_begin(self, widget, context):
        """
            Set icon
            @param widget as Gtk.Widget
            @param context as Gdk.DragContext
        """
        widget.drag_source_set_icon_name("emblem-music-symbolic")

    def __on_drag_data_get(self, widget, context, data, info, time):
        """
            Send track id
            @param widget as Gtk.Widget
            @param context as Gdk.DragContext
            @param data as Gtk.SelectionData
            @param info as int
            @param time as int
        """
        track_id = str(self._track.id)
        data.set_text(track_id, len(track_id))

    def __on_drag_data_received(self, widget, context, x, y, data, info, time):
        """
            Move track
            @param widget as Gtk.Widget
            @param context as Gdk.DragContext
            @param x as int
            @param y as int
            @param data as Gtk.SelectionData
            @param info as int
            @param time as int
        """
        from lollypop.view import View
        view = widget.get_ancestor(View)
        if view is not None:
            view.clear_animation()
        height = self.get_allocated_height()
        if y > height / 2:
            down = True
        else:
            down = False
        try:
            src = data.get_text()
            if self._track.id == int(src):
                return
            self.emit("track-moved", self._track.id, src, down)
        except:
            if len(App().window.container.view.get_ids()) == 1:
                App().playlists.import_uri(
                    App().window.container.view.get_ids()[0],
                    data.get_text(), self._track.id, down)


class TrackRow(Row):
    """
        A track row
    """

    def get_best_height(widget):
        """
            Calculate widget height
            @param widget as Gtk.Widget
        """
        ctx = widget.get_pango_context()
        layout = Pango.Layout.new(ctx)
        layout.set_text("a", 1)
        font_height = int(layout.get_pixel_size()[1])
        # Button min height + borders (application.css)
        menu_height = 24 + 2
        if font_height > menu_height:
            height = font_height
        else:
            height = menu_height
        return height

    def __init__(self, track, responsive_type):
        """
            Init row widget and show it
            @param track as Track
            @param responsive_type as ResponsiveType
        """
        Row.__init__(self, track, responsive_type)
        self.__parent_filter = False
        self._grid.insert_column(0)
        self._grid.attach(self._indicator, 0, 0, 1, 1)
        self.show_all()
        if responsive_type == ResponsiveType.DND:
            self.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [],
                                 Gdk.DragAction.MOVE)
            self.drag_source_add_text_targets()
            self.drag_dest_set(Gtk.DestDefaults.DROP,
                               [], Gdk.DragAction.MOVE)
            self.drag_dest_add_text_targets()
            self.connect("drag-begin", self.__on_drag_begin)
            self.connect("drag-data-get", self.__on_drag_data_get)
            self.connect("drag-data-received", self.__on_drag_data_received)

    @property
    def filter(self):
        """
            @return str
        """
        return self._track.name

    def set_filtered(self, b):
        """
            Set widget filtered
        """
        self.__parent_filter = b

    @property
    def filtered(self):
        """
            True if filtered by parent
        """
        return self.__parent_filter

#######################
# PRIVATE             #
#######################
    def __on_drag_begin(self, widget, context):
        """
            Set icon and update view padding
            @param widget as Gtk.Widget
            @param context as Gdk.DragContext
        """
        widget.drag_source_set_icon_name("emblem-music-symbolic")

    def __on_drag_data_get(self, widget, context, data, info, time):
        """
            Send track id
            @param widget as Gtk.Widget
            @param context as Gdk.DragContext
            @param data as Gtk.SelectionData
            @param info as int
            @param time as int
        """
        track = "t:%s:%s" % (self._track, self._track.album)
        data.set_text(track, len(track))

    def __on_drag_data_received(self, widget, context, x, y, data, info, time):
        """
            Move track
            @param widget as Gtk.Widget
            @param context as Gdk.DragContext
            @param x as int
            @param y as int
            @param data as Gtk.SelectionData
            @param info as int
            @param time as int
        """
        from lollypop.view import View
        view = widget.get_ancestor(View)
        if view is not None:
            view.clear_animation()
        height = self.get_allocated_height()
        if y > height / 2:
            down = True
        else:
            down = False
        try:
            (type_id, object_str, album_str) = data.get_text().split(":")
            if object_str == str(self._track):
                pass
            elif type_id == "t":
                self.emit("track-moved", object_str, album_str, down)
            elif type_id == "a":
                self.emit("album-moved", object_str, down)
        except Exception as e:
            Logger.error("Row::__on_drag_data_received(): %s" % e)


class TracksWidget(Gtk.ListBox):
    """
        A list of tracks
    """

    __gsignals__ = {
        "activated": (GObject.SignalFlags.RUN_FIRST,
                      None, (GObject.TYPE_PYOBJECT,))
    }

    def __init__(self, responsive_type):
        """
            Init track widget
            @param responsive_type as ResponsiveType
        """
        Gtk.ListBox.__init__(self)
        self.connect("destroy", self.__on_destroy)
        self.__queue_signal_id = App().player.connect("queue-changed",
                                                      self.__on_queue_changed)
        self.__loved_signal_id1 = App().playlists.connect(
            "playlist-add",
            self.__on_loved_playlist_changed)
        self.__loved_signal_id2 = App().playlists.connect(
            "playlist-del",
            self.__on_loved_playlist_changed)
        self.connect("row-activated", self.__on_activate)
        self.get_style_context().add_class("trackswidget")
        self.set_property("hexpand", True)
        self.set_property("selection-mode", Gtk.SelectionMode.NONE)
        if responsive_type == ResponsiveType.DND:
            self.drag_dest_set(Gtk.DestDefaults.DROP,
                               [], Gdk.DragAction.MOVE)
            self.drag_dest_add_text_targets()
            self.connect("drag-data-received", self.__on_drag_data_received)

    def update_headers(self, prev_album_id=None):
        """
            Update headers
            @param previous album id as int
        """
        for child in self.get_children():
            if child.track.album.id == prev_album_id:
                child.show_headers(False)
            else:
                child.show_headers(True)
            prev_album_id = child.track.album.id

    def update_indexes(self, start):
        """
            Update indexes
            @param start index as int
        """
        for row in self.get_children():
            row.track.set_number(start)
            row.update_num_label()
            start += 1

    def update_playing(self, track_id):
        """
            Update playing track
            @param track id as int
        """
        for row in self.get_children():
            row.set_indicator(row.track.id == track_id,
                              Track(row.track.id).loved)

    def update_duration(self, track_id):
        """
            Update playing track
            @param track id as int
        """
        for row in self.get_children():
            if row.id == track_id:
                row.update_duration()

    def show_spinner(self, track_id):
        """
            Show spinner for track_id
        """
        for row in self.get_children():
            if row.id == track_id:
                row.show_spinner()
                break

#######################
# PRIVATE             #
#######################
    def __on_drag_data_received(self, widget, context, x, y, data, info, time):
        """
            Move track
            @param widget as Gtk.Widget
            @param context as Gdk.DragContext
            @param x as int
            @param y as int
            @param data as Gtk.SelectionData
            @param info as int
            @param time as int
        """
        try:
            from lollypop.view import View
            view = widget.get_ancestor(View)
            if view is not None:
                view.clear_animation()
            value = int(data.get_text())
            bottom_row = self.get_children()[-1]
            bottom_row.emit("track-moved", bottom_row.id, value, False)
        except:
            if len(App().window.container.view.get_ids()) == 1:
                App().playlists.import_uri(
                    App().window.container.view.get_ids()[0],
                    data.get_text())

    def __on_queue_changed(self, unused):
        """
            Update all position labels
        """
        for row in self.get_children():
            row.update_num_label()

    def __on_loved_playlist_changed(self, widget, playlist_id,
                                    track_id, pos=None):
        """
            Updates the loved icon
            @param playlist as Playlist
            @param playlist id as int
            @param track id as int
            @param pos as unused
        """
        if playlist_id != Type.LOVED:
            return
        for row in self.get_children():
            if track_id == row.track.id:
                row.set_indicator(track_id == App().player.current_track.id,
                                  Track(track_id).loved)

    def __on_destroy(self, widget):
        """
            Remove signals
            @param widget as Gtk.Widget
        """
        if self.__queue_signal_id is not None:
            App().player.disconnect(self.__queue_signal_id)
            self.__queue_signal_id = None
        if self.__loved_signal_id1 is not None:
            App().playlists.disconnect(self.__loved_signal_id1)
            self.__loved_signal_id1 = None
        if self.__loved_signal_id2 is not None:
            App().playlists.disconnect(self.__loved_signal_id2)
            self.__loved_signal_id2 = None

    def __on_activate(self, widget, row):
        """
            Play activated item
            @param widget as TracksWidget
            @param row as TrackRow
        """
        self.emit("activated", row.track)
