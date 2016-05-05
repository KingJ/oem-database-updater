from oem_framework import models

from copy import deepcopy
import logging

log = logging.getLogger(__name__)


class Episode(models.Episode):
    @classmethod
    def from_season(cls, number, season):
        if not season:
            raise ValueError('Invalid value provided for "season"')

        # Build season identifiers
        identifiers = deepcopy(season.identifiers)

        if season.collection.source in identifiers:
            del identifiers[season.collection.source]

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
            season.names,

            supplemental=season.supplemental,
            **parameters
        )

        # Add extra details
        if season.episodes and number in season.episodes:
            episode.mappings = season.episodes[number].mappings

        return episode
