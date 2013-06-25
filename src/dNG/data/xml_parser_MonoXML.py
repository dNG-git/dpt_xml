# -*- coding: utf-8 -*-
##j## BOF

"""
MonoXML implementation for XML.py
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

from System.Xml import XmlNodeType
from time import time

try:
#
	_PY_STR = unicode.encode
	_PY_UNICODE_TYPE = unicode
#
except:
#
	_PY_STR = bytes.decode
	_PY_UNICODE_TYPE = str
#

class XmlParserMonoXml(object):
#
	"""
This implementation supports XmlNodeReader for XML parsing.

:author:    direct Netware Group
:copyright: direct Netware Group - All rights reserved
:package:   XML.py
:since:     v0.1.00
:license:   http://www.direct-netware.de/redirect.py?licenses;mpl2
            Mozilla Public License, v. 2.0
	"""

	def __init__(self, parser, timeout_retries = 5, event_handler = None):
	#
		"""
Constructor __init__(XmlParserMonoXml)

:param parser: Container for the XML document
:param current_time: Current UNIX timestamp
:param timeout_retries: Retries before timing out
:param event_handler: EventHandler to use

:since: v0.1.00
		"""

		if (event_handler != None): event_handler.debug("#echo(__FILEPATH__)# -xml.__init__()- (#echo(__LINE__)#)")

		self.event_handler = event_handler
		"""
The EventHandler is called whenever debug messages should be logged or errors
happened.
		"""
		self.parser = parser
		"""
Container for the XML document
		"""
		self.timeout_retries = (5 if (timeout_retries == None) else timeout_retries)
		"""
Retries before timing out
		"""
	#

	def xml2dict_MonoXML(self, XmlNodeReader, strict_standard = True):
	#
		"""
Uses the given XmlNodeReader to parse data for the defined parser instance.

:param XmlNodeReader: XmlNodeReader object
:param strict_standard: True to be standard compliant

:return: (dict) Multi-dimensional XML tree
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.xml2dict_MonoXML(XmlNodeReader, strict_standard)- (#echo(__LINE__)#)")
		var_return = { }

		if (hasattr(XmlNodeReader, "Read")):
		#
			is_available = True
			timeout_time = (time() + self.timeout_retries)

			self.parser.set({ })

			while (is_available and XmlNodeReader.NodeType != XmlNodeType.Element and time() < timeout_time): is_available = XmlNodeReader.Read()

			monoxml_dict = self.xml2dict_MonoXML_walker(XmlNodeReader, strict_standard)
			XmlNodeReader.Close()

			if (type(monoxml_dict) == dict): is_available = self.xml2dict_MonoXML_dict_walker(monoxml_dict, strict_standard)
			if (is_available): var_return = self.parser.get()
		#

		return var_return
	#

	def xml2dict_MonoXML_dict_walker(self, data_dict, strict_standard = True):
	#
		"""
Imports a pre-parsed XML dict into the given parser instance.

:param data_dict: Result dict of a "xml2dict_MonoXML_walker()"
:param strict_standard: True to be standard compliant

:access: protected
:return: (bool) True on success
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.xml2dict_MonoXML_dict_walker(data_dict, strict_standard)- (#echo(__LINE__)#)")
		var_return = False

		if (type(data_dict) == dict):
		#
			if (len(data_dict['value']) > 0 or len(data_dict['attributes']) > 0 or len(data_dict['children']) > 0):
			#
				if ((not strict_standard) and "value" in data_dict['attributes'] and len(data_dict['value']) < 1):
				#
					data_dict['value'] = data_dict['attributes']['value']
					del(data_dict['attributes']['value'])
				#

				self.parser.node_add(data_dict['node_path'], data_dict['value'], data_dict['attributes'])
			#

			if (len(data_dict['children']) > 0):
			#
				for child_dict in data_dict['children']: self.xml2dict_MonoXML_dict_walker(child_dict, strict_standard)
			#

			var_return = True
		#

		return var_return
	#

	def xml2dict_MonoXML_merged(self, XmlNodeReader):
	#
		"""
Uses the given XmlNodeReader to parse data as a merged tree.

:param XmlNodeReader: XmlNodeReader object

:return: (dict) Merged XML tree
:since:  v0.1.00
		"""

		global _PY_STR, _PY_UNICODE_TYPE
		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.xml2dict_MonoXML_merged(XmlNodeReader)- (#echo(__LINE__)#)")

		var_return = False

		if (hasattr(XmlNodeReader, "Read")):
		#
			depth = 0
			is_read = False
			is_valid = True
			node_change_check = False
			node_path = ""
			node_path_list = [ ]
			nodes_dict = { }
			timeout_time = (time() + self.timeout_retries)

			while (is_valid and time() < timeout_time):
			#
				if (XmlNodeReader.NodeType == XmlNodeType.CDATA):
				#
					if (node_path in nodes_dict): nodes_dict[node_path]['value'] += (XmlNodeReader.Value if ("xml:space" in nodes_dict[node_path]['attributes'] and nodes_dict[node_path]['attributes']['xml:space'] == "preserve") else XmlNodeReader.Value.strip())
				#
				elif (XmlNodeReader.NodeType == XmlNodeType.Element):
				#
					attributes_dict = { }
					node_name = XmlNodeReader.Name.lower()
					if (node_name[:12] == "digitstart__"): node_name = node_name[12:]

					if (XmlNodeReader.HasAttributes):
					#
						while (XmlNodeReader.MoveToNextAttribute() and time() < timeout_time):
						#
							attribute_name = XmlNodeReader.Name.lower()
							if (str != _PY_UNICODE_TYPE and type(attribute_name) == _PY_UNICODE_TYPE): attribute_name = _PY_STR(attribute_name, "utf-8")

							if (attribute_name.startswith("xmlns:")): attributes_dict["xmlns:{0}".format(attribute_name[6:])] = XmlNodeReader.Value
							elif (attribute_name == "xml:space"): attributes_dict['xml:space'] = XmlNodeReader.Value.lower()
							else: attributes_dict[attribute_name] = XmlNodeReader.Value
						#

						XmlNodeReader.MoveToElement()
					#

					node_path_list.append(node_name)
					node_path = "_".join(node_path_list)
					nodes_dict[node_path] = { "tag": node_name, "level": (1 + XmlNodeReader.Depth), "value": None, "attributes": attributes_dict }

					depth = XmlNodeReader.Depth
					is_read = True
					is_valid = XmlNodeReader.Read()
					node_change_check = True
				#
				elif (XmlNodeReader.NodeType == XmlNodeType.EndElement):
				#
					is_read = True
					is_valid = XmlNodeReader.Read()
					node_change_check = True
				#
				elif (XmlNodeReader.NodeType == XmlNodeType.Text and node_path in nodes_dict): nodes_dict[node_path]['value'] += (XmlNodeReader.Value if ("xml:space" in nodes_dict[node_path]['attributes'] and nodes_dict[node_path]['attributes']['xml:space'] == "preserve") else XmlNodeReader.Value.strip())

				if (node_change_check):
				#
					node_change_check = False

					if (node_path in nodes_dict[node_path]):
					#
						if ("value" in nodes_dict[node_path]['attributes'] and len(nodes_dict[node_path]['value']) < 1):
						#
							nodes_dict[node_path]['value'] = nodes_dict[node_path]['attributes']['value']
							del(nodes_dict[node_path]['attributes']['value'])
						#

						if (node_path in var_return):
						#
							if ("tag" in var_return[node_path]):
							#
								node_packed_dict = var_return[node_path].copy()
								var_return[node_path] = [ node_packed_dict ]
								node_packed_dict = None
							#

							var_return[node_path].append(nodes_dict[node_path])
						#
						else: var_return[node_path] = nodes_dict[node_path]

						del(nodes_dict[node_path])
					#

					depth = XmlNodeReader.Depth
					is_read = True
					node_path_list.pop()
					node_path = "_".join(node_path_list)
				#
				elif (XmlNodeReader.Depth < depth):
				#
					if (node_path in nodes_dict): del(nodes_dict[node_path])

					depth = XmlNodeReader.Depth
					node_path_list.pop()
					node_path = "_".join(node_path_list)
				#

				if (is_read): is_read = True
				elif (is_valid): is_valid = XmlNodeReader.Read()
			#

			XmlNodeReader.Close()
		#

		return var_return
	#

	def xml2dict_MonoXML_walker(self, XmlNodeReader, strict_standard = True, node_path = "", xml_level = 0):
	#
		"""
Converts XML data into a multi-dimensional dict using this recursive
algorithm.

:param XmlNodeReader: XmlNodeReader object
:param strict_standard: True to be standard compliant
:param node_path: Old node path (for recursive use only)
:param xml_level: Current XML depth

:access: protected
:return: (dict) XML tree node; False on error
:since:  v0.1.00
		"""

		global _PY_STR, _PY_UNICODE_TYPE
		if (str != _PY_UNICODE_TYPE and type(node_path) == _PY_UNICODE_TYPE): node_path = _PY_STR(node_path, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.xml2dict_MonoXML_walker(XmlNodeReader, strict_standard, {0}, {1:d})- (#echo(__LINE__)#)".format(node_path, xml_level))
		var_return = False

		if (hasattr (XmlNodeReader,"Read")):
		#
			attributes_dict = { }
			is_node = False
			is_preserved_mode = False
			is_read = True
			node_content = ""
			nodes_list = [ ]
			timeout_time = (time() + self.timeout_retries)

			while ((not is_node) and is_read and time() < timeout_time):
			#
				if (XmlNodeReader.NodeType == XmlNodeType.Element):
				#
					if (strict_standard):
					#
						node_name = XmlNodeReader.Name
						if (str != _PY_UNICODE_TYPE and type(node_name) == _PY_UNICODE_TYPE): node_name = _PY_STR(node_name, "utf-8")
					#
					else:
					#
						node_name = XmlNodeReader.Name.lower()
						if (str != _PY_UNICODE_TYPE and type(node_name) == _PY_UNICODE_TYPE): node_name = _PY_STR(node_name, "utf-8")
						if (node_name[:12] == "digitstart__"): node_name = node_name[12:]
					#

					if (XmlNodeReader.HasAttributes):
					#
						while (XmlNodeReader.MoveToNextAttribute() and time() < timeout_time):
						#
							attribute_name = XmlNodeReader.Name.lower()
							if (str != _PY_UNICODE_TYPE and type(attribute_name) == _PY_UNICODE_TYPE): attribute_name = _PY_STR(attribute_name, "utf-8")

							if (attribute_name.startswith("xmlns:")): attributes_dict["xmlns:{0}".format(attribute_name[6:])] = XmlNodeReader.Value
							elif (attribute_name == "xml:space"):
							#
								attributes_dict['xml:space'] = XmlNodeReader.Value.lower()
								is_preserved_mode = (attributes_dict['xml:space'] == "preserve")
							#
							elif (strict_standard): attributes_dict[XmlNodeReader.Name] = XmlNodeReader.Value
							else: attributes_dict[attribute_name] = XmlNodeReader.Value
						#

						XmlNodeReader.MoveToElement()
					#

					is_node = True
				#

				is_read = XmlNodeReader.Read()
			#

			if (is_node):
			#
				if (len(node_path) > 0): node_path = "{0} {1}".format(node_path, node_name)
				else: node_path = node_name
			#

			while (is_node and time() < timeout_time):
			#
				if (xml_level < XmlNodeReader.Depth):
				#
					if (XmlNodeReader.NodeType == XmlNodeType.CDATA): node_content += (XmlNodeReader.Value if (is_preserved_mode) else XmlNodeReader.Value.strip())
					elif (XmlNodeReader.NodeType == XmlNodeType.Element):
					#
						is_read = False
						nodes_list.append(self.xml2dict_MonoXML_walker(XmlNodeReader, strict_standard, node_path, XmlNodeReader.Depth))
					#
					elif (XmlNodeReader.NodeType == XmlNodeType.EndElement):
					#
						is_read = False
						XmlNodeReader.Read()
					#
					elif (XmlNodeReader.NodeType == XmlNodeType.Text): node_content += (XmlNodeReader.Value if (is_preserved_mode) else XmlNodeReader.Value.strip())
					elif (is_preserved_mode and (XmlNodeReader.NodeType == XmlNodeType.Whitespace or XmlNodeReader.NodeType == XmlNodeType.SignificantWhitespace)): node_content += XmlNodeReader.Value

					if (is_read):
					#
						if (is_node): is_node = XmlNodeReader.Read()
						else: XmlNodeReader.Read()
					#
					else: is_read = True
				#
				else: is_node = False
			#

			var_return = { "node_path": node_path, "value": node_content, "attributes": attributes_dict, "children": nodes_list }
		#

		return var_return
	#
#

##j## EOF