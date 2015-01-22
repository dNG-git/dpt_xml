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

# pylint: disable=invalid-name,undefined-variable

from xml.parsers import expat
import re

from .abstract_xml_parser import AbstractXmlParser, _PY_STR, _PY_UNICODE_TYPE

class XmlParserExpat(AbstractXmlParser):
#
	"""
This implementation supports expat for XML parsing.

:author:    direct Netware Group
:copyright: direct Netware Group - All rights reserved
:package:   XML.py
:since:     v0.1.00
:license:   https://www.direct-netware.de/redirect?licenses;mpl2
            Mozilla Public License, v. 2.0
	"""

	def __init__(self, parser, event_handler = None):
	#
		"""
Constructor __init__(XmlParserExpat)

:param parser: Container for the XML document
:param event_handler: EventHandler to use

:since: v0.1.00
		"""

		AbstractXmlParser.__init__(self, parser, event_handler)

		self.node_path = ""
		"""
Current node path of the parser
		"""
		self.node_path_list = [ ]
		"""
Current path as an array of node tags
		"""
		self.node_path_depth = 0
		"""
Current depth
		"""
		self.parser_active = False
		"""
True if not the last element has been reached
		"""
		self.parser_cache = { }
		"""
Parser data cache
		"""
		self.parser_cache_counter = 0
		"""
Cache entry counter
		"""
		self.parser_cache_link = ""
		"""
Links to the latest entry added
		"""
	#

	def _get_merged_result(self):
	#
		"""
Returns the merged result of an expat parsing operation if the parser
completed its work.

:return: (dict) Merged XML tree; None on error
:since:  v0.1.00
		"""

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -{0!r}._get_merged_result()- (#echo(__LINE__)#)".format(self))
		_return = None

		if ((not self.parser_active) and type(self.parser_cache) is dict and len(self.parser_cache) > 0):
		#
			_return = self.parser_cache
			self.parser_cache = { }
		#

		return _return
	#

	def handle_cdata(self, data):
	#
		"""
python.org: Called for character data. This will be called for normal
character data, CDATA marked content, and ignorable whitespace. Applications
which must distinguish these cases can use the StartCdataSectionHandler,
EndCdataSectionHandler, and ElementDeclHandler callbacks to collect the
required information.

:param data: Character data

:since: v0.1.00
		"""

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -{0!r}.handle_cdata()- (#echo(__LINE__)#)".format(self))

		if (self.parser_active):
		#
			if ("value" in self.parser_cache[self.parser_cache_link[self.node_path]]): self.parser_cache[self.parser_cache_link[self.node_path]]['value'] += data
			else: self.parser_cache[self.parser_cache_link[self.node_path]]['value'] = data
		#
	#

	def handle_element_end(self, name):
	#
		"""
Method to handle "end element" callbacks.

:param name: XML tag

:since: v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (str is not _PY_UNICODE_TYPE and type(name) is _PY_UNICODE_TYPE): name = _PY_STR(name, "utf-8")

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -{0!r}.handle_element_end({1})- (#echo(__LINE__)#)".format(self, name))

		if (self.parser_active):
		#
			node_path = self.parser_cache_link[self.node_path]

			del(self.parser_cache_link[self.node_path])
			self.node_path_list.pop()
			self.node_path_depth -= 1
			self.node_path = " ".join(self.node_path_list)

			if ("value" not in self.parser_cache[node_path]): self.parser_cache[node_path]['value'] = ""
			elif ("xml:space" not in self.parser_cache[node_path]['attributes']
			      or self.parser_cache[node_path]['attributes']['xml:space'] != "preserve"
			     ): self.parser_cache[node_path]['value'] = self.parser_cache[node_path]['value'].strip()

			if ((not self.strict_standard_mode)
			    and "value" in self.parser_cache[node_path]['attributes']
			    and len(self.parser_cache[node_path]['value']) < 1
			   ):
			#
				self.parser_cache[node_path]['value'] = self.parser_cache[node_path]['attributes']['value']
				del(self.parser_cache[node_path]['attributes']['value'])
			#

			if (self.node_path_depth < 1):
			#
				self.node_path = ""
				self.parser_active = False
			#
		#
	#

	def handle_cdata_merged(self, data):
	#
		"""
python.org: Called for character data. This will be called for normal
character data, CDATA marked content, and ignorable whitespace. Applications
which must distinguish these cases can use the StartCdataSectionHandler,
EndCdataSectionHandler, and ElementDeclHandler callbacks to collect the
required information. (Merged XML parser)

:param data: Character data

:since: v0.1.00
		"""

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -{0!r}.handle_cdata_merged()- (#echo(__LINE__)#)".format(self))

		if (self.parser_active):
		#
			if (self.parser_cache_link[self.node_path] > 0): self.parser_cache[self.node_path][self.parser_cache_link[self.node_path]]['value'] += data
			else: self.parser_cache[self.node_path]['value'] += data
		#
	#

	def handle_element_end_merged(self, name):
	#
		"""
Method to handle "end element" callbacks. (Merged XML parser)

:param name: XML tag

:since: v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (str is not _PY_UNICODE_TYPE and type(name) is _PY_UNICODE_TYPE): name = _PY_STR(name, "utf-8")

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -{0!r}.handle_element_end_merged({1})- (#echo(__LINE__)#)".format(self, name))

		if (self.parser_active):
		#
			node_ptr = (self.parser_cache[self.node_path][self.parser_cache_link[self.node_path]]
			            if (self.parser_cache_link[self.node_path] > 0) else
			            self.parser_cache[self.node_path]
			           )

			self.node_path_list.pop()
			self.node_path_depth -= 1
			self.node_path = "_".join(self.node_path_list)

			if ("xml:space" not in node_ptr['attributes']): node_ptr['value'] = node_ptr['value'].strip()
			elif (node_ptr['attributes']['xml:space'] != "preserve"): node_ptr['value'] = node_ptr['value'].strip()

			if ("value" in node_ptr['attributes'] and len(node_ptr['value']) < 1):
			#
				node_ptr['value'] = node_ptr['attributes']['value']
				del(node_ptr['attributes']['value'])
			#

			if (self.node_path_depth < 1):
			#
				self.node_path = ""
				self.parser_active = False
			#
		#
	#

	def handle_element_start_merged(self, name, attributes):
	#
		"""
Method to handle "start element" callbacks. (Merged XML parser)

:param name: XML tag
:param attributes: Node attributes

:since: v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (str is not _PY_UNICODE_TYPE and type(name) is _PY_UNICODE_TYPE): name = _PY_STR(name, "utf-8")

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -{0!r}.handle_element_start_merged({1})- (#echo(__LINE__)#)".format(self, name))

		if (not self.parser_active):
		#
			self.node_path = ""
			self.node_path_depth = 0
			self.parser_active = True
			self.parser_cache_link = { }
		#

		name = name.lower()
		if (name[:12] == "digitstart__"): name = name[12:]

		if (len(self.node_path) > 0): self.node_path += "_"
		self.node_path += name
		self.node_path_list.append(name)
		self.node_path_depth += 1

		for key in attributes:
		#
			if (str is not _PY_UNICODE_TYPE and type(key) is _PY_UNICODE_TYPE): key = _PY_STR(key, "utf-8")
			key_lowercase = key.lower()
			value = attributes[key]

			if (key_lowercase.startswith("xmlns:")):
			#
				attributes["xmlns:{0}".format(key[6:])] = value
				if (key[:6] != "xmlns:"): del(attributes[key])
			#
			elif (key_lowercase == "xml:space"):
			#
				attributes[key_lowercase] = value.lower()
				if (key != key_lowercase): del(attributes[key])
			#
			elif (key != key_lowercase):
			#
				del(attributes[key])
				attributes[key_lowercase] = value
			#
		#

		node_dict = { "tag": name, "level": self.node_path_depth, "value": "", "attributes": attributes }

		if (self.node_path in self.parser_cache):
		#
			if ("tag" in self.parser_cache[self.node_path]): self.parser_cache[self.node_path] = [ self.parser_cache[self.node_path], node_dict ]
			else: self.parser_cache[self.node_path].append(node_dict)

			self.parser_cache_link[self.node_path] += 1
		#
		else:
		#
			self.parser_cache[self.node_path] = node_dict
			self.parser_cache_link[self.node_path] = 0
		#
	#

	def handle_element_start(self, name, attributes):
	#
		"""
Method to handle "start element" callbacks.

:param name: XML tag
:param attributes: Node attributes

:since: v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (str is not _PY_UNICODE_TYPE and type(name) is _PY_UNICODE_TYPE): name = _PY_STR(name, "utf-8")

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -{0!r}.handle_element_start({1})- (#echo(__LINE__)#)".format(self, name))

		if (not self.parser_active):
		#
			self.node_path = ""
			self.node_path_depth = 0
			self.parser_active = True
			self.parser_cache_counter = 0
			self.parser_cache_link = { }
		#

		if (not self.strict_standard_mode):
		#
			name = name.lower()
			if (name[:12] == "digitstart__"): name = name[12:]
		#

		if (len(self.node_path) > 0): self.node_path += " "
		self.node_path += name
		self.node_path_list.append(name)
		self.node_path_depth += 1

		for key in attributes:
		#
			if (str is not _PY_UNICODE_TYPE and type(key) is _PY_UNICODE_TYPE): key = _PY_STR(key, "utf-8")
			key_lowercase = key.lower()
			value = attributes[key]

			if (key_lowercase.startswith("xmlns:")):
			#
				attributes["xmlns:{0}".format(key[6:])] = value
				if (key[:6] != "xmlns:"): del(attributes[key])
			#
			elif (key_lowercase == "xml:space"):
			#
				attributes[key_lowercase] = value.lower()
				if (key != key_lowercase): del(attributes[key])
			#
			elif ((not self.strict_standard_mode) and key != key_lowercase):
			#
				del(attributes[key])
				attributes[key_lowercase] = value
			#
		#

		self.parser_cache[self.parser_cache_counter] = { "node_path": self.node_path, "attributes": attributes }
		self.parser_cache_link[self.node_path] = self.parser_cache_counter
		self.parser_cache_counter += 1
	#

	def parse(self, data):
	#
		"""
Parses a given XML string and return the result in the format set by
"set_mode()" and "set_strict_standard()".

:return: (dict) Multi-dimensional or merged XML tree; None on error
:since:  v0.1.01
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -{0!r}.parse()- (#echo(__LINE__)#)".format(self))

		if (re.search("<\\?xml(.+?)encoding=", data) is None):
		#
			parser_ptr = expat.ParserCreate("UTF-8")
			if (str is not _PY_UNICODE_TYPE and type(data) is _PY_UNICODE_TYPE): data = _PY_STR(data, "utf-8")
		#
		else: parser_ptr = expat.ParserCreate()

		if (self.merged_mode):
		#
			parser_ptr.CharacterDataHandler = self.handle_cdata_merged
			parser_ptr.StartElementHandler = self.handle_element_start_merged
			parser_ptr.EndElementHandler = self.handle_element_end_merged
			parser_ptr.Parse(data, True)

			_return = self._get_merged_result()
		#
		else:
		#
			parser_ptr.CharacterDataHandler = self.handle_cdata
			parser_ptr.StartElementHandler = self.handle_element_start
			parser_ptr.EndElementHandler = self.handle_element_end
			parser_ptr.Parse(data, True)

			self._update_parser_with_result()
			_return = self.parser.get()
		#

		return _return
	#

	def _update_parser_with_result(self):
	#
		"""
Adds the result of an expat parsing operation to the defined XML instance if
the parser completed its work.

:return: (dict) Multi-dimensional XML tree; None on error
:since:  v0.1.00
		"""

		if (self.event_handler is not None): self.event_handler.debug("#echo(__FILEPATH__)# -{0!r}._update_parser_with_result()- (#echo(__LINE__)#)".format(self))
		_return = None

		if ((not self.parser_active) and type(self.parser_cache) is dict and len(self.parser_cache) > 0):
		#
			self.parser.set({ })

			for node_key in self.parser_cache:
			#
				node_dict = self.parser_cache[node_key]
				self.parser.add_node(node_dict['node_path'], node_dict['value'], node_dict['attributes'])
			#

			self.parser_cache = { }
		#

		return _return
	#
#

##j## EOF