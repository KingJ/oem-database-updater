from oem_updater.main import Updater

from argparse import ArgumentParser
import logging

log = logging.getLogger(__name__)


class UpdaterCLI(object):
    def __init__(self, updater=None):
        self.updater = updater or Updater()

    def parse_args(self):
        parser = ArgumentParser()
        parser.add_argument('base_path')
        parser.add_argument('-d', '--debug', action='store_true', default=False)

        # Add arguments from sources
        for source in self.updater.sources.itervalues():
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

        # Run updater
        if updater is None:
            updater = Updater()

        updater.run(**args.__dict__)
