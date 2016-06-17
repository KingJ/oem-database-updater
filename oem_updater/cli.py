from oem_updater.main import Updater
from oem_updater.sources import SOURCES

from argparse import ArgumentParser
import logging

log = logging.getLogger(__name__)


class UpdaterCLI(object):
    def parse_args(self):
        parser = ArgumentParser()
        parser.add_argument('base_path')
        parser.add_argument('-d', '--debug', action='store_true', default=False)
        parser.add_argument('-f', '--format', action='append')

        # Add arguments from sources
        for source in SOURCES.itervalues():
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
