from tests.core.mock import MockCollection

from oem_updater.sources.anidb.parser import Parser
from xml.etree import ElementTree
import os

BASE_DIR = os.path.dirname(__file__)


def test_cobra_the_animation():
    collection = MockCollection('tvdb', 'anidb')
    nodes = ElementTree.iterparse(os.path.join(BASE_DIR, 'fixtures', 'cobra-the-animation.xml'))

    current = None

    for _, node in nodes:
        if node.tag != 'anime':
            continue

        # Parse item
        item = Parser.parse_item(collection, node)

        if item is None:
            continue

        # Update `current` item
        if current is None:
            current = item
        else:
            current.add(item, 'tvdb')

    # Validate result
    assert current.identifiers == {'tvdb': '137151'}
    assert current.names == set()
    assert set(current.seasons.keys()) == {'0', '1'}

    # - Season 0
    assert current.seasons['0'].identifiers == {'anidb': '5894'}
    assert current.seasons['0'].names == {'Cobra The Animation: The Psychogun'}
    assert set(current.seasons['0'].episodes.keys()) == {'5', '6'}

    assert current.seasons['0'].episodes['5'].identifiers == {'anidb': '6392'}
    assert current.seasons['0'].episodes['5'].names == {'Cobra The Animation: Time Drive'}
    assert current.seasons['0'].episodes['6'].identifiers == {'anidb': '6392'}
    assert current.seasons['0'].episodes['6'].names == {'Cobra The Animation: Time Drive'}

    # - Season 1
    assert current.seasons['1'].identifiers == {'anidb': {'6392', '6494'}}
    assert current.seasons['1'].names == {'Cobra The Animation: Time Drive', 'Cobra The Animation'}
    assert len(current.seasons['1'].episodes.keys()) == 0


def test_gall_force():
    collection = MockCollection('tvdb', 'anidb')
    nodes = ElementTree.iterparse(os.path.join(BASE_DIR, 'fixtures', 'gall-force.xml'))

    current = None

    for _, node in nodes:
        if node.tag != 'anime':
            continue

        # Parse item
        item = Parser.parse_item(collection, node)

        if item is None:
            continue

        # Update `current` item
        if current is None:
            current = item
        else:
            current.add(item, 'tvdb')

    # Validate result
    assert current.identifiers == {'tvdb': '138691'}
    assert current.names == set()
    assert set(current.seasons.keys()) == {'0', '1'}

    # - Season 0
    assert current.seasons['0'].identifiers == {'anidb': '2891'}
    assert current.seasons['0'].names == {'Scramble Wars: Tsuppashire! Genom Trophy Rally'}
    assert set(current.seasons['0'].episodes.keys()) == {'2'}

    # - Season 1
    assert current.seasons['1'].identifiers == {'anidb': '760'}
    assert current.seasons['1'].names == {'Gall Force: Eternal Story'}
    assert set(current.seasons['1'].episodes.keys()) == set(str(x) for x in xrange(2, 14))

    assert current.seasons['1'].episodes['5'].identifiers == {'anidb': '2115'}
    assert current.seasons['1'].episodes['5'].names == {'Gall Force: Chikyuu Shou'}
