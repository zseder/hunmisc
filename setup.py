from setuptools import setup
from subprocess import call

call(['cd hunmisc/liblinear; bash install.sh'], shell=True)

setup(
    author='Attila Zseder',
    author_email='zseder@gmail.com',
    name='hunmisc',
    provides=['hunmisc'],
    url='https://github.com/zseder/hunmisc',
    packages=['hunmisc', 'hunmisc.db'],
    package_dir={'': '.'},
    include_package_data=True,
    zip_safe=False,
    platforms='any',
)
