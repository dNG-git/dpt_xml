# -*- coding: utf-8 -*-
##j## BOF

"""
Expat implementation for XML.py
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

try: _unicode_object = { "type": unicode, "str": unicode.encode }
except: _unicode_object = { "type": bytes, "str": bytes.decode }

class direct_xml_parser_expat(object):
#
	"""
This implementation supports expat for XML parsing.

:author:    direct Netware Group
:copyright: direct Netware Group - All rights reserved
:package:   XML.py
:since:     v0.1.00
:license:   http://www.direct-netware.de/redirect.py?licenses;mpl2
            Mozilla Public License, v. 2.0
	"""

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
Constructor __init__(direct_xml_parser_expat)

:param parser: Container for the XML document
:param event_handler: EventHandler to use

:since: v0.1.00
		"""

		if (event_handler != None): event_handler.debug("#echo(__FILEPATH__)# -xml.__init__()- (#echo(__LINE__)#)")

		self.data_merged_mode = False
		"""
True if the parser is set to merged
		"""
		self.event_handler = event_handler
		"""
The EventHandler is called whenever debug messages should be logged or errors
happened.
		"""
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
		self.parser = parser
		"""
Container for the XML document
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
		self.parser_strict_standard = True
		"""
True to be standard conform
		"""
	#

	def __del__(self):
	#
		"""
Destructor __del__(direct_xml_parser_expat)

:since: v0.1.00
		"""

		self.parser = None
	#

	def define_mode(self, mode = 1):
	#
		"""
Define the parser mode MODE_MERGED or MODE_TREE.

:param mode: Mode to select

:return: (bool) True if parser is set to merged mode
:since:  v0.1.00
		"""

		global _unicode_object
		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.define_mode({0:d})- (#echo(__LINE__)#)".format(mode))

		if ((not self.parser_active) and type(mode) == int):
		#
			if (mode == direct_xml_parser_expat.MODE_MERGED): self.data_merged_mode = True
			else: self.data_merged_mode = False
		#

		return self.data_merged_mode
	#

	def define_strict_standard(self, strict_standard):
	#
		"""
Changes the parser mode regarding being strict standard compliant.

:param strict_standard: True to be standard compliant

:return: (bool) Accepted state
:since:  v0.1.00
		"""

		global _unicode_object
		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.define_strict_standard(strict_standard)- (#echo(__LINE__)#)")

		if (type(strict_standard) == _unicode_object['type']): strict_standard = _unicode_object['str'](strict_standard, "utf-8")
		var_type = type(strict_standard)

		if ((var_type == bool or var_type == str) and strict_standard): self.parser_strict_standard = True
		elif (strict_standard == None and (not self.parser_strict_standard)): self.parser_strict_standard = True
		else: self.parser_strict_standard = False

		return self.parser_strict_standard
	#

	def expat_cdata(self, data):
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

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.expat_cdata(data)- (#echo(__LINE__)#)")

		if (self.parser_active):
		#
			if ("value" in self.parser_cache[self.parser_cache_link[self.node_path]]): self.parser_cache[self.parser_cache_link[self.node_path]]['value'] += data
			else: self.parser_cache[self.parser_cache_link[self.node_path]]['value'] = data
		#
	#

	def expat_element_end(self, name):
	#
		"""
Method to handle "end element" callbacks.

:param name: XML tag

:since: v0.1.00
		"""

		global _unicode_object
		if (type(name) == _unicode_object['type']): name = _unicode_object['str'](name, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.expat_element_end({0})- (#echo(__LINE__)#)".format(name))

		if (self.parser_active):
		#
			node_path = self.parser_cache_link[self.node_path]

			del(self.parser_cache_link[self.node_path])
			self.node_path_list.pop()
			self.node_path_depth -= 1
			self.node_path = " ".join(self.node_path_list)

			if ("value" in self.parser_cache[node_path]):
			#
				if ("xml:space" not in self.parser_cache[node_path]['attributes']): self.parser_cache[node_path]['value'] = self.parser_cache[node_path]['value'].strip()
				elif (self.parser_cache[node_path]['attributes']['xml:space'] != "preserve"): self.parser_cache[node_path]['value'] = self.parser_cache[node_path]['value'].strip()
			#
			else: self.parser_cache[node_path]['value'] = ""

			if ((not self.parser_strict_standard) and "value" in self.parser_cache[node_path]['attributes'] and len(self.parser_cache[node_path]['value']) < 1):
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

	def expat_merged_cdata(self, data):
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

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.expat_merged_cdata(data)- (#echo(__LINE__)#)")

		if (self.parser_active):
		#
			if (self.parser_cache_link[self.node_path] > 0): self.parser_cache[self.node_path][self.parser_cache_link[self.node_path]]['value'] += data
			else: self.parser_cache[self.node_path]['value'] += data
		#
	#

	def expat_merged_element_end(self, name):
	#
		"""
Method to handle "end element" callbacks. (Merged XML parser)

:param name: XML tag

:since: v0.1.00
		"""

		global _unicode_object
		if (type(name) == _unicode_object['type']): name = _unicode_object['str'](name, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.expat_merged_element_end({0})- (#echo(__LINE__)#)".format(name))

		if (self.parser_active):
		#
			if (self.parser_cache_link[self.node_path] > 0): node_ptr = self.parser_cache[self.node_path][self.parser_cache_link[self.node_path]]
			else: node_ptr = self.parser_cache[self.node_path]

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

	def expat_merged_element_start(self, name, attributes):
	#
		"""
Method to handle "start element" callbacks. (Merged XML parser)

:param name: XML tag
:param attributes: Node attributes

:since: v0.1.00
		"""

		global _unicode_object
		if (type(name) == _unicode_object['type']): name = _unicode_object['str'](name, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.expat_merged_element_start({0}, attributes)- (#echo(__LINE__)#)".format(name))

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
			if (type(key) == _unicode_object['type']): key = _unicode_object['str'](key, "utf-8")
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

	def expat_element_start(self, name, attributes):
	#
		"""
Method to handle "start element" callbacks.

:param name: XML tag
:param attributes: Node attributes

:since: v0.1.00
		"""

		global _unicode_object
		if (type(name) == _unicode_object['type']): name = _unicode_object['str'](name, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.expat_element_start({0}, attributes)- (#echo(__LINE__)#)".format(name))

		if (not self.parser_active):
		#
			self.node_path = ""
			self.node_path_depth = 0
			self.parser_active = True
			self.parser_cache_counter = 0
			self.parser_cache_link = { }
		#

		if (not self.parser_strict_standard):
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
			if (type(key) == _unicode_object['type']): key = _unicode_object['str'](key, "utf-8")
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
			elif ((not self.parser_strict_standard) and key != key_lowercase):
			#
				del(attributes[key])
				attributes[key_lowercase] = value
			#
		#

		self.parser_cache[self.parser_cache_counter] = { "node_path": self.node_path, "attributes": attributes }
		self.parser_cache_link[self.node_path] = self.parser_cache_counter
		self.parser_cache_counter += 1
	#

	def xml2dict_expat(self):
	#
		"""
Adds the result of an expat parsing operation to the defined XML instance if
the parser completed its work.

:return: (dict) Multi-dimensional XML tree
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.xml2dict_expat()- (#echo(__LINE__)#)")
		var_return = { }

		if ((not self.parser_active) and type(self.parser_cache) == dict and len(self.parser_cache) > 0):
		#
			self.parser.set({ })

			for node_key in self.parser_cache:
			#
				node_dict = self.parser_cache[node_key]
				self.parser.node_add(node_dict['node_path'], node_dict['value'], node_dict['attributes'])
			#

			self.parser_cache = { }
			var_return = self.parser.get()
		#

		return var_return
	#

	def xml2dict_expat_merged(self):
	#
		"""
Returns the merged result of an expat parsing operation if the parser
completed its work.

:return: (dict) Merged XML tree
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -xml.xml2array_expat_merged()- (#echo(__LINE__)#)")
		var_return = { }

		if ((not self.parser_active) and type(self.parser_cache) == dict and len(self.parser_cache) > 0):
		#
			var_return = self.parser_cache
			self.parser_cache = { }
		#

		return var_return
	#
#

##j## EOF