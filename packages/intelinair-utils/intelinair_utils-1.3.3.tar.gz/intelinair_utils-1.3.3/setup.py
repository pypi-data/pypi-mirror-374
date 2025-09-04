import setuptools

with open('src/intelinair_utils/__version__.py') as version_file:
    exec(version_file.read())

with open("requirements.txt", "r") as requirements_file:
    requirements = requirements_file.read().splitlines()

required = [req for req in requirements if not req.startswith('shapely')]

extras = {
    'shapely': ['shapely~=2.0']
}

setuptools.setup(
    name='intelinair_utils',
    version=globals()['__version__'],
    package_dir={'': 'src'},
    packages=setuptools.find_namespace_packages(where='src'),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=required,
    extras_require=extras
)
