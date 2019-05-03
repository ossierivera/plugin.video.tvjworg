# -*- coding: utf-8 -*-
"""

    Copyright (C) 2014-2016 ossierivera (plugin.video.tvjworg)
    Copyright (C) 2016-2018 plugin.video.tvjworg

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""

import re

from .exceptions import KodionException
from . import items
from . import constants


class AbstractProvider(object):
    RESULT_CACHE_TO_DISC = 'cache_to_disc'  # (bool)

    def __init__(self):
        # map for regular expression (path) to method (names)
        self._dict_path = {}

        # register some default paths
        self.register_path(r'^/$', '_internal_root')
        """
        Test each method of this class for the appended attribute '_re_match' by the
        decorator (RegisterProviderPath).
        The '_re_match' attributes describes the path which must match for the decorated method.
        """

        for method_name in dir(self):
            method = getattr(self, method_name)
            if hasattr(method, 'kodion_re_path'):
                self.register_path(method.kodion_re_path, method_name)

    def get_alternative_fanart(self, context):
        return context.get_fanart()

    def register_path(self, re_path, method_name):
        """
        Registers a new method by name (string) for the given regular expression
        :param re_path: regular expression of the path
        :param method_name: name of the method
        :return:
        """
        self._dict_path[re_path] = method_name

    def navigate(self, context):
      
	path = context.get_path()

        for key in self._dict_path:
            re_match = re.search(key, path, re.UNICODE)
            if re_match is not None:
                method_name = self._dict_path.get(key, '')
                method = getattr(self, method_name)
                if method is not None:
                    result = method(context, re_match)
                    if not isinstance(result, tuple):
                        result = result, {}
                    return result

        raise KodionException("Mapping for path '%s' not found" % path)

   

    def on_root(self, context, re_match):
        raise NotImplementedError()

    def _internal_root(self, context, re_match):
        return self.on_root(context, re_match)

    
    
    def handle_exception(self, context, exception_to_handle):
        return True

    def tear_down(self, context):
        pass
