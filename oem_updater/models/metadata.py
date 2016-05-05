from oem_core import models

import os


class Metadata(models.Metadata):
    def update(self, item, hash_key, hash):
        path = os.path.join(self.index.items_path, self.key)

        if not self.index.format.to_path(item, path):
            # Unable to write item to disk
            return False

        # Update metadata
        if not self.hashes or hash_key in self.hashes:
            self.revision += 1

        self.hashes[hash_key] = hash

        self.media = item.media
        return True
