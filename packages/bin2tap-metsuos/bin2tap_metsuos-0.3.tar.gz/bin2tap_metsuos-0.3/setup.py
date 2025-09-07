from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name='bin2tap-metsuos',
    version='0.3',
    author='Raül Torralba => Raúl Carrillo aka metsuke',
    description='MetsuOS Version to avoid skooltools bin2tap dep conflict. Convert a binary file into ZX Spectrum TAP file',
    long_description=README,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    entry_points='''
        [console_scripts]
        bin2tap=bin2tap_metsuos.cli:main
        bin2tap_metsuos=bin2tap_metsuos.cli:main
        bin2tap_zxsgm=bin2tap_metsuos.cli:main
    ''',
    url = 'https://github.com/metsuke/bin2tap-py-metsuos',
)