from oem_core.core.plugin import PluginManager
from oem_updater.models import Database

import logging
import os

log = logging.getLogger(__name__)

DEFAULT_FORMATS = [
    'json',
    'json/pretty',
    'msgpack',

    'minimize+json',
    'minimize+msgpack'
]


class Updater(object):
    def __init__(self, sources, collections=None, formats=None):
        self.collections = collections

        # Discover installed plugins
        PluginManager.discover()

        # Retrieve formats
        self.formats = dict(self._load_plugins(
            'format', formats or DEFAULT_FORMATS
        ))

        # Retrieve sources
        self.sources = dict(self._load_plugins(
            'database-updater', sources,
            construct=False
        ))

    @staticmethod
    def _load_plugins(kind, keys, construct=True):
        if not keys:
            return

        for name in keys:
            cls = PluginManager.get(kind, name)

            if cls is None:
                log.warn('Unable to find plugin: %r', name)
                continue

            if not cls.available:
                log.warn('Plugin %r is not available', name)
                continue

            if construct:
                yield cls.__key__, cls()
            else:
                yield cls.__key__, cls

    def run(self, base_path, **kwargs):
        if not os.path.exists(base_path):
            log.error('Path %r doesn\'t exist', base_path)
            return False

        for _, cls in self.sources.items():
            # Retrieve collections
            collections = cls.__collections__

            # Filter `collections` by provided list
            if self.collections is not None:
                collections = [
                    key for key in collections
                    if key in self.collections
                ]

            # Run updater on each collection
            for source, target in collections:
                # Build collection path
                database_path = os.path.join(
                    base_path,
                    self._build_package_name(source, target),
                    self._build_module_name(source, target)
                )

                # Ensure database exists
                if not os.path.exists(database_path):
                    log.warn('Unknown collection: %r -> %r', source, target)
                    continue

                # Run updater on database for each format
                for fmt in self.formats.itervalues():
                    if fmt.__construct__ is False:
                        continue

                    # Build updater client
                    client = UpdaterClient(fmt)

                    # Build database storage interface
                    storage = PluginManager.get('storage', 'file/database')(
                        self, source, target,
                        path=database_path
                    )

                    storage.initialize(client)

                    # Load database
                    database = Database.load(storage, source, target)

                    # Load database collections
                    database.load_collections([
                        (source, target),
                        (target, source)
                    ])

                    for collection in database.collections.itervalues():
                        # Run updater on collection
                        try:
                            s = cls(collection, **dict([
                                (key, value) for key, value in kwargs.items()
                                if key.startswith(cls.__key__ + '_')
                            ]))

                            if not s.run():
                                return False
                        except Exception as ex:
                            log.warn(
                                'Unable to run updater on %r (format: %r) - %s',
                                database_path, fmt, ex,
                                exc_info=True
                            )
                            return False

                        # Write collection to disk
                        try:
                            collection.write()
                        except Exception as ex:
                            log.warn('Unable to write collection to disk - %s', ex, exc_info=True)
                            return False

        return True

    @staticmethod
    def _build_module_name(source, target):
        return 'oem_database_%s_%s' % (
            source.replace(':', '_'),
            target.replace(':', '_')
        )

    @staticmethod
    def _build_package_name(source, target):
        return 'oem-database-%s-%s' % (
            source.replace(':', '-'),
            target.replace(':', '-')
        )


class UpdaterClient(object):
    def __init__(self, fmt):
        self.provider = UpdaterProvider(fmt)


class UpdaterProvider(object):
    def __init__(self, fmt):
        self.format = fmt


if __name__ == '__main__':
    from oem_framework.core.elapsed import Elapsed
    from oem_updater.cli import UpdaterCLI

    # Run CLI
    cli = UpdaterCLI()
    cli.run()

    # Display call statistics
    for line in Elapsed.format_statistics():
        log.info(line)
