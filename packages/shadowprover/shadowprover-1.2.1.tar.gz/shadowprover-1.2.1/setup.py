#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', "edn_format", "pydantic", "pyparsing", "fuzzywuzzy", "loguru", "colorama"]

test_requirements = [ ]

setup(
    author="Naveen Sundar Govindarajulu",
    author_email='naveensundarg@gmail.com',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
    ],
    #description="Framework for hexperimentation with higher-order modal quantified reasoning and planning",
    entry_points={
        'console_scripts': [
            'shadowprover=shadowprover.cli:main',
        ],
    },
    install_requires=requirements,
    # long_description=readme 
    # long_description_content_type='text/markdown',
        packages=find_packages(include=["shadowprover.fol", "shadowprover.experimental", "shadowprover.syntax", "shadowprover.unifiers", "shadowprover.reasoners", "shadowprover.planner", "shadowprover.inference_systems", "shadowprover.pyarmor_runtime_000000"]) , # Automatically find packages

    include_package_data=True,
    keywords='shadowprover',
    name='shadowprover',
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/naveensundarg/py_laser',
    version='1.2.1',
    zip_safe=False,
    
    
)

