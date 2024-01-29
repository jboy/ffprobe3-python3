ffprobe3-python3 module
=======================

A Python3 wrapper-library around the `ffprobe` command-line program to extract
metadata from media files or streams.

(**Note:** This wrapper-library depends on the `ffprobe` command-line program
to extract metadata from media files or streams.  The `ffprobe` program must
be installed, with an `ffprobe` executable that can be found by searching the
`$PATH` environment variable.)

This package began as a fork (and is now a complete rewrite) of package
``ffprobe-python`` which was maintained by Mark Ma:

- https://pypi.org/project/ffprobe-python/
- https://github.com/gbstack/ffprobe-python

Changes and improvements in this fork
-------------------------------------

Noteworthy improvements in this fork include:

- Fixed a few Python3 compatibility bugs in the pre-fork code.
- Re-wrote the `ffprobe` call to request & parse the `json` print-format.
- Handle "Chapter" in ffprobe output.  ("Stream" was already handled.)
- Support/allow remote media streams (as `ffprobe` program already does).
- Local-file-exists checks are optional (use `verify_local_mediafile=False`).
- More classes, with more attributes & methods for commonly-accessed metadata.
- Get datasize as bytes (`1185288357`) or human-readable (`"1.2 GB"`).
- Get duration as seconds (`5751.787`) or human-readable (`"01:35:51.79"`).
- Get "avg frame-rate" as FPS (`29.97`) or ratio 2-tuple (`(2516481, 83966)`).
- Get "r frame-rate" as FPS (`29.97`) or ratio 2-tuple (`(2997, 100)`).
- All ffprobe-output classes wrap & retain their JSON data for introspection.
- All ffprobe-output classes can be reconstructed from their JSON `repr()`.
- Added several derived exception classes for more-informative error reporting.
- Re-wrote the subprocess code to use convenient new Python3 library features.
- Documented the API (Sphinx/reST docstrings for modules, classes, methods).

These are the currently-implemented classes to wrap ffprobe JSON output:

- `FFprobe(ParsedJson)`
- `FFformat(ParsedJson)`
- `FFchapter(ParsedJson)`
- `FFstream(ParsedJson)`
- `FFattachmentStream(FFstream)`
- `FFaudioStream(FFstream)`
- `FFsubtitleStream(FFstream)`
- `FFvideoStream(FFstream)`

Significant API-breaking changes in this fork include:

- **Changed the client-facing API of functions & classes**.
- **No longer support Python 2 or Python3 < 3.3**.

I renamed this forked repo to `ffprobe3-python3`, because:

- The client-facing API of functions & classes has changed; and
- The supported Python version has changed from Python2 to **Python3 >= 3.3**.

---

Example usage
-------------

```python
#!/usr/bin/env python3

import ffprobe3

# Function `ffprobe3.probe(media_filename)` is the entry point to this module;
# it's the first function you want to call.

# Local media file:
ffprobe_output = ffprobe3.probe('media-file.mov')

# ... or, a remote video stream:
ffprobe_output = ffprobe3.probe('http://some-streaming-url.com:8080/stream')

# Examine the metadata in `ffprobe_output` (of class `FFprobe`):

# The "format" key in the parsed JSON becomes an `FFformat` instance:
media_format = ffprobe_output.format

# The size of the media in Bytes (if provided by `ffprobe`):
if media_format.size_B is not None:
    print("media size = %d Bytes" % media_format.size_B)
# ... or in human-readable base-10 prefix format (e.g., "567.8 MB"):
if media_format.size_human is not None:
    print("media size = %s" % media_format.size_human)

# The duration of the media:
if media_format.duration_secs is not None:
    print("media duration = %f secs" % media_format.duration_secs)
# ... or in human-readable "HH:MM:SS.ss" format (e.g., "01:04:14.80")
if media_format.duration_human is not None:
    print("media duration = %s (HH:MM:SS.ss)" % media_format.duration_human)

# Access a list of streams using `.streams`:
print("media contains %d streams" % len(ffprobe_output.streams))

# Access a list of chapters using `.chapters`:
print("media contains %d chapters" % len(ffprobe_output.chapters))

# Access specific stream types directly by named attribute of `FFprobe`:
# In this new code version, each stream attribute of class `FFprobe` also
# contains a list of instances of *only* a single specific derived class
# of base class `FFstream`:
# - `.attachment` -> `FFattachmentStream`
# - `.audio` -> `FFaudioStream`
# - `.subtitle` -> `FFsubtitleStream`
# - `.video` -> `FFvideoStream`
video_stream = ffprobe_output.video[0]  # assuming at least 1 video stream
audio_stream = ffprobe_output.audio[0]  # assuming at least 1 audio stream

# Derived class `FFvideoStream` has attributes `width` & `height` for
# the frame dimensions in pixels (or `None` if not found in the JSON):
video_width = video_stream.width
video_height = video_stream.height
if video_width is not None and video_height is not None:
    print("video frame shape = (%d, %d)" % (video_width, video_height))

# Class `FFvideoStream` also has a method `.get_frame_shape()`,
# which returns the frame (width, height) in pixels as a pair of ints
# (or `None` if *either* dimension's value is not found in the JSON):
video_frame_shape = video_stream.get_frame_shape()
if video_frame_shape is not None:
    print("video frame shape = (%d, %d)" % video_frame_shape)

# This `get_frame_shape()` is a method with a name that begins with `get_`
# (rather than simply an attribute called `frame_shape`, for example) to
# indicate that:
#     (a) It has a "default" `default` of `None`
#         (like Python's `dict.get(key, default=None)`).
# and:
#     (b) You may override this "default" `default` as a keyword argument
#         (for example, if you would rather return a pair `(None, None)`
#         than a single `None` value, for 2-tuple deconstruction).
#
# So you could instead use a 2-tuple deconstruction with a default `None`
# for each element:
(video_width, video_height) = video_stream.get_frame_shape((None, None))
if video_width is not None and video_height is not None:
    print("video frame shape = (%d, %d)" % (video_width, video_height))

# Derived class `FFaudioStream` has an attribute `.sample_rate_Hz`
# (which defaults to `None` if no value was provided by `ffprobe`):
if audio_stream.sample_rate_Hz is not None:
    print("audio sample rate = %d Hz" % audio_stream.sample_rate_Hz)

# Not sure which attributes & methods are available for each class?
# Every class has 3 introspection methods:
# - method `.list_attr_names()`
# - method `.list_getter_names()`
# - method `.keys()`

# Which attributes does this class offer?  Get a list of names:
print(audio_stream.list_attr_names())

# Which getter methods does this class offer?  Get a list of names:
print(audio_stream.list_getter_names())

# Which keys are in the original dictionary of parsed JSON for this class?
print(audio_stream.keys())
```

**To see a comprehensive usage** of (almost all) the attributes, methods, and
exceptions in the `ffprobe3` class & function API, also look at test module
[`tests/test_ffprobe3.py`](https://github.com/jboy/ffprobe3-python3/blob/master/tests/test_ffprobe3.py) (link into GitHub repo).

---

Why does this fork exist?
-------------------------

I was attempting to use Mark Ma's
[`ffprobe-python` package](https://pypi.org/project/ffprobe-python/) with Python3,
but I was blocked by a parsing error in the library:

```python
AttributeError: 'NoneType' object has no attribute 'groups'
```

This problem had already been reported
as [issue 2](https://github.com/gbstack/ffprobe-python/issues/2)
(almost 3 years ago) &
[issue 16](https://github.com/gbstack/ffprobe-python/issues/16)
(more than 18 months ago).  The most recent Github commit in
the [`ffprobe-python` repo](https://github.com/gbstack/ffprobe-python)
is dated 2021-05-13 (more than 18 months ago).
It looks like the `ffprobe-python` repo is no longer actively maintained?

This new repo now fixes the following bugs & implements the following
feature requests that are
["Open" issues](https://github.com/gbstack/ffprobe-python/issues)
on the `ffprobe-python` repo.

- **bug fix**
  ([issue 2](https://github.com/gbstack/ffprobe-python/issues/2),
  [issue 16](https://github.com/gbstack/ffprobe-python/issues/16)):
  Handle "Chapters" in media files (which are already supported by
  the command-line `ffprobe` program) instead of crashing.
  (Avoid error: `AttributeError: 'NoneType' object has no attribute 'groups'`)
- **bug fix**
  ([issue 4](https://github.com/gbstack/ffprobe-python/issues/4)):
  Handle non-HTTP remote streams (which are already supported by
  the command-line `ffprobe` program) instead of raising an error.
- **bug fix** (I assume, but I have no "problem" media file for testing)
  ([issue 14](https://github.com/gbstack/ffprobe-python/issues/14),
  [issue 19](https://github.com/gbstack/ffprobe-python/issues/19)):
  Handle "Side data" and multi-line fields in media files (which I *assume*
  will be handled correctly by the `json` print-format, if the command-line
  `ffprobe` program already prints the `SIDE_DATA` tags) instead of crashing.
- **feature request**
  ([issue 4](https://github.com/gbstack/ffprobe-python/issues/4),
  [issue 16](https://github.com/gbstack/ffprobe-python/issues/16)):
  Simplify the stream-parsing code by replacing the custom code with the `json`
  print-format that is already offered by the command-line `ffprobe` program.

What's the ancestry of this fork?
---------------------------------

This repo began as a bug-fixing fork (and is now a complete rewrite)
of package `ffprobe-python`,
which was created (2019) & maintained (2019--2021) by Mark Ma:

- [https://pypi.org/project/ffprobe-python/](https://pypi.org/project/ffprobe-python/)
- [https://github.com/gbstack/ffprobe-python](https://github.com/gbstack/ffprobe-python)

In turn, `ffprobe-python` is a fork of package `ffprobe3`,
which was created (2016) & maintained (2016--2019) by Dheerendra Rathor:

- [https://pypi.org/project/ffprobe3/](https://pypi.org/project/ffprobe3/)
- [https://github.com/DheerendraRathor/ffprobe3](https://github.com/DheerendraRathor/ffprobe3)

In turn, `ffprobe3` is a Python3 port of the original Python package `ffprobe`,
which was created (2013) & maintained (2013--2016) by Simon Hargreaves:

- [https://pypi.org/project/ffprobe/](https://pypi.org/project/ffprobe/)
- [https://github.com/simonh10/ffprobe](https://github.com/simonh10/ffprobe)

Thank you to Simon, Dheerendra, and Mark!

---

Which versions of Python are supported?
---------------------------------------

The **minimum supported Python version** is **Python3 >= 3.3**.

Python 3.3 was released on 2012-09-29 (more than 10 years ago now!).
Setting Python 3.3 as the minimum allows us to use the following
convenient Python3 language & library features:

- `__qualname__` attribute for the qualified name of classes
   ([PEP 3155](https://peps.python.org/pep-3155/))
- `yield from`
  [syntax for generator delegation](https://docs.python.org/3/whatsnew/3.3.html#pep-380)
  ([PEP 380](https://peps.python.org/pep-0380/))
- `raise NewException() from None`
  [syntax for suppressing exception context](https://docs.python.org/3/whatsnew/3.3.html#pep-409-suppressing-exception-context)
  ([PEP 409](https://peps.python.org/pep-0409/))
- exception base class [`subprocess.SubprocessError`](https://docs.python.org/3/library/subprocess.html#exceptions)
- [`subprocess.DEVNULL`](https://docs.python.org/3/library/subprocess.html#subprocess.DEVNULL)
- the `timeout` argument to functions
  [`subprocess.check_call`](https://docs.python.org/3/library/subprocess.html#subprocess.check_call),
  [`subprocess.Popen.communicate`](https://docs.python.org/3/library/subprocess.html#subprocess.Popen.communicate), and
  [`subprocess.Popen.wait`](https://docs.python.org/3/library/subprocess.html#subprocess.Popen.wait)
- [function `shlex.quote`](https://docs.python.org/3/library/shlex.html#shlex.quote),
  if we ever need to shell-quote strings
- [function `shutil.which`](https://docs.python.org/3/library/shutil.html#shutil.which),
  if we ever want to guess what `Popen` will use
- [the `asyncio` module](https://docs.python.org/3/library/asyncio.html)
  ([initially a package on PyPI](https://pypi.org/project/asyncio/),
  before it was officially incorporated into the Python3 stdlib in Python 3.4),
  if we ever want to switch from `subprocess` to
  [`asyncio.subprocess`](https://docs.python.org/3/library/asyncio-subprocess.html)

---

License
-------

(The MIT License)

Copyright © 2022--2024 James Boyden <pypi@jboy.me>

Maintained 2019--2021 by Mark Ma <519329064@qq.com>

Copyright © 2019 Mark Ma <519329064@qq.com>

Maintained 2016--2019 by Dheerendra Rathor <dheeru.rathor14@gmail.com>

Copyright © 2016 Dheerendra Rathor <dheeru.rathor14@gmail.com>

Maintained 2013--2016 by Simon Hargreaves <simon@simon-hargreaves.com>

Copyright © 2013 Simon Hargreaves <simon@simon-hargreaves.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the Software), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

