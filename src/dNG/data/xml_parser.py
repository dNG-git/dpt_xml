# -*- coding: utf-8 -*-
##j## BOF

"""
XML (Extensible Markup Language) is the easiest way to use a descriptive
language for controlling applications locally and world wide. This is the
parser implementation.
"""
"""n// NOTE
----------------------------------------------------------------------------
XML.py
Multiple XML parsers: Common abstraction layer
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

import re

try:
#
	import java.lang.System
	_direct_xml_mode = "java"
#
except ImportError: _direct_xml_mode = None

try:
#
	import clr
	clr.AddReference("System.Xml")
	from System.IO import StringReader
	from System.Xml import XmlDocument, XmlNodeReader

	from .xml_parser_MonoXML import direct_xml_parser_MonoXML
	_direct_xml_mode = "mono"
#
except ImportError: pass

if (_direct_xml_mode == None):
#
	from xml.parsers import expat

	from .xml_parser_expat import direct_xml_parser_expat
	_direct_xml_mode = "py"
#

try: _unicode_object = { "type": unicode, "str": unicode.encode }
except: _unicode_object = { "type": bytes, "str": bytes.decode }

class direct_xml_parser(object):
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
	RE_NODE_NAME_XMLNS = re.compile("^(.+?):(\\w+)$")
	"""
RegExp to split XML namespace node names
	"""
	RE_NODE_POSITION = re.compile("^(.+?)\\#(\\d+)$")
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
Constructor __init__(direct_xml_parser)

:param xml_charset: Charset to be added as information to XML output
:param parse_only: Parse data only
:param node_type: Dict implementation for new nodes
:param timeout_retries: Retries before timing out
:param event_handler: EventHandler to use

:since: v0.1.00
		"""

		global _direct_xml_mode

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
		self.data_charset = xml_charset.upper ()
		"""
Charset used
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
Cache of node pathes with a predefined NS (key = Compact name)
		"""
		self.data_ns_predefined_default = { }
		"""
Cache of node pathes with a predefined NS (key = Full name)
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

		if (_direct_xml_mode == "mono"): self.data_parser = direct_xml_parser_MonoXML(self, timeout_retries, event_handler)
		else: self.data_parser = direct_xml_parser_expat(self, event_handler)
	#

	def __del__(self):
	#
		"""
Destructor __del__(direct_xml_parser)

:since: v0.1.00
		"""

		self.data_parser = None
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

		global _unicode_object
		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.define_parse_only(parse_only)- (#echo(__LINE__)#)")

		if (type(parse_only) == _unicode_object['type']): parse_only = _unicode_object['str'](parse_only, "utf-8")
		var_type = type(parse_only)

		if ((var_type == bool or var_type == str) and parse_only): self.data_parse_only = True
		elif (parse_only == None and (not self.data_parse_only)): self.data_parse_only = True
		else: self.data_parse_only = False

		return self.data_parse_only
	#

	def dict_search(self, needle, haystack):
	#
		"""
Searches haystack for needle. 

:param needle: Value to be searched for
:param haystack: Dict to search in

:access: protected
:return: (mixed) Key; False on error
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.dict_search({0}, haystack)- (#echo(__LINE__)#)".format(needle))
		var_return = False

		if (needle in haystack):
		#
			for key in haystack:
			#
				if (haystack[key] == needle):
				#
					var_return = key
					break
				#
			#
		#

		return var_return
	#

	def dict2xml(self, xml_tree, strict_standard = True):
	#
		"""
Builds recursively a valid XML ouput reflecting the given XML dict tree.

:param xml_tree: XML dict tree level to work on
:param strict_standard: Be standard conform

:return: (str) XML output string
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.dict2xml(xml_tree, strict_standard)- (#echo(__LINE__)#)")
		var_return = ""

		if (isinstance(xml_tree, dict) and len(xml_tree) > 0):
		#
			for xml_node in xml_tree:
			#
				xml_node_dict = xml_tree[xml_node]

				if ("xml.mtree" in xml_node_dict):
				#
					del(xml_node_dict['xml.mtree'])
					var_return += self.dict2xml(xml_node_dict, strict_standard)
				#
				elif ("xml.item" in xml_node_dict):
				#
					var_return += self.dict2xml_item_encoder (xml_node_dict['xml.item'], False, strict_standard)
					xml_node_tag = (xml_node_dict['xml.item']['tag'] if (direct_xml_parser.RE_TAG_DIGIT.match(xml_node_dict['xml.item']['tag']) == None) else "digitstart__{0}".format(xml_node_dict['xml.item']['tag']))

					del(xml_node_dict['xml.item'])
					var_return += "{0}</{1}>".format(self.dict2xml(xml_node_dict, strict_standard), xml_node_tag)
				#
				elif (len(xml_node_dict['tag']) > 0): var_return += self.dict2xml_item_encoder(xml_node_dict, True, strict_standard)
			#
		#

		return var_return.strip()
	#

	def dict2xml_item_encoder(self, data, close_tag = True, strict_standard = True):
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

		global _unicode_object
		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.array2xml_item_encoder(data, {0}, strict_standard)- (#echo(__LINE__)#)".format(close_tag))

		var_return = ""

		is_value_attr_compatible = (False if (strict_standard) else True)

		if (isinstance(data, dict)):
		#
			if (len(data['tag']) > 0):
			#
				if (re.match("\\d", data['tag']) != None): data['tag'] = "digitstart__{0}".format(data['tag'])
				var_return += "<{0}".format(data['tag'])

				if ("attributes" in data):
				#
					for key in data['attributes']:
					#
						if (is_value_attr_compatible and key == "value" and len(data['value']) < 1): data['value'] = data['attributes'][key]
						else:
						#
							type_value = type(data['attributes'][key])

							if (type_value == int or type_value == float): value = str(data['attributes'][key])
							else: value = data['attributes'][key]

							if (type(value) == _unicode_object['type']): value = _unicode_object['str'](value, "utf-8")
							value = value.replace("&", "&amp;")
							value = value.replace("<", "&lt;")
							value = value.replace(">", "&gt;")
							value = value.replace('"', "&quot;")
							if (self.data_charset != "UTF-8"): value = value.encode(self.data_charset)

							var_return += " {0}=\"{1}\"".format(key, value)
						#
					#
				#

				if ("value" in data and (strict_standard or len(data['value']) > 0)):
				#
					type_value = type(data['value'])

					if (type_value == int or type_value == float): data['value'] = str(data['value'])
					else:
					#
						if (type_value == _unicode_object['type']): data['value'] = _unicode_object['str'](data['value'], "utf-8")

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
						var_return += " value=\"{0}\"".format(data['value'])
					#
				#

				if (is_value_attr_compatible and close_tag): var_return += " />"
				else:
				#
					var_return += ">"

					if ("value" in data and (not is_value_attr_compatible)):
					#
						if (type(data['value']) == _unicode_object['type']): data['value'] = _unicode_object['str'](data['value'], "utf-8")
						if (self.data_charset != "UTF-8"): data['value'] = data['value'].encode(self.data_charset)

						if ("<" not in data['value'] and ">" not in data['value']): var_return += data['value'].replace("&", "&amp;")
						else:
						#
							if ("]]>" in data['value']): data['value'] = data['value'].replace("]]>", "]]]]><![CDATA[>")
							var_return += "<![CDATA[{0}]]>".format(data['value'])
						#
					#
				#

				if ((not is_value_attr_compatible) and close_tag): var_return += "</{0}>".format(data['tag'])
			#
		#

		return var_return
	#

	def get(self):
	#
		"""
This operation just gives back the content of self.data.

:return: (dict) XML dict tree; False on error
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.get()- (#echo(__LINE__)#)")

		return (False if (self.data == None) else self.data)
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

		global _unicode_object
		if (type (node_path) == _unicode_object['type']): node_path = _unicode_object['str'](node_path, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.node_add({0}, value, attributes, add_recursively)- (#echo(__LINE__)#)".format(node_path))
		var_return = False

		if (self.data == None): self.data = self.node_type()
		type_value = type(value)

		if (type(node_path) == str and type_value == str or type_value == _unicode_object['type']):
		#
			node_path = self.ns_translate_path(node_path)

			if (len(self.data_cache_node) == 0 or re.match("^{0}".format(re.escape(node_path)), self.data_cache_node,re.I) == None):
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
				re_result = direct_xml_parser.RE_NODE_POSITION.match(node_name)

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
									var_return = True
								#
							#
							elif (node_ptr[node_name]['xml.mtree'] in node_ptr[node_name]):
							#
								is_available = True
								node_position = node_ptr[node_name]['xml.mtree']
								var_return = True
							#

							if (is_available):
							#
								if ((not isinstance(node_ptr[node_name][node_position], dict)) or "xml.item" not in node_ptr[node_name][node_position]): node_ptr[node_name][node_position] = { "xml.item": node_ptr[node_name][node_position] }
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

							node_ptr[node_name]['level'] = ((1 + node_ptr['xml.item']['level']) if ("xml.item" in node_ptr and "level" in node_ptr['xml.item']) else 1)
							node_ptr[node_name] = self.node_type([ ( "xml.item", node_ptr[node_name] ) ])
							node_ptr = node_ptr[node_name]
						#
					#

					if ((not is_available) and add_recursively):
					#
						node_dict = self.node_type(tag = node_name, level = 1, xmlns = { })

						if ("xml.item" in node_ptr):
						#
							if ("level" in node_ptr['xml.item']): node_dict['level'] = (1 + node_ptr['xml.item']['level'])
							if ("xmlns" in node_ptr['xml.item']): node_dict['xmlns'] = node_ptr['xml.item']['xmlns']
						#

						self.node_add_ns_cache(node_path_done, node_name, node_dict)

						is_available = True
						node_ptr[node_name] = self.node_type([ ( "xml.item", node_dict ) ])
						node_ptr = node_ptr[node_name]
					#

					if (len(node_path_done) > 0): node_path_done += " "
					node_path_done += node_name
				#
				else:
				#
					node_dict = self.node_type(tag = node_name, value = value, xmlns = { })

					if ("xml.item" in node_ptr and "xmlns" in node_ptr['xml.item']): node_dict['xmlns'] = node_ptr['xml.item']['xmlns']

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

							if (direct_xml_parser.RE_ATTRIBUTES_XMLNS.match(key) != None):
							#
								ns_name = key[6:]

								if (len(value) > 0): node_dict['xmlns'][ns_name] = (self.data_ns_default[value] if (value in self.data_ns_default) else value)
								elif (ns_name in node_dict['xmlns']): del(node_dict['xmlns'][ns_name])
							#
						#

						node_dict['attributes'] = attributes
					#

					self.node_add_ns_cache(node_path_done, node_name, node_dict)

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

					var_return = True
				#
			#
		#

		return var_return
	#

	def node_add_ns_cache(self, node_path_done, node_name, node_dict):
	#
		node_ns_name = ""
		re_result = direct_xml_parser.RE_NODE_NAME_XMLNS.match(node_name)

		if (re_result != None):
		#
			if (re_result.group(1) in node_dict['xmlns'] and type(node_dict['xmlns'][re_result.group(1)]) == int): node_ns_name = "{0}:{1}".format(node_dict['xmlns'][re_result.group(1)], re_result.group(2))
		#
		elif ("@" in node_dict['xmlns']): node_ns_name = "{0}:{1}".format(node_dict['xmlns']['@'], node_name)

		if (len(node_path_done) > 0):
		#
			self.data_ns_predefined_compact["{0} {1}".format(node_path_done, node_name)] = "{0} {1}".format(self.data_ns_predefined_compact[node_path_done], (node_name if (node_ns_name == "") else node_ns_name))
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
	def ns_register(self, ns, uri):
	#
		"""
Registers a namespace (URI) for later use with this XML reader instance.

:param ns: Output relevant namespace definition
:param uri: Uniform Resource Identifier

:since: v0.1.00
		"""

		global _unicode_object
		if (type(ns) == _unicode_object['type']): ns = _unicode_object['str'](ns, "utf-8")
		if (type(uri) == _unicode_object['type']): uri = _unicode_object['str'](uri, "utf-8")

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
		var_return = node

		if (isinstance(node, dict) and "tag" in node and "xmlns" in node and isinstance(node['xmlns'], dict)):
		#
			var_return['tag_ns'] = ""
			var_return['tag_parsed'] = node['tag']

			re_result = direct_xml_parser.RE_NODE_NAME_XMLNS.match(node['tag'])

			if (re_result != None and re_result.group(1) in node['xmlns'] and node['xmlns'][re_result.group(1)] in self.data_ns_compact):
			#
				tag_ns = self.dict_search(self.data_ns_compact[node['xmlns'][re_result.group(1)]] ,self.data_ns)

				if (tag_ns != False):
				#
					var_return['tag_ns'] = tag_ns
					var_return['tag_parsed'] = "{0}:{1}".format(tag_ns, re_result.group(2))
				#
			#

			if ("attributes" in node):
			#
				for key in node['attributes']:
				#
					re_result = direct_xml_parser.RE_NODE_NAME_XMLNS.match(key)

					if (re_result != None and re_result.group(1) in node['xmlns'] and node['xmlns'][re_result.group(1)] in self.data_ns_compact):
					#
						tag_ns = self.dict_search(self.data_ns_compact[node['xmlns'][re_result.group(1)]], self.data_ns)

						if (tag_ns != False):
						#
							var_return['attributes']["{0}:{1}".format(tag_ns, re_result.group(2))] = node['attributes'][key]
							del(var_return['attributes'][key])
						#
					#
				#
			#
		#

		return var_return
	#

	def ns_translate_path(self, node_path):
	#
		"""
Checks input path for predefined namespaces converts it to the internal
path.

:param node_path: Path to the new node; delimiter is space

:return: (str) Output node path
:since:  v0.1.00
		"""

		global _unicode_object
		if (type(node_path) == _unicode_object['type']): node_path = _unicode_object['str'](node_path, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.ns_translate_path({0})- (#echo(__LINE__)#)".format(node_path))
		var_return = node_path

		nodes_list = node_path.split(" ")
		node_path = ""

		while (len(nodes_list) > 0):
		#
			node_name = nodes_list.pop(0)
			if (len(node_path) > 0): node_path += " "

			if (":" in node_name):
			#
				re_result = direct_xml_parser.RE_NODE_NAME_XMLNS.match(node_name)

				if (re_result == None): node_path += node_name
				else: node_path += "{0}:{1}".format((self.data_ns_default[self.data_ns[re_result.group(1)]] if (re_result.group(1) in self.data_ns and self.data_ns[re_result.group(1)] in self.data_ns_default) else re_result.group(1)), re_result.group(2))
			#
			else: node_path += node_name
		#

		if (node_path in self.data_ns_predefined_default): var_return = self.data_ns_predefined_default[node_path]
		return var_return
	#

	def ns_unregister(self, ns = ""):
	#
		"""
Unregisters a namespace or clears the cache (if ns is empty).

:param ns: Output relevant namespace definition

:since: v0.1.00
		"""

		global _unicode_object
		if (type(ns) == _unicode_object['type']): ns = _unicode_object['str'](ns, "utf-8")

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
		var_return = False

		if ((self.data == None or overwrite) and isinstance(xml_tree, dict)):
		#
			self.data = xml_tree
			var_return = True
		#

		return var_return
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

	def xml2dict(self, data, treemode = True, strict_standard = True):
	#
		"""
Converts XML data into a multi-dimensional XML tree or merged one.

:param data: Input XML data
:param strict_standard: True to be standard compliant
:param treemode: Create a multi-dimensional result

:return: (dict) Multi-dimensional XML tree or merged one; False on error
:since:  v0.1.00
		"""

		global _direct_xml_mode, _unicode_object
		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.xml2dict(data, treemode, strict_standard)- (#echo(__LINE__)#)")
		var_return = False

		try:
		#
			if (_direct_xml_mode == "mono"):
			#
				if (type(data) == _unicode_object['type']): data = _unicode_object['str'](data, "utf-8")

				parser_ptr = XmlDocument()
				parser_ptr.LoadXml(data)
				parser_ptr = XmlNodeReader(parser_ptr)

				if (parser_ptr != None): var_return = (self.data_parser.xml2dict_MonoXML(parser_ptr, strict_standard) if (treemode) else self.data_parser.xml2dict_MonoXML_merged(parser_ptr))
			#
			elif (re.search("<\\?xml(.+?)encoding=", data) == None):
			#
				parser_ptr = expat.ParserCreate("UTF-8")
				if (type(data) == _unicode_object['type']): data = _unicode_object['str'](data, "utf-8")
			#
			else: parser_ptr = expat.ParserCreate()
		#
		except: parser_ptr = None

		if (_direct_xml_mode == "py" and parser_ptr != None):
		#
			if (treemode):
			#
				self.data_parser.define_mode(direct_xml_parser_expat.MODE_TREE)
				self.data_parser.define_strict_standard(strict_standard)

				parser_ptr.CharacterDataHandler = self.data_parser.expat_cdata
				parser_ptr.StartElementHandler = self.data_parser.expat_element_start
				parser_ptr.EndElementHandler = self.data_parser.expat_element_end
				parser_ptr.Parse(data, True)

				var_return = self.data_parser.xml2dict_expat()
			#
			else:
			#
				self.data_parser.define_mode(direct_xml_parser_expat.MODE_MERGED)

				parser_ptr.CharacterDataHandler = self.data_parser.expat_merged_cdata
				parser_ptr.StartElementHandler = self.data_parser.expat_merged_element_start
				parser_ptr.EndElementHandler = self.data_parser.expat_merged_element_end
				parser_ptr.Parse(data, True)

				var_return = self.data_parser.xml2dict_expat_merged ()
			#
		#

		if (treemode and self.data_parse_only):
		#
			self.data = None
			self.ns_unregister()
		#

		return var_return
	#
#

##j## EOF