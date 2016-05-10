from oem_core import models


class Index(models.Index):
    def create(self, key):
        return self.storage.create(self.collection, key)

    def write(self):
        # Write index to path
        return self.storage.format.to_path(
            self, self.storage.path
        )
