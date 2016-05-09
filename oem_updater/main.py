import logging
logging.basicConfig(level=logging.DEBUG)

from oem_core.core.plugin import PluginManager
from oem_updater.models import Database
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
    'json/pretty',
    'msgpack',

    'minimize+json',
    'minimize+msgpack'
]

DEFAULT_SOURCES = [
    'anidb'
]


class Updater(object):
    def __init__(self, collections=DEFAULT_COLLECTIONS, formats=None, sources=DEFAULT_SOURCES):
        self.collections = collections

        # Discover installed plugins
        PluginManager.discover()

        # Retrieve formats
        self.formats = dict(self._load_formats(formats))

        # Retrieve references to sources
        self.sources = dict([
            (key, SOURCES[key])
            for key in sources
        ])

    @staticmethod
    def _load_formats(formats):
        for name in (formats or DEFAULT_FORMATS):
            cls = PluginManager.get('format', name)

            if cls is None:
                log.warn('Unable to find plugin: %r', name)
                continue

            if not cls.available:
                log.warn('Plugin %r is not available', name)
                continue

            yield cls.__key__, cls()

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
                'oem-database-%s-%s' % (source, target),
                'oem_database_%s_%s' % (source, target)
            )

            # Ensure database exists
            if not os.path.exists(database_path):
                log.warn('Unknown collection: %r -> %r', source, target)
                continue

            # Run updater on database for each format
            for fmt in self.formats.itervalues():
                if fmt.__construct__ is False:
                    continue

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
    from oem_framework.core.elapsed import Elapsed
    from oem_updater.cli import UpdaterCLI

    # Run CLI
    cli = UpdaterCLI()
    cli.run()

    # Display call statistics
    for line in Elapsed.format_statistics():
        print line
