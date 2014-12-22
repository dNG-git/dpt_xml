# -*- coding: utf-8 -*-
##j## BOF

"""
XML.py
Multiple XML parsers: Common abstraction layer
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?py;xml

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(pyXmlVersion)#
#echo(__FILEPATH__)#
"""

# pylint: disable=invalid-name

try:
#
	_PY_STR = unicode.encode
	_PY_UNICODE_TYPE = unicode
#
except NameError:
#
	_PY_STR = bytes.decode
	_PY_UNICODE_TYPE = str
#

class AbstractXmlParser(object):
#
	"""
This abstract class provides the setters used for different XML parser
implementations.

:author:    direct Netware Group
:copyright: direct Netware Group - All rights reserved
:package:   XML.py
:since:     v0.1.00
:license:   https://www.direct-netware.de/redirect?licenses;mpl2
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

	def __init__(self, parser, event_handler = None):
	#
		"""
Constructor __init__(XmlParserExpat)

:param parser: Container for the XML document
:param event_handler: EventHandler to use

:since: v0.1.00
		"""

		if (event_handler is not None): event_handler.debug("#echo(__FILEPATH__)# -{0!r}.__init__()- (#echo(__LINE__)#)".format(self))

		self.merged_mode = False
		"""
True if the parser is set to merged
		"""
		self.event_handler = event_handler
		"""
The EventHandler is called whenever debug messages should be logged or errors
happened.
		"""
		self.parser = parser
		"""
Container for the XML document
		"""
		self.strict_standard_mode = True
		"""
True to be standard conform
		"""
	#

	def parse(self, data):
	#
		"""
Parses a given XML string and return the result in the format set by
"set_mode()" and "set_strict_standard()".

:return: (dict) Multi-dimensional or merged XML tree; None on error
:since:  v0.1.01
		"""

		raise RuntimeError("Not implemented")
	#

	def set_mode(self, mode = 1):
	#
		"""
Define the parser mode MODE_MERGED or MODE_TREE.

:param mode: Mode to select

:since: v0.1.00
		"""

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_mode({1:d})- (#echo(__LINE__)#)".format(self, mode))

		self.merged_mode = (mode == AbstractXmlParser.MODE_MERGED)
	#

	def set_strict_standard(self, strict_standard_mode):
	#
		"""
Changes the parser mode regarding being strict standard compliant.

:param strict_standard_mode: True to be standard compliant

:since: v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -{0!r}.set_strict_standard(strict_standard_mode)- (#echo(__LINE__)#)".format(self))

		if (str != _PY_UNICODE_TYPE and type(strict_standard_mode) == _PY_UNICODE_TYPE): strict_standard_mode = _PY_STR(strict_standard_mode, "utf-8")
		_type = type(strict_standard_mode)

		if ((_type == bool or _type == str) and strict_standard_mode): self.strict_standard_mode = True
		elif (strict_standard_mode is None and (not self.strict_standard_mode)): self.strict_standard_mode = True
		else: self.strict_standard_mode = False
	#
#

##j## EOF