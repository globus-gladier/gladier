import os
from setuptools import find_packages, setup

# Single source of truth for version
version_ns = {}
with open(os.path.join("gladier", "version.py")) as f:
    exec(f.read(), version_ns)
version = version_ns['__version__']

with open('README.rst') as f:
    long_description = f.read()

install_requires = []
with open('requirements.txt') as reqs:
    for line in reqs.readlines():
        req = line.strip()
        if not req or req.startswith('#'):
            continue
        install_requires.append(req)

setup(
    name="gladier",
    description="Tooling for rapid deployment of automation tooling.",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/globus-gladier/gladier',
    version=version,
    packages=find_packages(),
    install_requires=install_requires,
    python_requires=">=3.6",
    license='Apache 2.0',
    maintainer='',
    maintainer_email='',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
