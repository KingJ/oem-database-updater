from oem_core.models import Item
from oem_core.models.episode import Episode, EpisodeMapping
from oem_core.models.season import Season, SeasonMapping
from oem_updater.core.elapsed import Elapsed
from oem_updater.core.helpers import try_convert

import logging
import re

log = logging.getLogger(__name__)


class Parser(object):
    __version__ = 0x00

    @classmethod
    @Elapsed.track
    def parse_item(cls, collection, node):
        # Retrieve AniDb identifier
        anidb_id = node.attrib.get('anidbid').split(',')

        if len(anidb_id) == 1:
            anidb_id = anidb_id[0]
        elif len(anidb_id) < 1:
            anidb_id = None

        # Construct item
        item = Item.construct(
            collection=collection,
            media=cls.get_media(collection),

            identifiers={
                'anidb': anidb_id
            },

            names={node.find('name').text},
            default_season=node.attrib.get('defaulttvdbseason'),
            episode_offset=node.attrib.get('episodeoffset')
        )

        imdb_id = node.attrib.get('imdbid')
        tvdb_id = node.attrib.get('tvdbid')
        mappings = list(node.findall('mapping-list//mapping'))
        supplemental = node.find('supplemental-info')

        # Add target identifiers
        if collection.source == 'imdb' or collection.target == 'imdb':
            if imdb_id and imdb_id.startswith('tt'):
                item.identifiers['imdb'] = imdb_id.split(',')
            else:
                # Invalid item
                return None
        elif collection.source == 'tvdb' or collection.target == 'tvdb':
            if imdb_id:
                # log.debug('Ignoring item %r, IMDB identifier available', anidb_id)
                return None

            if tvdb_id and try_convert(tvdb_id, int) is not None:
                item.identifiers['tvdb'] = tvdb_id.split(',')
            else:
                # Invalid item
                return None
        else:
            raise ValueError('Unknown service for: %r' % collection)

        for service, keys in item.identifiers.items():
            if type(keys) is not list:
                continue

            # Filter out "unknown" identifiers
            item.identifiers[service] = [
                key for key in item.identifiers[service]
                if key != 'unknown'
            ]

            # Collapse lists with only 1 key
            if len(keys) < 2:
                item.identifiers[service] = keys[0]

        if item.media == 'show':
            # Parse mappings
            if not cls.parse_mappings(collection, item, mappings):
                return None

        # Add supplemental
        if supplemental is not None:
            item.supplemental = {}

            # TODO store all supplemental nodes
            for key in ['studio']:
                node = supplemental.find(key)

                if node is not None:
                    item.supplemental[key] = node.text

        return item

    @classmethod
    def get_media(cls, collection):
        key = (collection.source, collection.target)

        if key in [('anidb', 'tvdb'), ('tvdb', 'anidb')]:
            return 'show'

        if key in [('anidb', 'imdb'), ('imdb', 'anidb')]:
            return 'movie'

        raise Exception('Unknown collection media: %r' % collection)

    @classmethod
    def parse_mappings(cls, collection, item, mappings):
        if not mappings:
            return True

        error = False

        for mapping in mappings:
            source_season = mapping.attrib.get(collection.source + 'season')
            target_season = mapping.attrib.get(collection.target + 'season')

            # Ensure season exists
            if source_season not in item.seasons:
                # Construct season
                item.seasons[source_season] = Season(collection, item, source_season)

            # Parse mapping
            if mapping.text:
                error |= not cls.parse_mappings_episode(collection, item, mapping, (source_season, target_season))
            else:
                error |= not cls.parse_mappings_season(collection, item, mapping, (source_season, target_season))

        return not error

    @classmethod
    def parse_mappings_episode(cls, collection, item, mapping, (source_season, target_season)):
        episodes = list(cls.parse_episodes(collection, mapping.text))

        if not episodes:
            return False

        # Construct episodes
        for source_episode, target_episode in episodes:
            if source_episode not in item.seasons[source_season].episodes:
                # Construct episode
                item.seasons[source_season].episodes[source_episode] = Episode(
                    collection,
                    item.seasons[source_season],

                    number=source_episode
                )

            # Construct episode
            item.seasons[source_season].episodes[source_episode].mappings.append(
                EpisodeMapping(
                    collection,
                    item.seasons[source_season].episodes[source_episode],

                    season=target_season,
                    number=target_episode
                )
            )

        return True

    @classmethod
    def parse_mappings_season(cls, collection, item, mapping, (source_season, target_season)):
        # TODO reverse season mapping if `collection.source` != "anidb"

        item.seasons[source_season].mappings.append(
            SeasonMapping(
                collection, target_season,

                start=mapping.attrib.get('start'),
                end=mapping.attrib.get('end'),

                offset=mapping.attrib.get('offset')
            )
        )

        return True

    @classmethod
    def parse_episodes(cls, collection, value):
        episodes = [
            tuple(episode.split('-'))
            for episode in re.split(r"[;:]", value)
            if episode
        ]

        for item in episodes:
            if len(item) != 2:
                continue

            num_anidb, num_other = item

            # Select source + target numbers
            if collection.source == 'anidb':
                num_source, num_target = num_anidb, num_other
            else:
                num_source, num_target = num_other, num_anidb

            # Ensure source number is defined
            if num_source == '0':
                continue

            # Yield item to iterator
            yield num_source, num_target
