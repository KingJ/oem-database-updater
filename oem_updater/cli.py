from oem_core.core.plugin import PluginManager
from oem_updater.main import Updater

from argparse import ArgumentParser
import logging

log = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)


class UpdaterCLI(object):
    def parse_args(self):
        parser = ArgumentParser()
        parser.add_argument('base_path')
        parser.add_argument('-d', '--debug', action='store_true', default=False)
        parser.add_argument('-c', '--collection', action='append')
        parser.add_argument('-f', '--format', action='append')
        parser.add_argument('-s', '--source', action='append', required=True)

        # Discover installed plugins
        PluginManager.discover()

        # Add arguments from updater sources
        for _, source in PluginManager.list_ordered('database-updater'):
            for argument in source.__parameters__:
                if 'name' not in argument:
                    log.warn('Invalid source argument: %r', argument)
                    continue

                parser.add_argument('--%s-%s' % (source.__key__, argument['name']), **argument.get('kwargs', {}))

        # Parse command line arguments
        return parser.parse_args()

    def run(self, updater=None):
        args = self.parse_args()

        # Setup logging
        logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

        # Setup logger levels
        logging.getLogger("tvdb_api").setLevel(logging.INFO)

        # Construct updater
        if updater is None:
            updater = Updater(
                args.source,
                collections=self._parse_collections(args.collection),
                formats=args.format
            )

        # Run updater
        updater.run(**args.__dict__)

    @staticmethod
    def _parse_collections(collections):
        if not collections:
            return None

        def iterator():
            for key in collections:
                # Parse key
                fragments = key.split('^')

                if len(fragments) != 2:
                    log.warn('Invalid collection key: %r', key)
                    continue

                yield tuple(fragments)

        return list(iterator())
