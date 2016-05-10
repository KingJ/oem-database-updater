from oem_core import models
from oem_framework.core.helpers import timestamp_utc

import os


class Metadata(models.Metadata):
    def update(self, item, hash_key, hash):
        if not self.storage.format.to_path(item, self.storage.path):
            # Unable to write item to disk
            return False

        # Update metadata
        if not self.hashes or hash_key in self.hashes:
            now = timestamp_utc()

            # Update timestamps
            if self.created_at is None:
                # Set initial timestamps
                self.created_at = now
                self.updated_at = now
            else:
                self.updated_at = now

        self.hashes[hash_key] = hash

        self.media = item.media
        return True
