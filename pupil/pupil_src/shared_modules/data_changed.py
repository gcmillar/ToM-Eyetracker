"""
(*)~---------------------------------------------------------------------------
Pupil - eye tracking platform
Copyright (C) 2012-2019 Pupil Labs

Distributed under the terms of the GNU
Lesser General Public License (LGPL v3.0).
See COPYING and COPYING.LESSER for license details.
---------------------------------------------------------------------------~(*)

Contains classes to announce available data between different plugins. Data (e.g.
pupil positions or gaze) is produced by some plugins and consumed by others. Data
consumers need to know if data producers provide new data or if the data producer
changed (e.g. the user switched from Pupil From Recording to Offline Pupil Detection)

This module provides an Announcer that can be used by producers and a Listener that
can be used by consumers.

All announced data has a unique token, so Listeners know if they receive multiple
announcements for the same data and can ignore redundant announcements.
"""
import os
import random
import weakref

from observable import Observable


class Announcer:
    _plugin_role = "producer"

    def __init__(self, topic, rec_dir, plugin):
        """
        Makes it easy to announce data to Listeners over the IPC. Create a new
        Announcer for every topic.

        Args:
            topic: The notification topic the token is used for (e.g.
                "pupil_positions"). This can be an arbitrary string (without
                whitespace and special characters by convention), but Announcers and
                Listeners for the same kind of data must use the same!
            rec_dir: Root directory of recording as in g_pool.rec_dir
            plugin: The plugin that uses the Announcer (usually the one that creates it)
        """
        self._topic = topic
        self._plugin = weakref.ref(plugin)
        # we could use plugin.pretty_class_name but that has usually spaces and file
        # names without spaces are nice!
        self._plugin_name = type(plugin).__name__
        self._rec_dir = rec_dir
        # Instead of initializing the token with None, wo could immediately read the
        # last token from file. However, the data provided by the plugin might not be
        # available right from the beginning (because it takes time to load it). If
        # listeners request the current token before the data is available, we should
        # only answer as soon as the data is available. So it is much better to wait
        # for announce_existing() to be called until we load the token from file.
        self._current_token = None
        plugin.add_observer("on_notify", self._on_notify)

    def announce_new(self):
        """
        Announce that new data is available for the topic. New means that is has
        never been broadcasted before (not even in a previous run of the software).
        """
        token = _create_new_token()
        self._notify_all(token)
        _write_token_to_file(
            token, self._plugin_role, self._topic, self._plugin_name, self._rec_dir
        )

    def announce_existing(self):
        """
        Announce that data for a topic is available, which was already announced
        some time ago (the exact same data).
        Also use this, if you always announce the same data but do not know if you
        already announced it. In case you never announced it, an announce_new() is
        automatically triggered.
        """
        if self._current_token is None:
            read_token = _read_token_from_file(
                self._topic, self._plugin_role, self._plugin_name, self._rec_dir
            )
            if read_token is not None:
                self._current_token = read_token
            else:
                self.announce_new()
                return
        self._notify_all(self._current_token)

    def _notify_all(self, token):
        self._plugin().notify_all(
            {
                "subject": "data_changed.{}.announce_token".format(self._topic),
                "token": token,
            }
        )

    def _on_notify(self, notification):
        if (
            notification["subject"]
            == "data_changed.{}.request_token".format(self._topic)
            and self._current_token is not None
        ):
            self.announce_existing()


class Listener(Observable):
    _plugin_role = "consumer"

    def __init__(self, topic, rec_dir, plugin):
        """
        Listens for data of a specific topic on the IPC. Create a new Listener for
        every topic.

        Args:
            topic: The notification topic the token is used for (e.g.
                "pupil_positions"). This can be an arbitrary string (without
                whitespace and special characters by convention), but Announcers and
                Listeners for the same kind of data must use the same!
            rec_dir: Root directory of recording as in g_pool.rec_dir
            plugin: The plugin that uses the Announcer (usually the one that creates it)
        """
        self._topic = topic
        self._plugin = weakref.ref(plugin)
        self._plugin_name = type(plugin).__name__
        self._rec_dir = rec_dir
        self._current_token = _read_token_from_file(
            self._topic, self._plugin_role, self._plugin_name, self._rec_dir
        )

        plugin.add_observer("on_notify", self._on_notify)

        # when the listener is started it does not know the current token for the
        # topic, so it is asking for an announcement
        self._request_token()

    def on_data_changed(self):
        """
        Add an observer to this to get notified when new data is announced. This is
        NOT triggered for announcements when the data stayed the same.
        """
        pass

    def _request_token(self):
        self._plugin().notify_all(
            {"subject": "data_changed.{}.request_token".format(self._topic)}
        )

    def _on_notify(self, notification):
        if notification["subject"] == "data_changed.{}.announce_token".format(
            self._topic
        ):
            received_token = notification["token"]
            if received_token != self._current_token and received_token is not None:
                self._current_token = received_token
                _write_token_to_file(
                    self._current_token,
                    self._plugin_role,
                    self._topic,
                    self._plugin_name,
                    self._rec_dir,
                )
                self.on_data_changed()


def _create_new_token():
    """
    Returns: A random string like e.g. "04bfd332"
    """
    return "{:0>8x}".format(random.getrandbits(32))


def _write_token_to_file(token, plugin_role, topic, plugin_name, rec_dir):
    file_path = _get_token_file_path(plugin_role, topic, plugin_name, rec_dir)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # IO Errors will be raised!
    with open(file_path, "w") as f:
        f.write(token)


def _read_token_from_file(topic, plugin_role, plugin_name, rec_dir):
    file_path = _get_token_file_path(plugin_role, topic, plugin_name, rec_dir)
    try:
        with open(file_path, "r") as f:
            token = f.read()
            return token
    except FileNotFoundError:
        return None


def _get_token_file_path(plugin_role, topic, plugin_name, rec_dir):
    file_name = "{}_{}_{}.token".format(topic, plugin_role, plugin_name)
    file_path = os.path.join(rec_dir, "offline_data", "tokens", file_name)
    return file_path
