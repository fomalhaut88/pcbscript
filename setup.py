from setuptools import setup


with open('README.md') as f:
    long_description = f.read()


setup(
    name='pcbscript',
    version="1.1.0",
    description='A library to design PCB layout using an internal DSL.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Alexander Khlebushchev',
    author_email='alexfomalhaut@gmail.com',
    url="https://github.com/fomalhaut88/pcbscript",
    project_urls={
        "Homepage": "https://github.com/fomalhaut88/pcbscript",
        "Source": "https://github.com/fomalhaut88/pcbscript",
        "Issues": "https://github.com/fomalhaut88/pcbscript/issues",
    },
    license="MIT",
    packages=['pcbscript'],
    entry_points = {
        'console_scripts': ['pcbscript = pcbscript:main']
    },
    zip_safe=False,
    install_requires=[
        'CairoSVG>=2.8',
        'Pillow>=12',
        'svgwrite>=1.4',
    ],
    python_requires=">=3.12",
    keywords="pcb",
)
