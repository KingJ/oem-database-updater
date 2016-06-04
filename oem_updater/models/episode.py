from oem_framework import models

from copy import deepcopy
import logging

log = logging.getLogger(__name__)


class Episode(models.Episode):
    def update(self, item):
        for key, names in item.names.iteritems():
            self.names[key] = names

        self.supplemental = item.supplemental
        self.parameters = item.parameters
        return True

    @classmethod
    def from_season(cls, number, season):
        if not season:
            raise ValueError('Invalid value provided for "season"')

        # Build episode identifiers
        identifiers = deepcopy(season.identifiers)

        if season.collection.source in identifiers:
            del identifiers[season.collection.source]

        # Ensure "names" is in dictionary format
        names = season.names

        if type(names) is not dict:
            # Retrieve target key
            target_key = identifiers[season.collection.target]

            # Convert "names" to dictionary
            names = {target_key: season.names}

        # Build season parameters
        parameters = deepcopy(season.parameters)

        if 'default_season' in parameters:
            del parameters['default_season']

        # Construct season
        episode = Episode(
            season.collection,
            season,

            number,

            identifiers,
            names,

            supplemental=season.supplemental,
            **parameters
        )

        # Add extra details
        if season.episodes and number in season.episodes:
            episode.mappings = season.episodes[number].mappings

        return episode
