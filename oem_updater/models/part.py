from oem_framework import models

from copy import deepcopy
import logging
import six

log = logging.getLogger(__name__)


class Part(models.Part):
    def add(self, item, service):
        pass

    def update(self, item):
        for key, names in six.iteritems(item.names):
            self.names[key] = names

        self.supplemental = item.supplemental
        self.parameters = item.parameters
        return True

    @classmethod
    def from_movie(cls, movie, number, item):
        if not item:
            raise ValueError('Invalid value provided for "season"')

        # Build part identifiers
        identifiers = deepcopy(item.identifiers)

        if item.collection.source in identifiers:
            del identifiers[item.collection.source]

        # Ensure "names" is in dictionary format
        names = item.names

        if type(names) is not dict:
            # Retrieve target key
            target_key = identifiers[item.collection.target]

            # Convert "names" to dictionary
            names = {target_key: item.names}

        # Build part parameters
        parameters = deepcopy(item.parameters)

        if 'episode_offset' in parameters:
            del parameters['episode_offset']

        # Construct season
        part = Part(
            item.collection,
            movie,

            number,

            identifiers,
            names,

            supplemental=item.supplemental,
            **parameters
        )

        return part
