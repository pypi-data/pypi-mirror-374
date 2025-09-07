from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name='bin2tap',
    version='0.5',
    author='Raül Torralba',
    description='Convert a binary file into ZX Spectrum TAP file',
    long_description=README,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'bin2tap=zxbin2tap.cli:main',
            'zxbin2tap=zxbin2tap.cli:main',
        ],
    },
    url = 'https://github.com/rtorralba/bin2tap',
)