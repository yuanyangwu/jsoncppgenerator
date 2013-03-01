#!/usr/bin/python

#  The MIT License (MIT)
#
#  Copyright (c) 2012 Yuanyang Wu
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#  OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.

import string
import os.path
import types
import xml.dom.minidom

from jsoncpphandler import CppHeaderHandler, CppBodyBuilder, CppTest, CppFormat
from jsondetailcpp import JSONDetailCppClass

def debug_xml_node(node, indent):
	print "  " * indent + node.localName + " " + \
		", ".join([str(item[0]) + "=" + str(item[1]) for item in node.attributes.items()])
	for n in node.childNodes:
		if n.nodeType == n.ELEMENT_NODE:
			debug_xml_node(n, indent + 1)

class XmlUtil:
	def get_node_attribute_value(xml_node, attr_name, default_value = None):
		if xml_node.attributes.has_key(attr_name):
			return str(xml_node.attributes.getNamedItem(attr_name).value)
		else:
			return default_value

	def get_node_attribute_dic(xml_node):
		ret = {}
		for item in xml_node.attributes.items():
			ret[str(item[0])] = str(item[1])
		return ret

	def get_child_element_node(xml_node, element_name):
		for n in xml_node.childNodes:
			if n.nodeType == n.ELEMENT_NODE:
				if str(n.localName) == element_name:
					return n
		return None

	get_node_attribute_value = staticmethod(get_node_attribute_value)
	get_node_attribute_dic = staticmethod(get_node_attribute_dic)
	get_child_element_node = staticmethod(get_child_element_node)

class JSONXSDConstant:
	basic_arrays = {
		"string": "detail::StringArray",
		"int": "detail::IntArray",
		"long": "detail::Int64Array",
		"boolean": "detail::BooleanArray",
		"double": "detail::DoubleArray"
		}

	def is_basic_type(typename):
		return JSONXSDConstant.basic_arrays.has_key(typename)

	def get_cpp_class_name(typename, is_multiple):
		arrayclass = JSONXSDConstant.basic_arrays.get(typename)
		if arrayclass == None:
			classname = typename
			if is_multiple:
				classname = classname + "Array"
			return CppFormat.classname(classname)
		else:
			if is_multiple:
				# array basic type
				return arrayclass
			else:
				# single basic type
				return typename

		return None

	is_basic_type = staticmethod(is_basic_type)
	get_cpp_class_name = staticmethod(get_cpp_class_name)

class JSONXSDFile:
	def __init__(self, filepath):
		self.filepath = filepath
		self.elements = {}
		self.simpletypes = {}
		self.complextypes = {}
		self.parse_file()

	def get_element_definition(self, element_name):
		assert self.elements.has_key(element_name), ("element must be defined")
		element = self.elements[element_name]
		if self.is_basic_type(element["type_name"]):
			return element
		else:
			assert False, ("TODO simpleType complexType")

	def is_basic_type(self, typename):
		return self.get_basic_type(typename) != None

	def get_basic_type(self, typename):
		if JSONXSDConstant.basic_arrays.has_key(typename):
			return typename

		def_node = self.simpletypes.get(typename)
		if def_node != None:
			self.parse_simpletype_full(def_node)
			return self.get_basic_type(def_node["base_type_name"])

		return None

	def is_single_basic_type(self, element_name):
		assert self.elements.has_key(element_name), ("element must be defined")
		element = self.elements[element_name]
		return (not element["is_multiple"]) and self.is_basic_type(element["type_name"])

	def is_array_basic_type(self, element_name):
		assert self.elements.has_key(element_name), ("element must be defined")
		element = self.elements[element_name]
		return element["is_multiple"] and self.is_basic_type(element["type_name"])

	def get_element_class_and_deps(self, element_name):
		element = self.elements[element_name]
		return self.get_type_deps_simple(element["type_name"], element["is_multiple"])

	def get_type_deps_simple(self, typename, is_multiple):
		basic_typename = self.get_basic_type(typename)
		if basic_typename != None:
			if is_multiple:
				# basic array
				return (basic_typename, True), set([(basic_typename, True)])
			else:
				# basic single
				return (basic_typename, False), set()
		else:
			# complexType
			if is_multiple:
				return (typename, True), set([(typename, False), (typename, True)])
			else:
				return (typename, False), set([(typename, False)])

	def get_type_deps(self, typename):
		deps = set()

		if self.simpletypes.has_key(typename):
			return deps

		def_node = self.complextypes[typename]
		self.parse_complextype_full(def_node)
		if def_node.has_key("sequence_elements"):
			for n in def_node["sequence_elements"]:
				if n.has_key("ref_name"):
					cur_class, cur_deps = self.get_element_class_and_deps(n["ref_name"])
				else:
					cur_class, cur_deps = self.get_type_deps_simple(n["type_name"], n["is_multiple"])
				deps = deps.union(cur_deps)

		return deps

	def parse_file(self):
		dom = xml.dom.minidom.parse(self.filepath)
		self.parse_schema_node(dom.childNodes[0])

	def parse_schema_node(self, xml_node):
		for n in xml_node.childNodes:
			if n.nodeType == n.ELEMENT_NODE:
				if str(n.localName) == "element":
					def_node = self.parse_element_node(n, True)
					self.elements[def_node["name"]] = def_node
				if str(n.localName) == "simpleType":
					def_node = self.parse_simpletype_node(n)
					self.simpletypes[def_node["name"]] = def_node
				if str(n.localName) == "complexType":
					def_node = self.parse_complextype_node(n)
					self.complextypes[def_node["name"]] = def_node

	def parse_element_node(self, xml_node, require_name_attr):
		def_node = {}
		def_node["xml_node"] = xml_node

		attrs = XmlUtil.get_node_attribute_dic(xml_node)

		if attrs.has_key("ref"):
			def_node["ref_name"] = attrs["ref"]
			assert not require_name_attr, ("top level <element> most NOT have attribute \"ref\"")
		else:
			if attrs.has_key("name"):
				def_node["name"] = attrs["name"]
			elif require_name_attr:
				assert False, ("""<element> must has attribute "name".""")

			assert attrs.has_key("type"), ("<element> \"" + def_node.get("name", "(None)") + "\" must has attribute \"type\"")
			def_node["type_name"] = attrs["type"].split(":")[-1]

		min_occurs = attrs.get("minOccurs", "1")
		max_occurs = attrs.get("maxOccurs", "1")
		def_node["is_multiple"] = (max_occurs != "1") or ((min_occurs != "0") and (min_occurs != "1"))
		return def_node

	def parse_simpletype_node(self, xml_node):
		def_node = {}
		def_node["xml_node"] = xml_node

		def_node["name"] = XmlUtil.get_node_attribute_value(xml_node, "name")
		assert ["name"] != None, ("""<simpleType> must has attribute "name".""")
		return def_node

	def parse_simpletype_full(self, def_node):
		xml_node = def_node["xml_node"]

		restriction_node = XmlUtil.get_child_element_node(xml_node, "restriction")
		assert restriction_node != None, ("simpleType \"" + def_node.get("name", "(None)") + "\" must has \"restriction\" child node")

		base_type_name = XmlUtil.get_node_attribute_value(restriction_node, "base")
		assert base_type_name != None, ("simpleType \"" + def_node.get("name", "(None)") + "\" must has attribute \"base\" in \"restriction\" node")
		def_node["base_type_name"] = base_type_name.split(":")[-1]

	def parse_complextype_node(self, xml_node):
		def_node = {}
		def_node["xml_node"] = xml_node

		def_node["name"] = XmlUtil.get_node_attribute_value(xml_node, "name")
		assert ["name"] != None, ("""<simpleType> must has attribute "name".""")
		return def_node

	def parse_complextype_full(self, def_node):
		xml_node = def_node["xml_node"]

		node = XmlUtil.get_child_element_node(xml_node, "sequence")
		if node != None:
			sequence_elements = []
			for n in node.childNodes:
				if n.nodeType == n.ELEMENT_NODE:
					sequence_elements.append(self.parse_element_node(n, False))
			def_node["sequence_elements"] = sequence_elements

class JSONXSDWalker:
	def __init__(self, json_xsd_file):
		self.schema = json_xsd_file
		self.basic_types = ["string", "int", "long", "boolean", "double"]
		self.json_handlers = []

	def walk(self, typename, is_multiple):
		assert not JSONXSDConstant.is_basic_type(typename), ("only complexType should be passed")

		if is_multiple:
			self.walk_array_complex_type(typename)
		else:
			# single complex type
			def_node = self.schema.complextypes[typename]
			if def_node.has_key("sequence_elements"):
				self.walk_single_complex_sequence(typename)

	def walk_single_complex_sequence(self, complex_type_name):
		parent_names = []
		name = JSONXSDConstant.get_cpp_class_name(complex_type_name, False)
		for handler in self.json_handlers:
			handler.handle_object_start(parent_names, name)

		def_node = self.schema.complextypes[complex_type_name]
		for n in def_node["sequence_elements"]:
			if n.has_key("ref_name"):
				cur_class, cur_deps = self.schema.get_element_class_and_deps(n["ref_name"])
				ref_def_node = self.schema.get_element_definition(n["ref_name"])
				cur_name = ref_def_node["name"]
			else:
				cur_class, cur_deps = self.schema.get_type_deps_simple(n["type_name"], n["is_multiple"])
				cur_name = n["name"]
			typename, is_multiple = cur_class

			child_parent_names = parent_names[:]
			child_parent_names.append(name)
			child_name = cur_name
			child_type_name = JSONXSDConstant.get_cpp_class_name(typename, is_multiple)
			for handler in self.json_handlers:
				if is_multiple:
					# array
					handler.handle_array_start(child_parent_names, child_name, child_type_name)
					handler.handle_array_end(child_parent_names, child_name, child_type_name)
				else:
					if JSONXSDConstant.is_basic_type(typename):
						# single basic type
						if child_type_name == "boolean":
							handler.handle_boolean(child_parent_names, child_name)
						elif child_type_name == "double":
							handler.handle_float(child_parent_names, child_name)
						elif child_type_name == "int":
							handler.handle_int(child_parent_names, child_name)
						elif child_type_name == "long":
							handler.handle_int64(child_parent_names, child_name)
						elif child_type_name == "string":
							handler.handle_string(child_parent_names, child_name)
						else:
							assert False, ("Unsupported type: " + child_type_name)
					else:
						# encode/decode array and object in same way
						handler.handle_object_start(child_parent_names, child_name, typename)
						handler.handle_object_end(child_parent_names, child_name, typename)

		for handler in self.json_handlers:
			handler.handle_object_end(parent_names, name)

	def walk_array_complex_type(self, complex_type_name):
		parent_names = []
		name = JSONXSDConstant.get_cpp_class_name(complex_type_name, True)
		for handler in self.json_handlers:
			handler.handle_array_start(parent_names, name, complex_type_name)

		child_parent_names = parent_names[:]
		child_parent_names.append(name)
		# array element has no name
		# use "None" to indicate parent is array
		child_name = None
		for handler in self.json_handlers:
			handler.handle_object_start(child_parent_names, child_name, complex_type_name)
			handler.handle_object_end(child_parent_names, child_name, complex_type_name)

		for handler in self.json_handlers:
			handler.handle_array_end(parent_names, name, complex_type_name)

def parse_options():
	import optparse

	usage_msg = """usage: %prog [options] XSDFile"""
	parser = optparse.OptionParser(usage=usage_msg)
	parser.add_option("--element", dest="element_name", default="",
		help="required. Generate code against specified <element> name in XSD file")
	parser.add_option("--dstdir", dest="dstdir", default=".",
		help="directory to save the generated code files, default is current directory")
	parser.add_option("--namespace", dest="namespace", default="",
		help="""C++ namespace seperated with "::", for example, "com::company". Default is no namespace""")
	parser.add_option("--stringtype", dest="stringtype", default="std::string",
		help="""C++ string type, std::string or std::wstring, default is std::string""")
	parser.add_option("--gentest", action="store_true", dest="gentest", default=False,
		help="""generate test code "main.cpp", default is false""")
	options, reminder = parser.parse_args()

	valid = True
	if len(reminder) != 1:
		valid = False

	if valid and options.element_name == "":
		valid = False

	if valid and (len(options.namespace) > 0):
		l = options.namespace.split("::")
		if l.count("") > 0:
			valid = False

		if len([x for x in l if x.count(":") > 0]) > 0:
			valid = False

	if valid and (options.stringtype not in ["std::string", "std::wstring"]):
		valid = False

	if not valid:
		parser.print_help()
		exit(1)

	options.jsonxsdfile = reminder[0]

	return options

if __name__ == "__main__":
	options = parse_options()

	dom = xml.dom.minidom.parse(options.jsonxsdfile)
	#debug_xml_node(dom.childNodes[0], 0)

	schema = JSONXSDFile(options.jsonxsdfile)
	#import pprint
	#pprint.pprint(schema.elements)
	#pprint.pprint(schema.simpletypes)
	#pprint.pprint(schema.complextypes)
	#jsondef = schema.get_element_definition(options.element_name)
	#pprint.pprint(jsondef)
	#exit(0)

	cur_class, cur_deps = schema.get_element_class_and_deps(options.element_name)
	#print "cur_class: ", cur_class
	#print "cur_deps", cur_deps

	typename, is_multiple = cur_class
	new_deps = cur_deps
	dep_types = set()
	array_types = set()
	while len(new_deps) > 0:
		typename, is_multiple = new_deps.pop()
		if typename in JSONXSDConstant.basic_arrays:
			if is_multiple:
				array_types.add( (typename, is_multiple) )
		elif (typename, is_multiple) in dep_types:
			pass # ignore already parsed type
		else:
			cur_deps = schema.get_type_deps(typename)
			new_deps = new_deps.union(cur_deps)
			dep_types.add( (typename, is_multiple) )

	#print "dep_types: ", dep_types
	#print "array_types: ", array_types

	typename, is_multiple = cur_class
	if JSONXSDConstant.is_basic_type(typename) and not is_multiple:
		#single basic/simple type
		exit(0)

	classname = JSONXSDConstant.get_cpp_class_name(typename, is_multiple)
	if options.gentest:
		cpptest = CppTest(classname, options.namespace, options.stringtype)
		cpptest.savefile(os.path.join(options.dstdir, cpptest.filename))

	for typename, is_multiple in array_types:
		classname = JSONXSDConstant.get_cpp_class_name(typename, is_multiple)
		detailCpp = JSONDetailCppClass()
		detailCpp.save_to_dir(classname, options.dstdir, options.namespace, options.stringtype)

	for typename, is_multiple in dep_types:
		walker = JSONXSDWalker(schema)

		cppheader = CppHeaderHandler(options.namespace, options.stringtype)
		walker.json_handlers.append(cppheader)
		cppbodybuilder = CppBodyBuilder(options.namespace, options.stringtype)
		walker.json_handlers.extend(cppbodybuilder.handlers)

		# print "walking " + typename + ", " + str(is_multiple)
		walker.walk(typename, is_multiple)
		cppheader.save_to_dir(options.dstdir)
		cppbodybuilder.save_to_dir(options.dstdir)

