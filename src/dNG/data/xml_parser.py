# -*- coding: utf-8 -*-

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

# pylint: disable=import-error,invalid-name,unused-import

from weakref import proxy, ProxyTypes
import re

try: from collections.abc import Mapping
except ImportError: from collections import Mapping

try: from html import escape as html_escape
except ImportError:
    from cgi import escape as html_escape
#

_IMPLEMENTATION_JAVA = 1
"""
Java based Python implementation
"""
_IMPLEMENTATION_PYTHON = 2
"""
Native Python implementation
"""
_IMPLEMENTATION_MONO = 3
"""
Mono/.NET based Python implementation
"""

try:
    _PY_STR = unicode.encode
    _PY_UNICODE_TYPE = unicode
except NameError:
    _PY_STR = bytes.decode
    _PY_UNICODE_TYPE = str
#

from .abstract_xml_parser import AbstractXmlParser

try:
    import java.lang.System
    _mode = _IMPLEMENTATION_JAVA
except ImportError: _mode = None

try:
    from .xml_parser_MonoXML import XmlParserMonoXml
    _mode = _IMPLEMENTATION_MONO
except ImportError: pass

if (_mode is None):
    from .xml_parser_expat import XmlParserExpat
    _mode = _IMPLEMENTATION_PYTHON
#

class XmlParser(object):
    """
This class provides a bridge between Python and XML to read XML on the fly.

:author:    direct Netware Group
:copyright: direct Netware Group - All rights reserved
:package:   XML.py
:since:     v0.1.0
:license:   https://www.direct-netware.de/redirect?licenses;mpl2
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
    RE_NODE_POSITIONS = re.compile("\\#(\\d+)(\W|$)")
    """
RegExp to find the first specified position for node names
    """
    RE_TAG_DIGIT = re.compile("^\\d")
    """
RegExp to find node names starting with a number (and are not standard
compliant)
    """

    def __init__(self, xml_charset = "UTF-8", node_type = dict, timeout_retries = 5, log_handler = None):
        """
Constructor __init__(XmlParser)

:param xml_charset: Charset to be added as information to XML output
:param node_type: Dict implementation for new nodes
:param timeout_retries: Retries before timing out
:param log_handler: Log handler to use

:since: v0.1.0
        """

        # global: _IMPLEMENTATION_MONO, _mode

        self._data = None
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
        self._log_handler = None
        """
The log handler is called whenever debug messages should be logged or errors
happened.
        """
        self.node_type = node_type
        """
Dict implementation used to create new nodes
        """
        self.parser_instance = None
        """
The selected parser implementation
        """

        if (log_handler is not None): self.log_handler = log_handler

        if (_mode == _IMPLEMENTATION_MONO): self.parser_instance = XmlParserMonoXml(self, timeout_retries, log_handler)
        else: self.parser_instance = XmlParserExpat(self, log_handler)
    #

    @property
    def data(self):
        """
Return the Python representation data of this "XmlParser" instance.

:return: (mixed) Python representation data; None if not parsed
:since:  v1.0.0
        """

        return self._data.copy()
    #

    @property
    def log_handler(self):
        """
Returns the LogHandler.

:return: (object) LogHandler in use
:since:  v1.0.0
        """

        return self._log_handler
    #

    @log_handler.setter
    def log_handler(self, log_handler):
        """
Sets the LogHandler.

:param log_handler: LogHandler to use

:since: v1.0.0
        """

        self._log_handler = (log_handler if (isinstance(log_handler, ProxyTypes)) else proxy(log_handler))
    #

    def add_node(self, node_path, value = "", attributes = "", add_recursively = True):
        """
Adds a XML node with content - recursively if required.

:param node_path: Path to the new node - delimiter is space
:param value: Value for the new node
:param attributes: Attributes of the node
:param add_recursively: True to create the required tree recursively

:return: (bool) False on error
:since:  v0.1.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        if (str is not _PY_UNICODE_TYPE):
            if (type(node_path) is _PY_UNICODE_TYPE): node_path = _PY_STR(node_path, "utf-8")
            if (type(value) is _PY_UNICODE_TYPE): value = _PY_STR(value, "utf-8")
        #

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.add_node({0})- (#echo(__LINE__)#)".format(node_path))
        _return = False

        if (self._data is None): self._data = self.node_type()

        if (type(node_path) == str):
            node_path = self._translate_ns_path(node_path)

            if (self.data_cache_node == ""
                or re.match("^{0}(\W|$)".format(re.escape(self.data_cache_node)), node_path, re.I) is None
                or ("xml.item" not in self.data_cache_ptr and "xml.mtree" not in self.data_cache_ptr)
               ):
                node_path_done = ""
                node_ptr = self._data
            else:
                node_path = node_path[len(self.data_cache_node):].strip()
                node_path_done = XmlParser.RE_NODE_POSITIONS.sub("\\2", self.data_cache_node)
                node_ptr = self.data_cache_ptr
            #

            is_available = True
            nodes_list = node_path.split(" ")

            while (is_available and len(nodes_list) > 0):
                is_available = False
                node_name = nodes_list.pop(0)
                re_result = XmlParser.RE_NODE_POSITION.match(node_name)

                if (re_result is None): node_position = -1
                else:
                    node_name = re_result.group(1)
                    node_position = int(re_result.group(2))
                #

                if (len(nodes_list) > 0):
                    if (node_name in node_ptr):
                        is_available = True

                        if ("xml.mtree" in node_ptr[node_name]):
                            mtree_node = node_ptr[node_name]

                            if (node_position >= 0):
                                if (node_position in mtree_node): _return = True
                            elif (mtree_node['xml.mtree'] in mtree_node):
                                node_position = mtree_node['xml.mtree']
                                _return = True
                            else: is_available = False

                            if (is_available):
                                if ((not isinstance(mtree_node[node_position], Mapping))
                                    or "xml.item" not in mtree_node[node_position]
                                   ): mtree_node[node_position] = self._convert_leaf_to_node(mtree_node[node_position])

                                node_ptr = mtree_node[node_position]
                            #
                        elif ("xml.item" in node_ptr[node_name]): node_ptr = node_ptr[node_name]
                        else:
                            node_ptr[node_name] = self._convert_leaf_to_node(node_ptr[node_name])
                            node_ptr = node_ptr[node_name]
                        #
                    #

                    if ((not is_available) and add_recursively):
                        node_dict = self.node_type(tag = node_name,
                                                   value = '',
                                                   attributes = { },
                                                   xmlns = { }
                                                  )

                        if ("xml.item" in node_ptr and "xmlns" in node_ptr['xml.item']):
                            node_dict['xmlns'] = node_ptr['xml.item']['xmlns'].copy()
                        #

                        self._add_node_ns_cache(node_path_done, node_name, node_dict)

                        is_available = True
                        node_ptr[node_name] = self._convert_leaf_to_node(node_dict)
                        node_ptr = node_ptr[node_name]
                    #
                else:
                    if (type(value) is not str): value = str(value)

                    node_dict = self.node_type(tag = node_name,
                                               value = value,
                                               attributes = { },
                                               xmlns = { }
                                              )

                    if ("xml.item" in node_ptr and "xmlns" in node_ptr['xml.item']): node_dict['xmlns'] = node_ptr['xml.item']['xmlns'].copy()

                    if (isinstance(attributes, Mapping) and len(attributes) > 0):
                        if ("xmlns" in attributes):
                            if (len(attributes['xmlns']) > 0):
                                if (attributes['xmlns'] not in self.data_ns_default):
                                    self.data_ns_counter += 1
                                    self.data_ns_default[attributes['xmlns']] = self.data_ns_counter
                                    self.data_ns_compact[self.data_ns_counter] = attributes['xmlns']
                                #

                                node_dict['xmlns']['@'] = self.data_ns_default[attributes['xmlns']]
                            elif ("@" in node_dict['xmlns']): del(node_dict['xmlns']['@'])
                        #

                        for key in attributes:
                            value = attributes[key]
                            value_type = type(value)

                            if ((value_type in ( str, _PY_UNICODE_TYPE )) and XmlParser.RE_ATTRIBUTES_XMLNS.match(key) is not None):
                                ns_name = key[6:]

                                if (len(value) > 0): node_dict['xmlns'][ns_name] = (self.data_ns_default[value] if (value in self.data_ns_default) else value)
                                elif (ns_name in node_dict['xmlns']): del(node_dict['xmlns'][ns_name])
                            #
                        #

                        node_dict['attributes'] = attributes
                    #

                    if (node_name in node_ptr):
                        if (not isinstance(node_ptr[node_name], Mapping)):
                            node_dict[node_name] = node_ptr[node_name]
                            node_ptr[node_name] = node_dict
                        elif ("xml.mtree" not in node_ptr[node_name]):
                            node_ptr[node_name] = self.node_type([ ( 0, node_ptr[node_name] ), ( 1, node_dict ) ])
                            node_ptr[node_name]['xml.mtree'] = 1
                        else:
                            node_ptr[node_name]['xml.mtree'] += 1
                            node_ptr[node_name][node_ptr[node_name]['xml.mtree']] = node_dict
                        #
                    else: node_ptr[node_name] = node_dict

                    self._add_node_ns_cache(node_path_done, node_name, node_dict)

                    _return = True
                #

                if (len(node_path_done) > 0): node_path_done += " "
                node_path_done += node_name
            #
        #

        return _return
    #

    def _add_node_ns_cache(self, node_path_done, node_name, node_dict):
        """
Caches XML namespace data for the given XML node.

:param node_path_done: XML node path containing the given XML node
:param node_name: XML node name
:param node_dict: XML node

:since: v0.1.0
        """

        node_ns_name = ""
        re_result = XmlParser.RE_NODE_NAME_XMLNS.match(node_name)

        if (re_result is not None):
            if (re_result.group(1) in node_dict['xmlns']
                and type(node_dict['xmlns'][re_result.group(1)]) is int
               ): node_ns_name = "{0}:{1}".format(node_dict['xmlns'][re_result.group(1)], re_result.group(2))
        elif ("@" in node_dict['xmlns']): node_ns_name = "{0}:{1}".format(node_dict['xmlns']['@'], node_name)

        if (len(node_path_done) > 0):
            self.data_ns_predefined_compact["{0} {1}".format(node_path_done, node_name)] = "{0} {1}".format(self.data_ns_predefined_compact[node_path_done],
                                                                                                            (node_name if (node_ns_name == "") else node_ns_name)
                                                                                                           )

            self.data_ns_predefined_default[self.data_ns_predefined_compact["{0} {1}".format(node_path_done, node_name)]] = "{0} {1}".format(node_path_done, node_name)
        elif (node_ns_name == ""):
            self.data_ns_predefined_compact[node_name] = node_name
            self.data_ns_predefined_default[node_name] = node_name
        else:
            self.data_ns_predefined_compact[node_name] = node_ns_name
            self.data_ns_predefined_default[node_ns_name] = node_name
        #
    #

    def _convert_leaf_to_node(self, node_ptr):
        """
Convert an XML leaf to a node.

:param node_ptr: XML leaf pointer

:return: XML node dict
:since:  v0.1.0
        """

        return self.node_type([ ( "xml.item", node_ptr ) ])
    #

    def dict_to_xml(self, xml_tree, strict_standard_mode = True):
        """
Builds recursively a valid XML ouput reflecting the given XML dict tree.

:param xml_tree: XML dict tree level to work on
:param strict_standard_mode: Be standard conform

:return: (str) XML output string
:since:  v0.1.0
        """

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.dict_to_xml()- (#echo(__LINE__)#)")
        _return = ""

        if (isinstance(xml_tree, Mapping) and len(xml_tree) > 0):
            for xml_node in xml_tree:
                xml_node_dict = xml_tree[xml_node]

                if ("xml.mtree" in xml_node_dict):
                    del(xml_node_dict['xml.mtree'])
                    _return += self.dict_to_xml(xml_node_dict, strict_standard_mode)
                elif ("xml.item" in xml_node_dict):
                    _return += self.dict_to_xml_item_encoder(xml_node_dict['xml.item'], False, strict_standard_mode)

                    xml_node_tag = (xml_node_dict['xml.item']['tag']
                                    if (XmlParser.RE_TAG_DIGIT.match(xml_node_dict['xml.item']['tag']) is None) else
                                    "digitstart__{0}".format(xml_node_dict['xml.item']['tag'])
                                   )

                    del(xml_node_dict['xml.item'])
                    _return += "{0}</{1}>".format(self.dict_to_xml(xml_node_dict, strict_standard_mode), xml_node_tag)
                elif (len(xml_node_dict['tag']) > 0): _return += self.dict_to_xml_item_encoder(xml_node_dict, True, strict_standard_mode)
            #
        #

        return _return.strip()
    #

    def dict_to_xml_item_encoder(self, data, close_tag = True, strict_standard_mode = True):
        """
Builds recursively a valid XML ouput reflecting the given XML dict tree.

:param data: Dict containing information about the current item
:param close_tag: Output will contain an ending tag if true
:param strict_standard_mode: Be standard conform

:return: (str) XML output string
:since:  v0.1.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        _return = ""

        if (isinstance(data, Mapping)):
            if (len(data['tag']) > 0):
                if (re.match("\\d", data['tag']) is not None): data['tag'] = "digitstart__{0}".format(data['tag'])
                _return += "<{0}".format(data['tag'])

                if ("attributes" in data):
                    for key in data['attributes']:
                        if (data['attributes'][key] is None): value = ""
                        else:
                            value = data['attributes'][key]
                            value_type = type(value)

                            if (str is not _PY_UNICODE_TYPE and value_type is _PY_UNICODE_TYPE): value = _PY_STR(value, "utf-8")
                            elif (value_type is not str): value = str(value)

                            value = value.replace("&", "&amp;")
                            value = value.replace("<", "&lt;")
                            value = value.replace(">", "&gt;")
                            value = value.replace('"', "&quot;")
                            if (self.data_charset != "UTF-8"): value = value.encode(self.data_charset)
                        #

                        _return += " {0}=\"{1}\"".format(key, value)
                    #
                #

                value = None

                if ("value" in data):
                    value = data['value']
                    value_type = type(value)

                    if (str is not _PY_UNICODE_TYPE and value_type is _PY_UNICODE_TYPE): value = _PY_STR(value, "utf-8")
                    elif (value_type is not str): value = str(value)
                #

                if (close_tag
                    and (not strict_standard_mode)
                    and (value is None or len(value) < 1)
                   ): _return += " />"
                else:
                    _return += ">"

                    if (value is not None):
                        if (self.data_charset != "UTF-8"): value = value.encode(self.data_charset)

                        if ("<" not in value and ">" not in value): _return += value.replace("&", "&amp;")
                        elif (self.data_cdata_encoding):
                            if ("]]>" in value): value = value.replace("]]>", "]]]]><![CDATA[>")
                            _return += "<![CDATA[{0}]]>".format(value)
                        else: _return += html_escape(value, True)
                    #

                    if (close_tag): _return += "</{0}>".format(data['tag'])
                #
            #
        #

        return _return
    #

    def parse(self, data, strict_standard_mode = True):
        """
Parses the given XML data.

:param data: Input XML data
:param strict_standard_mode: True to be standard compliant

:since: v0.1.2
        """

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.parse()- (#echo(__LINE__)#)")

        self._data = None
        self.data_cache_node = ""
        self.data_cache_ptr = None

        self.parser_instance.set_mode(AbstractXmlParser.MODE_TREE)
        self.parser_instance.set_strict_standard(strict_standard_mode)
        self.parser_instance.parse(data)
    #

    def register_ns(self, ns, uri):
        """
Registers a namespace (URI) for later use with this XML reader instance.

:param ns: Output relevant namespace definition
:param uri: Uniform Resource Identifier

:since: v0.1.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        if (str is not _PY_UNICODE_TYPE):
            if (type(ns) is _PY_UNICODE_TYPE): ns = _PY_STR(ns, "utf-8")
            if (type(uri) is _PY_UNICODE_TYPE): uri = _PY_STR(uri, "utf-8")
        #

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.register_ns({0}, {1})- (#echo(__LINE__)#)".format(ns, uri))
        self.data_ns[ns] = uri

        if (uri not in self.data_ns_default):
            self.data_ns_counter += 1
            self.data_ns_default[uri] = self.data_ns_counter
            self.data_ns_compact[self.data_ns_counter] = uri
        #
    #

    def translate_ns(self, node):
        """
Translates the tag value if a predefined namespace matches. The translated
tag will be saved as "tag_ns" and "tag_parsed".

:param node: XML tree node

:return: (dict) Checked XML tree node
:since:  v0.1.0
        """

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.translate_ns()- (#echo(__LINE__)#)")
        _return = node

        if (isinstance(node, Mapping) and "tag" in node and isinstance(node.get("xmlns"), Mapping)):
            _return['tag_ns'] = ""
            _return['tag_parsed'] = node['tag']

            re_result = XmlParser.RE_NODE_NAME_XMLNS.match(node['tag'])

            if (re_result is not None and re_result.group(1) in node['xmlns'] and node['xmlns'][re_result.group(1)] in self.data_ns_compact):
                tag_ns = XmlParser._search_dict(self.data_ns_compact[node['xmlns'][re_result.group(1)]], self.data_ns)

                if (tag_ns is not None):
                    _return['tag_ns'] = tag_ns
                    _return['tag_parsed'] = "{0}:{1}".format(tag_ns, re_result.group(2))
                #
            #

            if ("attributes" in node):
                for key in node['attributes']:
                    re_result = XmlParser.RE_NODE_NAME_XMLNS.match(key)

                    if (re_result is not None and re_result.group(1) in node['xmlns'] and node['xmlns'][re_result.group(1)] in self.data_ns_compact):
                        tag_ns = XmlParser._search_dict(self.data_ns_compact[node['xmlns'][re_result.group(1)]], self.data_ns)

                        if (tag_ns is not None):
                            _return['attributes']["{0}:{1}".format(tag_ns, re_result.group(2))] = node['attributes'][key]
                            del(_return['attributes'][key])
                        #
                    #
                #
            #
        #

        return _return
    #

    def _translate_ns_path(self, node_path):
        """
Checks input path for predefined namespaces converts it to the internal
path.

:param node_path: Path to the new node; delimiter is space

:return: (str) Output node path
:since:  v0.1.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        if (str is not _PY_UNICODE_TYPE and type(node_path) is _PY_UNICODE_TYPE): node_path = _PY_STR(node_path, "utf-8")

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml._translate_ns_path({0})- (#echo(__LINE__)#)".format(node_path))
        _return = node_path

        nodes_list = node_path.split(" ")
        node_path = ""

        while (len(nodes_list) > 0):
            node_name = nodes_list.pop(0)
            if (len(node_path) > 0): node_path += " "

            if (":" in node_name):
                re_result = XmlParser.RE_NODE_NAME_XMLNS.match(node_name)

                if (re_result is None): node_path += node_name
                else:
                    node_path += "{0}:{1}".format((self.data_ns_default[self.data_ns[re_result.group(1)]]
                                                   if (re_result.group(1) in self.data_ns and self.data_ns[re_result.group(1)] in self.data_ns_default) else
                                                   re_result.group(1)
                                                  ),
                                                  re_result.group(2)
                                                 )
            else: node_path += node_name
        #

        if (node_path in self.data_ns_predefined_default): _return = self.data_ns_predefined_default[node_path]
        return _return
    #

    def set_xml_tree(self, data_dict, overwrite = False):
        """
Sets the Python representation data of this "XmlResource" instance.

:param data_dict: Python representation data
:param overwrite: True to overwrite the current (non-empty) cache

:return: (bool) True on success
:since:  v1.0.0
        """

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.set_xml_tree()- (#echo(__LINE__)#)")
        _return = False

        if ((self._data is None or overwrite) and isinstance(data_dict, Mapping)):
            self._data = data_dict
            _return = True
        #

        return _return
    #

    def set_cdata_encoding(self, use_cdata = True):
        """
Uses or disables CDATA nodes to encode embedded XML.

:param use_cdata: Use CDATA nodes

:since: v0.1.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.set_cdata_encoding()- (#echo(__LINE__)#)")

        _type = type(use_cdata)

        if ((_type is bool and use_cdata) or (_type is str and use_cdata == "1")): self.data_cdata_encoding = True
        elif (use_cdata is None and (not self.data_cdata_encoding)): self.data_cdata_encoding = True
        else: self.data_cdata_encoding = False
    #

    def unregister_ns(self, ns = ""):
        """
Unregisters a namespace or clears the cache (if ns is empty).

:param ns: Output relevant namespace definition

:since: v0.1.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        if (str is not _PY_UNICODE_TYPE and type(ns) is _PY_UNICODE_TYPE): ns = _PY_STR(ns, "utf-8")

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.unregister_ns({0})- (#echo(__LINE__)#)".format(ns))

        if (len(ns) > 0):
            if (ns in self.data_ns):
                del(self.data_ns_compact[self.data_ns_default[self.data_ns[ns]]])
                del(self.data_ns_default[self.data_ns[ns]])
                del(self.data_ns[ns])
            #
        else:
            self.data_ns = { }
            self.data_ns_compact = { }
            self.data_ns_counter = 0
            self.data_ns_default = { }
            self.data_ns_predefined_compact = { }
            self.data_ns_predefined_default = { }
        #
    #

    def xml_to_merged_dict(self, data):
        """
Converts XML data into a merged XML dictionary.

:param data: Input XML data

:return: (dict) Merged XML dictionary; None on error
:since:  v1.0.0
        """

        # global: _mode, _PY_STR, _PY_UNICODE_TYPE
        # pylint: disable=broad-except

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.xml_to_merged_dict()- (#echo(__LINE__)#)")
        _return = None

        try:
            self.parser_instance.set_mode(AbstractXmlParser.MODE_MERGED)
            _return = self.parser_instance.parse(data)
        except Exception: pass

        return _return
    #

    @staticmethod
    def _search_dict(needle, haystack):
        """
Searches haystack for needle.

:param needle: Value to be searched for
:param haystack: Dict to search in

:return: (mixed) Key; None on error
:since:  v0.1.0
        """

        _return = None

        if (needle in haystack):
            for key in haystack:
                if (haystack[key] == needle):
                    _return = key
                    break
                #
            #
        #

        return _return
    #

    @staticmethod
    def xml_to_dict(data, treemode = True, strict_standard_mode = True):
        """
Converts XML data into a multi-dimensional XML tree or merged one.

:param data: Input XML data
:param treemode: Create a multi-dimensional result
:param strict_standard_mode: True to be standard compliant

:return: (dict) Multi-dimensional XML tree or merged one; None on error
:since:  v1.0.0
        """

        _return = None

        xml_parser = XmlParser()

        if (treemode):
            xml_parser.parse(data, strict_standard_mode)
            _return = xml_parser.data
        else:
            _return = xml_parser.xml_to_merged_dict(data)
        #

        return _return
    #
#
