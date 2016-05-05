from oem_core import models
from oem_updater.models.metadata import Metadata


class Index(models.Index):
    def write(self):
        # Write index to path
        return self.format.to_path(
            self, self.path
        )
