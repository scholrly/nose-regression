from setuptools import setup
import os

def read(*rnames):
        return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='nose-regression',
    version='1.0',
    author='Edd Purcell',
    author_email='epurcell3@gatech.edu',
    maintainer='Matt Luongo',
    maintainer_email='mhluongo@gmail.com',
    description='A simple regression testing plugin for nose.',
    long_description=read('README.rst'),
    url='http://packages.python.org/nose-regression',
    py_modules=['nose_regression'],
    entry_points={
        'nose.plugins.0.10': [
            'nose_regression = nose_regression:Regression'
            ]
        },
    platforms=['posix'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance',
    ],
)
