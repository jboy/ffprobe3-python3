"""
A Python3 wrapper-library around the ``ffprobe`` command-line program.

(**Note:** This wrapper-library depends on the ``ffprobe`` command-line program
to extract metadata from media files or streams.  The ``ffprobe`` program must
be installed, with an ``ffprobe`` executable that can be found by searching the
``$PATH`` environment variable.)

This package is a fork (now actually a **complete rewrite**) of package
``ffprobe-python`` which was maintained by Mark Ma:

- https://pypi.org/project/ffprobe-python/
- https://github.com/gbstack/ffprobe-python

----

Changes and improvements in this fork:

Noteworthy improvements in this fork include:

- Fixed a few Python3 compatibility bugs in the pre-fork code.
- Re-wrote the ``ffprobe`` call to request & parse the ``json`` print-format.
- Handle "Chapter" in ffprobe output.  ("Stream" was already handled.)
- Support/allow remote media streams (as ``ffprobe`` program already does).
- Local-file-exists checks are optional (use ``verify_local_mediafile=False``).
- More classes, with more attributes & methods for commonly-accessed metadata.
- Get datasize as bytes (``1185288357``) or human-readable (``"1.2 GB"``).
- Get duration as seconds (``5751.787``) or human-readable (``"01:35:51.79"``).
- Get "avg frame-rate" as FPS (``29.97``) or ratio 2-tuple (``(2516481, 83966)``).
- Get "r frame-rate" as FPS (``29.97``) or ratio 2-tuple (``(2997, 100)``).
- All ffprobe-output classes wrap & retain their JSON data for introspection.
- All ffprobe-output classes can be reconstructed from their JSON ``repr()``.
- Added several derived exception classes for more-informative error reporting.
- Re-wrote the subprocess code to use convenient new Python3 library features.
- Documented the API (Sphinx/reST docstrings for modules, classes, methods).

These are the currently-implemented classes to wrap ffprobe JSON output:

- ``FFprobe(ParsedJson)``
- ``FFformat(ParsedJson)``
- ``FFchapter(ParsedJson)``
- ``FFstream(ParsedJson)``
- ``FFattachmentStream(FFstream)``
- ``FFaudioStream(FFstream)``
- ``FFsubtitleStream(FFstream)``
- ``FFvideoStream(FFstream)``

Significant API-breaking changes in this fork include:

- **Changed the client-facing API of functions & classes**.
- **No longer support Python 2 or Python3 < 3.3**.

Read the updated ``README.md`` file for a longer list of changes & reasons.

----

Example usage::

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

**To see a comprehensive usage** of (almost all) the attributes, methods, and
exceptions in the `ffprobe3` class & function API, also look at test module
`tests/test_ffprobe3.py <https://github.com/jboy/ffprobe3-python3/blob/master/tests/test_ffprobe3.py>`_ (link into GitHub repo).
"""

import json
import os
import re
import subprocess

from collections.abc import Mapping
from .exceptions import *


# A list, so you can modify the command-line arguments if you really insist.
# Don't shoot yourself in the foot!
_SPLIT_COMMAND_LINE = [
        'ffprobe',
        '-v',
        # Use a log-level ('-v') of 'error' rather than 'quiet',
        # so that `ffprobe` at least reports a single-line error message
        # in the case of failure.
        'error', #'quiet',
        '-print_format',
        'json',
        '-show_chapters',
        '-show_format',
        '-show_streams',
]

# Match anything that looks like a URI Scheme to specify a remote media stream:
#  https://en.wikipedia.org/wiki/Uniform_Resource_Identifier#Syntax
#  https://en.wikipedia.org/wiki/List_of_URI_schemes
_URI_SCHEME = re.compile("^[a-z][a-z0-9-]*://")


def probe(media_filename, *,
        communicate_timeout=10.0,  # a timeout in seconds
        ffprobe_cmd_override=None,
        verify_local_mediafile=True):
    """
    Wrap the ``ffprobe`` command, requesting the ``json`` print-format.
    Parse the JSON output into a hierarchy of :class:`ParsedJson` classes.

    **Note:** This function is the entry point to this module;
    it's the first function you want to call.  This function will return
    a valid, appropriately-populated instance of class :class:`FFprobe`
    (or raise some derived class of the exception base class
    :class:`ffprobe3.exceptions.FFprobeError` trying).

    Args:
        media_filename (str):
            filename of local media or URI of remote media to probe
        communicate_timeout (positive float, optional):
            a timeout in seconds for ``subprocess.Popen.communicate``
        ffprobe_cmd_override (str, optional):
            file-path of a command to invoke instead of default ``"ffprobe"``
        verify_local_mediafile (bool, optional):
            verify `media_filename` exists, if it's a local file (sanity check)

    Returns:
        a new instance of class :class:`FFprobe`

    Raises:
        FFprobeError: the base class of all exception classes in this package
        FFprobeExecutableError: ffprobe command not found in ``$PATH``
        FFprobeInvalidArgumentError: invalid value to `communicate_timeout`
        FFprobeJsonParseError: JSON parser was unable to parse ffprobe output
        FFprobeMediaFileError: specified local media file does not exist
        FFprobeOverrideFileError: `ffprobe_cmd_override` file not found
        FFprobePopenError: ``subprocess.Popen`` failed, raised an exception
        FFprobeSubprocessError: ffprobe command returned non-zero exit status

    **Note:** If parameter `ffprobe_cmd_override` receives a non-``None``
    argument, it must be a string that specifies the full file-path (either
    absolute or relative to the current directory) to an executable to call,
    to provide the functionality of the ``ffprobe`` command.

    The intention of parameter `ffprobe_cmd_override` is to enable client code
    to specify a particular executable to call, instead of searching ``$PATH``
    for the default ``ffprobe`` command.  Reasons for this might include:

    - Security: Specify a particular known/trusted executable to call,
      rather than relying upon whatever happens to be found first in ``$PATH``.
    - Control: Call a particular executable instead of what is installed in
      the system ``$PATH``.

    (This library defaults to searching for ``ffprobe`` in ``$PATH`` because:
    (a) it's the easiest way to get started using this library (rather than
    requiring a new library user to search for, and specify, the full file-path
    to the ``ffprobe`` command on their own system); and (b) searching for an
    executable in ``$PATH`` is what ``subprocess.Popen`` does *by default*.)

    Example usage of this function::

        import ffprobe3

        # Local media file
        ffprobe_output = ffprobe3.probe('media-file.mov')

        # or, Remote video stream
        ffprobe_output = ffprobe3.probe('http://some-streaming-url.com:8080/stream')
    """

    split_cmdline = list(_SPLIT_COMMAND_LINE)  # Roger, copy that.
    ffprobe_cmd = split_cmdline[0]

    if ffprobe_cmd_override is not None:
        if not os.path.isfile(ffprobe_cmd_override):
            raise FFprobeOverrideFileError(ffprobe_cmd_override)
        else:
            ffprobe_cmd = ffprobe_cmd_override
            split_cmdline[0] = ffprobe_cmd_override

    if communicate_timeout is not None:
        # Verify that this non-None value is some kind of positive number.
        if not isinstance(communicate_timeout, (int, float)):
            raise FFprobeInvalidArgumentError('communicate_timeout',
                    'Supplied timeout is non-None and non-numeric',
                    communicate_timeout)
        if communicate_timeout <= 0.0:
            raise FFprobeInvalidArgumentError('communicate_timeout',
                    'Supplied timeout is non-None and non-positive',
                    communicate_timeout)

    # Verify that the specified media exists (if it's a local file).
    # We perform this by default as a helpful (but optional!) sanity check.
    #
    # [Of course, we WILL ultimately find out whether a local media file exists
    # -- when we attempt to probe it with `ffprobe`.  But at that stage, there
    # are any number of other media file faults that might occur, requiring us
    # to decipher whatever error message `ffprobe` prints to stderr:
    # - Specified file is not actually a media file.
    # - Specified media file is corrupted part-way through.
    # - Communication timeout for remote media stream.
    # - etc.
    #
    # So at the cost of an extra filesystem access, this sanity check verifies
    # this one particular requirement in advance, with a specific error message
    # in case of failure.]
    #
    # And of course, we don't perform this check when accessing remote media
    # (e.g., over HTTP)...  The previous version of `ffprobe-python` did that,
    # and it was reported as an issue (which is still Open):
    #  https://github.com/gbstack/ffprobe-python/issues/4
    if verify_local_mediafile:
        # How do we detect when the media file is remote rather than local?
        # If you run `ffprobe -protocols`, it prints the file protocols that
        # it supports.  On my system, that list (joined at newlines) is:
        #
        #       Input: async bluray cache concat crypto data file ftp gopher
        #       hls http httpproxy https mmsh mmst pipe rtp sctp srtp subfile
        #       tcp tls udp udplite unix rtmp rtmpe rtmps rtmpt rtmpte sftp
        #
        # But rather than hard-coding a list of protocols, let's just match
        # anything that *looks* like a URI Scheme:
        #  https://en.wikipedia.org/wiki/Uniform_Resource_Identifier#Syntax
        #  https://en.wikipedia.org/wiki/List_of_URI_schemes
        if _URI_SCHEME.match(media_filename) is None:
            # It doesn't look like the URI of a remote media file.
            if not os.path.isfile(media_filename):
                raise FFprobeMediaFileError(media_filename)

    # NOTE #1: Python3 docs say that its `Popen` does not call a system shell:
    #  https://docs.python.org/3/library/subprocess.html#security-considerations
    #   '''
    #   Security Considerations
    #
    #   Unlike some other popen functions, this implementation will never
    #   implicitly call a system shell. This means that all characters,
    #   including shell metacharacters, can safely be passed to child
    #   processes.
    #   '''
    #
    # So we should not need to shell-quote the command-line arguments.
    #
    # NOTE #2: I found some info about command-line arguments on Windows:
    #  https://docs.python.org/3/library/subprocess.html#converting-argument-sequence
    #
    # But I don't use Windows, so I can't test anything, sorry...
    split_cmdline.append(media_filename)

    try:
        # https://docs.python.org/3/library/subprocess.html#subprocess.Popen
        proc = subprocess.Popen(split_cmdline,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                encoding="cp437")
    # We catch the following plausible exceptions specifically,
    # in case we decide that we want to process any of them specially.
    except FileNotFoundError as e:
        # This exception is raised if the specified executable cannot be found.
        # Class `FileNotFoundError` is a subclass of `OSError`, so this failure
        # would be handled by the exception handler for `OSError` that follows;
        # but recognizing `FileNotFoundError` first, enables us to provide a
        # more-specific exception type with a more-descriptive error message.
        raise FFprobeExecutableError(ffprobe_cmd) from e
    except OSError as e:
        # https://docs.python.org/3/library/subprocess.html#exceptions
        #   '''
        #   The most common exception raised is `OSError`. This occurs,
        #   for example, when trying to execute a non-existent file.
        #   '''
        raise FFprobePopenError(e, 'OSError') from e
    except ValueError as e:
        #   '''
        #   A `ValueError` will be raised if `Popen` is called with
        #   invalid arguments.
        #   '''
        raise FFprobePopenError(e, 'ValueError') from e
    except subprocess.SubprocessError as e:
        #   '''
        #   Exceptions defined in this module all inherit from
        #   `SubprocessError`.
        #
        #   New in version 3.3: The `SubprocessError` base class was added.
        #   '''
        raise FFprobePopenError(e, 'subprocess.SubprocessError') from e

    # NOTE #3: We allow the caller of this constructor to specify remote
    # media files at HTTP or FTP URIs, which might be very slow if there
    # are network problems.
    #
    # Hence, we specify a `timeout` argument to the following subprocess
    # function (a timeout value which may be configured by the caller
    # using the optional parameter `communicate_timeout`).
    #
    # NOTE #4: We use `Popen.communicate` rather than `Popen.wait`,
    # because as the docs for `Popen.wait` warn us:
    #  https://docs.python.org/3/library/subprocess.html#subprocess.Popen.wait
    #   '''
    #   Note: This will deadlock when using `stdout=PIPE` or `stderr=PIPE`
    #   and the child process generates enough output to a pipe such that
    #   it blocks waiting for the OS pipe buffer to accept more data.
    #   Use `Popen.communicate()` when using pipes to avoid that.
    #   '''
    #
    # The docs for `Popen.communicate` helpfully provide the code idiom
    # that we should use here:
    #  https://docs.python.org/3/library/subprocess.html#subprocess.Popen.communicate
    #   '''
    #   If the process does not terminate after `timeout` seconds,
    #   a `TimeoutExpired` exception will be raised. Catching this
    #   exception and retrying communication will not lose any output.
    #
    #   The child process is not killed if the timeout expires, so
    #   in order to cleanup properly a well-behaved application should
    #   kill the child process and finish communication:
    #   '''
    try:
        (outs, errs) = proc.communicate(timeout=communicate_timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        (outs, errs) = proc.communicate()
    # Because we specified `universal_newlines=True` to `subprocess.Popen`,
    # `outs` & `errs` are text strings.
    #
    # XXX: I'm using `Popen.communicate`; so this function will close the
    # pipes for me automatically, right?  Because `Popen.communicate` waits
    # for the process to terminate?  Meaning it internally calls `Popen.wait`
    # or something similar?  Which closes the pipes?  I'm just being extra
    # careful, because the docs are not entirely clear on the matter:
    #   '''
    #   Read data from stdout and stderr, until end-of-file is reached.
    #   Wait for process to terminate and set the `returncode` attribute.
    #   '''
    # and:
    #   '''
    #   The child process is not killed if the timeout expires, so in order
    #   to cleanup properly a well-behaved application should kill the
    #   child process and finish communication:
    #   '''

    try:
        parsed_json = json.loads(outs)
    except json.decoder.JSONDecodeError as e:
        raise FFprobeJsonParseError(e, 'json.decoder.JSONDecodeError') from e
    exit_status = proc.returncode
    if exit_status != 0:
        raise FFprobeSubprocessError(split_cmdline, exit_status, errs)

    return FFprobe(split_cmdline=split_cmdline, parsed_json=parsed_json)


class ParsedJson(Mapping):
    """
    Class `ParsedJson` contains a dictionary of parsed JSON.

    This class is a lightweight wrapper around the dictionaries of parsed JSON.
    We use this `Mapping`-interface container class as an alternative to either:

    - inheriting from built-in class ``dict``; or
    - mixing arbitrary JSON keys (produced by an external program)
      into a per-instance ``__dict__``.

    Instead, an instance of this class will reference (and share) the original
    ``dict`` instance of parsed JSON that was supplied to its constructor.
    It will **not copy** the argument ``dict`` items into a new ``dict`` owned
    exclusively by this instance.  As a result, for a given ``ffprobe`` output,
    all instances of derived classes of `ParsedJson` will **share the same
    original tree** of ``dict`` instances that was returned by ``json.loads``;
    they will each reference a different subtree of the shared tree.

    This class provides some convenient accessor methods for parsed JSON keys:

    - Python `abstract Mapping <https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes>`_
      interface (for Pythonic ``dict``-lookup):
      :func:`__contains__`, :func:`__getitem__`, :func:`__iter__`, :func:`__len__`,
      :func:`get`, :func:`keys`
    - lookup with type-conversion: :func:`get_as_float`, :func:`get_as_int`, etc.

    For convenient introspection of class `ParsedJson` (or any derived class),
    a list of accessor methods for that class is returned by
    :func:`list_getter_names`.  Example usage::

        >>> import ffprobe3
        >>> p = ffprobe3.probe("movie.mp4")
        >>> v = p.video[0]
        >>> v
        FFvideoStream(parsed_json={ ... valid JSON ... })
        >>> v.list_getter_names()
        ['get', 'get_as_float', 'get_as_int', 'get_datasize_as_human',
        'get_duration_as_human', 'get_frame_shape']

    For convenience, each of the multiple classes that derive from this class
    will define data attributes and/or additional accessor methods appropriate
    to that type.  For convenient introspection, a list of data attributes is
    returned by :func:`list_attr_names`.  Example usage::

        >>> import ffprobe3
        >>> p = ffprobe3.probe("movie.mp4")
        >>> v = p.video[0]
        >>> v
        FFvideoStream(parsed_json={ ... valid JSON ... })
        >>> v.list_attr_names()
        ['avg_frame_rate', 'bit_rate_bps', 'bit_rate_kbps', 'codec_long_name',
        'codec_name', 'codec_type', 'duration_secs', 'height', 'index',
        'parsed_json', 'r_frame_rate', 'width']

    In general, client code should not need to construct this class manually.
    Derived classes of this class are constructed by function :func:`probe`.
    But client code *will* want to invoke the methods of returned instances
    of those derived classes.
    """

    def __init__(self, parsed_json):
        """Construct a wrapper that references the ``dict``-like `parsed_json`.

        Note: An instance of this class will reference (and share) the original
        ``dict`` instance of parsed JSON that was supplied to its constructor.
        It will **not copy** the argument ``dict`` items into a new ``dict``
        owned exclusively by this instance.
        """
        # Verify that the supplied `parsed_json` allows value lookup
        # by string keys (even if `parsed_json` is actually empty).
        # We rely on this duck-type assumption later.
        if not isinstance(parsed_json, Mapping):
            raise FFprobeInvalidArgumentError('parsed_json',
                    'Supplied parsed JSON is not a dictionary',
                    parsed_json)

        self.parsed_json = parsed_json

    def __contains__(self, key):
        """Return whether `key` in parsed JSON.

        Returns:
            ``bool``

        This method is required to implement the Python
        `abstract Mapping <https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes>`_
        interface.
        """
        return (key in self.parsed_json)

    def __eq__(self, other):
        """Compare the contained parsed JSON of `self` & `other` for equality.

        Returns:
            ``bool``

        This is implemented as a dictionary-equality comparison.

        This method is required to implement the Python
        `abstract Mapping <https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes>`_
        interface.
        """
        return self.parsed_json == other.parsed_json

    def __getitem__(self, key):
        """Return the value for `key`, if `key` in parsed JSON; else raise `KeyError`.

        This method is required to implement the Python
        `abstract Mapping <https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes>`_
        interface.
        """
        return self.parsed_json[key]

    def __iter__(self):
        """Return an iterator over the keys in parsed JSON.

        This method is required to implement the Python
        `abstract Mapping <https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes>`_
        interface.
        """
        yield from self.parsed_json

    def __len__(self):
        """Return the count of keys in parsed JSON.

        Returns:
            ``int``

        This method is required to implement the Python
        `abstract Mapping <https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes>`_
        interface.
        """
        return len(self.parsed_json)

    def __repr__(self):
        """Return a string that would yield an object with the same value.

        Returns:
            ``str``

        Because this class is constructed from a ``dict`` of parsed JSON,
        its ``repr`` is basically a ``repr`` of its ``dict`` of parsed JSON,
        surrounded by parentheses, with its class-name in front.

        Reconstructing a `ParsedJson` (or any derived class) instance from its
        `repr` string should work perfectly, **except for** any preceding module
        namespaces that are needed (depending on how the classes & functions in
        this module were imported).

        For example::

            >>> import ffprobe3
            >>> p = ffprobe3.probe("movie.mp4")
            >>> v = p.video[0]
            >>> v
            FFvideoStream(parsed_json={ ... valid JSON ... })
            >>> repr(v)
            "FFvideoStream(parsed_json={ ... valid JSON ... })"
            >>> eval(repr(v))
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
              File "<string>", line 1, in <module>
            NameError: name 'FFvideoStream' is not defined
            >>> ffprobe3.FFvideoStream
            <class 'ffprobe3.ffprobe3.FFvideoStream'>
            >>> eval("ffprobe3." + repr(v))
            FFvideoStream(parsed_json={ ... valid JSON ... })
            >>> eval("ffprobe3." + repr(v)) == v
            True

        [**Standard disclaimer:**  Using ``eval`` on untrusted strings
        (from an external source) is dangerous and insecure.  Don't use
        ``eval`` on untrusted strings!]
        """
        return '%s(parsed_json=%s)' % \
                (type(self).__qualname__, repr(self.parsed_json))

    def get(self, key, default=None):
        """Return the value for `key`, if `key` in parsed JSON; else `default`.

        If `key` is not found in parsed JSON, default to `default`.
        If `default` is not supplied, default to ``None``.

        This method will never raise a `KeyError`.
        """
        return self.parsed_json.get(key, default)

    def get_as_float(self, key, default=None):
        """Return the value for `key` as a ``float``, if `key` is in parsed JSON
        and can be converted to a ``float``; else `default`.

        Returns:
            ``float`` or `default`

        If `key` is not found in parsed JSON, default to `default`.
        If conversion to ``float`` fails, default to `default`.
        (Basically, if anything goes wrong, default to `default`.)
        If `default` is not supplied, default to ``None``.

        This method will never raise an exception.
        """
        try:
            return float(self.parsed_json[key])
        except Exception:
            return default

    def get_as_int(self, key, default=None):
        """Return the value for `key` as an ``int``, if `key` is in parsed JSON
        and can be converted to an ``int``; else `default`.

        Returns:
            ``int`` or `default`

        If `key` is not found in parsed JSON, default to `default`.
        If conversion to ``int`` fails, default to `default`.
        (Basically, if anything goes wrong, default to `default`.)
        If `default` is not supplied, default to ``None``.

        This method will never raise an exception.
        """
        try:
            return int(self.parsed_json[key])
        except Exception:
            return default

    def get_datasize_as_human(self, key, default=None, *,
            suffix='', use_base_10=True):
        """Return a data-size for `key` in a "human-readable” base-10 format;
        else `default`.

        Args:
            key (str): parsed JSON dictionary key to look-up the data-size value
            default (str, optional): fall-back value to return if this method fails
            suffix (str, optional): units of data-size (e.g., ``"B"`` for Bytes)
            use_base_10 (bool, optional): use base-10 units rather than base-2 units

        Returns:
            ``str`` (e.g., ``"567.8 MB"`` or ``"1.3 GiB"``) or `default`

        If `key` is not found in parsed JSON, default to `default`.
        If conversion of data-size to ``float`` fails, default to `default`.
        (Basically, if anything goes wrong, default to `default`.)
        If `default` is not supplied, default to ``None``.

        This method will never raise an exception.

        Note that if `default` is returned, no `suffix` will be appended
        within the result.  (How do you append a string suffix to ``None``?)
        """
        if use_base_10:
            # This is the default, because it's what `ls -lh` does.
            divisor = 1000.0
        else:
            # Use base 2 instead.
            divisor = 1024.0

        try:
            num = float(self.parsed_json[key])
            for unit in ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z']:
                if abs(num) < divisor:
                    if unit and not use_base_10:
                        # We're not using base 10; it must be base 2 instead.
                        # And there is a non-empty unit (e.g., 'k', 'M', etc.).
                        # So, postfix the unit by 'i' (e.g., 'ki', 'Mi', etc.).
                        return "%3.1f %si%s" % (num, unit, suffix)
                    return "%3.1f %s%s" % (num, unit, suffix)
                num /= divisor
            # The number is large enough that we've reached "Yotta-" ('Y'),
            # the largest decimal unit prefix in the metric system:
            #  https://en.wikipedia.org/wiki/Yotta-
            if not use_base_10:
                # We're not using base 10; it must be base 2 instead.
                # So, postfix the unit by 'i' (ie, 'Yi').
                return "%.1f %s%s" % (num, 'Yi', suffix)
            return "%.1f %s%s" % (num, 'Y', suffix)
        except Exception:
            return default

    def get_duration_as_human(self, default=None):
        """Return the duration as a string ``"HH:MM:SS.ss"``; else `default`.

        Returns:
            ``str`` (e.g., ``"01:04:14.80"``) or `default`

        If ``"duration"`` key is not found in parsed JSON, default to `default`.
        If conversion of duration to ``float`` fails, default to `default`.
        (Basically, if anything goes wrong, default to `default`.)
        If `default` is not supplied, default to ``None``.

        This method will never raise an exception.
        """
        try:
            # Only the seconds
            duration_secs = float(self.parsed_json["duration"])
            # Minutes, seconds
            duration_mins = duration_secs // 60
            duration_secs -= duration_mins * 60
            # Hours, minutes, seconds
            duration_hours = duration_mins // 60
            duration_mins -= duration_hours * 60
            return "%02d:%02d:%05.2f" % \
                    (int(duration_hours), int(duration_mins), duration_secs)
        except Exception:
            return default

    def list_attr_names(self):
        """Return the names of pre-defined attributes in this class.

        This method is useful for introspection of the derived class API.
        Similar methods: :func:`list_getter_names`, :func:`keys`

        Example usage::

            >>> import ffprobe3
            >>> p = ffprobe3.probe("movie.mp4")
            >>> v = p.video[0]
            >>> v
            FFvideoStream(parsed_json={ ... valid JSON ... })
            >>> v.list_attr_names()
            ['avg_frame_rate', 'bit_rate_bps', 'bit_rate_kbps',
            'codec_long_name', 'codec_name', 'codec_type',
            'duration_secs', 'height', 'index', 'parsed_json',
            'r_frame_rate', 'width']
            >>> v.bit_rate_bps
            2149704
            >>> v.bit_rate_kbps
            2149.704
            >>> v.duration_secs
            7076.152417
            >>> (v.width, v.height)
            (1904, 1072)
            >>> a = p.audio[0]
            >>> a
            FFaudioStream(parsed_json={ ... valid JSON ... })
            >>> a.list_attr_names()
            ['bit_rate_bps', 'bit_rate_kbps', 'channel_layout',
            'codec_long_name', 'codec_name', 'codec_type',
            'duration_secs', 'index', 'num_channels', 'parsed_json',
            'sample_rate_Hz']
        """
        return [attr_name for attr_name in dir(self)
                if not (attr_name.startswith("_") or
                        attr_name.startswith("get") or
                        attr_name.startswith("is_") or
                        attr_name.startswith("list_") or
                        attr_name in ("keys", "items", "values"))]

    def list_getter_names(self):
        """Return the names of dict-lookup getter-methods in this class.

        This method is useful for introspection of the derived class API.
        Similar methods: :func:`list_attr_names`, :func:`keys`

        Example usage::

            >>> import ffprobe3
            >>> p = ffprobe3.probe("movie.mp4")
            >>> v = p.video[0]
            >>> v
            FFvideoStream(parsed_json={ ... valid JSON ... })
            >>> v.keys()
            dict_keys(['avg_frame_rate', 'level', 'nb_frames', 'disposition',
            'display_aspect_ratio', 'sample_aspect_ratio', 'has_b_frames',
            'duration_ts', 'coded_width', 'chroma_location', 'codec_type',
            'codec_tag_string', 'refs', 'duration', 'bit_rate', 'tags',
            'width', 'pix_fmt', 'start_time', 'codec_tag', 'profile',
            'bits_per_raw_sample', 'height', 'time_base', 'index',
            'codec_long_name', 'codec_name', 'start_pts', 'coded_height',
            'is_avc', 'r_frame_rate', 'codec_time_base', 'nal_length_size'])
            >>> v.list_getter_names()
            ['get', 'get_as_float', 'get_as_int', 'get_datasize_as_human',
            'get_duration_as_human', 'get_frame_shape']
            >>> v.get("duration")
            '7076.152417'
            >>> v.get_as_float("duration")
            7076.152417
            >>> v.get_duration_as_human()
            '01:57:56.15'
            >>> v.get_frame_shape()
            (1904, 1072)
        """
        return [attr_name for attr_name in dir(self)
                if attr_name.startswith("get")]

    def keys(self):
        """Return the keys in the top-level dictionary of parsed JSON.

        This method is useful for introspection of the parsed JSON.
        Similar methods: :func:`list_attr_names`, :func:`list_getter_names`

        Example usage::

            >>> import ffprobe3
            >>> p = ffprobe3.probe("movie.mp4")
            >>> v = p.video[0]
            >>> v
            FFvideoStream(parsed_json={ ... valid JSON ... })
            >>> v.keys()
            dict_keys(['avg_frame_rate', 'level', 'nb_frames', 'disposition',
            'display_aspect_ratio', 'sample_aspect_ratio', 'has_b_frames',
            'duration_ts', 'coded_width', 'chroma_location', 'codec_type',
            'codec_tag_string', 'refs', 'duration', 'bit_rate', 'tags',
            'width', 'pix_fmt', 'start_time', 'codec_tag', 'profile',
            'bits_per_raw_sample', 'height', 'time_base', 'index',
            'codec_long_name', 'codec_name', 'start_pts', 'coded_height',
            'is_avc', 'r_frame_rate', 'codec_time_base', 'nal_length_size'])
        """
        return self.parsed_json.keys()


class FFprobe(ParsedJson):
    """
    Class `FFprobe` contains the parsed probe output of the ``ffprobe`` command.

    **Note:** Function :func:`probe` is the entry point to this module; it's
    the first function you want to call.  Function :func:`probe` will return
    a valid, appropriately-populated instance of this class `FFprobe`
    (or raise some derived class of the exception base class
    :class:`ffprobe3.exceptions.FFprobeError` trying).

    This class `FFprobe` is a lightweight, convenient wrapper around the JSON
    printed by the ``ffprobe`` command, which has been parsed into dictionaries
    by function :func:`probe`.  This class is both the "root" of a "tree" of
    JSON-wrapper classes, and the "container" of this tree of classes.

    The following data attributes provide convenient access to frequently-used
    keys & values in the "root" level of JSON:

    :ivar format: (:class:`FFformat`) parsed format metadata
    :ivar streams: (list of derived classes of :class:`FFstream`) all parsed streams
    :ivar chapters: (list of :class:`FFchapter`) parsed chapters
    :ivar attachment: (list of :class:`FFattachmentStream`) only parsed attachment streams
    :ivar audio: (list of :class:`FFaudioStream`) only parsed audio streams
    :ivar subtitle: (list of :class:`FFsubtitleStream`) only parsed subtitle streams
    :ivar video: (list of :class:`FFvideoStream`) only parsed video streams

    In addition, the original ``dict`` instance of the parsed JSON output
    from ``ffprobe`` can always be accessed directly in the ``.parsed_json``
    attribute of base class :class:`ParsedJson`.

    The following data attributes enable retrospective review of the command
    that was executed to produce this parsed probe output:

    :ivar split_cmdline: (list of ``str``) split command-line that was executed
    :ivar executed_cmd: (``str``) command executable filename that was executed
    :ivar media_filename: (``str``) media filename that was probed

    In general, client code should not need to construct this class manually.
    It is constructed and returned by function :func:`probe`.  But client code
    *will* want to examine the attributes of a returned instance of this class.

    Example construction::

        ffprobe_output = FFprobe(split_cmdline=[...], parsed_json={...})

    Args:
        split_cmdline (list of strings, optional): split command-line that was executed
        parsed_json (dict, optional): valid parsed JSON output from ``ffprobe`` command

    Raises:
        FFprobeInvalidArgumentError: invalid value supplied for function argument
    """
    def __init__(self, *, split_cmdline=[], parsed_json={}):
        # Verify that `split_cmdline` is a non-string sequence that contains
        # at least 2 strings (ie, the command name & the media file name).
        # We rely on this assumption later.
        if isinstance(split_cmdline, str):
            raise FFprobeInvalidArgumentError('split_cmdline',
                    'Supplied split command-line is actually a single string',
                    split_cmdline)

        try:
            if len(split_cmdline) < 2:
                raise FFprobeInvalidArgumentError('split_cmdline',
                        'Supplied split command-line has too few elements',
                        split_cmdline)
        except (AttributeError, TypeError, ValueError) as e:
            raise FFprobeInvalidArgumentError('split_cmdline',
                    'Supplied split command-line is not a sequence',
                    split_cmdline) from e

        try:
            for s in split_cmdline:
                if not isinstance(s, str):
                    raise FFprobeInvalidArgumentError('split_cmdline',
                            'Supplied split command-line contains non-strings',
                            split_cmdline)
        except (AttributeError, TypeError, ValueError) as e:
            raise FFprobeInvalidArgumentError('split_cmdline',
                    'Supplied split command-line is not a sequence',
                    split_cmdline) from e

        self.split_cmdline = split_cmdline
        self.executed_cmd = split_cmdline[0]
        self.media_filename = split_cmdline[-1]

        super().__init__(parsed_json)
        # Pick out some particular expected keys from the parsed JSON.
        self.format = FFformat(self.get("format", {}))
        self.streams = [_construct_ffstream_subclass(stream)
                for stream in self.get("streams", [])]
        self.chapters = [FFchapter(chapter)
                for chapter in self.get("chapters", [])]

        self.attachment =   [s for s in self.streams if s.is_attachment()]
        self.audio =        [s for s in self.streams if s.is_audio()]
        self.subtitle =     [s for s in self.streams if s.is_subtitle()]
        self.video =        [s for s in self.streams if s.is_video()]

    def __repr__(self):
        """Return a string that would yield an object with the same value."""
        return '%s(split_cmdline=%s, parsed_json=%s)' % \
                (type(self).__qualname__, self.split_cmdline, self.parsed_json)

    def __str__(self):
        """Return a string containing a human-readable summary of the object."""
        return '%s(%s "%s" => (%s): %s, %s, %s kb/s, %d streams, %d chapters)' % \
                (type(self).__qualname__,
                        self.executed_cmd, self.media_filename,
                        self.format.format_name,
                        self.format.duration_human,
                        self.format.size_human,
                        self.format.bit_rate_kbps,
                        len(self.streams), len(self.chapters))


class FFformat(ParsedJson):
    """
    Class `FFformat` contains the format metadata for some media probed by ``ffprobe``.

    **Note:** Function :func:`probe` is the entry point to this module; it's
    the first function you want to call.  Function :func:`probe` will return
    a valid, appropriately-populated instance of :class:`FFprobe`, which in
    turn will contain a valid, appropriately-populated instance of this class
    `FFformat`.

    This class `FFformat` is a lightweight, convenient wrapper around the
    JSON sub-tree for the ``"format"`` key.

    The following data attributes provide convenient access to frequently-used
    keys & values expected in the "format" metadata returned by ``ffprobe``:

    :ivar format_name: (``str`` or ``None``) short name of the format
    :ivar format_long_name: (``str`` or ``None``) long name of the format
    :ivar duration_secs: (``float`` or ``None``) media duration in seconds
    :ivar duration_human: (``str`` or ``None``) media duration in "human-readable" ``HH:MM:SS.ss`` format (e.g., ``"01:04:14.80"``)
    :ivar num_streams: (``int`` or ``None``) number of streams in the media
    :ivar bit_rate_bps: (``int`` or ``None``) media bit-rate in bits-per-second
    :ivar bit_rate_kbps: (``float`` or ``None``) media bit-rate in kilobits-per-second
    :ivar size_B: (``int`` or ``None``) media size in Bytes
    :ivar size_human: (``str`` or ``None``) media size in "human-readable" base-10 prefix format (e.g., ``"567.8 MB"``)

    In addition, the original ``dict`` instance of the parsed JSON output
    from ``ffprobe`` can always be accessed directly in the ``.parsed_json``
    attribute of base class :class:`ParsedJson`.

    In general, client code should not need to construct this class manually.
    It is constructed by function :func:`probe`.  But client code *will* want
    to examine the attributes of a returned instance of this class.
    """
    def __init__(self, parsed_json):
        super().__init__(parsed_json)
        self.format_name =          self.get('format_name')
        self.format_long_name =     self.get('format_long_name')
        self.duration_secs =        self.get_as_float('duration')
        self.duration_human =       self.get_duration_as_human()
        self.num_streams =          self.get_as_int('nb_streams')
        self.bit_rate_bps =         self.get_as_int('bit_rate')
        try:
            self.bit_rate_kbps = float(self.bit_rate_bps) / 1000.0
        except (TypeError, ValueError):
            self.bit_rate_kbps = None
        self.size_B =               self.get_as_int('size')
        self.size_human =           self.get_datasize_as_human('size', suffix='B')

    def __str__(self):
        """Return a string containing a human-readable summary of the object."""
        return '%s((%s): %s, %s, %s kb/s)' % \
                (type(self).__qualname__, self.format_name,
                        self.duration_human, self.size_human,
                        self.bit_rate_kbps)


class FFchapter(ParsedJson):
    """
    Class `FFchapter` is an individual chapter in some media probed by ``ffprobe``.

    **Note:** Function :func:`probe` is the entry point to this module; it's
    the first function you want to call.  Function :func:`probe` will return
    a valid, appropriately-populated instance of :class:`FFprobe`, which in
    turn will contain zero or more valid, appropriately-populated instances
    of this class `FFchapter`.

    This class `FFchapter` is a lightweight, convenient wrapper around each
    JSON sub-tree in the list for the ``"chapters"`` key.

    The following data attributes provide convenient access to frequently-used
    keys & values expected in the metadata for an individual chapter:

    :ivar id: (``str`` or ``None``) chapter identifier
    :ivar title: (``str`` or ``None``) chapter title

    In addition, the original ``dict`` instance of the parsed JSON output
    from ``ffprobe`` can always be accessed directly in the ``.parsed_json``
    attribute of base class :class:`ParsedJson`.

    In general, client code should not need to construct this class manually.
    It is constructed by function :func:`probe`.  But client code *will* want
    to examine the attributes of a returned instance of this class.
    """
    def __init__(self, parsed_json):
        super().__init__(parsed_json)
        self.id = self.get('id')
        # This JSON might not have a "tags" key; or the value of the "tags" key
        # might not be a nested dictionary; or that nested dictionary might not
        # have a "title" key.
        try:
            self.title = self['tags']['title']
        except Exception:
            self.title = None

    def __str__(self):
        """Return a string containing a human-readable summary of the object."""
        return '%s(chapters[%s]: "%s")' % \
                (type(self).__qualname__, self.id, self.title)


class FFstream(ParsedJson):
    """
    Class `FFstream` is an individual stream in some media probed by ``ffprobe``.

    **Note:** Function :func:`probe` is the entry point to this module; it's
    the first function you want to call.  Function :func:`probe` will return
    a valid, appropriately-populated instance of :class:`FFprobe`, which in
    turn will contain zero or more valid, appropriately-populated instances
    of this class `FFstream`.

    This class `FFstream` is a lightweight, convenient wrapper around each
    JSON sub-tree in the list for the ``"streams"`` key.

    This class `FFstream` is also the **non-abstract base class** for several
    derived classes that correspond to specific kinds of stream (as indicated
    by the ``codec_type``).  Each derived class has attributes & methods
    relevant to its own corresponding kind of stream.  Currently-implemented
    derived classes:

    - :class:`FFattachmentStream`: ``(codec_type == "attachment")``
    - :class:`FFaudioStream`: ``(codec_type == "audio")``
    - :class:`FFsubtitleStream`: ``(codec_type == "subtitle")``
    - :class:`FFvideoStream`: ``(codec_type == "video")``

    If no ``codec_type`` is specified, or the specified ``codec_type`` is not
    recognized, then a plain old `FFstream` will be returned.

    The following data attributes provide convenient access to frequently-used
    keys & values expected in the metadata for an individual stream:

    :ivar index: (``int`` or ``str`` or ``None``) index in the list of streams
    :ivar codec_type: (``str`` or ``None``) type-name of the kind of stream
    :ivar codec_name: (``str`` or ``None``) short name of the specific codec used
    :ivar codec_long_name: (``str`` or ``None``) long name of the specific codec used
    :ivar duration_secs: (``float`` or ``None``) stream duration in seconds

    In addition, the original ``dict`` instance of the parsed JSON output
    from ``ffprobe`` can always be accessed directly in the ``.parsed_json``
    attribute of base class :class:`ParsedJson`.

    In general, client code should not need to construct this class manually.
    It is constructed by function :func:`probe`.  But client code *will* want
    to examine the attributes of a returned instance of this class.
    """
    def __init__(self, parsed_json):
        super().__init__(parsed_json)
        self.index =            self.get('index')
        self.codec_type =       self.get('codec_type')
        self.codec_name =       self.get('codec_name')
        self.codec_long_name =  self.get('codec_long_name')
        self.duration_secs =    self.get_as_float('duration')

    def __str__(self):
        """Return a string containing a human-readable summary of the object."""
        return '%s(streams[%s]: %s(%s))' % \
                (type(self).__qualname__, self.index,
                        self.codec_type, self.codec_name)

    def is_attachment(self):
        """Return whether this `FFstream` instance is an attachment stream."""
        return self.codec_type == 'attachment'

    def is_audio(self):
        """Return whether this `FFstream` instance is an audio stream."""
        return self.codec_type == 'audio'

    def is_subtitle(self):
        """Return whether this `FFstream` instance is a subtitle stream."""
        return self.codec_type == 'subtitle'

    def is_video(self):
        """Return whether this `FFstream` instance is a video stream."""
        return self.codec_type == 'video'


class FFattachmentStream(FFstream):
    """
    Class `FFattachmentStream` is an individual attachment stream in some media
    probed by ``ffprobe``.

    This class `FFattachmentStream` is a derived class of base class
    :class:`FFstream` that has additional data attributes & methods relevant
    to an attachment stream (currently none).

    **Note:** An instance of this class `FFattachmentStream` may **only** be
    constructed for `parsed_json` with ``(codec_type == "attachment")``.
    Otherwise an exception :class:`FFprobeStreamSubclassError` will be raised.

    Raises:
        FFprobeStreamSubclassError: ``(codec_type != "attachment")``
    """
    def __init__(self, parsed_json):
        super().__init__(parsed_json)
        if self.codec_type != 'attachment':
            raise FFprobeStreamSubclassError(
                    type(self).__qualname__, self.codec_type, 'attachment')

    def __str__(self):
        """Return a string containing a human-readable summary of the object."""
        return '%s(streams[%s]: %s(%s))' % \
                (type(self).__qualname__, self.index,
                        self.codec_type, self.codec_name)


class FFaudioStream(FFstream):
    """
    Class `FFaudioStream` is an individual audio stream in some media
    probed by ``ffprobe``.

    This class `FFaudioStream` is a derived class of base class
    :class:`FFstream` that has additional data attributes & methods relevant
    to an audio stream.

    The following data attributes provide convenient access to frequently-used
    keys & values expected in the metadata for an audio stream:

    :ivar num_channels: (``int`` or ``None``) number of audio channels
    :ivar num_frames: (``int`` or ``None``) number of frames
    :ivar channel_layout: (``str`` or ``None``) audio channel configuration (e.g., ``"stereo"``)
    :ivar sample_rate_Hz: (``int`` or ``None``) audio sample-rate in Hz
    :ivar bit_rate_bps: (``int`` or ``None``) audio bit-rate in bits-per-second
    :ivar bit_rate_kbps: (``float`` or ``None``) audio bit-rate in kilobits-per-second

    **Note:** An instance of this class `FFaudioStream` may **only** be
    constructed for `parsed_json` with ``(codec_type == "audio")``.
    Otherwise an exception :class:`FFprobeStreamSubclassError` will be raised.

    Raises:
        FFprobeStreamSubclassError: ``(codec_type != "audio")``
    """
    def __init__(self, parsed_json):
        super().__init__(parsed_json)
        if self.codec_type != 'audio':
            raise FFprobeStreamSubclassError(
                    type(self).__qualname__, self.codec_type, 'audio')

        self.num_channels =     self.get_as_int('channels')
        self.num_frames =       self.get_as_int('nb_frames')
        self.channel_layout =   self.get('channel_layout')
        self.sample_rate_Hz =   self.get_as_int('sample_rate')
        self.bit_rate_bps =     self.get_as_int('bit_rate')
        try:
            self.bit_rate_kbps = float(self.bit_rate_bps) / 1000.0
        except (TypeError, ValueError):
            self.bit_rate_kbps = None

    def __str__(self):
        """Return a string containing a human-readable summary of the object."""
        return '%s(streams[%s]: %s(%s): %s channels (%s), %s Hz, %s kb/s)' % \
                (type(self).__qualname__, self.index,
                        self.codec_type, self.codec_name,
                        self.num_channels, self.channel_layout,
                        self.sample_rate_Hz, self.bit_rate_kbps)


class FFsubtitleStream(FFstream):
    """
    Class `FFsubtitleStream` is an individual subtitle stream in some media
    probed by ``ffprobe``.

    This class `FFsubtitleStream` is a derived class of base class
    :class:`FFstream` that has additional data attributes & methods relevant
    to a subtitle stream (currently none).

    **Note:** An instance of this class `FFsubtitleStream` may **only** be
    constructed for `parsed_json` with ``(codec_type == "subtitle")``.
    Otherwise an exception :class:`FFprobeStreamSubclassError` will be raised.

    Raises:
        FFprobeStreamSubclassError: ``(codec_type != "subtitle")``
    """
    def __init__(self, parsed_json):
        super().__init__(parsed_json)
        if self.codec_type != 'subtitle':
            raise FFprobeStreamSubclassError(
                    type(self).__qualname__, self.codec_type, 'subtitle')

    def __str__(self):
        """Return a string containing a human-readable summary of the object."""
        return '%s(streams[%s]: %s(%s))' % \
                (type(self).__qualname__, self.index,
                        self.codec_type, self.codec_name)


class FFvideoStream(FFstream):
    """
    Class `FFvideoStream` is an individual video stream in some media
    probed by ``ffprobe``.

    This class `FFvideoStream` is a derived class of base class
    :class:`FFstream` that has additional data attributes & methods relevant
    to a video stream.

    The following data attributes provide convenient access to frequently-used
    keys & values expected in the metadata for a video stream:

    :ivar width: (``int`` or ``None``) frame width in pixels
    :ivar height: (``int`` or ``None``) frame height in pixels
    :ivar avg_frame_rate: (``str`` or ``None``) "average frame rate"
    :ivar r_frame_rate: (``str`` or ``None``) "r frame rate"
    :ivar num_frames: (``int`` or ``None``) number of frames
    :ivar bit_rate_bps: (``int`` or ``None``) video bit-rate in bits-per-second
    :ivar bit_rate_kbps: (``float`` or ``None``) video bit-rate in kilobits-per-second
    :ivar side_data_list: (``list`` or ``None``) video stream side-data

    **Note:** An instance of this class `FFvideoStream` may **only** be
    constructed for `parsed_json` with ``(codec_type == "video")``.
    Otherwise an exception :class:`FFprobeStreamSubclassError` will be raised.

    Raises:
        FFprobeStreamSubclassError: ``(codec_type != "video")``
    """
    def __init__(self, parsed_json):
        super().__init__(parsed_json)
        if self.codec_type != 'video':
            raise FFprobeStreamSubclassError(
                    type(self).__qualname__, self.codec_type, 'video')

        self.width =            self.get_as_int('width')
        self.height =           self.get_as_int('height')
        self.avg_frame_rate =   self.get('avg_frame_rate')
        self.r_frame_rate =     self.get('r_frame_rate')
        self.num_frames =       self.get_as_int('nb_frames')
        self.bit_rate_bps =     self.get_as_int('bit_rate')
        try:
            self.bit_rate_kbps = float(self.bit_rate_bps) / 1000.0
        except (TypeError, ValueError):
            self.bit_rate_kbps = None
        self.side_data_list =   self.get('side_data_list')

    def __str__(self):
        """Return a string containing a human-readable summary of the object."""
        return '%s(streams[%s]: %s(%s): %sx%s, %s fps, %s kb/s)' % \
                (type(self).__qualname__, self.index,
                        self.codec_type, self.codec_name,
                        self.width, self.height,
                        self.avg_frame_rate, self.bit_rate_kbps)

    def get_frame_rate_as_ratio(self, key, default=None):
        """Return a frame-rate for `key` as 2-tuple `(numerator, denominator)`;
        else `default`.

        Args:
            key (str): parsed JSON dictionary key to look-up the frame-rate value
            default (str, optional): fall-back value to return if this method fails

        Returns:
            ``tuple`` of 2 elements (e.g., ``(2997, 100)``) or `default`

        We expect that the frame-rate returned by ``ffprobe`` will be a string
        with format ``n/d``, where:

        - `n` looks like ``int`` ("number of frames" or "numerator in ratio").
        - `d` looks like ``int`` ("duration (secs)" or "denominator in ratio").

        This method will return a 2-tuple ``(int(n), int(d))``.

        Note: This method does NOT verify that `n` & `d` are positive integers.
        They might be zero or even negative!

        More generally, this method does NOT attempt to validate the ratio,
        nor to reduce ratios by their Greatest Common Divisor.  This method
        simply reports the integers that were returned by ``ffprobe``.

        If you want/need more validation of the ratio, you might consider
        the similar method :func:`get_frame_rate_as_float`.

        If `key` is not found in parsed JSON, default to `default`.
        If the frame-rate doesn't look like ``"int/int"``, default to `default`.
        If conversion of numerator or denominator to ``int`` fails, default to
        `default`.

        (Basically, if anything goes wrong, default to `default`.)
        If `default` is not supplied, default to ``None``.

        This method will never raise an exception.
        """
        try:
            # Possible exception: `key` is not found.
            frame_rate = self.parsed_json[key]
            # Possible exception: `frame_rate` doesn't match regex,
            # so `None` is returned, which has no method `.groups()`.
            (n, d) = re.match("^(-?[0-9]+)/(-?[0-9]+)$", frame_rate).groups()
            # Possible exception: `int(n)` fails or `int(d)` fails.
            return (int(n), int(d))
        except Exception:
            return default

    def get_frame_rate_as_float(self, key, default=None):
        """Return a frame-rate for `key` as a ``float``; else `default`.

        Args:
            key (str): parsed JSON dictionary key to look-up the frame-rate value
            default (str, optional): fall-back value to return if this method fails

        Returns:
            ``float`` (frames per second) or `default`

        We expect that the frame-rate returned by ``ffprobe`` will be a string
        with format ``n/d``, where:

        - `n` looks like ``int`` ("number of frames" or "numerator in ratio").
        - `d` looks like ``int`` ("duration (secs)" or "denominator in ratio").

        This method will return a ``float`` equal to ``(float(n) / float(d))``.

        If `key` is not found in parsed JSON, default to `default`.
        If the frame-rate doesn't look like ``"int/int"``, default to `default`.
        If conversion of numerator or denominator to ``int`` fails, default to
        `default`.
        If a numerator or denominator is negative or zero, default to `default`.

        (Basically, if anything goes wrong, default to `default`.)
        If `default` is not supplied, default to ``None``.

        This method will never raise an exception.
        """
        try:
            # Possible exception: `self.get_frame_rate_as_ratio(key)` fails,
            # so its "default" `default` of `None` is returned,
            # which cannot be 2-tuple deconstructed into `(n, d)`.
            (n, d) = self.get_frame_rate_as_ratio(key)
            if n <= 0 or d <= 0:
                # Either `n` or `d` (or both!) is negative or zero.
                return default
            # Possible exception: `float(n)` fails or `float(d)` fails.
            return (float(n) / float(d))
        except Exception:
            return default

    def get_avg_frame_rate(self, default=None):
        """Return ``avg_frame_rate`` as a ``float``; else `default`.

        This is the "average frame rate" over the whole video stream.

        Returns:
            ``float`` (frames per second) or `default`

        We expect that the frame-rate returned by ``ffprobe`` will be a string
        with format ``n/d``, where:

        - `n` looks like ``int`` ("total number of frames").
        - `d` looks like ``int`` ("total duration (secs)").

        This method will return a ``float`` equal to ``(float(n) / float(d))``.

        If the frame-rate doesn't look like ``"int/int"``, default to `default`.
        If conversion of numerator or denominator to ``int`` fails, default to
        `default`.
        If a numerator or denominator is negative or zero, default to `default`.

        (Basically, if anything goes wrong, default to `default`.)
        If `default` is not supplied, default to ``None``.

        This method will never raise an exception.
        """
        return self.get_frame_rate_as_float("avg_frame_rate", default=default)

    def get_r_frame_rate(self, default=None):
        """Return ``r_frame_rate`` as a ``float``; else `default`.

        This is the mysteriously-named "r frame rate":

            "The lowest framerate with which all timestamps can be represented
            accurately (it is the least common multiple of all framerates in
            the stream)."

        Returns:
            ``float`` (frames per second) or `default`

        We expect that the frame-rate returned by ``ffprobe`` will be a string
        with format ``n/d``, where:

        - `n` looks like ``int`` ("number of frames" or "numerator in ratio").
        - `d` looks like ``int`` ("duration (secs)" or "denominator in ratio").

        This method will return a ``float`` equal to ``(float(n) / float(d))``.

        If the frame-rate doesn't look like ``"int/int"``, default to `default`.
        If conversion of numerator or denominator to ``int`` fails, default to
        `default`.
        If a numerator or denominator is negative or zero, default to `default`.

        (Basically, if anything goes wrong, default to `default`.)
        If `default` is not supplied, default to ``None``.

        This method will never raise an exception.
        """
        return self.get_frame_rate_as_float("r_frame_rate", default=default)

    def get_frame_shape(self, default=None):
        """Return frame (width, height) as a pair ``(int, int)``; else `default`.

        Note that this shape is (width, height), like a human would report it;
        rather than (height, width), like in a Numpy array shape.

        If there's video "side data" that includes a rotation that's a
        multiple of 90 or 270 degrees, swap the (width, height) values
        to rotate the frame shape (orientation) accordingly.

        If `default` is not supplied, it defaults to ``None``, so this method
        will never raise a `KeyError`.

        API design note: This is a method with a name that begins with ``get_``
        (rather than simply an attribute called ``frame_shape``, for example)
        to indicate that:
            (a) It has a "default" `default` of ``None``
                (like Python's ``dict.get(key, default=None)``).
        and:
            (b) You may override this "default" `default` as a keyword argument
                (for example, if you would rather return a pair ``(None, None)``
                than a single ``None`` value, for 2-tuple deconstruction).
        """
        try:
            height = int(self.height)
            width = int(self.width)
            if self.get_frame_rotation(default=0) % 360 in (90, 270):
                # Rotate the frame shape (orientation).
                return (height, width)
            else:
                return (width, height)
        except Exception:
            return default

    def get_frame_rotation(self, default=None):
        """Return frame rotation from ``side_data`` as ``int``; else `default`.

        If `default` is not supplied, it defaults to ``None``, so this method
        will never raise an exception.
        """
        try:
            rotations = [d["rotation"] for d in self.side_data_list]
            return rotations[0]
        except Exception as e:
            return default

    def get_side_data(self, internal=False):
        """Return a list of video stream side-data.

        This method always returns a `list`, even if no `"side_data_list"`
        was found in the parsed JSON output (meaning that data attribute
        `self.side_data_list` has the value `None`).
        """
        if internal:
            # Return a reference to the internal list `self.side_data_list`.
            if self.side_data_list is None:
                # Modify internal `self.side_data_list` to be a list.
                self.side_data_list = []
            return self.side_data_list
        else:
            # Always return a new list, whether a copy or a new empty list.
            return (self.side_data_list[:] if self.side_data_list is not None else [])


_KNOWN_FFSTREAM_SUBCLASSES = dict(
    attachment= FFattachmentStream,
    audio=      FFaudioStream,
    subtitle=   FFsubtitleStream,
    video=      FFvideoStream,
)

def _construct_ffstream_subclass(parsed_json):
    codec_type = parsed_json.get('codec_type')
    if codec_type is not None:
        constructor = _KNOWN_FFSTREAM_SUBCLASSES.get(codec_type)
        if constructor is not None:
            return constructor(parsed_json)
    return FFstream(parsed_json)
