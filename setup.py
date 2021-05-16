from setuptools import setup

setup(
   name='ZlochTeamFactory_Website',
   version='1.0',
   description='Using flask to create the ZlochTeamFactor\'s website',
   author='Baptiste Zloch',
   author_email='baptiste.zloch@epfedu.fr',
   packages=['ZlochTeamFactory_Website'],  #same as name
   install_requires=['wheel', 'bar', 'greek'], #external packages as dependencies
)