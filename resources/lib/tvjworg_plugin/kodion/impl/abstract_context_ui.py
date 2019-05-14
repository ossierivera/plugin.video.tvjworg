# -*- coding: utf-8 -*-
"""

    Copyright (C) 2014-2016 ossierivera (plugin.video.tvjworg)
    Copyright (C) 2016-2018 plugin.video.tvjworg

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""


class AbstractContextUI(object):
    def __init__(self):
        pass

    def create_progress_dialog(self, heading, text=None, background=False):
        raise NotImplementedError()

    def get_skin_id(self):
        raise NotImplementedError()

    def on_keyboard_input(self, title, default='', hidden=False):
        raise NotImplementedError()

    def on_numeric_input(self, title, default=''):
        raise NotImplementedError()

    def on_yes_no_input(self, title, text):
        raise NotImplementedError()

    def on_ok(self, title, text):
        raise NotImplementedError()

    def on_remove_content(self, content_name):
        raise NotImplementedError()

    def on_select(self, title, items=None):
        raise NotImplementedError()

    def open_settings(self):
        raise NotImplementedError()

    def show_notification(self, message, header='', image_uri='', time_milliseconds=5000):
        raise NotImplementedError()

