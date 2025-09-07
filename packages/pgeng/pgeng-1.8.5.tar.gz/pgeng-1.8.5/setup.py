import setuptools
from pathlib import Path

path = Path(__file__).parent.resolve()

def read(rel_path):
	with open(path.joinpath(rel_path)) as file:
		return file.read()

def get_version(rel_path):
	for line in read(rel_path).splitlines():
		if line.startswith('__version__'):
			delim = '"' if '"' in line else "'"
			return line.split(delim)[1]
	raise RuntimeError('Unable to find version string')

with open(path.joinpath('README.md'), encoding='utf-8') as f:
	long_description = f.read()

packages = []
for file in sorted(path.rglob('*')):
	if file.name == '__init__.py':
		names = file.parts[file.parts.index(path.name) + 1:-1]
		packages.append('.'.join(names))

install_requires = read('requirements.txt').splitlines()

setuptools.setup(
	name='pgeng',
	version=get_version('pgeng/__init__.py'),
	author='Qamynn',
	description='Useful functions and classes for PyGame',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/Qamynn/pgeng',
	license='MIT',
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
	],
	packages=packages,
	include_package_data=True,
	install_requires=install_requires,
	python_requires='>=3.6',
)
