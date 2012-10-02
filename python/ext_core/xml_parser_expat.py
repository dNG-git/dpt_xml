# -*- coding: utf-8 -*-
##j## BOF

"""
XML (Extensible Markup Language) is the easiest way to use a descriptive
language for controlling applications locally and world wide.
"""
"""n// NOTE
----------------------------------------------------------------------------
Extended Core: XML
Multiple XML parsers: Common abstraction layer
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.php?ext_core_xml

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.php?licenses;mpl2
----------------------------------------------------------------------------
#echo(extCoreXmlVersion)#
extCore_xml/#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

try: _unicode_object = { "type": unicode,"str": unicode.encode }
except: _unicode_object = { "type": bytes,"str": bytes.decode }

class direct_xml_parser_expat (object):
#
	"""
This implementation supports expat for XML parsing.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    ext_core
:subpackage: xml
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.php?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	data_merged_mode = False
	"""
True if the parser is set to merged
	"""
	debug = None
	"""
Debug message container
	"""
	node_path = ""
	"""
Current node path of the parser
	"""
	node_path_list = [ ]
	"""
Current path as an array of node tags
	"""
	node_path_depth = 0
	"""
Current depth
	"""
	parser = None
	"""
Container for the XML document
	"""
	parser_active = False
	"""
True if not the last element has been reached
	"""
	parser_cache = { }
	"""
Parser data cache
	"""
	parser_cache_counter = 0
	"""
Cache entry counter
	"""
	parser_cache_link = ""
	"""
Links to the latest entry added
	"""
	parser_strict_standard = True
	"""
True to be standard conform
	"""

	"""
----------------------------------------------------------------------------
Construct the class
----------------------------------------------------------------------------
	"""

	def __init__ (self,parser,debug = False):
	#
		"""
Constructor __init__ (direct_xml_parser_expat)

:param parser: Container for the XML document
:param debug: Debug flag

:since: v0.1.00
		"""

		if (debug): self.debug = [ "xml/#echo(__FILEPATH__)# -xml_parser.__init__ (direct_xml_parser_expat)- (#echo(__LINE__)#)" ]
		else: self.debug = None

		"""
----------------------------------------------------------------------------
Connect to the Python container for the XML document
----------------------------------------------------------------------------
		"""

		self.data_merged_mode = False
		self.node_path_list = [ ]
		self.parser = parser
		self.parser_active = False
		self.parser_cache = { }
		self.parser_strict_standard = True
	#

	def __del__ (self):
	#
		"""
Destructor __del__ (direct_xml_parser_expat)

:since: v0.1.00
		"""

		self.del_direct_xml_parser_expat ()
	#

	def del_direct_xml_parser_expat (self):
	#
		"""
Destructor del_direct_xml_parser_expat (direct_xml_parser_expat)

:since: v0.1.00
		"""

		self.parser = None
	#

	def define_mode (self,mode = ""):
	#
		"""
Define the parser mode ("tree" or "merged").

:param mode: Mode to select

:return: (bool) True if parser is set to merged mode
:since:  v0.1.00
		"""

		global _unicode_object
		if (type (mode) == _unicode_object['type']): mode = _unicode_object['str'] (mode,"utf-8")

		if (self.debug != None): self.debug.append ("xml/#echo(__FILEPATH__)# -xml_parser.define_mode ({0})- (#echo(__LINE__)#)".format (mode))

		f_type = type (mode)

		if ((not self.parser_active) and (type (mode) == str)):
		#
			if (mode == "merged"): self.data_merged_mode = True
			else: self.data_merged_mode = False
		#

		return self.data_merged_mode
	#

	def define_strict_standard (self,strict_standard):
	#
		"""
Changes the parser mode regarding being strict standard conform.

:param strict_standard: Be standard conform

:return: (bool) Accepted state
:since:  v0.1.00
		"""

		global _unicode_object
		if (self.debug != None): self.debug.append ("xml/#echo(__FILEPATH__)# -xml_parser.define_strict_standard (strict_standard)- (#echo(__LINE__)#)")

		if (type (strict_standard) == _unicode_object['type']): strict_standard = _unicode_object['str'] (strict_standard,"utf-8")
		f_type = type (strict_standard)

		if (((f_type == bool) or (f_type == str)) and (strict_standard)): self.parser_strict_standard = True
		elif ((strict_standard == None) and (not self.parser_strict_standard)): self.parser_strict_standard = True
		else: self.parser_strict_standard = False

		return self.parser_strict_standard
	#

	def expat_cdata (self,data):
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

		if (self.debug != None): self.debug.append ("xml/#echo(__FILEPATH__)# -xml_parser.expat_cdata (data)- (#echo(__LINE__)#)")

		if (self.parser_active):
		#
			if ("value" in self.parser_cache[self.parser_cache_link[self.node_path]]): self.parser_cache[self.parser_cache_link[self.node_path]]['value'] += data
			else: self.parser_cache[self.parser_cache_link[self.node_path]]['value'] = data
		#
	#

	def expat_element_end (self,name):
	#
		"""
Method to handle "end element" callbacks.

:param name: XML tag

:since: v0.1.00
		"""

		global _unicode_object
		if (type (name) == _unicode_object['type']): name = _unicode_object['str'] (name,"utf-8")

		if (self.debug != None): self.debug.append ("xml/#echo(__FILEPATH__)# -xml_parser.expat_element_end ({0})- (#echo(__LINE__)#)".format (name))

		if (self.parser_active):
		#
			f_node_path = self.parser_cache_link[self.node_path]

			del (self.parser_cache_link[self.node_path])
			self.node_path_list.pop ()
			self.node_path_depth -= 1
			self.node_path = " ".join (self.node_path_list)

			if ("value" in self.parser_cache[f_node_path]):
			#
				if ("xml:space" in self.parser_cache[f_node_path]['attributes']):
				#
					if (self.parser_cache[f_node_path]['attributes']['xml:space'] != "preserve"): self.parser_cache[f_node_path]['value'] = self.parser_cache[f_node_path]['value'].strip ()
				#
				else: self.parser_cache[f_node_path]['value'] = self.parser_cache[f_node_path]['value'].strip ()
			#
			else: self.parser_cache[f_node_path]['value'] = ""

			if ((not self.parser_strict_standard) and ("value" in self.parser_cache[f_node_path]['attributes']) and (len (self.parser_cache[f_node_path]['value']) < 1)):
			#
				self.parser_cache[f_node_path]['value'] = self.parser_cache[f_node_path]['attributes']['value']
				del (self.parser_cache[f_node_path]['attributes']['value'])
			#

			if (self.node_path_depth < 1):
			#
				self.node_path = ""
				self.parser_active = False
			#
		#
	#

	def expat_merged_cdata (self,data):
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

		if (self.debug != None): self.debug.append ("xml/#echo(__FILEPATH__)# -xml_parser.expat_merged_cdata (data)- (#echo(__LINE__)#)")

		if (self.parser_active):
		#
			if (self.parser_cache_link[self.node_path] > 0): self.parser_cache[self.node_path][self.parser_cache_link[self.node_path]]['value'] += data
			else: self.parser_cache[self.node_path]['value'] += data
		#
	#

	def expat_merged_element_end (self,name):
	#
		"""
Method to handle "end element" callbacks. (Merged XML parser)

:param name: XML tag

:since: v0.1.00
		"""

		global _unicode_object
		if (type (name) == _unicode_object['type']): name = _unicode_object['str'] (name,"utf-8")

		if (self.debug != None): self.debug.append ("xml/#echo(__FILEPATH__)# -xml_parser.expat_merged_element_end ({0})- (#echo(__LINE__)#)".format (name))

		if (self.parser_active):
		#
			if (self.parser_cache_link[self.node_path] > 0): f_node_pointer = self.parser_cache[self.node_path][self.parser_cache_link[self.node_path]]
			else: f_node_pointer = self.parser_cache[self.node_path]

			self.node_path_list.pop ()
			self.node_path_depth -= 1
			self.node_path = "_".join (self.node_path_list)

			if ("xml:space" in f_node_pointer['attributes']):
			#
				if (f_node_pointer['attributes']['xml:space'] != "preserve"): f_node_pointer['value'] = f_node_pointer['value'].strip ()
			#
			else: f_node_pointer['value'] = f_node_pointer['value'].strip ()

			if (("value" in f_node_pointer['attributes']) and (len (f_node_pointer['value']) < 1)):
			#
				f_node_pointer['value'] = f_node_pointer['attributes']['value']
				del (f_node_pointer['attributes']['value'])
			#

			if (self.node_path_depth < 1):
			#
				self.node_path = ""
				self.parser_active = False
			#
		#
	#

	def expat_merged_element_start (self,name,attributes):
	#
		"""
Method to handle "start element" callbacks. (Merged XML parser)

:param name: XML tag
:param attributes: Node attributes

:since: v0.1.00
		"""

		global _unicode_object
		if (type (name) == _unicode_object['type']): name = _unicode_object['str'] (name,"utf-8")

		if (self.debug != None): self.debug.append ("xml/#echo(__FILEPATH__)# -xml_parser.expat_merged_element_start ({0},attributes)- (#echo(__LINE__)#)".format (name))

		if (not self.parser_active):
		#
			self.node_path = ""
			self.node_path_depth = 0
			self.parser_active = True
			self.parser_cache_link = { }
		#

		name = name.lower ()
		if (name.find ("digitstart__") == 0): name = name[12:]

		if (len (self.node_path) > 0): self.node_path += "_"
		self.node_path += name
		self.node_path_list.append (name)
		self.node_path_depth += 1

		for f_key in attributes:
		#
			if (type (f_key) == _unicode_object['type']): f_key = _unicode_object['str'] (f_key,"utf-8")
			f_key_lowercase = f_key.lower ()
			f_value = attributes[f_key]

			if (f_key_lowercase.startswith ("xmlns:")):
			#
				attributes[("xmlns:{0}".format (f_key[6:]))] = f_value
				if ((f_key != "xmlns:{0}".format (f_key[6:]))): del (attributes[f_key])
			#
			elif (f_key_lowercase == "xml:space"):
			#
				attributes[f_key_lowercase] = f_value.lower ()
				if (f_key != f_key_lowercase): del (attributes[f_key])
			#
			elif (f_key != f_key_lowercase):
			#
				del (attributes[f_key])
				attributes[f_key_lowercase] = f_value
			#
		#

		f_node_dict = { "tag": name,"level": self.node_path_depth,"value": "","attributes": attributes }

		if (self.node_path in self.parser_cache):
		#
			if ("tag" in self.parser_cache[self.node_path]): self.parser_cache[self.node_path] = [ self.parser_cache[self.node_path],f_node_dict ]
			else: self.parser_cache[self.node_path].append (f_node_dict)

			self.parser_cache_link[self.node_path] += 1
		#
		else:
		#
			self.parser_cache[self.node_path] = f_node_dict
			self.parser_cache_link[self.node_path] = 0
		#
	#

	def expat_element_start (self,name,attributes):
	#
		"""
Method to handle "start element" callbacks.

:param name: XML tag
:param attributes: Node attributes

:since: v0.1.00
		"""

		global _unicode_object
		if (type (name) == _unicode_object['type']): name = _unicode_object['str'] (name,"utf-8")

		if (self.debug != None): self.debug.append ("xml/#echo(__FILEPATH__)# -xml_parser.expat_element_start ({0},attributes)- (#echo(__LINE__)#)".format (name))

		if (not self.parser_active):
		#
			self.node_path = ""
			self.node_path_depth = 0
			self.parser_active = True
			self.parser_cache_counter = 0
			self.parser_cache_link ={ }
		#

		if (not self.parser_strict_standard):
		#
			name = name. lower ()
			if (name.find ("digitstart__") == 0): name = name[12:]
		#

		if (len (self.node_path) > 0): self.node_path += " "
		self.node_path += name
		self.node_path_list.append (name)
		self.node_path_depth += 1

		for f_key in attributes:
		#
			if (type (f_key) == _unicode_object['type']): f_key = _unicode_object['str'] (f_key,"utf-8")
			f_key_lowercase = f_key.lower ()
			f_value = attributes[f_key]

			if (f_key_lowercase.startswith ("xmlns:")):
			#
				attributes[("xmlns:{0}".format (f_key[6:]))] = f_value
				if (f_key != "xmlns:{0}".format (f_key[6:])): del (attributes[f_key])
			#
			elif (f_key_lowercase == "xml:space"):
			#
				attributes[f_key_lowercase] = f_value.lower ()
				if (f_key != f_key_lowercase): del (attributes[f_key])
			#
			elif ((not self.parser_strict_standard) and (f_key != f_key_lowercase)):
			#
				del (attributes[f_key])
				attributes[f_key_lowercase] = f_value
			#
		#

		self.parser_cache[self.parser_cache_counter] = { "node_path": self.node_path,"attributes": attributes }
		self.parser_cache_link[self.node_path] = self.parser_cache_counter
		self.parser_cache_counter += 1
	#

	def xml2array_expat (self):
	#
		"""
Adds the result of an expat parsing operation to the defined XML instance if
the parser completed its work.

:return: (dict) Multi-dimensional XML tree
:since:  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("xml/#echo(__FILEPATH__)# -xml_parser.xml2array_expat ()- (#echo(__LINE__)#)")
		f_return = { }

		if ((not self.parser_active) and (type (self.parser_cache) == dict) and (len (self.parser_cache) > 0)):
		#
			self.parser.set ({ })

			for f_node_key in self.parser_cache:
			#
				f_node_dict = self.parser_cache[f_node_key]
				self.parser.node_add (f_node_dict['node_path'],f_node_dict['value'],f_node_dict['attributes'])
			#

			self.parser_cache = { }
			f_return = self.parser.get ()
		#

		return f_return
	#

	def xml2array_expat_merged (self):
	#
		"""
Returns the merged result of an expat parsing operation if the parser
completed its work.

:return: (dict) Merged XML tree
:since:  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("xml/#echo(__FILEPATH__)# -xml_parser.xml2array_expat_merged ()- (#echo(__LINE__)#)")
		f_return = { }

		if ((not self.parser_active) and (type (self.parser_cache) == dict) and (len (self.parser_cache) > 0)):
		#
			f_return = self.parser_cache
			self.parser_cache = { }
		#

		return f_return
	#
#

##j## EOF