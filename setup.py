from setuptools import setup
from subprocess import call

from setuptools.command.install import install

class HunmiscInstall(install):
    def run(self):
        install.run(self)
        cwd = self.install_libbase
        call(['cd {0}/hunmisc/liblinear; bash install.sh'.format(cwd)], shell=True)

setup(
    author='Attila Zseder',
    author_email='zseder@gmail.com',
    name='hunmisc',
    provides=['hunmisc'],
    url='https://github.com/zseder/hunmisc',
    packages=['hunmisc', 'hunmisc.db', 'hunmisc.liblinear', 'hunmisc.xstring'],
    scripts=["hunmisc/liblinear/install.sh", "hunmisc/liblinear/liblinear.patch"],
    package_dir={'': '.'},
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    cmdclass={'install': HunmiscInstall}
)
