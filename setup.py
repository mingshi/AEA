from setuptools import find_packages
from setuptools import setup

setup(name='AEA',
      version='0.1.dev',

      package_dir={'': 'src'},
      packages=find_packages('src'),

      install_requires=['tornado==2.4.1',
                        'SQLAlchemy==0.8.0']

)
