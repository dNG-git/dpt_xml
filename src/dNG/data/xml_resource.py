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

# pylint: disable=invalid-name

from .xml_parser import XmlParser

try:
    _PY_STR = unicode.encode
    _PY_UNICODE_TYPE = unicode
except NameError:
    _PY_STR = bytes.decode
    _PY_UNICODE_TYPE = str
#

class XmlResource(XmlParser):
    """
This class extends the bridge between Python and XML to work with XML and
create valid documents.

:author:    direct Netware Group
:copyright: direct Netware Group - All rights reserved
:package:   XML.py
:since:     v0.1.0
:license:   https://www.direct-netware.de/redirect?licenses;mpl2
            Mozilla Public License, v. 2.0
    """

    def __init__(self, xml_charset = "UTF-8", node_type = dict, timeout_retries = 5, log_handler = None):
        """
Constructor __init__(XmlResource)

:param xml_charset: Charset to be added as information to XML output
:param node_type: Dict implementation for new nodes
:param timeout_retries: Retries before timing out
:param log_handler: Log handler to use

:since: v0.1.0
        """

        XmlParser.__init__(self, xml_charset, node_type, timeout_retries, log_handler)
    #

    @XmlParser.data.setter
    def data(self, data_dict):
        """
Sets the Python representation data of this "XmlResource" instance.

:param data_dict: Python representation data

:since: v1.0.0
        """

        self.set_xml_tree(data_dict, True)
    #

    @property
    def xml(self):
        """
Returns the XML string for the Python representation data of this instance.

:return: (str) Result string
:since:  v1.0.0
        """

        return self.export_data()
    #

    def change_node_attributes(self, node_path, attributes):
        """
Change the attributes of a specified node. Note: XMLNS updates must be
handled by the calling code.

:param node_path: Path to the new node - delimiter is space
:param attributes: Attributes of the node

:return: (bool) False on error
:since:  v0.1.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        if (str is not _PY_UNICODE_TYPE and type(node_path) is _PY_UNICODE_TYPE): node_path = _PY_STR(node_path, "utf-8")

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.change_node_attributes({0})- (#echo(__LINE__)#)".format(node_path))
        _return = False

        if (type(node_path) is str and isinstance(attributes, dict)):
            node_path = self._translate_ns_path(node_path)
            node_ptr = self._get_node_ptr(node_path)

            if (isinstance(node_ptr, dict)):
                if ("xml.item" in node_ptr): node_ptr['xml.item']['attributes'] = attributes
                else: node_ptr['attributes'] = attributes

                _return = True
            #
        #

        return _return
    #

    def change_node_value(self, node_path, value):
        """
Change the value of a specified node.

:param node_path: Path to the new node; delimiter is space
:param value: Value for the new node

:return: (bool) False on error
:since:  v0.1.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        if (str is not _PY_UNICODE_TYPE and type(node_path) is _PY_UNICODE_TYPE): node_path = _PY_STR(node_path, "utf-8")

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.change_node_value({0})- (#echo(__LINE__)#)".format(node_path))
        _return = False

        if (type(node_path) is str and (not isinstance(value, dict)) and (not isinstance(value, list))):
            node_path = self._translate_ns_path(node_path)
            node_ptr = self._get_node_ptr(node_path)

            if (isinstance(node_ptr, dict)):
                if ("xml.item" in node_ptr): node_ptr['xml.item']['value'] = value
                else: node_ptr['value'] = value

                _return = True
            #
        #

        return _return
    #

    def count_node(self, node_path):
        """
Count the occurrence of a specified node.

:param node_path: Path to the node; delimiter is space

:return: (int) Counted number off matching nodes
:since:  v0.1.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        if (str is not _PY_UNICODE_TYPE and type(node_path) is _PY_UNICODE_TYPE): node_path = _PY_STR(node_path, "utf-8")

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.count_node({0})- (#echo(__LINE__)#)".format(node_path))
        _return = 0

        if (type(node_path) is str):
            """
Get the parent node of the target.
            """

            node_path = self._translate_ns_path(node_path)
            node_path_list = node_path.split(" ")

            if (len(node_path_list) > 1):
                node_name = node_path_list.pop()
                node_path = " ".join(node_path_list)
                node_ptr = self._get_node_ptr(node_path)
            else:
                node_name = node_path
                node_ptr = self._data
            #

            if (isinstance(node_ptr, dict)):
                node_name = self.translate_ns_name(node_ptr, node_name)

                if (node_name in node_ptr):
                    _return = ((len(node_ptr[node_name]) - 1) if ("xml.mtree" in node_ptr[node_name]) else 1)
                #
            #
        #

        return _return
    #

    def export_data(self, flush = False, strict_standard_mode = True):
        """
Convert the Python representation data into a XML string.

:param flush: True to delete the cache content
:param strict_standard_mode: True to be standard compliant

:return: (str) Result string
:since:  v1.0.0
        """

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.export_data()- (#echo(__LINE__)#)")

        if (self._data is None or len(self._data) < 1): _return = ""
        else:
            _return = self.dict_to_xml(self._data, strict_standard_mode)
            if (flush): self._data = { }
        #

        return _return
    #

    def get_node(self, node_path, remove_metadata = True):
        """
Read a specified node including all children if applicable.

:param node_path: Path to the node; delimiter is space
:param remove_metadata: False to not remove the xml.item node

:return: (dict) XML node element; None on error
:since:  v0.1.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        if (str is not _PY_UNICODE_TYPE and type(node_path) is _PY_UNICODE_TYPE): node_path = _PY_STR(node_path, "utf-8")

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.get_node({0})- (#echo(__LINE__)#)".format(node_path))
        _return = None

        if (type(node_path) is str):
            node_path = self._translate_ns_path(node_path)
            node_ptr = self._get_node_ptr(node_path)

            if (isinstance(node_ptr, dict)):
                _return = node_ptr.copy()
                if (remove_metadata and "xml.item" in _return): del(_return['xml.item'])
            #
        #

        return _return
    #

    def get_node_attributes(self, node_path):
        """
Returns the attributes of a specified node.

:param node_path: Path to the node; delimiter is space

:return: (str) Attributes for the node; None if undefined
:since:  v0.1.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        if (str is not _PY_UNICODE_TYPE and type(node_path) is _PY_UNICODE_TYPE): node_path = _PY_STR(node_path, "utf-8")

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.get_node_attributes({0})- (#echo(__LINE__)#)".format(node_path))
        _return = None

        if (type(node_path) is str):
            node_path = self._translate_ns_path(node_path)
            node_ptr = self._get_node_ptr(node_path)

            if (isinstance(node_ptr, dict)): _return = (node_ptr['xml.item']['attributes'] if ("xml.item" in node_ptr) else node_ptr['attributes'])
        #

        return _return
    #

    def _get_node_ptr(self, node_path):
        """
Returns the pointer to a specific node.

:param node_path: Path to the node - delimiter is space

:return: (dict) XML node element; False on error
:since:  v0.1.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        if (str is not _PY_UNICODE_TYPE and type(node_path) is _PY_UNICODE_TYPE): node_path = _PY_STR(node_path, "utf-8")

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml._get_node_ptr({0})- (#echo(__LINE__)#)".format(node_path))
        _return = None

        if (type(node_path) is str):
            if (self.data_cache_node != "" and node_path[:len(self.data_cache_node)] == self.data_cache_node):
                node_path = node_path[len(self.data_cache_node):].strip()
                node_ptr = self.data_cache_ptr
            else: node_ptr = self._data

            is_valid = True
            node_path_list = (node_path.split(" ") if (len(node_path) > 0) else [ ])

            while (is_valid and len(node_path_list) > 0):
                is_valid = False
                node_name = node_path_list.pop(0)
                re_result = XmlResource.RE_NODE_POSITION.match(node_name)

                if (re_result is None): node_position = -1
                else:
                    node_name = re_result.group(1)
                    node_position = int(re_result.group(2))
                #

                node_name = self.translate_ns_name(node_ptr, node_name)

                if (node_name in node_ptr):
                    if ("xml.mtree" in node_ptr[node_name]):
                        if (node_position >= 0):
                            if (node_position in node_ptr[node_name]):
                                is_valid = True
                                node_ptr = node_ptr[node_name][node_position]
                            #
                        elif (node_ptr[node_name]['xml.mtree'] in node_ptr[node_name]):
                            is_valid = True
                            node_ptr = node_ptr[node_name][node_ptr[node_name]['xml.mtree']]
                        #
                    else:
                        is_valid = True
                        node_ptr = node_ptr[node_name]
                    #
                #
            #

            if (is_valid): _return = node_ptr
        #

        return _return
    #

    def get_node_value(self, node_path):
        """
Returns the value of a specified node.

:param node_path: Path to the node; delimiter is space

:return: (str) Value for the node; None if undefined
:since:  v0.1.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        if (str is not _PY_UNICODE_TYPE and type(node_path) is _PY_UNICODE_TYPE): node_path = _PY_STR(node_path, "utf-8")

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.get_node_value({0})- (#echo(__LINE__)#)".format(node_path))
        _return = None

        if (type(node_path) is str):
            node_path = self._translate_ns_path(node_path)
            node_ptr = self._get_node_ptr(node_path)

            if (isinstance(node_ptr, dict)): _return = (node_ptr['xml.item']['value'] if ("xml.item" in node_ptr) else node_ptr['value'])
        #

        return _return
    #

    def get_ns_uri(self, data):
        """
Returns the registered namespace (URI) for a given XML NS or node name
containing the registered XML NS.

:param data: XML NS or node name

:return: (str) Namespace (URI)
:since:  v0.1.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        if (str is not _PY_UNICODE_TYPE and type(data) is _PY_UNICODE_TYPE): data = _PY_STR(data, "utf-8")

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.get_ns_uri({0})- (#echo(__LINE__)#)".format(data))
        _return = ""

        re_result = XmlResource.RE_NODE_NAME_XMLNS.match(data)

        if (re_result is not None):
            if (re_result.group(1) in self.data_ns): _return = self.data_ns[re_result.group(1)]
        elif (data in self.data_ns): _return = self.data_ns[data]

        return _return
    #

    def import_dict(self, data_dict, overwrite = False):
        """
Read and convert a simple multi-dimensional dict into our XML tree.

:param data_dict: Input dict
:param overwrite: True to overwrite the current (non-empty) cache

:return: (bool) True on success
:since:  v0.1.0
        """

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.import_dict()- (#echo(__LINE__)#)")
        _return = False

        if (self._data is None or len(self._data) < 1 or overwrite):
            self._data = self.import_dict_walker(data_dict)
            _return = True
        #

        return _return
    #

    def import_dict_walker(self, data_dict):
        """
Read and convert a single dimension of an dictionary for our XML tree.

:param data_dict: Input dict

:return: (dict) Result XML tree dict
:since:  v0.1.0
        """

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.import_dict_walker()- (#echo(__LINE__)#)")
        _return = { }

        if (isinstance(data_dict, dict)):
            for key in data_dict:
                key_type = type(key)
                value = data_dict[key]

                if (key_type in ( int, float ) or len(key) > 0):
                    if (isinstance(value, dict)):
                        node_dict = self.node_type([ ( "xml.item", { "tag": key, "xmlns": { } } ) ])
                        node_dict.update(self.import_dict_walker(value))
                        _return[key] = node_dict
                    elif (isinstance(value, list)): _return[key] = self.node_type(tag = key, value = value, xmlns = { })
                #
            #
        #

        return _return
    #

    def remove_node(self, node_path):
        """
Remove a node and all children if applicable.

:param node_path: Path to the node - delimiter is space

:return: (bool) False on error
:since:  v0.1.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        if (str is not _PY_UNICODE_TYPE and type(node_path) is _PY_UNICODE_TYPE): node_path = _PY_STR(node_path, "utf-8")

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.remove_node({0})- (#echo(__LINE__)#)".format(node_path))
        _return = False

        if (type(node_path) is str):
            """
Get the parent node of the target.
            """

            node_path = self._translate_ns_path(node_path)
            node_path_list = node_path.split(" ")

            if (len(node_path_list) > 1):
                node_name = node_path_list.pop()
                node_path = " ".join(node_path_list)
                node_ptr = self._get_node_ptr(node_path)

                if (self.data_cache_node != "" and node_path[:len(self.data_cache_node)] == self.data_cache_node):
                    self.data_cache_node = ""
                    self.data_cache_ptr = self._data
                #
            else:
                node_name = node_path
                node_ptr = self._data

                self.data_cache_node = ""
                self.data_cache_ptr = self._data
            #

            if (isinstance(node_ptr, dict)):
                re_result = XmlResource.RE_NODE_POSITION.match(node_name)

                if (re_result is None): node_position = -1
                else:
                    node_name = re_result.group(1)
                    node_position = int(re_result.group(2))
                #

                node_name = self.translate_ns_name(node_ptr, node_name)

                if (node_name in node_ptr):
                    if ("xml.mtree" in node_ptr[node_name]):
                        if (node_position >= 0):
                            if (node_position in node_ptr[node_name]):
                                del(node_ptr[node_name][node_position])
                                _return = True
                            #
                        elif (node_ptr[node_name]['xml.mtree'] in node_ptr[node_name]):
                            del(node_ptr[node_name][node_ptr[node_name]['xml.mtree']])
                            _return = True
                        #

                        """
Update the mtree counter or remove it if applicable.
                        """

                        if (_return):
                            node_ptr[node_name]['xml.mtree'] -= 1

                            if (node_ptr[node_name]['xml.mtree'] > 0):
                                node_dict = self.node_type([ ( "xml.mtree", node_ptr[node_name]['xml.mtree'] ) ])
                                del(node_ptr[node_name]['xml.mtree'])

                                node_position = 0

                                for key in node_ptr[node_name]:
                                    value = node_ptr[node_name][key]
                                    node_dict[node_position] = value
                                    node_position += 1
                                #

                                node_ptr[node_name] = node_dict
                            else: node_ptr[node_name] = node_ptr[node_name][0]
                        #
                    else:
                        del(node_ptr[node_name])
                        self.remove_node_ns_cache(node_path)
                        _return = True
                    #
                #
            #
        #

        return _return
    #

    def remove_node_ns_cache(self, node_path):
        """
Removes cached XML namespace data of the given XML node.

:param node_path: XML node path

:since: v0.1.0
        """

        if (node_path in self.data_ns_predefined_compact):
            del(self.data_ns_predefined_default[self.data_ns_predefined_compact[node_path]])
            del(self.data_ns_predefined_compact[node_path])
        #
    #

    def set_cached_node(self, node_path):
        """
Set the cache pointer to a specific node.

:param node_path: Path to the node - delimiter is space

:return: (bool) True on success
:since:  v0.1.0
        """

        # global: _PY_STR, _PY_UNICODE_TYPE

        if (str is not _PY_UNICODE_TYPE and type(node_path) is _PY_UNICODE_TYPE): node_path = _PY_STR(node_path, "utf-8")

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -xml.set_cached_node({0})- (#echo(__LINE__)#)".format(node_path))
        _return = False

        if (type(node_path) is str):
            node_path = self._translate_ns_path(node_path)

            if (node_path == self.data_cache_node): _return = True
            else:
                node_ptr = self._get_node_ptr(node_path)

                if (isinstance(node_ptr, dict)):
                    self.data_cache_node = node_path
                    self.data_cache_ptr = node_ptr
                    _return = True
                #
            #
        #

        return _return
    #

    def translate_ns_name(self, node, name):
        """
Translates the node name if it is the predefined default namespace for the
node.

:param node: XML tree node
:param name: Requested node name

:return: (str) Translated node name
:since:  v0.1.0
        """

        _return = name

        re_result = XmlResource.RE_NODE_NAME_XMLNS.match(name)

        if (re_result is not None and re_result.group(1) in self.data_ns and re_result.group(2) in node):
            translated_name = re_result.group(2)

            if ("xml.mtree" in node[translated_name]):
                if ("xml.item" in node[translated_name][0]
                    and "@" in node[translated_name][0]['xml.item']['xmlns']
                    and node[translated_name][0]['xml.item']['xmlns']['@'] in self.data_ns_compact
                    and self.data_ns_compact[node[translated_name][0]['xml.item']['xmlns']['@']] == self.data_ns[re_result.group(1)]
                   ): _return = translated_name
                elif ("xmlns" in node[translated_name][0]
                      and "@" in node[translated_name][0]['xmlns']
                      and node[translated_name][0]['xmlns']['@'] in self.data_ns_compact
                      and self.data_ns_compact[node[translated_name][0]['xmlns']['@']] == self.data_ns[re_result.group(1)]
                     ): _return = translated_name
            elif ("xml.item" in node[translated_name]
                  and "@" in node[translated_name]['xml.item']['xmlns']
                  and node[translated_name]['xml.item']['xmlns']['@'] in self.data_ns_compact
                  and self.data_ns_compact[node[translated_name]['xml.item']['xmlns']['@']] == self.data_ns[re_result.group(1)]
                 ): _return = translated_name
            elif ("xmlns" in node[translated_name]
                  and "@" in node[translated_name]['xmlns']
                  and node[translated_name]['xmlns']['@'] in self.data_ns_compact
                  and self.data_ns_compact[node[translated_name]['xmlns']['@']] == self.data_ns[re_result.group(1)]
                 ): _return = translated_name
        #

        return _return
    #
#
