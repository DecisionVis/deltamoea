"""
setup.py: Loosely cribbed from the example in pypa

https://github.com/pypa/sampleproject/blob/master/setup.py
"""
from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.rst"), encoding='utf-8') as fp:
    long_description = fp.read()

setup(
    name="deltamoea",
    version='1.5',
    description='Multi-Objective Grid Search Algorithm',
    long_description=long_description,
    url='https://github.com/DecisionVis/deltamoea',
    author="DecisionVis LLC",
    author_email="team@decisionvis.com",
    license="BSD",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
    ],
    keywords=[
        "δMOEA", "MOEA", "grid search", "optimization", "multi-objective"],
    packages=['deltamoea'],
)

