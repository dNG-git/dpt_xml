# -*- coding: utf-8 -*-

"""
direct Python Toolbox
All-in-one toolbox to encapsulate Python runtime variants
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?dpt;xml

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(dptXmlVersion)#
#echo(__FILEPATH__)#
"""

# pylint: disable=invalid-name

from weakref import proxy, ProxyTypes

try:
    _PY_STR = unicode.encode
    _PY_UNICODE_TYPE = unicode
except NameError:
    _PY_STR = bytes.decode
    _PY_UNICODE_TYPE = str
#

class AbstractXmlParser(object):
    """
This abstract class provides the setters used for different XML parser
implementations.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    dpt
:subpackage: xml
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    # pylint: disable=unused-argument

    MODE_MERGED = 1
    """
Non standard compliant merged parser mode
    """
    MODE_TREE = 2
    """
Tree parsing mode
    """

    __slots__ = [ "_log_handler", "_merged_mode", "parser", "_strict_mode" ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self, parser, log_handler = None):
        """
Constructor __init__(XmlParserExpat)

:param parser: Container for the XML document
:param log_handler: Log handler to use

:since: v1.0.0
        """

        if (log_handler is not None): log_handler.debug("#echo(__FILEPATH__)# -{0!r}.__init__()- (#echo(__LINE__)#)".format(self))

        self._log_handler = None
        """
The log handler is called whenever debug messages should be logged or errors
happened.
        """
        self._merged_mode = False
        """
True if the parser is set to merged
        """
        self.parser = parser
        """
Container for the XML document
        """
        self._strict_mode = True
        """
True to be standard conform
        """
    #

    @property
    def log_handler(self):
        """
Returns the log handler.

:return: (object) Log handler in use
:since:  v1.0.0
        """

        return self._log_handler
    #

    @log_handler.setter
    def log_handler(self, log_handler):
        """
Sets the log handler.

:param log_handler: Log handler to use

:since: v1.0.0
        """

        self._log_handler = (log_handler if (isinstance(log_handler, ProxyTypes)) else proxy(log_handler))
    #

    @property
    def mode(self):
        """
Returns the parser mode used.

:return: (int) Mode used
:since:  v1.0.0
        """

        return (AbstractXmlParser.MODE_MERGED if (self._merged_mode) else AbstractXmlParser.MODE_TREE)
    #

    @mode.setter
    def mode(self, mode = 1):
        """
Define the parser mode MODE_MERGED or MODE_TREE.

:param mode: Mode to select

:since: v1.0.0
        """

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -{0!r}.mode({1:d})- (#echo(__LINE__)#)".format(self, mode))

        self._merged_mode = (mode == AbstractXmlParser.MODE_MERGED)
    #

    @property
    def strict_standard_mode(self):
        """
Returns true if the parser mode is set to be strict standard compliant.

:return: (bool) True if strict standard compliant
:since:  v1.0.0
        """

        return self._strict_mode
    #

    @strict_standard_mode.setter
    def strict_standard_mode(self, strict_mode):
        """
Changes the parser mode regarding being strict standard compliant.

:param strict_standard_mode: True to be standard compliant

:since: v1.0.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -{0!r}.strict_standard_mode()- (#echo(__LINE__)#)".format(self))

        _type = type(strict_mode)

        if ((_type is bool and strict_mode) or (_type is str and strict_mode == "1")): self._strict_mode = True
        elif (strict_mode is None and (not self._strict_mode)): self._strict_mode = True
        else: self._strict_mode = False
    #

    def parse(self, data):
        """
Parses a given XML string and return the result in the format set by "mode"
and "strict_standard_mode".

:return: (dict) Multi-dimensional or merged XML tree; None on error
:since:  v1.0.0
        """

        raise RuntimeError("Not implemented")
    #
#
