from setuptools import find_packages
from setuptools import setup

import tornado_tyron

description="""
Tornado redis/pubsub event notifier
"""

setup(
    name="tornado_tyron",
    version=tornado_tyron.__version__,
    url='https://github.com/tbarbugli/tornado_tyron',
    license='BSD',
    platforms=['OS Independent'],
    description = description.strip(),
    author = 'Tommaso Barbugli',
    author_email = 'tbarbugli@gmail.com',
    maintainer = 'Tommaso Barbugli',
    maintainer_email = 'tbarbugli@gmail.com',
    packages=find_packages(),
    install_requires = [
        'redis',
        'tornado'
    ],
    entry_points={
        'console_scripts': [
            'tornado_tyron = tornado_tyron.tyron:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
    ]
)