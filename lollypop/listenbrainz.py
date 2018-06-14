# Copyright (c) 2018 Philipp Wolfer <ph.wolfer@gmail.com>
# Copyright (c) 2018 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
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

from gi.repository import Soup, GObject, Gio, GLib

import json
import time

from lollypop.helper_task import TaskHelper
from lollypop.logger import Logger

HOST_NAME = "api.listenbrainz.org"
PATH_SUBMIT = "/1/submit-listens"


class ListenBrainz(GObject.GObject):
    """
        Submit listens to ListenBrainz.org.

        See https://listenbrainz.readthedocs.io/en/latest/dev/api.html
    """

    user_token = GObject.Property(type=str, default=None)

    def __init__(self):
        """
            Init ListenBrainz object
        """
        GObject.GObject.__init__(self)
        self.__queue = []
        self.__next_request_time = 0

    def listen(self, track, time):
        """
            Submit a listen for a track
            @param track as Track
            @param time as int
        """
        payload = self.__get_payload(track)
        payload[0]["listened_at"] = time
        self.__submit("single", payload)

    def playing_now(self, track):
        """
            Submit a playing now notification for a track
            @param track as Track
        """
        payload = self.__get_payload(track)
        self.__submit("playing_now", payload)

    @property
    def can_love(self):
        """
            True if engine can love
            @return bool
        """
        return False

    @property
    def available(self):
        """
            True if service available
            @return bool
        """
        return self.user_token != ""

#######################
# PRIVATE             #
#######################
    def __clean_queue(self):
        """
            Send tracks in queue
        """
        if self.__queue:
            (listen_type, payload) = self.__queue.pop(0)
            helper = TaskHelper()
            helper.run(self.__request, listen_type, payload)
            GLib.timeout_add(1000, self.__clean_queue)

    def __submit(self, listen_type, payload):
        """
            Submit payload to service in a thread
            @param listen_type as str
            @param payload as []
        """
        if Gio.NetworkMonitor.get_default().get_network_available():
            helper = TaskHelper()
            self.__clean_queue()
            helper.run(self.__request, listen_type, payload)
        else:
            self.__queue.append((listen_type, payload))

    def __request(self, listen_type, payload, retry=0):
        """
            Submit payload to service
            @param listen_type as str
            @param payload as []
            @param retry as int (internal)
        """
        self.__wait_for_ratelimit()
        Logger.debug("ListenBrainz %s: %r" % (listen_type, payload))
        data = {
            "listen_type": listen_type,
            "payload": payload
        }
        body = json.dumps(data).encode("utf-8")
        session = Soup.Session.new()
        uri = "https://%s%s" % (HOST_NAME, PATH_SUBMIT)
        msg = Soup.Message.new("POST", uri)
        msg.set_request("application/json",
                        Soup.MemoryUse.STATIC,
                        body)
        msg.request_headers.append("Authorization",
                                   "Token %s" % self.user_token)
        try:
            status = session.send_message(msg)
            response_headers = msg.get_property("response-headers")
            self.__handle_ratelimit(response_headers)
            # Too Many Requests
            if status == 429 and retry < 5:
                self.__request(listen_type, payload, retry + 1)
        except Exception as e:
            print("ListenBrainz::__submit():", e)

    def __wait_for_ratelimit(self):
        """
            Sleep to respect service X-RateLimit
        """
        now = time.time()
        if self.__next_request_time > now:
            delay = self.__next_request_time - now
            Logger.debug("ListenBrainz rate limit applies, delay %d" % delay)
            time.sleep(delay)

    def __handle_ratelimit(self, response):
        """
            Set rate limit from response
            @param response as Soup.MessageHeaders
        """
        remaining = response.get("X-RateLimit-Remaining")
        reset_in = response.get("X-RateLimit-Reset-In")
        if remaining is None or reset_in is None:
            return
        Logger.debug("ListenBrainz X-RateLimit-Remaining: %s" % remaining)
        Logger.debug("ListenBrainz X-RateLimit-Reset-In: %s" % reset_in)
        if (int(remaining) == 0):
            self.__next_request_time = time.time() + int(reset_in)

    def __get_payload(self, track):
        """
            Build payload from track
            @param track as Track
        """
        artists = ", ".join(track.artists)
        payload = {
            "track_metadata": {
                "artist_name": artists,
                "track_name": track.title,
                "release_name": track.album_name,
                "additional_info": {
                    "release_mbid": track.album.mb_album_id,
                    "recording_mbid": track.mb_track_id,
                    "tracknumber": track.number
                }
            }
        }
        return [payload]
