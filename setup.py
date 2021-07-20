import pathlib

from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


# This call to setup() does all the work
setup(
    name="django-unoletutils",
    zip_safe=False,
    version="1.5.3",
    description="Django app with utils for Unolet",
    long_description=README,
    long_description_content_type="text/markdown",
    url="http://www.unolet.com/development/#django-unoletutils",
    download_url = 'https://github.com/wilmerm/django-unoletutils.git',
    author="Wilmer Martinez",
    author_email="wilmermorelmartinez@gmail.com",
    license="BSD-3-Clause",
    packages=["unoletutils"], #find_packages(where="src"), # ["tojson"]
    #package_dir={"": "src"},
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=[
        "Django>=2.2",
    ],
)
