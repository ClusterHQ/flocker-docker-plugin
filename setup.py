# Copyright ClusterHQ Limited. See LICENSE file for details.

"""
Start the Flocker Docker Plugin
"""
from setuptools import setup

with open("README.md") as readme:
    description = readme.read()

    setup(
        name="FlockerDockerPlugin",
        version="0.1",
        author="ClusterHQ Labs",
        author_email="labs@clusterhq.com",
        url="https://clusterhq.com/",
        long_description=description,
        license="Apache License, Version 2.0",
        classifiers=[
            "License :: OSI Approved :: Apache Software License",
        ],
        install_requires=[
            "pyasn1>=0.1",
            "Twisted>=14",
            "PyYAML>=3",
            "treq>=14",
        ],
        packages=[
            "flockerdockerplugin",
            "txflocker",
        ],
        package_data={
            "flockerdockerplugin": ["*.tac"],
        },
        scripts=[
            "bin/flocker-docker-plugin",
        ]
    )
