from oem_framework.plugin import Plugin
import logging

log = logging.getLogger(__name__)


class Source(Plugin):
    __collections__ = []
    __parameters__ = []

    def __init__(self, collection, kwargs):
        self.collection = collection
        self._kwargs = kwargs

    def run(self):
        raise NotImplementedError

    def param(self, name, default=None):
        s_name = '%s_%s' % (self.__key__, name)

        if self._kwargs.get(s_name):
            return self._kwargs[s_name]

        if self._kwargs.get(name):
            return self._kwargs[name]

        return default
