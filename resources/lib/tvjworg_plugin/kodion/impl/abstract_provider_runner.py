# -*- coding: utf-8 -*-
"""

    Copyright (C) 2014-2016 ossierivera (plugin.video.tvjworg)
    Copyright (C) 2016-2018 plugin.video.tvjworg

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""


class AbstractProviderRunner(object):
    def __init__(self):
        pass

    def run(self, provider, context=None):
        raise NotImplementedError()
