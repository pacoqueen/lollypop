# Lollypop music player

![Lollypop logo](https://raw.githubusercontent.com/pacoqueen/lollypop/master/data/icons/hicolor/256x256/apps/org.gnome.Lollypop.png)

Lollypop is a beautiful GNOME music playing application. It's like [GNOME Music](https://wiki.gnome.org/Apps/Music) on steroids.

Forked from [mainstream repository](https://gitlab.gnome.org/World/lollypop) {[`commit e9e8eda9c635e4afe756e07aa5e28ac5eba30470`](https://gitlab.gnome.org/World/lollypop/commit/9e8eda9c635e4afe756e07aa5e28ac5eba30470)} just to add a couple _must-have_ for me:

0. (_bonus track_) Remove donation banner.

1. Open containing directory of a song or album.

2. Jump to currently playing artist.

3. Back button in lyrics view.

You —probably— don't want to install this version. Go to the [official and most updated](https://gitlab.gnome.org/World/lollypop) one instead.

> All credits to Cédric Bellegarde for an excellent piece of software.

---

* For users: [Lollypop in GNOME wiki](https://wiki.gnome.org/Apps/Lollypop).

* For packagers: You need to provide [Lollypop-Portal](https://gitlab.gnome.org/gnumdk/lollypop-portal). Is where Lollypop interact with other applications to set covers, tag tracks, etc. via dbus. If you clone _this_ repository, pull the submodule too instead the original one.

* For translators: [Contribute online](https://hosted.weblate.org/projects/gnumdk/lollypop). Download [translations from gitlab repository](https://gitlab.gnome.org/gnumdk/lollypop-po). Included as a submodule too.

It provides:

- MP3/4, ogg and FLAC.
- Genre/cover browsing
- Genre/artist/cover browsing
- Search
- Main playlist (called queue in other apps)
- Party mode
- Replay gain
- Cover art downloader
- Context artist view
- MTP sync
- Fullscreen view
- Radios support
- Last.fm support
- Auto install codecs
- HiDPI support
- TuneIn support

## Depends on

- `gtk3 >= 3.20`
- `gobject-introspection`
- `appstream-glib`
- `gir1.2-gstreamer-1.0 (Debian)`
- `python3`
- `meson >= 0.40`
- `ninja`
- `totem-plparser`
- `python-cairo`
- `python-gobject`
- `python-sqlite`
- `python-pylast >= 1.0`

## Building from git

```bash
$ git clone https://gitlab.gnome.org/World/lollypop.git
$ cd lollypop
$ meson builddir --prefix=/usr
# sudo ninja -C builddir install
```

In case you want the integration with [Last.fm](http://last.fm) to work you need to install `pylast`

```bash
# apt-get install python3-pip
# pip3 install pylast
```

### On Debian (Jessie)

```bash
$ git clone https://gitlab.gnome.org/World/lollypop.git
$ cd lollypop
# apt-get install meson libglib2.0-dev yelp-tools libgirepository1.0-dev libgtk-3-dev
$ meson builddir --prefix=/usr
# sudo ninja -C builddir install
```

### On Fedora

```bash
$ git clone https://gitlab.gnome.org/World/lollypop.git
$ cd lollypop
# sudo dnf install meson glib2-devel yelp-tools gtk3-devel gobject-introspection-devel python3
$ meson builddir --prefix=/usr
# sudo ninja -C builddir install
```
