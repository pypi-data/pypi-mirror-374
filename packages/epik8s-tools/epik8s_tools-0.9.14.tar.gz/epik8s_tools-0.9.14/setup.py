
# setup.py
# python3 setup.py sdist bdist_wheel
# python3 -m twine upload dist/*

from setuptools import setup, find_packages
from epik8s_tools import __version__

setup(
    name="epik8s-tools",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,  # Ensure to include files from MANIFEST.in

    entry_points={
        'console_scripts': [
        'epik8s-gen=epik8s_tools.epik8s_gen:main',
        'epik8s-opigen=epik8s_tools.opigen:main_opigen',
        'epik8s-compose=epik8s_tools.epik8s_compose:main_compose',
        'epik8s-run=epik8s_tools.epik8s_run:main_run'
        ],
    },
    install_requires=[
        
        'pyyaml','Jinja2','phoebusgen','jnjrender'
        
        # Add any external dependencies here
    ],
    author="Andrea Michelotti",
    author_email="andrea.michelotti@infn.it",
    description="A set of tools for generating Kubernetes Helm charts for EPICS-based systems.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/yourusername/epik8s-tools",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
