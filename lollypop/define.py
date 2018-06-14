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

# This is global object initialised at lollypop start
# member init order is important!

from gi.repository import Gio, GLib

LOLLYPOP_DATA_PATH = GLib.get_user_data_dir() + "/lollypop"

App = Gio.Application.get_default

GOOGLE_API_ID = "015987506728554693370:waw3yqru59a"

TAG_EDITORS = ["kid3-qt", "exfalso", "easytag", "picard", "puddletag"]


# Represent what to do on next track
class NextContext:
    NONE = 0             # Continue playback
    REPEAT_TRACK = 1     # Repeat current track
    STOP = 2             # Stop after track/album/artist


class GstPlayFlags:
    GST_PLAY_FLAG_VIDEO = 1 << 0  # We want video output
    GST_PLAY_FLAG_AUDIO = 1 << 1  # We want audio output
    GST_PLAY_FLAG_TEXT = 1 << 3   # We want subtitle output


class Loading:
    NONE = 0
    LEFT = 1
    RIGHT = 2
    ALL = 3
    STOP = 4


class ResponsiveType:
    FIXED = 0
    DND = 1
    SEARCH = 2
    LIST = 3


class ArtSize:
    NONE = 0
    SMALL = 33
    MEDIUM = 48  # If changed, adapt width request in AlbumRow
    ARTIST_SMALL = 60
    HEADER = 100
    BIG = 200
    FULLSCREEN = 500
    ARTIST = 800
    MONSTER = 900
    MAX = 4000


class Shuffle:
    NONE = 0             # No shuffle
    TRACKS = 1           # Shuffle by tracks on genre
    ALBUMS = 2           # Shuffle by albums on genre


class PowerManagement:
    NONE = 0             # Use OS defaults
    IDLE = 1             # Inhibit screensaver
    SUSPEND = 2          # Inhibit suspend
    BOTH = 3             # Inhibit screensaver and suspend


class WindowSize:
    SMALL = 400
    MEDIUM = 500
    BIG = 700
    MONSTER = 800
    XXLARGE = 1000


class OrderBy:
    ARTIST = 0
    NAME = 1
    YEAR = 2
    POPULARITY = 3


# Order is important
class Type:
    NONE = -1
    POPULARS = -2
    RANDOMS = -3
    RECENTS = -4
    PLAYLISTS = -5
    RADIOS = -6
    EXTERNALS = -7
    SEARCH = -8
    NOPARTY = -9
    ALBUMS = -10
    ALL = -11
    USB_DISKS = -12
    LOVED = -997
    NEVER = -998
    DEVICES = -1000
    SEPARATOR = -2000
    COMPILATIONS = -2001


PROXY_BUS = "org.gnome.Lollypop.Portal"
PROXY_PATH = "/org/gnome/LollypopPortal"
PROXY_INTERFACE = "org.gnome.Lollypop.Portal"


SPOTIFY_CLIENT_ID = "0b144843878a46b2b12e0958c342c3ac"
SPOTIFY_SECRET = "265ab8e057684f1b9e69e0c58f4881c1"

ENCODING = ["utf_8",
            "iso8859_1",
            "utf_16",
            "utf_16_be"]
