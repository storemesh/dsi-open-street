import os
from setuptools import find_packages, setup

package = "dsi_walking_map"

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='dsi-walking-map',
    version='0.1.0',
    packages=find_packages(where="src"),
    package_dir={"": "src"},

    url='https://github.com/storemesh/dsi-open-street/invitations', 
    author='DigitalStoreMesh Co.,Ltd',
    author_email='contact@storemesh.com',
    
    description='A library to create and visualize walkable city maps from OpenStreetMap data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT License',
    
    include_package_data=True,
    package_data={
        package: ['assets/*.png'],
    },
    
    install_requires=[
        "osmnx",
        "networkx",
        "matplotlib",
        "pandas",
        "geopandas",
        "shapely",
        "Pillow"
    ],
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    python_requires='>=3.8',
)