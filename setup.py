"""A setuptools based setup module.

Based on:
 https://github.com/pypa/sampleproject/blob/db5806e0a3204034c51b1c00dde7d5eb3fa2532e/setup.py

See:
 https://python-packaging.readthedocs.io/en/latest/minimal.html
 https://packaging.python.org/guides/distributing-packages-using-setuptools/
 https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup
# from distutils.core import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='ffprobe3-python3',
    version='2.0.0-beta',
    description="""A Python3 wrapper-library around the 'ffprobe' command-line program to extract metadata from media files or streams.""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Simon Hargreaves, Dheerendra Rathor, Mark Ma, James Boyden',
    author_email='pypi@jboy.me',
    maintainer='James Boyden',
    maintainer_email='pypi@jboy.me',
    url='https://github.com/jboy/ffprobe3-python3',
    # Specify that the source code is in a subdirectory `ffprobe3`
    # under the project root directory.
    packages=['ffprobe3'],
    # These keywords simply appear on the project page;
    # they're for use in catalogues, and in searches by humans.
    keywords='ffmpeg, ffprobe, mpeg, mp4, media, audio, video, json, metadata',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        # Note: These classifiers are NOT checked by `pip_install`;
        # they're purely for use in searches by humans on PyPI.
        # So, we must specify all Python versions that are relevant.
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Video',
    ],
    # Specify which Python versions we support.
    # This field WILL be checked & enforced by `pip_install`.
    python_requires=">=3.3, <4",
    # List additional URLs that are relevant to the project.
    # The dict keys are what's used to render the link text on PyPI.
    project_urls={
        'Source': 'https://github.com/jboy/ffprobe3-python3',
    }
)
