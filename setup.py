from setuptools import setup

from pcbscript import __version__


setup(
    name='pcbscript',
    version=__version__,
    description='A library to design PCB layout using an internal DSL.',
    author='Alexander Khlebushchev',
    author_email='mail@fomalhaut.su',
    packages=[
        'pcbscript',
    ],
    entry_points = {
        'console_scripts': ['pcbscript = pcbscript:main']
    },
    zip_safe=False,
    install_requires=open('requirements.txt').readlines(),
)
