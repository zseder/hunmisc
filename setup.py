from setuptools import setup
from subprocess import call

from setuptools.command.install import install

class HunmiscInstall(install):
    def run(self):
        install.run(self)
        cwd = self.install_libbase
        call(['cd {0}/hunmisc/liblinear; bash install.sh'.format(
            cwd)], shell=True)

def my_setup():
    return setup(
        author='Attila Zseder',
        author_email='zseder@gmail.com',
        name='hunmisc',
        provides=['hunmisc'],
        url='https://github.com/zseder/hunmisc',
        packages=[
            'hunmisc', 'hunmisc.db', 'hunmisc.liblinear', 'hunmisc.xstring',
            'hunmisc.spell_checker', 'hunmisc.utils', 'hunmisc.corpustools'],
        package_data={
            "hunmisc": ["liblinear/install.sh", "liblinear/liblinear.patch"]},
        package_dir={'': '.'},
        include_package_data=True,
        zip_safe=False,
        platforms='any',
        install_requires=["DAWG"],
        cmdclass={'install': HunmiscInstall})

if __name__ == "__main__":
    my_setup()
