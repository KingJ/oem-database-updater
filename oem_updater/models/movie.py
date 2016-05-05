from oem_framework import models

import logging

log = logging.getLogger(__name__)


class Movie(models.Movie):
    def add(self, item, service):
        # Ensure item is different
        if self == item:
            return True

        # TODO manage movie duplicates
        log.warn('Ignored Movie.add(), function not implemented yet')
