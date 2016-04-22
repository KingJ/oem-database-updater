from oem_core.models.collection import Collection
from oem_core.models.database import Database
from oem_core.models.format import Format
from oem_updater.sources import SOURCES

import logging
import os

log = logging.getLogger(__name__)

DEFAULT_COLLECTIONS = [
    ('anidb', 'tvdb'),
    ('anidb', 'imdb')
]

DEFAULT_FORMATS = [
    'json',
    # 'mpack',
    # 'min.json',
    # 'min.mpack'
]

DEFAULT_SOURCES = [
    'anidb'
]


class Updater(object):
    def __init__(self, collections=DEFAULT_COLLECTIONS, formats=DEFAULT_FORMATS, sources=DEFAULT_SOURCES):
        self.collections = collections

        # Parse format extensions
        self.formats = [
            Format.from_extension(fmt)
            for fmt in formats
        ]

        # Retrieve references to sources
        self.sources = dict([
            (key, SOURCES[key])
            for key in sources
        ])

    def run(self, base_path, **kwargs):
        if not os.path.exists(base_path):
            log.error('Path %r doesn\'t exist', base_path)
            return False

        for source, target in self.collections:
            # Retrieve source class
            cls = self.sources.get(source)

            if not cls:
                log.warn('Unknown source: %r', source)
                continue

            # Build collection path
            database_path = os.path.join(
                base_path,
                'oem-%s-%s' % (source, target),
                'oem_%s_%s' % (source, target)
            )

            # Ensure database exists
            if not os.path.exists(database_path):
                log.warn('Unknown collection: %r -> %r', source, target)
                continue

            # Run updater on database for each format
            for fmt in self.formats:
                # Load database
                database = Database.load(database_path, fmt, source, target)

                # Load database collections
                database.load_collections([
                    (source, target),
                    (target, source)
                ])

                for collection in database.collections.itervalues():
                    # Run updater on collection
                    try:
                        s = cls(collection, **kwargs)
                        s.run()
                    except Exception, ex:
                        log.warn('Unable to run updater on %r (format: %r) - %s', database_path, fmt, ex, exc_info=True)
                        return False

                    # Write collection to disk
                    try:
                        collection.write()
                    except Exception, ex:
                        log.warn('Unable to write collection to disk - %s', ex, exc_info=True)
                        return False

        return True


if __name__ == '__main__':
    from oem_updater.core.elapsed import Elapsed
    from oem_updater.cli import UpdaterCLI

    # Run CLI
    cli = UpdaterCLI()
    cli.run()

    # Display call statistics
    for line in Elapsed.format_statistics():
        print line
