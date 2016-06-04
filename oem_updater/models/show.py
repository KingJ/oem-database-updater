from oem_framework import models
from oem_framework.models.core import ModelRegistry

import logging

log = logging.getLogger(__name__)


class Show(models.Show):
    def add(self, item, service):
        # Ensure item is different
        if self == item:
            return True

        if self.matches_identifiers(item.identifiers):
            return self.update(item)

        # Demote current show to a season
        if self.collection.target in self.identifiers and not self.demote(service):
            return False

        # Add seasons to current show
        season_numbers = set([
            s.number for s in item.seasons.itervalues()
        ] + [
            item.parameters.get('default_season')
        ])

        error = False

        for season_num in season_numbers:
            # Construct season
            season = ModelRegistry['Season'].from_show(self, season_num, item)

            if season_num in self.seasons:
                # Update existing season
                if not self.seasons[season_num].add(season, service):
                    error = True

                continue

            # Store new season
            self.seasons[season_num] = season

        return not error

    def update(self, item):
        for key, names in item.names.iteritems():
            self.names[key] = names

        self.supplemental = item.supplemental
        self.parameters = item.parameters
        return True

    def clear(self):
        if self.collection.target not in self.identifiers:
            return False

        # Reset attributes
        self.names = {}

        self.supplemental = {}
        self.parameters = {}

        # Remove target collection identifier
        del self.identifiers[self.collection.target]
        return True

    def demote(self, service):
        # Update existing seasons
        for season_num, season in self.seasons.items():
            self.seasons[season_num].update_attributes(
                identifiers=self.identifiers,
                names=self.names,

                supplemental=self.supplemental,
                parameters=self.parameters
            )

        # Retrieve season number
        season_num = self.parameters.get('default_season')

        if season_num is None:
            raise NotImplementedError

        # Create season from current show
        season = ModelRegistry['Season'].from_show(self, season_num, self)

        if season_num in self.seasons:
            self.seasons[season_num].add(season, service)
        else:
            self.seasons[season_num] = season

        # Clear show
        return self.clear()
