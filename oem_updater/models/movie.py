from oem_framework import models
from oem_framework.core.helpers import try_convert
from oem_framework.models.core import ModelRegistry

import logging
import six

log = logging.getLogger(__name__)


class Movie(models.Movie):
    def add(self, item, service):
        # Ensure item is different
        if self == item:
            return True

        if self.matches_identifiers(item.identifiers):
            return self.update(item)

        # Demote current movie to a part
        if self.collection.target in self.identifiers and not self.demote(service):
            return False

        # Retrieve part number
        i_part_num = item.parameters.get('episode_offset')

        if i_part_num is not None:
            i_part_num = str(try_convert(i_part_num, int, 0) + 1)
        else:
            i_part_num = '1'

        # Add parts to current movie
        part_numbers = set([
            s.number for s in six.itervalues(item.parts)
        ] + [
            i_part_num
        ])

        error = False

        for part_num in part_numbers:
            # Construct part
            part = ModelRegistry['Part'].from_movie(self, part_num, item)

            if part_num in self.parts:
                # Update existing part
                if not self.parts[part_num].add(part, service):
                    error = True

                continue

            # Store new part
            self.parts[part_num] = part

        return not error

    def update(self, item):
        for key, names in six.iteritems(item.names):
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
        # Update existing parts
        for part_num, part in self.parts.items():
            self.parts[part_num].update_attributes(
                identifiers=self.identifiers,
                names=self.names,

                supplemental=self.supplemental,
                parameters=self.parameters
            )

        # Retrieve part number
        part_num = self.parameters.get('episode_offset')

        if part_num is not None:
            part_num = str(try_convert(part_num, int, 0) + 1)
        else:
            part_num = '1'

        # Create part from current show
        part = ModelRegistry['Part'].from_movie(self, part_num, self)

        if part_num in self.parts:
            self.parts[part_num].add(part, service)
        else:
            self.parts[part_num] = part

        # Clear show
        return self.clear()
