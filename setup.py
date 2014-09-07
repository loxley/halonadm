from setuptools import setup, find_packages
import sys
import os

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

if sys.version_info < (3, 0):
    install_requires = "suds"
else:
    install_requires = "suds-jurko"

setup(name='halonadm',
      version='1.0.0',
      description='Manage Halon SP servers easily',
      long_description=(read('README.rst')),
      url='https://github.com/loxley/halonadm.git/',
      author='Johan Svensson',
      author_email='johan@loxley.se',
      license='GPLv2',
      packages=find_packages(),
      package_data={
          'halonadm': ['halonadm.conf'],
      },
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'halonadm = halonadm.halonadm:main',
          ],
      },
      install_requires=install_requires,
      classifiers=[
          'Environment :: Console',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ])
