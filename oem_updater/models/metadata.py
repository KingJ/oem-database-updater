from oem_core import models
from oem_framework.core.helpers import timestamp_utc

import os


class Metadata(models.Metadata):
    def update(self, item, hash_key, hash):
        path = os.path.join(self.index.items_path, self.key)

        if not self.index.format.to_path(item, path):
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
