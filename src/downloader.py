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

from gi.repository import GLib

from threading import Thread
import json

from lollypop.cache import InfoCache
from lollypop.define import Lp, GOOGLE_API_ID, Type
from lollypop.utils import debug, get_network_available
from lollypop.lio import Lio


class Downloader:
    """
        Download from the web
    """
    try:
        from lollypop.wikipedia import Wikipedia
    except:
        Wikipedia = None

    def __init__(self):
        """
            Init art downloader
        """
        self.__albums_queue = []
        self.__albums_history = []
        self.__in_albums_download = False
        self.__cache_artists_running = False

    def cache_album_art(self, album_id):
        """
            Download album artwork
            @param album id as int
        """
        if album_id in self.__albums_history:
            return
        if get_network_available():
            self.__albums_queue.append(album_id)
            if not self.__in_albums_download:
                t = Thread(target=self.__cache_albums_art)
                t.daemon = True
                t.start()

    def cache_artists_info(self):
        """
            Cache info for all artists
        """
        if self.__cache_artists_running:
            return
        self.__cache_artists_running = True
        t = Thread(target=self.__cache_artists_info)
        t.daemon = True
        t.start()

    def get_google_arts(self, search):
        """
            Get arts on duck image corresponding to search
            @param search words as string
            @return [urls as string]
        """
        data = None
        urls = []

        if not get_network_available():
            return []

        cs_api_key = Lp().settings.get_value("cs-api-key").get_string()

        try:
            f = Lio.File.new_for_uri("https://www.googleapis.com/"
                                     "customsearch/v1?key=%s&cx=%s"
                                     "&q=%s&searchType=image" %
                                     (cs_api_key,
                                      GOOGLE_API_ID,
                                      GLib.uri_escape_string(search,
                                                             "",
                                                             False)))

            (status, data, tag) = f.load_contents()
            if status:
                decode = json.loads(data.decode("utf-8"))
                if decode is None:
                    return urls
                for item in decode["items"]:
                    urls.append(item["link"])
        except Exception as e:
            print(e)
        return urls

#######################
# PROTECTED           #
#######################
    def _get_lastfm_artist_info(self, artist):
        """
            Return lastfm artist information
            @param artist as str
            @return (url as str/None, content as str)
        """
        if Lp().lastfm is not None:
            return Lp().lastfm.get_artist_info(artist)
        else:
            return (None, None)

    def _get_wp_artist_info(self, artist):
        """
            Return wikipedia artist information
            @param artist as str
            @return (url as str/None, content as str)
        """
        if Downloader.Wikipedia is not None:
            wp = Downloader.Wikipedia()
            return wp.get_page_infos(artist)
        else:
            return (None, None)

    def _get_deezer_artist_info(self, artist):
        """
            Return deezer artist information
            @param artist as str
            @return (url as str/None, content as None)
        """
        try:
            artist_formated = GLib.uri_escape_string(
                                artist, None, True).replace(" ", "+")
            s = Lio.File.new_for_uri("https://api.deezer.com/search/artist/?"
                                     "q=%s&output=json&index=0&limit=1&" %
                                     artist_formated)
            (status, data, tag) = s.load_contents()
            if status:
                decode = json.loads(data.decode("utf-8"))
                return (decode["data"][0]["picture_xl"], None)
        except Exception as e:
            debug("Downloader::_get_deezer_artist_artwork(): %s [%s]" %
                  (e, artist))
        return (None, None)

    def _get_spotify_artist_info(self, artist):
        """
            Return spotify artist information
            @param artist as str
            @return (url as str/None, content as None)
        """
        try:
            artist_formated = GLib.uri_escape_string(
                                artist, None, True).replace(" ", "+")
            s = Lio.File.new_for_uri("https://api.spotify.com/v1/search?q=%s"
                                     "&type=artist" % artist_formated)
            (status, data, tag) = s.load_contents()
            if status:
                decode = json.loads(data.decode("utf-8"))
                for item in decode["artists"]["items"]:
                    if item["name"].lower() == artist.lower():
                        return (item["images"][0]["url"], None)
        except Exception as e:
            debug("Downloader::_get_spotify_artist_artwork(): %s [%s]" %
                  (e, artist))
        return (None, None)

    def _get_deezer_album_artwork(self, artist, album):
        """
            Get album artwork from deezer
            @param artist as string
            @param album as string
            @return image as bytes
            @tread safe
        """
        image = None
        try:
            album_formated = GLib.uri_escape_string(album, None, True)
            s = Lio.File.new_for_uri("https://api.deezer.com/search/album/?"
                                     "q=%s&output=json" %
                                     album_formated)
            (status, data, tag) = s.load_contents()
            if status:
                decode = json.loads(data.decode("utf-8"))
                url = None
                for item in decode["data"]:
                    if item["artist"]["name"].lower() == artist.lower():
                        url = item["cover_xl"]
                        break
                if url is not None:
                    s = Lio.File.new_for_uri(url)
                    (status, image, tag) = s.load_contents()
        except Exception as e:
            print("Downloader::__get_deezer_album_artwork: %s" % e)
        return image

    def _get_spotify_album_artwork(self, artist, album):
        """
            Get album artwork from spotify
            @param artist as string
            @param album as string
            @return image as bytes
            @tread safe
        """
        image = None
        artists_spotify_ids = []
        try:
            artist_formated = GLib.uri_escape_string(
                                artist, None, True).replace(" ", "+")
            s = Lio.File.new_for_uri("https://api.spotify.com/v1/search?q=%s"
                                     "&type=artist" % artist_formated)
            (status, data, tag) = s.load_contents()
            if status:
                decode = json.loads(data.decode("utf-8"))
                for item in decode["artists"]["items"]:
                    artists_spotify_ids.append(item["id"])

            for artist_spotify_id in artists_spotify_ids:
                s = Lio.File.new_for_uri("https://api.spotify.com/v1/artists/"
                                         "%s/albums" % artist_spotify_id)
                (status, data, tag) = s.load_contents()
                if status:
                    decode = json.loads(data.decode("utf-8"))
                    url = None
                    for item in decode["items"]:
                        if item["name"] == album:
                            url = item["images"][0]["url"]
                            break

                    if url is not None:
                        s = Lio.File.new_for_uri(url)
                        (status, image, tag) = s.load_contents()
                    break
        except Exception as e:
            print("Downloader::_get_album_art_spotify: %s [%s/%s]" %
                  (e, artist, album))
        return image

    def _get_itunes_album_artwork(self, artist, album):
        """
            Get album artwork from itunes
            @param artist as string
            @param album as string
            @return image as bytes
            @tread safe
        """
        image = None
        try:
            album_formated = GLib.uri_escape_string(
                                album, None, True).replace(" ", "+")
            s = Lio.File.new_for_uri("https://itunes.apple.com/search"
                                     "?entity=album&term=%s" % album_formated)
            (status, data, tag) = s.load_contents()
            if status:
                decode = json.loads(data.decode("utf-8"))
                for item in decode["results"]:
                    if item["artistName"].lower() == artist.lower():
                        url = item["artworkUrl60"].replace("60x60",
                                                           "512x512")
                        s = Lio.File.new_for_uri(url)
                        (status, image, tag) = s.load_contents()
                        break
        except Exception as e:
            print("Downloader::_get_album_art_itunes: %s [%s/%s]" %
                  (e, artist, album))
        return image

    def _get_lastfm_album_artwork(self, artist, album):
        """
            Get album artwork from lastfm
            @param artist as string
            @param album as string
            @return data as bytes
            @tread safe
        """
        image = None
        if Lp().lastfm is not None:
            try:
                last_album = Lp().lastfm.get_album(artist, album)
                url = last_album.get_cover_image(4)
                if url is not None:
                    s = Lio.File.new_for_uri(url)
                    (status, image, tag) = s.load_contents()
            except Exception as e:
                print("Downloader::_get_album_art_lastfm: %s [%s/%s]" %
                      (e, artist, album))
        return image

#######################
# PRIVATE             #
#######################
    def __cache_artists_info(self):
        """
            Cache info for all artists
        """
        # We create cache if needed
        InfoCache.init()
        # Then cache for lastfm/wikipedia/spotify/deezer/...
        for (artist_id, artist, sort) in Lp().artists.get([]):
            if not get_network_available() or\
                    InfoCache.exists(artist):
                continue
            artwork_set = False
            for (api, helper, unused) in InfoCache.WEBSERVICES:
                debug("Downloader::__cache_artists_info(): %s@%s" % (artist,
                                                                     api))
                if helper is None:
                    continue
                try:
                    method = getattr(self, helper)
                    (url, content) = method(artist)
                    if url is not None:
                        s = Lio.File.new_for_uri(url)
                        (status, data, tag) = s.load_contents()
                        if status:
                            artwork_set = True
                            InfoCache.add(artist, content, data, api)
                            debug("Downloader::__cache_artists_info(): %s"
                                  % url)
                        else:
                            InfoCache.add(artist, None, None, api)
                except Exception as e:
                    print("Downloader::__cache_artists_info():", e, artist)
                    InfoCache.add(artist, None, None, api)
            if artwork_set:
                GLib.idle_add(Lp().art.emit, "artist-artwork-changed", artist)
        self.__cache_artists_running = False

    def __cache_albums_art(self):
        """
            Cache albums artwork (from queue)
            @thread safe
        """
        self.__in_albums_download = True
        try:
            while self.__albums_queue:
                album_id = self.__albums_queue.pop()
                album = Lp().albums.get_name(album_id)
                artist_ids = Lp().albums.get_artist_ids(album_id)
                is_compilation = artist_ids and\
                    artist_ids[0] == Type.COMPILATIONS
                if is_compilation:
                    artist = ""
                else:
                    artist = ", ".join(Lp().albums.get_artists(album_id))
                for (api, unused, helper) in InfoCache.WEBSERVICES:
                    if helper is None:
                        continue
                    method = getattr(self, helper)
                    data = method(artist, album)
                    if data is not None:
                        break
                if data is None:
                    self.__albums_history.append(album_id)
                    continue
                Lp().art.save_album_artwork(data, album_id)
        except Exception as e:
            print("Downloader::__cache_albums_art: %s" % e)
        self.__albums_history.append(album_id)
        self.__in_albums_download = False
