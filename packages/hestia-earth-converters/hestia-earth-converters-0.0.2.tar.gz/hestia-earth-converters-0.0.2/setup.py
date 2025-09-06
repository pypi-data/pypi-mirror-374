import pathlib
from setuptools import find_packages, setup

VERSION = '0.0.2'

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / 'README.md').read_text()

BASE_REQUIRES = (HERE / 'hestia_earth/converters/base/requirements.txt').read_text().splitlines()

EXTRAS_REQUIRES = {
    'SimaPro': (HERE / 'hestia_earth/converters/simapro/requirements.txt').read_text().splitlines()
}

# This call to setup() does all the work
setup(
    name='hestia-earth-converters',
    version=VERSION,
    description="HESTIA's set of file converters",
    long_description=README,
    long_description_content_type='text/markdown',
    url="https://gitlab.com/hestia-earth/hestia-convert-base",
    author='@ToffeeLabs',
    author_email='community@hestia.earth',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.9',
    ],
    packages=find_packages(exclude=['tests', 'scripts']),
    include_package_data=True,
    install_requires=BASE_REQUIRES,
    python_requires='>=3.9',
    extras_require=EXTRAS_REQUIRES,
    scripts=[
        'bin/hestia-convert'
    ]
)
