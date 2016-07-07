import logging
logging.basicConfig(level=logging.DEBUG)

from oem_core.core.plugin import PluginManager
from oem_updater.main import Updater

from argparse import ArgumentParser

log = logging.getLogger(__name__)


class UpdaterCLI(object):
    def parse_args(self):
        parser = ArgumentParser()
        parser.add_argument('base_path')
        parser.add_argument('-d', '--debug', action='store_true', default=False)
        parser.add_argument('-f', '--format', action='append')

        # Discover installed plugins
        PluginManager.discover()

        # Add arguments from updater sources
        for _, source in PluginManager.list_ordered('database-updater'):
            for argument in source.__parameters__:
                if 'name' not in argument:
                    log.warn('Invalid source argument: %r', argument)
                    continue

                parser.add_argument('--%s-%s' % (source.__key__, argument['name']), **argument.get('kwargs', {}))

        return parser.parse_args()

    def run(self, updater=None):
        args = self.parse_args()

        # Setup logging
        logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

        # Setup logger levels
        logging.getLogger("tvdb_api").setLevel(logging.INFO)

        # Construct updater
        if updater is None:
            updater = Updater(formats=args.format)

        # Run updater
        updater.run(**args.__dict__)
