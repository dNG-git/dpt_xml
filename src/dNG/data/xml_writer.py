# -*- coding: utf-8 -*-
##j## BOF

"""
XML (Extensible Markup Language) is the easiest way to use a descriptive
language for controlling applications locally and world wide. This extended
class provides object-oriented definition capabilities.
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

from .xml_parser import direct_xml_parser

try: _unicode_object = { "type": unicode, "str": unicode.encode }
except: _unicode_object = { "type": bytes, "str": bytes.decode }

class direct_xml_writer(direct_xml_parser):
#
	"""
This class extends the bridge between Python and XML to work with XML and
create valid documents.

:author:    direct Netware Group
:copyright: direct Netware Group - All rights reserved
:package:   XML.py
:since:     v1.0.0
:license:   http://www.direct-netware.de/redirect.py?licenses;mpl2
            Mozilla Public License, v. 2.0
	"""

	def __init__(self, xml_charset = "UTF-8", node_type = dict, timeout_retries = 5, event_handler = None):
	#
		"""
Constructor __init__(direct_xml_writer)

:param xml_charset: Charset to be added as information to XML output
:param node_type: Dict implementation for new nodes
:param timeout_retries: Retries before timing out
:param event_handler: EventHandler to use

:since: v0.1.00
		"""

		direct_xml_parser.__init__(self, xml_charset, False, node_type, timeout_retries, event_handler)
	#

	def cache_export(self, flush = False, strict_standard = True):
	#
		"""
Convert the cached XML tree into a XML string.

:param flush: True to delete the cache content
:param strict_standard: True to be standard compliant

:return: (str) Result string
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.cache_export(flush, strict_standard)- (#echo(__LINE__)#)")

		if (self.data == None or len(self.data) < 1): var_return = ""
		else:
		#
			var_return = self.dict2xml(self.data, strict_standard)
			if (flush): self.data = { }
		#

		return var_return
	#

	def dict_import(self, data_dict, overwrite = False):
	#
		"""
Read and convert a simple multi-dimensional dict into our XML tree.

:param data_dict: Input dict
:param overwrite: True to overwrite the current (non-empty) cache

:return: (bool) True on success
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.dict_import(data_dict, overwrite)- (#echo(__LINE__)#)")
		var_return = False

		if (self.data == None or len(self.data) < 1 or overwrite):
		#
			self.data = self.dict_import_walker(data_dict)
			var_return = True
		#

		return var_return
	#

	def dict_import_walker(self, data_dict, xml_level = 1):
	#
		"""
Read and convert a single dimension of an dictionary for our XML tree.

:param data_dict: Input dict
:param xml_level: Current level of an multi-dimensional dict

:return: (dict) Result XML tree dict
:since:  v0.1.00
		"""

		global _unicode_object
		if (type(xml_level) == _unicode_object['type']): xml_level = _unicode_object['str'](xml_level, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.dict_import_walker(data_dict, {0:d})- (#echo(__LINE__)#)".format(xml_level))
		var_return = { }

		if (isinstance(data_dict, dict)):
		#
			for key in data_dict:
			#
				var_type = type(key)
				value = data_dict[key]

				if (var_type == int or var_type == float or len(key) > 0):
				#
					if (isinstance(value, dict)):
					#
						node_dict = self.node_type([ ( "xml.item", { "tag": key,"level": xml_level,"xmlns": { } } ) ])
						node_dict.update(self.dict_import_walker(value, (1 + xml_level)))
						var_return[key] = node_dict
					#
					elif (isinstance(value, list)): var_return[key] = self.node_type(tag = key, value = value, xmlns = { })
				#
			#
		#

		return var_return
	#

	def node_change_attributes(self, node_path, attributes):
	#
		"""
Change the attributes of a specified node. Note: XMLNS updates must be
handled by the calling code.

:param node_path: Path to the new node - delimiter is space
:param attributes: Attributes of the node

:return: (bool) False on error
:since:  v0.1.00
		"""

		global _unicode_object
		if (type(node_path) == _unicode_object['type']): node_path = _unicode_object['str'](node_path, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.node_change_attributes({0}, attributes)- (#echo(__LINE__)#)".format(node_path))
		var_return = False

		if (type(node_path) == str and type(attributes) == dict):
		#
			node_path = self.ns_translate_path(node_path)
			node_ptr = self.node_get_ptr(node_path)

			if (isinstance(node_ptr, dict)):
			#
				if ("xml.item" in node_ptr): node_ptr['xml.item']['attributes'] = attributes
				else: node_ptr['attributes'] = attributes

				var_return = True
			#
		#

		return var_return
	#

	def node_change_value(self, node_path, value):
	#
		"""
Change the value of a specified node.

:param node_path: Path to the new node; delimiter is space
:param value: Value for the new node

:return: (bool) False on error
:since:  v0.1.00
		"""

		global _unicode_object
		if (type(node_path) == _unicode_object['type']): node_path = _unicode_object['str'](node_path, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.node_change_value({0}, value)- (#echo(__LINE__)#)".format(node_path))
		var_return = False

		var_type = type(value)

		if (type(node_path) == str and (not isinstance(var_type, dict)) and (not isinstance(var_type, list))):
		#
			node_path = self.ns_translate_path(node_path)
			node_ptr = self.node_get_ptr(node_path)

			if (isinstance(node_ptr, dict)):
			#
				if ("xml.item" in node_ptr): node_ptr['xml.item']['value'] = value
				else: node_ptr['value'] = value

				var_return = True
			#
		#

		return var_return
	#

	def node_count(self, node_path):
	#
		"""
Count the occurrence of a specified node.

:param node_path: Path to the node; delimiter is space

:return: (int) Counted number off matching nodes
:since:  v0.1.00
		"""

		global _unicode_object
		if (type(node_path) == _unicode_object['type']): node_path = _unicode_object['str'](node_path, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.node_count({0})- (#echo(__LINE__)#)".format(node_path))
		var_return = 0

		if (type(node_path) == str):
		#
			"""
Get the parent node of the target.
			"""

			node_path = self.ns_translate_path(node_path)
			node_path_list = node_path.split(" ")

			if (len(node_path_list) > 1):
			#
				node_name = node_path_list.pop()
				node_path = " ".join(node_path_list)
				node_ptr = self.node_get_ptr(node_path)
			#
			else:
			#
				node_name = node_path
				node_ptr = self.data
			#

			if (isinstance(node_ptr, dict)):
			#
				node_name = self.ns_translate_name(node_ptr, node_name)
				if (node_name in node_ptr): var_return = ((len(node_ptr[node_name]) - 1) if ("xml.mtree" in node_ptr[node_name]) else 1)
			#
		#

		return var_return
	#

	def node_get(self, node_path, remove_metadata = True):
	#
		"""
Read a specified node including all children if applicable.

:param node_path: Path to the node; delimiter is space
:param remove_metadata: False to not remove the xml.item node

:return: (dict) XML node element; False on error
:since:  v0.1.00
		"""

		global _unicode_object
		if (type(node_path) == _unicode_object['type']): node_path = _unicode_object['str'](node_path, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.node_get({0})- (#echo(__LINE__)#)".format(node_path))
		var_return = False

		if (type(node_path) == str):
		#
			node_path = self.ns_translate_path(node_path)
			node_ptr = self.node_get_ptr(node_path)

			if (isinstance(node_ptr, dict)):
			#
				var_return = node_ptr.copy()
				if (remove_metadata and "xml.item" in var_return): del(var_return['xml.item'])
			#
		#

		return var_return
	#

	def node_get_ptr(self, node_path):
	#
		"""
Returns the pointer to a specific node.

:param node_path: Path to the node - delimiter is space

:return: (dict) XML node element; False on error
:since:  v0.1.00
		"""

		global _unicode_object
		if (type(node_path) == _unicode_object['type']): node_path = _unicode_object['str'](node_path, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.node_get_ptr({0})- (#echo(__LINE__)#)".format(node_path))
		var_return = False

		if (type(node_path) == str):
		#
			if (len(self.data_cache_node) > 0 and node_path[:len(self.data_cache_node)] == self.data_cache_node):
			#
				node_path = node_path[len(self.data_cache_node):].strip()
				node_ptr = self.data_cache_ptr
			#
			else: node_ptr = self.data

			is_valid = True
			node_path_list = (node_path.split(" ") if (len(node_path) > 0) else [ ])

			while (is_valid and len(node_path_list) > 0):
			#
				is_valid = False
				node_name = node_path_list.pop(0)
				re_result = direct_xml_writer.RE_NODE_POSITION.match(node_name)

				if (re_result == None): node_position = -1
				else:
				#
					node_name = re_result.group(1)
					node_position = int(re_result.group(2))
				#

				node_name = self.ns_translate_name(node_ptr, node_name)

				if (node_name in node_ptr):
				#
					if ("xml.mtree" in node_ptr[node_name]):
					#
						if (node_position >= 0):
						#
							if (node_position in node_ptr[node_name]):
							#
								is_valid = True
								node_ptr = node_ptr[node_name][node_position]
							#
						#
						elif (node_ptr[node_name]['xml.mtree'] in node_ptr[node_name]):
						#
							is_valid = True
							node_ptr = node_ptr[node_name][node_ptr[node_name]['xml.mtree']]
						#
					#
					else:
					#
						is_valid = True
						node_ptr = node_ptr[node_name]
					#
				#
			#

			if (is_valid): var_return = node_ptr
		#

		return var_return
	#

	def node_remove(self, node_path):
	#
		"""
Remove a node and all children if applicable.

:param node_path: Path to the node - delimiter is space

:return: (bool) False on error
:since:  v0.1.00
		"""

		global _unicode_object
		if (type(node_path) == _unicode_object['type']): node_path = _unicode_object['str'](node_path, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.node_remove({0})- (#echo(__LINE__)#)".format(node_path))
		var_return = False

		if (type(node_path) == str):
		#
			"""
Get the parent node of the target.
			"""

			node_path = self.ns_translate_path(node_path)
			node_path_list = node_path.split(" ")

			if (len (node_path_list) > 1):
			#
				node_name = node_path_list.pop()
				node_path = " ".join(node_path_list)
				node_ptr = self.node_get_ptr(node_path)

				if (len(self.data_cache_node) > 0 and node_path[:len(self.data_cache_node)] == self.data_cache_node):
				#
					self.data_cache_node = ""
					self.data_cache_ptr = self.data
				#
			#
			else:
			#
				node_name = node_path
				node_ptr = self.data

				self.data_cache_node = ""
				self.data_cache_ptr = self.data
			#

			if (isinstance(node_ptr, dict)):
			#
				re_result = direct_xml_writer.RE_NODE_POSITION.match(node_name)

				if (re_result == None): node_position = -1
				else:
				#
					node_name = re_result.group(1)
					node_position = int(re_result.group(2))
				#

				node_name = self.ns_translate_name(node_ptr, node_name)

				if (node_name in node_ptr):
				#
					if ("xml.mtree" in node_ptr[node_name]):
					#
						if (node_position >= 0):
						#
							if (node_position in node_ptr[node_name]):
							#
								del(node_ptr[node_name][node_position])
								var_return = True
							#
						#
						elif (node_ptr[node_name]['xml.mtree'] in node_ptr[node_name]):
						#
							del (node_ptr[node_name][node_ptr[node_name]['xml.mtree']])
							var_return = True
						#

						"""
Update the mtree counter or remove it if applicable.
						"""

						if (var_return):
						#
							node_ptr[node_name]['xml.mtree'] -= 1

							if (node_ptr[node_name]['xml.mtree'] > 0):
							#
								node_dict = self.node_type([ ( "xml.mtree", node_ptr[node_name]['xml.mtree'] ) ])
								del(node_ptr[node_name]['xml.mtree'])

								node_position = 0

								for key in node_ptr[node_name]:
								#
									value = node_ptr[node_name][key]
									node_dict[node_position] = value
									node_position += 1
								#
							#
							else:
							#
								del(node_ptr[node_name]['xml.mtree'])
								node_ptr[node_name] = node_ptr[node_name].pop()
							#
						#
					#
					else:
					#
						del(node_ptr[node_name])
						var_return = True
					#
				#
			#
		#

		return var_return
	#

	def node_set_cache_path(self, node_path):
	#
		"""
Set the cache pointer to a specific node.

:param node_path: Path to the node - delimiter is space

:return: (bool) True on success
:since:  v0.1.00
		"""

		global _unicode_object
		if (type(node_path) == _unicode_object['type']): node_path = _unicode_object['str'](node_path, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.node_set_cache_path({0})- (#echo(__LINE__)#)".format(node_path))
		var_return = False

		if (type(node_path) == str):
		#
			node_path = self.ns_translate_path(node_path)

			if (node_path == self.data_cache_node): var_return = True
			else:
			#
				node_ptr = self.node_get_ptr(node_path)

				if (isinstance(node_ptr, dict)):
				#
					self.data_cache_node = node_path
					self.data_cache_ptr = node_ptr
					var_return = True
				#
			#
		#

		return var_return
	#

	def ns_get_uri(self, data):
	#
		"""
Returns the registered namespace (URI) for a given XML NS or node name
containing the registered XML NS.

:param data: XML NS or node name

:return: (str) Namespace (URI)
:since:  v0.1.00
		"""

		global _unicode_object
		if (type(data) == _unicode_object['type']): data = _unicode_object['str'](data, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.ns_get_uri({0})- (#echo(__LINE__)#)".format(data))
		var_return = ""

		re_result = direct_xml_writer.RE_NODE_NAME_XMLNS.match(data)

		if (re_result != None):
		#
			if (re_result.group(1) in self.data_ns): var_return = self.data_ns[re_result.group(1)]
		#
		elif (data in self.data_ns): var_return = self.data_ns[data]

		return var_return
	#

	def ns_translate_name(self, node, name):
	#
		"""
Translates the node name if it is the predefined default namespace for the
node.

:param node: XML tree node
:param name: Requested node name

:return: (str) Translated node name
:since:  v0.1.00
		"""

		var_return = name

		re_result = direct_xml_writer.RE_NODE_NAME_XMLNS.match(name)

		if (re_result != None and re_result.group(1) in self.data_ns and re_result.group(2) in node):
		#
			translated_name = re_result.group(2)

			if ("xml.mtree" in node[translated_name]):
			#
				if ("xml.item" in node[translated_name][0] and "@" in node[translated_name][0]['xml.item']['xmlns'] and node[translated_name][0]['xml.item']['xmlns']['@'] in self.data_ns_compact and self.data_ns_compact[node[translated_name][0]['xml.item']['xmlns']['@']] == self.data_ns[re_result.group(1)]): var_return = translated_name
				elif ("xmlns" in node[translated_name][0] and "@" in node[translated_name][0]['xmlns'] and node[translated_name][0]['xmlns']['@'] in self.data_ns_compact and self.data_ns_compact[node[translated_name][0]['xmlns']['@']] == self.data_ns[re_result.group(1)]): var_return = translated_name
			#
			elif ("xml.item" in node[translated_name] and "@" in node[translated_name]['xml.item']['xmlns'] and node[translated_name]['xml.item']['xmlns']['@'] in self.data_ns_compact and self.data_ns_compact[node[translated_name]['xml.item']['xmlns']['@']] == self.data_ns[re_result.group(1)]): var_return = translated_name
			elif ("xmlns" in node[translated_name] and "@" in node[translated_name]['xmlns'] and node[translated_name]['xmlns']['@'] in self.data_ns_compact and self.data_ns_compact[node[translated_name]['xmlns']['@']] == self.data_ns[re_result.group(1)]): var_return = translated_name
		#

		return var_return
	#
#

##j## EOF