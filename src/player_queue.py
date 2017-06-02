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

from gettext import gettext as _

from lollypop.objects import Track
from lollypop.define import Lp
from lollypop.utils import get_network_available


class QueuePlayer:
    """
        Manage queue
    """

    def __init__(self):
        """
            Init queue
        """
        self.__queue = []
        self.__backup_next = None

    def append_to_queue(self, track_id, notify=True):
        """
            Append track to queue,
            remove previous track if exist
            @param track id as int
            @param notify as bool
        """
        track = Track(track_id)
        if track.is_web and\
           not get_network_available():
            if Lp().notify is not None:
                Lp().notify.send(_("No network available,"
                                   " can't play this track"),
                                 track.uri)
            return
        if track_id in self.__queue:
            self.__queue.remove(track_id)
        self.__queue.append(track_id)
        if self.__backup_next is None:
            self.__backup_next = self._next_track
        self.set_next()
        self.set_prev()
        if notify:
            self.emit("queue-changed")

    def insert_in_queue(self, track_id, pos=0, notify=True):
        """
            Prepend track to queue,
            remove previous track if exist
            @param track id as int
            @param notify as bool
        """
        track = Track(track_id)
        if track.is_web and\
           not get_network_available():
            if Lp().notify is not None:
                Lp().notify.send(_("No network available,"
                                   " can't play this track"),
                                 track.uri)
            return
        if track_id in self.__queue:
            self.__queue.remove(track_id)
        self.__queue.insert(pos, track_id)
        if self.__backup_next is None:
            self.__backup_next = self._next_track
        self.set_next()
        self.set_prev()
        if notify:
            self.emit("queue-changed")

    def del_from_queue(self, track_id, notify=True):
        """
            Remove track from queue
            @param track id as int
            @param notify as bool
        """
        if track_id in self.__queue:
            self.__queue.remove(track_id)
            if not self.__queue and self.__backup_next is not None:
                self._next_track = self.__backup_next
                self.__backup_next = None
            else:
                self.set_next()
            self.set_prev()
        if notify:
            self.emit("queue-changed")

    def clear_queue(self, notify=True):
        """
            Set queue
            @param [ids as int]
            @param notify as bool
        """
        self.__queue = []
        if self.__backup_next is None:
            self.set_next()
        else:
            self._next_track = self.__backup_next
            self.__backup_next = None
        self.set_prev()
        if notify:
            self.emit("queue-changed")

    @property
    def queue(self):
        """
            Return queue
            @return [ids as int]
        """
        return self.__queue

    def track_in_queue(self, track):
        """
            True if track exists in queue
            @param track as Track
            @return bool
        """
        if self.__queue:
            return track.id in self.__queue
        else:
            return False

    def album_in_queue(self, album):
        """
            True if album id exists in queue
            @param album as Album
            @return bool
        """
        if self.__queue:
            union = set(self.__queue) & set(album.track_ids)
            return len(union) == len(album.track_ids)
        else:
            return False

    def get_track_position(self, track_id):
        """
            Return track position in queue
            @param track id as int
            @return position as int
        """
        return self.__queue.index(track_id) + 1

    def next(self):
        """
            Get next track id
            @return Track
        """
        track_id = None
        if self.__queue:
            track_id = self.__queue[0]
        return Track(track_id)

#######################
# PRIVATE             #
#######################
