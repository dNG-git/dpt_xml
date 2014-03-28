# -*- coding: utf-8 -*-
##j## BOF

"""
XML.py
Multiple XML parsers: Common abstraction layer
"""
"""n// NOTE
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?py;xml

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.py?licenses;mpl2
----------------------------------------------------------------------------
#echo(pyXmlVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

# pylint: disable=import-error,invalid-name,unused-import

from cgi import escape as html_escape
import re

try:
#
	import java.lang.System
	_mode = "java"
#
except ImportError: _mode = None

try:
#
	import clr
	clr.AddReference("System.Xml")
	from System.IO import StringReader
	from System.Xml import XmlDocument, XmlNodeReader

	from .xml_parser_MonoXML import XmlParserMonoXml
	_mode = "mono"
#
except ImportError: pass

if (_mode == None):
#
	from xml.parsers import expat

	from .xml_parser_expat import XmlParserExpat
	_mode = "py"
#

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

class XmlParser(object):
#
	"""
This class provides a bridge between Python and XML to read XML on the fly.

:author:    direct Netware Group
:copyright: direct Netware Group - All rights reserved
:package:   XML.py
:since:     v1.0.0
:license:   http://www.direct-netware.de/redirect.py?licenses;mpl2
            Mozilla Public License, v. 2.0
	"""

	RE_ATTRIBUTES_XMLNS = re.compile("xmlns\\:", re.I)
	"""
RegExp to find xmlns attributes
	"""
	RE_NODE_NAME_XMLNS = re.compile("^(.+):(\\w+)$")
	"""
RegExp to split XML namespace node names
	"""
	RE_NODE_POSITION = re.compile("^(.+)\\#(\\d+)$")
	"""
RegExp to find node names with a specified position in a list
	"""
	RE_TAG_DIGIT = re.compile("^\\d")
	"""
RegExp to find node names starting with a number (and are not standard
compliant)
	"""

	def __init__(self, xml_charset = "UTF-8", parse_only = True, node_type = dict, timeout_retries = 5, event_handler = None):
	#
		"""
Constructor __init__(XmlParser)

:param xml_charset: Charset to be added as information to XML output
:param parse_only: Parse data only
:param node_type: Dict implementation for new nodes
:param timeout_retries: Retries before timing out
:param event_handler: EventHandler to use

:since: v0.1.00
		"""

		# global: _mode

		self.data = None
		"""
XML data
		"""
		self.data_cache_node = ""
		"""
Path of the cached node pointer
		"""
		self.data_cache_ptr = None
		"""
Reference of the cached node pointer (string if unset)
		"""
		self.data_charset = xml_charset.upper()
		"""
Charset used
		"""
		self.data_cdata_encoding = True
		"""
Put embedded XML in a CDATA node
		"""
		self.data_ns = { }
		"""
Cache for known XML NS (URI)
		"""
		self.data_ns_compact = { }
		"""
Cache for the compact number of a XML NS
		"""
		self.data_ns_counter = 0
		"""
Counter for the compact link numbering
		"""
		self.data_ns_default = { }
		"""
Cache for the XML NS and the corresponding number
		"""
		self.data_ns_predefined_compact = { }
		"""
Cache of node paths with a predefined NS (key = Compact name)
		"""
		self.data_ns_predefined_default = { }
		"""
Cache of node paths with a predefined NS (key = Full name)
		"""
		self.data_parse_only = parse_only
		"""
Parse data only
		"""
		self.data_parser = None
		"""
The selected parser implementation
		"""
		self.event_handler = event_handler
		"""
The EventHandler is called whenever debug messages should be logged or errors
happened.
		"""
		self.node_type = node_type
		"""
Dict implementation used to create new nodes
		"""

		if (_mode == "mono"): self.data_parser = XmlParserMonoXml(self, timeout_retries, event_handler)
		else: self.data_parser = XmlParserExpat(self, event_handler)
	#

	def define_cdata_encoding(self, use_cdata = True):
	#
		"""
Uses or disables CDATA nodes to encode embedded XML.

:param use_cdata: Use CDATA nodes

:return: (bool) Accepted state
:since:  v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (str != _PY_UNICODE_TYPE and type(use_cdata) == _PY_UNICODE_TYPE): use_cdata = _PY_STR(use_cdata, "utf-8")
		_type = type(use_cdata)

		if ((_type == bool or _type == str) and use_cdata): self.data_cdata_encoding = True
		elif (use_cdata == None and (not self.data_cdata_encoding)): self.data_cdata_encoding = True
		else: self.data_cdata_encoding = False

		return self.data_cdata_encoding
	#

	def define_parse_only(self, parse_only = True):
	#
		"""
Changes the object behaviour of deleting cached data after parsing is
completed.

:param parse_only: Parse data only

:return: (bool) Accepted state
:since:  v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (str != _PY_UNICODE_TYPE and type(parse_only) == _PY_UNICODE_TYPE): parse_only = _PY_STR(parse_only, "utf-8")
		_type = type(parse_only)

		if ((_type == bool or _type == str) and parse_only): self.data_parse_only = True
		elif (parse_only == None and (not self.data_parse_only)): self.data_parse_only = True
		else: self.data_parse_only = False

		return self.data_parse_only
	#

	def dict_to_xml(self, xml_tree, strict_standard = True):
	#
		"""
Builds recursively a valid XML ouput reflecting the given XML dict tree.

:param xml_tree: XML dict tree level to work on
:param strict_standard: Be standard conform

:return: (str) XML output string
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.dict_to_xml(xml_tree, strict_standard)- (#echo(__LINE__)#)")
		_return = ""

		if (isinstance(xml_tree, dict) and len(xml_tree) > 0):
		#
			for xml_node in xml_tree:
			#
				xml_node_dict = xml_tree[xml_node]

				if ("xml.mtree" in xml_node_dict):
				#
					del(xml_node_dict['xml.mtree'])
					_return += self.dict_to_xml(xml_node_dict, strict_standard)
				#
				elif ("xml.item" in xml_node_dict):
				#
					_return += self.dict_to_xml_item_encoder (xml_node_dict['xml.item'], False, strict_standard)

					xml_node_tag = (
						xml_node_dict['xml.item']['tag']
						if (XmlParser.RE_TAG_DIGIT.match(xml_node_dict['xml.item']['tag']) == None) else
						"digitstart__{0}".format(xml_node_dict['xml.item']['tag'])
					)

					del(xml_node_dict['xml.item'])
					_return += "{0}</{1}>".format(self.dict_to_xml(xml_node_dict, strict_standard), xml_node_tag)
				#
				elif (len(xml_node_dict['tag']) > 0): _return += self.dict_to_xml_item_encoder(xml_node_dict, True, strict_standard)
			#
		#

		return _return.strip()
	#

	def dict_to_xml_item_encoder(self, data, close_tag = True, strict_standard = True):
	#
		"""
Builds recursively a valid XML ouput reflecting the given XML dict tree.

:param data: Dict containing information about the current item
:param close_tag: Output will contain an ending tag if true
:param strict_standard: Be standard conform

:access: protected
:return: (str) XML output string
:since:  v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		_return = ""

		is_value_attr_compatible = (False if (strict_standard) else True)

		if (isinstance(data, dict)):
		#
			if (len(data['tag']) > 0):
			#
				if (re.match("\\d", data['tag']) != None): data['tag'] = "digitstart__{0}".format(data['tag'])
				_return += "<{0}".format(data['tag'])

				if ("attributes" in data):
				#
					for key in data['attributes']:
					#
						if (is_value_attr_compatible and key == "value" and len(data['value']) < 1): data['value'] = data['attributes'][key]
						else:
						#
							type_value = type(data['attributes'][key])

							if (type_value == int or type_value == float): value = str(data['attributes'][key])
							elif (data['attributes'][key] == None): value = ""
							else:
							#
								value = data['attributes'][key]

								if (str != _PY_UNICODE_TYPE and type_value == _PY_UNICODE_TYPE): value = _PY_STR(value, "utf-8")
								value = value.replace("&", "&amp;")
								value = value.replace("<", "&lt;")
								value = value.replace(">", "&gt;")
								value = value.replace('"', "&quot;")
								if (self.data_charset != "UTF-8"): value = value.encode(self.data_charset)
							#

							_return += " {0}=\"{1}\"".format(key, value)
						#
					#
				#

				if (is_value_attr_compatible and "value" in data):
				#
					type_value = type(data['value'])

					if (type_value == int or type_value == float): data['value'] = str(data['value'])
					else:
					#
						if (str != _PY_UNICODE_TYPE and type_value == _PY_UNICODE_TYPE): data['value'] = _PY_STR(data['value'], "utf-8")

						if (is_value_attr_compatible):
						#
							if ("&" in data['value']): is_value_attr_compatible = False
							elif ("<" in data['value']): is_value_attr_compatible = False
							elif (">" in data['value']): is_value_attr_compatible = False
							elif ('"' in data['value']): is_value_attr_compatible = False
							elif (re.search("\\s", data['value'].replace(" ","_")) != None): is_value_attr_compatible = False
						#
					#

					if (is_value_attr_compatible):
					#
						if (self.data_charset != "UTF-8"): data['value'] = data['value'].encode(self.data_charset)
						_return += " value=\"{0}\"".format(data['value'])
					#
				#

				if (is_value_attr_compatible and close_tag): _return += " />"
				else:
				#
					_return += ">"

					if ("value" in data):
					#
						if (str != _PY_UNICODE_TYPE and type(data['value']) == _PY_UNICODE_TYPE): data['value'] = _PY_STR(data['value'], "utf-8")
						if (self.data_charset != "UTF-8"): data['value'] = data['value'].encode(self.data_charset)

						if ("<" not in data['value'] and ">" not in data['value']): _return += data['value'].replace("&", "&amp;")
						elif (self.data_cdata_encoding):
						#
							if ("]]>" in data['value']): data['value'] = data['value'].replace("]]>", "]]]]><![CDATA[>")
							_return += "<![CDATA[{0}]]>".format(data['value'])
						#
						else: _return += html_escape(data['value'], True)
					#

					if (close_tag): _return += "</{0}>".format(data['tag'])
				#
			#
		#

		return _return
	#

	def get(self):
	#
		"""
This operation just gives back the content of self.data.

:return: (dict) XML dict tree; None if not parsed error
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.get()- (#echo(__LINE__)#)")
		return self.data
	#

	def node_add(self, node_path, value = "", attributes = "", add_recursively = True):
	#
		"""
Adds a XML node with content - recursively if required.

:param node_path: Path to the new node - delimiter is space
:param value: Value for the new node
:param attributes: Attributes of the node
:param add_recursively: True to create the required tree recursively

:return: (bool) False on error
:since:  v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (str != _PY_UNICODE_TYPE and type(node_path) == _PY_UNICODE_TYPE): node_path = _PY_STR(node_path, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.node_add({0}, value, attributes, add_recursively)- (#echo(__LINE__)#)".format(node_path))
		_return = False

		if (self.data == None): self.data = self.node_type()
		type_value = type(value)

		if (type(node_path) == str and type_value == str or type_value == _PY_UNICODE_TYPE):
		#
			node_path = self._ns_translate_path(node_path)

			if (self.data_cache_node == "" or re.match("^{0}".format(re.escape(node_path)), self.data_cache_node,re.I) == None):
			#
				node_path_done = ""
				node_ptr = self.data
			#
			else:
			#
				node_path = node_path[len(self.data_cache_node):].strip()
				node_path_done = self.data_cache_node
				node_ptr = self.data_cache_ptr
			#

			is_available = True
			nodes_list = node_path.split(" ")

			while (is_available and len(nodes_list) > 0):
			#
				is_available = False
				node_name = nodes_list.pop(0)
				re_result = XmlParser.RE_NODE_POSITION.match(node_name)

				if (re_result == None): node_position = -1
				else:
				#
					node_name = re_result.group(1)
					node_position = int(re_result.group(2))
				#

				if (len(nodes_list) > 0):
				#
					if (node_name in node_ptr):
					#
						if ("xml.mtree" in node_ptr[node_name]):
						#
							if (node_position >= 0):
							#
								if (node_position in node_ptr[node_name]):
								#
									is_available = True
									_return = True
								#
							#
							elif (node_ptr[node_name]['xml.mtree'] in node_ptr[node_name]):
							#
								is_available = True
								node_position = node_ptr[node_name]['xml.mtree']
								_return = True
							#

							if (is_available):
							#
								if (
									(not isinstance(node_ptr[node_name][node_position], dict)) or
									"xml.item" not in node_ptr[node_name][node_position]
								): node_ptr[node_name][node_position] = { "xml.item": node_ptr[node_name][node_position] }

								node_ptr = node_ptr[node_name][node_position]
							#
						#
						elif ("xml.item" in node_ptr[node_name]):
						#
							is_available = True
							node_ptr = node_ptr[node_name]
						#
						else:
						#
							is_available = True
							self._node_covert_intermediate(node_ptr, node_path_done, node_name)
							node_ptr = node_ptr[node_name]
						#
					#

					if ((not is_available) and add_recursively):
					#
						node_dict = self.node_type(tag = node_name, level = 1, xmlns = { })

						if ("xml.item" in node_ptr):
						#
							if ("level" in node_ptr['xml.item']): node_dict['level'] = (1 + node_ptr['xml.item']['level'])
							if ("xmlns" in node_ptr['xml.item']): node_dict['xmlns'] = node_ptr['xml.item']['xmlns'].copy()
						#

						self._node_add_ns_cache(node_path_done, node_name, node_dict)

						is_available = True
						node_ptr[node_name] = self.node_type([ ( "xml.item", node_dict ) ])
						node_ptr = node_ptr[node_name]
					#
				#
				else:
				#
					node_dict = self.node_type(tag = node_name, value = value, xmlns = { })

					if ("xml.item" in node_ptr and "xmlns" in node_ptr['xml.item']): node_dict['xmlns'] = node_ptr['xml.item']['xmlns'].copy()

					if (isinstance(attributes, dict) and len(attributes) > 0):
					#
						if ("xmlns" in attributes):
						#
							if (len(attributes['xmlns']) > 0):
							#
								if (attributes['xmlns'] in self.data_ns_default): node_dict['xmlns']['@'] = self.data_ns_default[attributes['xmlns']]
								else:
								#
									self.data_ns_counter += 1
									self.data_ns_default[attributes['xmlns']] = self.data_ns_counter
									self.data_ns_compact[self.data_ns_counter] = attributes['xmlns']
									node_dict['xmlns']['@'] = self.data_ns_counter
								#
							#
							elif ("@" in node_dict['xmlns']): del(node_dict['xmlns']['@'])
						#

						for key in attributes:
						#
							value = attributes[key]
							type_value = type(value)

							if ((type_value == str or type_value == _PY_UNICODE_TYPE) and XmlParser.RE_ATTRIBUTES_XMLNS.match(key) != None):
							#
								ns_name = key[6:]

								if (len(value) > 0): node_dict['xmlns'][ns_name] = (self.data_ns_default[value] if (value in self.data_ns_default) else value)
								elif (ns_name in node_dict['xmlns']): del(node_dict['xmlns'][ns_name])
							#
						#

						node_dict['attributes'] = attributes
					#

					self._node_add_ns_cache(node_path_done, node_name, node_dict)

					if (node_name in node_ptr):
					#
						if ((not isinstance(node_ptr[node_name], dict)) or "xml.mtree" not in node_ptr[node_name]):
						#
							node_ptr[node_name] = self.node_type([ ( 0, node_ptr[node_name] ), ( 1, node_dict ) ])
							node_ptr[node_name]['xml.mtree'] = 1
						#
						else:
						#
							node_ptr[node_name]['xml.mtree'] += 1
							node_ptr[node_name][node_ptr[node_name]['xml.mtree']] = node_dict
						#
					#
					else: node_ptr[node_name] = node_dict

					_return = True
				#

				if (len(node_path_done) > 0): node_path_done += " "
				node_path_done += node_name
			#
		#

		return _return
	#

	def _node_add_ns_cache(self, node_path_done, node_name, node_dict):
	#
		"""
Caches XML namespace data for the given XML node.

:param node_path_done: XML node path containing the given XML node
:param node_name: XML node name
:param node_dict: XML node

:since: v0.1.00
		"""

		node_ns_name = ""
		re_result = XmlParser.RE_NODE_NAME_XMLNS.match(node_name)

		if (re_result != None):
		#
			if (
				re_result.group(1) in node_dict['xmlns'] and
				type(node_dict['xmlns'][re_result.group(1)]) == int
			): node_ns_name = "{0}:{1}".format(node_dict['xmlns'][re_result.group(1)], re_result.group(2))
		#
		elif ("@" in node_dict['xmlns']): node_ns_name = "{0}:{1}".format(node_dict['xmlns']['@'], node_name)

		if (len(node_path_done) > 0):
		#
			self.data_ns_predefined_compact["{0} {1}".format(node_path_done, node_name)] = "{0} {1}".format(
				self.data_ns_predefined_compact[node_path_done],
				(node_name if (node_ns_name == "") else node_ns_name)
			)

			self.data_ns_predefined_default[self.data_ns_predefined_compact["{0} {1}".format(node_path_done, node_name)]] = "{0} {1}".format(node_path_done, node_name)
		#
		elif (node_ns_name == ""):
		#
			self.data_ns_predefined_compact[node_name] = node_name
			self.data_ns_predefined_default[node_name] = node_name
		#
		else:
		#
			self.data_ns_predefined_compact[node_name] = node_ns_name
			self.data_ns_predefined_default[node_ns_name] = node_name
		#
	#

	def _node_covert_intermediate(self, node_ptr, node_path_done, node_name):
	#
		"""
Caches XML namespace data for the given XML node.

:param node_ptr: Parent XML node pointer
:param node_path_done: XML node path containing the given XML node
:param node_name: XML leaf name to be converted to a node

:since: v0.1.00
		"""

		node_ptr[node_name]['level'] = (
			(1 + node_ptr['xml.item']['level'])
			if ("xml.item" in node_ptr and "level" in node_ptr['xml.item']) else
			1
		)

		node_ptr[node_name] = self.node_type([ ( "xml.item", node_ptr[node_name] ) ])
		node_ptr = node_ptr[node_name]

		if (self.data_cache_node != ""):
		#
			node_path_changed = ("{0} {1}".format(node_path_done, node_name) if (len(node_path_done) > 0) else node_name)
			if (self.data_cache_node == node_path_changed): self.data_cache_ptr = node_ptr
		#
	#

	def ns_register(self, ns, uri):
	#
		"""
Registers a namespace (URI) for later use with this XML reader instance.

:param ns: Output relevant namespace definition
:param uri: Uniform Resource Identifier

:since: v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (str != _PY_UNICODE_TYPE):
		#
			if (type(ns) == _PY_UNICODE_TYPE): ns = _PY_STR(ns, "utf-8")
			if (type(uri) == _PY_UNICODE_TYPE): uri = _PY_STR(uri, "utf-8")
		#

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.ns_register({0}, {1})- (#echo(__LINE__)#)".format(ns, uri))
		self.data_ns[ns] = uri

		if (uri not in self.data_ns_default):
		#
			self.data_ns_counter += 1
			self.data_ns_default[uri] = self.data_ns_counter
			self.data_ns_compact[self.data_ns_counter] = uri
		#
	#

	def ns_translate(self, node):
	#
		"""
Translates the tag value if a predefined namespace matches. The translated
tag will be saved as "tag_ns" and "tag_parsed".

:param node: XML tree node

:return: (dict) Checked XML tree node
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.ns_translate(node)- (#echo(__LINE__)#)")
		_return = node

		if (isinstance(node, dict) and "tag" in node and "xmlns" in node and isinstance(node['xmlns'], dict)):
		#
			_return['tag_ns'] = ""
			_return['tag_parsed'] = node['tag']

			re_result = XmlParser.RE_NODE_NAME_XMLNS.match(node['tag'])

			if (re_result != None and re_result.group(1) in node['xmlns'] and node['xmlns'][re_result.group(1)] in self.data_ns_compact):
			#
				tag_ns = XmlParser._dict_search(self.data_ns_compact[node['xmlns'][re_result.group(1)]] ,self.data_ns)

				if (tag_ns != None):
				#
					_return['tag_ns'] = tag_ns
					_return['tag_parsed'] = "{0}:{1}".format(tag_ns, re_result.group(2))
				#
			#

			if ("attributes" in node):
			#
				for key in node['attributes']:
				#
					re_result = XmlParser.RE_NODE_NAME_XMLNS.match(key)

					if (re_result != None and re_result.group(1) in node['xmlns'] and node['xmlns'][re_result.group(1)] in self.data_ns_compact):
					#
						tag_ns = XmlParser._dict_search(self.data_ns_compact[node['xmlns'][re_result.group(1)]], self.data_ns)

						if (tag_ns != None):
						#
							_return['attributes']["{0}:{1}".format(tag_ns, re_result.group(2))] = node['attributes'][key]
							del(_return['attributes'][key])
						#
					#
				#
			#
		#

		return _return
	#

	def _ns_translate_path(self, node_path):
	#
		"""
Checks input path for predefined namespaces converts it to the internal
path.

:param node_path: Path to the new node; delimiter is space

:return: (str) Output node path
:since:  v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (str != _PY_UNICODE_TYPE and type(node_path) == _PY_UNICODE_TYPE): node_path = _PY_STR(node_path, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml._ns_translate_path({0})- (#echo(__LINE__)#)".format(node_path))
		_return = node_path

		nodes_list = node_path.split(" ")
		node_path = ""

		while (len(nodes_list) > 0):
		#
			node_name = nodes_list.pop(0)
			if (len(node_path) > 0): node_path += " "

			if (":" in node_name):
			#
				re_result = XmlParser.RE_NODE_NAME_XMLNS.match(node_name)

				if (re_result == None): node_path += node_name
				else:
				#
					node_path += "{0}:{1}".format(
						(
							self.data_ns_default[self.data_ns[re_result.group(1)]]
							if (re_result.group(1) in self.data_ns and self.data_ns[re_result.group(1)] in self.data_ns_default) else
							re_result.group(1)
						),
						re_result.group(2)
					)
			#
			else: node_path += node_name
		#

		if (node_path in self.data_ns_predefined_default): _return = self.data_ns_predefined_default[node_path]
		return _return
	#

	def ns_unregister(self, ns = ""):
	#
		"""
Unregisters a namespace or clears the cache (if ns is empty).

:param ns: Output relevant namespace definition

:since: v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE

		if (str != _PY_UNICODE_TYPE and type(ns) == _PY_UNICODE_TYPE): ns = _PY_STR(ns, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.ns_unregister({0})- (#echo(__LINE__)#)".format(ns))

		if (len(ns) > 0):
		#
			if (ns in self.data_ns):
			#
				del(self.data_ns_compact[self.data_ns_default[self.data_ns[ns]]])
				del(self.data_ns_default[self.data_ns[ns]])
				del(self.data_ns[ns])
			#
		#
		else:
		#
			self.data_ns = { }
			self.data_ns_compact = { }
			self.data_ns_counter = 0
			self.data_ns_default = { }
			self.data_ns_predefined_compact = { }
			self.data_ns_predefined_default = { }
		#
	#

	def set(self, xml_tree, overwrite = False):
	#
		"""
"Imports" a XML tree into the cache.

:param xml_tree: Input tree dict
:param overwrite: True to overwrite the current (non-empty) cache

:return: (bool) True on success
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.set(xml_tree, overwrite)- (#echo(__LINE__)#)")
		_return = False

		if ((self.data == None or overwrite) and isinstance(xml_tree, dict)):
		#
			self.data = xml_tree
			_return = True
		#

		return _return
	#

	def set_event_handler(self, event_handler):
	#
		"""
Sets the EventHandler.

:param event_handler: EventHandler to use

:since: v0.1.00
		"""

		self.event_handler = event_handler
	#

	def xml_to_dict(self, data, treemode = True, strict_standard = True):
	#
		"""
Converts XML data into a multi-dimensional XML tree or merged one.

:param data: Input XML data
:param strict_standard: True to be standard compliant
:param treemode: Create a multi-dimensional result

:return: (dict) Multi-dimensional XML tree or merged one; None on error
:since:  v0.1.00
		"""

		# global: _mode, _PY_STR, _PY_UNICODE_TYPE
		# pylint: disable=broad-except

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.xml_to_dict(data, treemode, strict_standard)- (#echo(__LINE__)#)")
		_return = None

		try:
		#
			if (_mode == "mono"):
			#
				if (str != _PY_UNICODE_TYPE and type(data) == _PY_UNICODE_TYPE): data = _PY_STR(data, "utf-8")

				parser_ptr = XmlDocument()
				parser_ptr.LoadXml(data)
				parser_ptr = XmlNodeReader(parser_ptr)

				if (parser_ptr != None):
				#
					_return = (
						self.data_parser.xml_to_dict_MonoXML(parser_ptr, strict_standard)
						if (treemode) else
						self.data_parser.xml_to_dict_MonoXML_merged(parser_ptr)
					)
				#
			#

			if (_mode == "py"):
			#
				if (re.search("<\\?xml(.+?)encoding=", data) == None):
				#
					parser_ptr = expat.ParserCreate("UTF-8")
					if (str != _PY_UNICODE_TYPE and type(data) == _PY_UNICODE_TYPE): data = _PY_STR(data, "utf-8")
				#
				else: parser_ptr = expat.ParserCreate()

				if (treemode):
				#
					self.data_parser.define_mode(XmlParserExpat.MODE_TREE)
					self.data_parser.define_strict_standard(strict_standard)

					parser_ptr.CharacterDataHandler = self.data_parser.expat_cdata
					parser_ptr.StartElementHandler = self.data_parser.expat_element_start
					parser_ptr.EndElementHandler = self.data_parser.expat_element_end
					parser_ptr.Parse(data, True)

					_return = self.data_parser.xml_to_dict_expat()
				#
				else:
				#
					self.data_parser.define_mode(XmlParserExpat.MODE_MERGED)

					parser_ptr.CharacterDataHandler = self.data_parser.expat_merged_cdata
					parser_ptr.StartElementHandler = self.data_parser.expat_merged_element_start
					parser_ptr.EndElementHandler = self.data_parser.expat_merged_element_end
					parser_ptr.Parse(data, True)

					_return = self.data_parser.xml_to_dict_expat_merged ()
				#
			#
		#
		except Exception: pass

		if (treemode and self.data_parse_only):
		#
			self.data = None
			self.ns_unregister()
		#

		return _return
	#

	@staticmethod
	def _dict_search(needle, haystack):
	#
		"""
Searches haystack for needle.

:param needle: Value to be searched for
:param haystack: Dict to search in

:access: protected
:return: (mixed) Key; None on error
:since:  v0.1.00
		"""

		_return = None

		if (needle in haystack):
		#
			for key in haystack:
			#
				if (haystack[key] == needle):
				#
					_return = key
					break
				#
			#
		#

		return _return
	#
#

##j## EOF