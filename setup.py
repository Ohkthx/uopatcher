from setuptools import setup

setup(
    name='uopatcher',
    version='1.0',
    python_requires='>=3.9.1',
    packages=['uopatcher'],
    package_dir={'': 'uopatcher'},
    url='https://github.com/Ohkthx/uopatcher',
    license='GNU General Public License v3.0',
    author='Ohkthx',
    author_email='',
    description='Ultima Online Manifest Patcher',
    install_requires=['requests'],
)
