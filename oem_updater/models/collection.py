from oem_core import models

import logging

log = logging.getLogger(__name__)


class Collection(models.Collection):
    def write(self):
        # Write indices to disk
        if not self.index.write():
            log.warn('Unable to write index %r to disk', self.index)
            return False

        # Indices written to disk successfully
        return True
