import os
from setuptools import setup

# allow setup.py to be run from any path
#os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-unoletutils',
    version = '1.4',
    packages = ['unoletutils'],
    include_package_data=True,
    license = 'BSD License',  # example license
    description = 'Django app with utils for Unolet',
    long_description = 'Django app with utils for Unolet. See more: https://www.unolet.com/development/unoletutils/',
    url='http://www.unolet.com/development/unoletutils/',
    download_url = 'https://github.com/wilmerm/unoletutils.git',
    author = 'Wilmer Martinez',
    author_email = 'wilmermorelmartinez@gmail.com',
    classifiers=[],
)
