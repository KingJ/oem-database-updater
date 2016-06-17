from setuptools import setup


setup(
    name='oem-updater',
    version='1.0.0',

    author="Dean Gardiner",
    author_email="me@dgardiner.net",

    install_requires=[
        'appdirs>=1.4.0',
        'msgpack-python>=0.4.7',

        'git+git://github.com/fuzeman/anidb.py.git#egg=anidb.py',
        'git+git://github.com/fuzeman/tvdb_api.git#egg=tvdb_api'
    ]
)
