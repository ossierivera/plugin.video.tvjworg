# -*- coding: utf-8 -*-
"""

    Copyright (C) 2014-2016 ossierivera (plugin.video.tvjworg)
    Copyright (C) 2016-2018 plugin.video.tvjworg

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""

from tvjworg_plugin.kodion import runner
from tvjworg_plugin import tvjworg

__provider__ = tvjworg.Provider()
runner.run(__provider__)
