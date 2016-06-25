from oem_updater.models import Show
from tests.core.mock import MockCollection, MockFormat, MockStorage


def test_hex():
    collection = MockCollection(
        'tvdb', 'anidb',
        MockStorage(MockFormat(supports_binary=False))
    )

    current = Show(
        collection,

        identifiers={
            'anidb': 522,
            'tvdb': 103691
        },
        names=set([
            'Juusenki L-Gaim'
        ]),

        default_season='1'
    )

    assert current.hash() == '3ebb6975a11352bac5de4217f9dd553d'


def test_binary():
    collection = MockCollection(
        'tvdb', 'anidb',
        MockStorage(MockFormat(supports_binary=True))
    )

    current = Show(
        collection,

        identifiers={
            'anidb': 522,
            'tvdb': 103691
        },
        names=set([
            'Juusenki L-Gaim'
        ]),

        default_season='1'
    )

    assert current.hash() == b'>\xbbiu\xa1\x13R\xba\xc5\xdeB\x17\xf9\xddU='
