from setuptools import setup
from mrtools import version


setup(
    author='Attila Zseder',
    author_email='zseder@gmail.com',
    name='hunmisc',
    version=version,
    provides=['hunmisc'],
    url='https://github.com/zseder/hunmisc',
    packages=['hunmisc', 'hunmisc.db'],
    package_dir={'': '.'},
    include_package_data=True,
    zip_safe=False,
    platforms='any',
)
