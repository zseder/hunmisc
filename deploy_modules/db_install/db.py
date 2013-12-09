"""Installs the EntityDB module"""
from fabric.api import local, lcd, cd, run
import cliqz
import os

def resource_file( name ):
	"""Return a resource file relative to the directory of this script"""
	return os.path.join( os.path.dirname( __file__ ), name )

def install_db():
	path = '/opt/hunmisc'
	cliqz.log_action('Installing Entity DB')
	cliqz.cli.system_package('build-essential', 'python-dev')
	cliqz.cli.python_package('dawg')
	pkg = cliqz.package.gen_definition()
	pkg['strip'] = 0
	with lcd( resource_file( '.' ) ):
		local( 'PACKAGE={} make package'.format( pkg['local'] ) )
	cliqz.package.install( pkg, path )
	with cd(path):
		run('python setup.py install')
	return path
