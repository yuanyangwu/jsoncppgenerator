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
import json
import types

class JSONBaseHandler:

	print_trace = False

	def is_parent_array(self, name):
		return name == None

	def handle_object_start(self, parent_names, name):
		if JSONBaseHandler.print_trace:
			print "--" * len(parent_names) + "handle_object_start " + str(name)

	def handle_object_end(self, parent_names, name):
		if JSONBaseHandler.print_trace:
			print "--" * len(parent_names) + "handle_object_end " + str(name)
	def handle_array_start(self, parent_names, name):
		if JSONBaseHandler.print_trace:
			print "--" * len(parent_names) + "handle_array_start " + str(name)

	def handle_array_end(self, parent_names, name):
		if JSONBaseHandler.print_trace:
			print "--" * len(parent_names) + "handle_array_end " + str(name)

	def handle_boolean(self, parent_names, name):
		if JSONBaseHandler.print_trace:
			print "--" * len(parent_names) + "handle_boolean " + str(name)

	def handle_float(self, parent_names, name):
		if JSONBaseHandler.print_trace:
			print "--" * len(parent_names) + "handle_float " + str(name)

	def handle_int(self, parent_names, name):
		if JSONBaseHandler.print_trace:
			print "--" * len(parent_names) + "handle_int " + str(name)

	def handle_string(self, parent_names, name):
		if JSONBaseHandler.print_trace:
			print "--" * len(parent_names) + "handle_string " + str(name)

class JSONWalker:
	def __init__(self, rawjson, rootname):
		self.rawjson = rawjson
		self.rootname = rootname
		self.complex_type_walkers = {
			types.DictType: self.walk_object,
			types.ListType: self.walk_array
			}
		self.all_type_walkers = {
			types.DictType: self.walk_object,
			types.ListType: self.walk_array,
			types.BooleanType: self.walk_boolean,
			types.FloatType: self.walk_float,
			types.IntType: self.walk_int,
			types.LongType: self.walk_int,
			types.UnicodeType: self.walk_string
			}
		self.json_handlers = []

	def walk(self):
		value = self.rawjson
		walker = self.complex_type_walkers.get(type(value))
		assert walker != None, ("json root node is neither object nor array")

		name = str(self.rootname)
		walker([], name, value)

	def walk_object(self, parent_names, name, rawjson):
		assert type(rawjson) == types.DictType
		assert not self.is_null_type(rawjson)

		for handler in self.json_handlers:
			handler.handle_object_start(parent_names, name)

		child_parent_names = parent_names[:]
		child_parent_names.append(name)
		for child_name in sorted(rawjson.keys()):
			value = rawjson.get(child_name)
			walker = self.all_type_walkers.get(type(value))
			assert walker != None, ("Unsupported type: " + str(type(value)) + " value:" + str(value))
			walker(child_parent_names, str(child_name), value)

		for handler in self.json_handlers:
			handler.handle_object_end(parent_names, name)


	def walk_array(self, parent_names, name, rawjson):
		assert type(rawjson) == types.ListType
		assert not self.is_null_type(rawjson)
		for handler in self.json_handlers:
			handler.handle_array_start(parent_names, name)

		child_parent_names = parent_names[:]
		child_parent_names.append(name)
		# array element has no name
		# use "None" to indicate parent is array
		child_name = None #str(name) + "_element"
		value = rawjson[0]
		walker = self.all_type_walkers.get(type(value))
		assert walker != None, ("Unsupported type: " + str(type(value)) + " value:" + str(value))
		walker(child_parent_names, child_name, value)

		for handler in self.json_handlers:
			handler.handle_array_end(parent_names, name)

	def walk_boolean(self, parent_names, name, rawjson):
		assert type(rawjson) == types.BooleanType
		assert not self.is_null_type(rawjson)
		for handler in self.json_handlers:
			handler.handle_boolean(parent_names, name)

	def walk_float(self, parent_names, name, rawjson):
		assert type(rawjson) == types.FloatType
		assert not self.is_null_type(rawjson)
		for handler in self.json_handlers:
			handler.handle_float(parent_names, name)

	def walk_int(self, parent_names, name, rawjson):
		assert type(rawjson) in [types.IntType, types.LongType]
		assert not self.is_null_type(rawjson)
		for handler in self.json_handlers:
			handler.handle_int(parent_names, name)

	def walk_string(self, parent_names, name, rawjson):
		assert type(rawjson) == types.UnicodeType
		assert not self.is_null_type(rawjson)
		for handler in self.json_handlers:
			handler.handle_string(parent_names, name)

	def is_null_type(self, rawjson):
		if type(rawjson) in [types.DictType, types.ListType]:
			return len(rawjson) == 0
		return rawjson == None

class JSONFile:
	def __init__(self, filepath):
		self.filepath = filepath
		self.rawjson = self.decode_json()
		self.classname = self.generate_classname()
		self.jsonwalker = self.generate_jsonwalker()

	def decode_json(self):
		f = open(self.filepath)
		return json.load(f)

	def generate_classname(self):
		return os.path.basename(self.filepath).split(".")[0]

	def generate_jsonwalker(self):
		return JSONWalker(self.rawjson, self.classname)


###############################################################################
# Convert JSON to C++
#

class CppFormat:
	def headerfilename(name):
		return CppFormat.classname(name) + ".h"

	def bodyfilename(name):
		return CppFormat.classname(name) + ".cpp"

	def arrayelement_classname(parent_names):
		if len(parent_names) == 0:
			return ""
		if parent_names[-1] != None:
			return ""

		return "ArrayElement" + CppFormat.arrayelement_classname(parent_names[0:len(parent_names)-1])

	def classname(name, parent_names = []):
		if name == None:
			# array's element
			names = parent_names[:]
			names.append(name)
			return CppFormat.arrayelement_classname(names)

		return "".join([string.upper(x[0]) + x[1:] for x in name.split("_")])

	def fieldname(name):
		n = CppFormat.classname(name)
		return "m_" + string.lower(n[0]) + n[1:]

	def indent(level):
		return "  " * level

	def class_decorator(names):
		return "::".join([CppFormat.classname(names[-i], names[:len(names)-i]) for i in xrange(len(names), 0, -1)])

	def namespace_begin(namespace):
		if namespace == "":
			return ""

		ret = ""
		level = 0
		for n in namespace.split("::"):
			ret += CppFormat.indent(level) + "namespace " + n + "\n"
			ret += CppFormat.indent(level) + "{\n"
			level += 1
		ret += "\n"
		return ret

	def namespace_end(namespace):
		if namespace == "":
			return ""

		ret = "\n"
		level = namespace.count("::")
		for n in reversed(namespace.split("::")):
			ret += CppFormat.indent(level) + "} // namespace " + n + "\n"
			level -= 1
		return ret

	def stringtype_w(stringtype):
		if stringtype == "std::wstring":
			return "w"
		return ""

	def stringtype_L(stringtype):
		if stringtype == "std::wstring":
			return "L"
		return ""

	def method_decodejson_istream_signature(names, stringtype):
		decorator = ""
		if len(names) > 0:
			decorator = CppFormat.class_decorator(names) + "::"
		return "void " + decorator \
			+ "DecodeJSON(std::" + CppFormat.stringtype_w(stringtype) + "istream & is)"

	def method_decodejson_object_signature(names, stringtype):
		decorator = ""
		if len(names) > 0:
			decorator = CppFormat.class_decorator(names) + "::"
		return "void " + decorator \
			+ "DecodeJSON(const json_spirit::" + CppFormat.stringtype_w(stringtype) + "Object & obj)"

	def method_decodejson_array_signature(names, stringtype):
		decorator = ""
		if len(names) > 0:
			decorator = CppFormat.class_decorator(names) + "::"
		return "void " + decorator \
			+ "DecodeJSON(const json_spirit::" + CppFormat.stringtype_w(stringtype) + "Array & array)"

	def method_encodejson_ostream_signature(names, stringtype):
		decorator = ""
		if len(names) > 0:
			decorator = CppFormat.class_decorator(names) + "::"
		return "void " + decorator \
			+ "EncodeJSON(std::" + CppFormat.stringtype_w(stringtype) + "ostream & os, bool isPrettyPrint) const"

	def method_encodejson_object_signature(names, stringtype):
		decorator = ""
		if len(names) > 0:
			decorator = CppFormat.class_decorator(names) + "::"
		return "void " + decorator \
			+ "EncodeJSON(json_spirit::" + CppFormat.stringtype_w(stringtype) + "Object & obj) const"

	def method_encodejson_array_signature(names, stringtype):
		decorator = ""
		if len(names) > 0:
			decorator = CppFormat.class_decorator(names) + "::"
		return "void " + decorator \
			+ "EncodeJSON(json_spirit::" + CppFormat.stringtype_w(stringtype) + "Array & array) const"

	headerfilename = staticmethod(headerfilename)
	bodyfilename = staticmethod(bodyfilename)
	arrayelement_classname = staticmethod(arrayelement_classname)
	classname = staticmethod(classname)
	fieldname = staticmethod(fieldname)
	indent = staticmethod(indent)
	class_decorator = staticmethod(class_decorator)
	namespace_begin = staticmethod(namespace_begin)
	namespace_end = staticmethod(namespace_end)
	stringtype_w = staticmethod(stringtype_w)
	stringtype_L = staticmethod(stringtype_L)
	method_decodejson_istream_signature = staticmethod(method_decodejson_istream_signature)
	method_decodejson_object_signature = staticmethod(method_decodejson_object_signature)
	method_decodejson_array_signature = staticmethod(method_decodejson_array_signature)
	method_encodejson_ostream_signature = staticmethod(method_encodejson_ostream_signature)
	method_encodejson_object_signature = staticmethod(method_encodejson_object_signature)
	method_encodejson_array_signature = staticmethod(method_encodejson_array_signature)

class CppHeaderHandler(JSONBaseHandler):

	file_begin_template = string.Template(
"""
/* 
 * The MIT License (MIT)
 * 
 * Copyright (c) 2012 Yuanyang Wu
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
 * OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 * ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 */


#ifndef _${classname}_H_
#define _${classname}_H_

#include <istream>
#include <ostream>
#include <string>
#include <vector>
#include <boost/optional.hpp>
#include <json_spirit.h>

"""
	)

	file_end = """

#endif
"""

	class_begin_template = string.Template(
"""
${indent}class ${classname}
${indent}{
${indent}public:
${indent}  void DecodeJSON(std::${w}istream & is);
${indent}  ${method_decodejson_signature};
${indent}  void EncodeJSON(std::${w}ostream & os, bool isPrettyPrint = false) const;
${indent}  ${method_encodejson_signature};

"""
	)

	class_end_template = string.Template(
"""${indent}};

"""
	)

	field_of_object_template = string.Template(
"""${indent}boost::optional<${type}> ${name};
"""
	)

	element_type_of_array_template = string.Template(
"""${indent}typedef boost::optional<${type}> ArrayElementType;
"""
	)

	array_type_of_array_template = string.Template(
"""${indent}  typedef std::vector<ArrayElementType> ArrayType;
${indent}  ArrayType m_array;
"""
	)

	def __init__(self, namespace, stringtype):
		self.namespace = namespace
		self.stringtype = stringtype
		self.filename = ""
		self.file_begin = ""
		self.class_decl = ""
		self.file_end = CppHeaderHandler.file_end

	def content(self):
		return self.file_begin \
			+ CppFormat.namespace_begin(self.namespace) \
			+ self.class_decl \
			+ CppFormat.namespace_end(self.namespace) \
			+ self.file_end

	def save_to_dir(self, dirpath):
		f = open(os.path.join(dirpath, self.filename), "w")
		f.write(self.content())
		f.close()

	def handle_object_start(self, parent_names, name):
		classname = CppFormat.classname(name, parent_names)

		if len(parent_names) == 0:
			self.filename = CppFormat.headerfilename(name)
			self.file_begin = CppHeaderHandler.file_begin_template.substitute({
					"classname": classname
				})

		self.class_decl += CppHeaderHandler.class_begin_template.substitute({
				"indent": CppFormat.indent(len(parent_names)),
				"classname" : classname,
				"w": CppFormat.stringtype_w(self.stringtype),
				"method_decodejson_signature": CppFormat.method_decodejson_object_signature([], self.stringtype),
				"method_encodejson_signature": CppFormat.method_encodejson_object_signature([], self.stringtype)
			})

	def handle_object_end(self, parent_names, name):
		self.class_decl += CppHeaderHandler.class_end_template.substitute({
				"indent": CppFormat.indent(len(parent_names))
			})

		if len(parent_names) > 0:
			if self.is_parent_array(name):
				self.class_decl += CppHeaderHandler.element_type_of_array_template.substitute({
						"indent": CppFormat.indent(len(parent_names)),
						"type": CppFormat.classname(name, parent_names)
					})
			else:
				self.class_decl += CppHeaderHandler.field_of_object_template.substitute({
						"indent": CppFormat.indent(len(parent_names)),
						"type": CppFormat.classname(name),
						"name": CppFormat.fieldname(name)
					})

	def handle_array_start(self, parent_names, name):
		if len(parent_names) == 0:
			self.filename = CppFormat.headerfilename(name)
			self.file_begin = CppHeaderHandler.file_begin_template.substitute({
					"classname": string.upper(CppFormat.classname(name))
				})

		self.class_decl += CppHeaderHandler.class_begin_template.substitute({
				"indent": CppFormat.indent(len(parent_names)),
				"classname" : CppFormat.classname(name),
				"w": CppFormat.stringtype_w(self.stringtype),
				"method_decodejson_signature": CppFormat.method_decodejson_array_signature([], self.stringtype),
				"method_encodejson_signature": CppFormat.method_encodejson_array_signature([], self.stringtype)
			})

	def handle_array_end(self, parent_names, name):
		self.class_decl += CppHeaderHandler.array_type_of_array_template.substitute({
				"indent": CppFormat.indent(len(parent_names))
			})
		self.class_decl += CppHeaderHandler.class_end_template.substitute({
				"indent": CppFormat.indent(len(parent_names))
			})

		if len(parent_names) > 0:
			if self.is_parent_array(name):
				self.class_decl += CppHeaderHandler.element_type_of_array_template.substitute({
						"indent": CppFormat.indent(len(parent_names)),
						"type": CppFormat.classname(name, parent_names)
					})
			else:
				self.class_decl += CppHeaderHandler.field_of_object_template.substitute({
						"indent": CppFormat.indent(len(parent_names)),
						"type": CppFormat.classname(name),
						"name": CppFormat.fieldname(name)
					})

	def handle_boolean(self, parent_names, name):
		self.handle_simple_type(parent_names, name, "bool")

	def handle_float(self, parent_names, name):
		self.handle_simple_type(parent_names, name, "double")

	def handle_int(self, parent_names, name):
		self.handle_simple_type(parent_names, name, "int")

	def handle_string(self, parent_names, name):
		self.handle_simple_type(parent_names, name, self.stringtype)

	def handle_simple_type(self, parent_names, name, cpptype):
		if self.is_parent_array(name):
			self.class_decl += CppHeaderHandler.element_type_of_array_template.substitute({
					"indent": CppFormat.indent(len(parent_names)),
					"type": cpptype
				})
		else:
			self.class_decl += CppHeaderHandler.field_of_object_template.substitute({
					"indent": CppFormat.indent(len(parent_names)),
					"type": cpptype,
					"name": CppFormat.fieldname(name)
				})


class CppBodyConstant:

	file_begin_template = string.Template(
"""
/* 
 * The MIT License (MIT)
 * 
 * Copyright (c) 2012 Yuanyang Wu
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
 * OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 * ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 */


#include <boost/foreach.hpp>
#include "${headerfilename}"

"""
	)

	file_end = """
"""

	###############################
	# decodejson
	method_decodejson_istream_for_object_template = string.Template(
"""${method_signature}
{
  json_spirit::${w}Value value;
  json_spirit::read(is, value);
  DecodeJSON(value.get_obj());
}
"""
	)

	method_decodejson_object_begin_template = string.Template(
"""${method_signature}
{
  BOOST_FOREACH(json_spirit::${w}Pair pair, obj)
  {
    if (pair.value_.is_null()) continue;

"""
	)

	method_decodejson_object_do_bool_template = string.Template(
"""    if (pair.name_ == ${L}"${jsonname}")
    {
      ${fieldname} = pair.value_.get_bool();
    }
    else
"""
	)

	method_decodejson_object_do_int_template = string.Template(
"""    if (pair.name_ == ${L}"${jsonname}")
    {
      ${fieldname} = pair.value_.get_int();
    }
    else
"""
	)

	method_decodejson_object_do_float_template = string.Template(
"""    if (pair.name_ == ${L}"${jsonname}")
    {
      ${fieldname} = pair.value_.get_real();
    }
    else
"""
	)

	method_decodejson_object_do_string_template = string.Template(
"""    if (pair.name_ == ${L}"${jsonname}")
    {
      ${fieldname} = pair.value_.get_str();
    }
    else
"""
	)

	method_decodejson_object_do_object_template = string.Template(
"""    if (pair.name_ == ${L}"${jsonname}")
    {
      ${classname} value;
      value.DecodeJSON(pair.value_.get_obj());
      ${fieldname} = value;
    }
    else
"""
	)

	method_decodejson_object_do_array_template = string.Template(
"""    if (pair.name_ == ${L}"${jsonname}")
    {
      ${classname} value;
      value.DecodeJSON(pair.value_.get_array());
      ${fieldname} = value;
    }
    else
"""
	)

	method_decodejson_object_end = """    {
      // do nothing
    }
  }
}
"""

	method_decodejson_istream_for_array_template = string.Template(
"""${method_signature}
{
  json_spirit::${w}Value value;
  json_spirit::read(is, value);
  DecodeJSON(value.get_array());
}
"""
	)

	method_decodejson_array_begin_template = string.Template(
"""${method_signature}
{
  BOOST_FOREACH(const json_spirit::${w}Value & value, array)
  {
    ArrayElementType element;
    if (!value.is_null())
    {
"""
	)

	method_decodejson_array_end = """    }
    m_array.push_back(element);
  }
}
"""

	method_decodejson_array_do_bool = """      element = value.get_bool();
"""

	method_decodejson_array_do_int = """      element = value.get_int();
"""

	method_decodejson_array_do_float = """      element = value.get_real();
"""

	method_decodejson_array_do_string = """      element = value.get_str();
"""

	method_decodejson_array_do_object_template = string.Template(
"""      ${classname} e;
      e.DecodeJSON(value.get_obj());
      element = e;
"""
	)

	method_decodejson_array_do_array_template = string.Template(
"""      ${classname} e;
      e.DecodeJSON(value.get_array());
      element = e;
"""
	)

	###############################
	# encodejson
	method_encodejson_ostream_for_object_template = string.Template(
"""${method_signature}
{
  json_spirit::${w}Object obj;
  EncodeJSON(obj);
  unsigned int options = json_spirit::remove_trailing_zeros;
  if (isPrettyPrint)
  {
    options = json_spirit::pretty_print|json_spirit::remove_trailing_zeros;
  }
  json_spirit::write(obj, os, options);
}
"""
	)

	method_encodejson_object_begin_template = string.Template(
"""${method_signature}
{
"""
	)

	method_encodejson_object_end = """}
"""

	method_encodejson_object_do_simple_type_template = string.Template(
"""  if (${fieldname}) { obj.push_back(json_spirit::${w}Pair(${L}"${jsonname}", *${fieldname})); }
"""
	)

	method_encodejson_object_do_object_template = string.Template(
"""  if (${fieldname})
  {
    json_spirit::${w}Object child;
    (*${fieldname}).EncodeJSON(child);
    obj.push_back(json_spirit::${w}Pair(${L}"${jsonname}", child));
  }
"""
	)

	method_encodejson_object_do_array_template = string.Template(
"""  if (${fieldname})
  {
    json_spirit::${w}Array child;
    (*${fieldname}).EncodeJSON(child);
    obj.push_back(json_spirit::${w}Pair(${L}"${jsonname}", child));
  }
"""
	)

	method_encodejson_ostream_for_array_template = string.Template(
"""${method_signature}
{
  json_spirit::${w}Array array;
  EncodeJSON(array);
  json_spirit::write(array, os,
    json_spirit::pretty_print|json_spirit::remove_trailing_zeros);
}
"""
	)

	method_encodejson_array_begin_template = string.Template(
"""${method_signature}
{
  BOOST_FOREACH(const ArrayElementType & value, m_array)
  {
"""
	)

	method_encodejson_array_end = """  }
}
"""

	method_encodejson_array_do_simple_type_template = string.Template(
"""
    if (value) { array.push_back(json_spirit::${w}Value(*value)); }
    else { array.push_back(json_spirit::${w}Value()); }
"""
	)

	method_encodejson_array_do_object_template = string.Template(
"""    if (value)
    {
      json_spirit::${w}Object child;
      (*value).EncodeJSON(child);
      array.push_back(json_spirit::${w}Value(child));
    }
    else { array.push_back(json_spirit::${w}Value()); }

"""
	)

	method_encodejson_array_do_array_template = string.Template(
"""    if (value)
    {
      json_spirit::${w}Array child;
      (*value).EncodeJSON(child);
      array.push_back(json_spirit::${w}Value(child));
    }
    else { array.push_back(json_spirit::${w}Value()); }

"""
	)

class CppBodyFileHandler(JSONBaseHandler):
	def __init__(self):
		self.filename = ""
		self.file_begin = ""
		self.file_end = CppBodyConstant.file_end

	def handle_object_start(self, parent_names, name):
		if len(parent_names) == 0:
			self.filename = CppFormat.bodyfilename(name)
			self.file_begin = CppBodyConstant.file_begin_template.substitute({
					"headerfilename": CppFormat.headerfilename(name)
				})

	def handle_array_start(self, parent_names, name):
		if len(parent_names) == 0:
			self.filename = CppFormat.bodyfilename(name)
			self.file_begin = CppBodyConstant.file_begin_template.substitute({
					"headerfilename": CppFormat.headerfilename(name)
				})

class CppMethodBaseHandler(JSONBaseHandler):
	def __init__(self, stringtype):
		self.filename = ""
		self.stringtype = stringtype
		self.methods = {}

	def content(self):
		return "\n".join([self.methods.get(method) for method in sorted(self.methods.keys())])

	def handle_object_start(self, parent_names, name):
		if len(parent_names) == 0:
			self.filename = CppFormat.bodyfilename(name)

	def handle_array_start(self, parent_names, name):
		if len(parent_names) == 0:
			self.filename = CppFormat.bodyfilename(name)

class CppMethodDecodeHandler(CppMethodBaseHandler):
	def __init__(self, stringtype):
		CppMethodBaseHandler.__init__(self, stringtype)

	def handle_object_start(self, parent_names, name):
		CppMethodBaseHandler.handle_object_start(self, parent_names, name)

		if len(parent_names) > 0:
			if self.is_parent_array(name):
				parent_method_decodejson_array = CppFormat.method_decodejson_array_signature(parent_names, self.stringtype)
				self.methods[parent_method_decodejson_array] += CppBodyConstant.method_decodejson_array_do_object_template.substitute({"classname": CppFormat.classname(name, parent_names)})
			else:
				parent_method_decodejson_object = CppFormat.method_decodejson_object_signature(parent_names, self.stringtype)
				self.methods[parent_method_decodejson_object] += CppBodyConstant.method_decodejson_object_do_object_template.substitute({
						"jsonname": name,
						"fieldname": CppFormat.fieldname(name),
						"classname": CppFormat.classname(name),
						"L": CppFormat.stringtype_L(self.stringtype)
					})

		names = parent_names[:]
		names.append(name)

		method_decodejson_istream = CppFormat.method_decodejson_istream_signature(names, self.stringtype)
		self.methods[method_decodejson_istream] = CppBodyConstant.method_decodejson_istream_for_object_template.substitute({
				"method_signature": method_decodejson_istream,
				"w": CppFormat.stringtype_w(self.stringtype)
			})

		method_decodejson_object = CppFormat.method_decodejson_object_signature(names, self.stringtype)
		self.methods[method_decodejson_object] = CppBodyConstant.method_decodejson_object_begin_template.substitute({
				"method_signature": method_decodejson_object,
				"w": CppFormat.stringtype_w(self.stringtype)
			})

	def handle_object_end(self, parent_names, name):
		names = parent_names[:]
		names.append(name)
		method_decodejson_object = CppFormat.method_decodejson_object_signature(names, self.stringtype)
		self.methods[method_decodejson_object] += CppBodyConstant.method_decodejson_object_end

	def handle_array_start(self, parent_names, name):
		CppMethodBaseHandler.handle_array_start(self, parent_names, name)

		if len(parent_names) > 0:
			if self.is_parent_array(name):
				parent_method_decodejson_array = CppFormat.method_decodejson_array_signature(parent_names, self.stringtype)
				self.methods[parent_method_decodejson_array] += CppBodyConstant.method_decodejson_array_do_array_template.substitute({"classname": CppFormat.classname(name, parent_names)})
			else:
				parent_method_decodejson_object = CppFormat.method_decodejson_object_signature(parent_names, self.stringtype)
				self.methods[parent_method_decodejson_object] += CppBodyConstant.method_decodejson_object_do_array_template.substitute({
						"jsonname": name,
						"fieldname": CppFormat.fieldname(name),
						"classname": CppFormat.classname(name),
						"L": CppFormat.stringtype_L(self.stringtype)
					})

		names = parent_names[:]
		names.append(name)

		method_decodejson_istream = CppFormat.method_decodejson_istream_signature(names, self.stringtype)
		self.methods[method_decodejson_istream] = CppBodyConstant.method_decodejson_istream_for_array_template.substitute({
				"method_signature": method_decodejson_istream,
				"w": CppFormat.stringtype_w(self.stringtype)
			})

		method_decodejson_array = CppFormat.method_decodejson_array_signature(names, self.stringtype)
		self.methods[method_decodejson_array] = CppBodyConstant.method_decodejson_array_begin_template.substitute({
				"method_signature": method_decodejson_array,
				"w": CppFormat.stringtype_w(self.stringtype)
			})

	def handle_array_end(self, parent_names, name):
		names = parent_names[:]
		names.append(name)
		method_decodejson_array = CppFormat.method_decodejson_array_signature(names, self.stringtype)
		self.methods[method_decodejson_array] += CppBodyConstant.method_decodejson_array_end

	def handle_simple_type_for_decodejson(self, parent_names, name, array_string, object_template):
		if self.is_parent_array(name):
			parent_method_decodejson_array = CppFormat.method_decodejson_array_signature(parent_names, self.stringtype)
			self.methods[parent_method_decodejson_array] += array_string
		else:
			parent_method_decodejson_object = CppFormat.method_decodejson_object_signature(parent_names, self.stringtype)
			self.methods[parent_method_decodejson_object] += object_template.substitute({
					"jsonname": name,
					"fieldname": CppFormat.fieldname(name),
					"L": CppFormat.stringtype_L(self.stringtype)
				})

	def handle_boolean(self, parent_names, name):
		self.handle_simple_type_for_decodejson(parent_names, name,
				CppBodyConstant.method_decodejson_array_do_bool,
				CppBodyConstant.method_decodejson_object_do_bool_template
			)

	def handle_float(self, parent_names, name):
		self.handle_simple_type_for_decodejson(parent_names, name,
				CppBodyConstant.method_decodejson_array_do_float,
				CppBodyConstant.method_decodejson_object_do_float_template
			)

	def handle_int(self, parent_names, name):
		self.handle_simple_type_for_decodejson(parent_names, name,
				CppBodyConstant.method_decodejson_array_do_int,
				CppBodyConstant.method_decodejson_object_do_int_template
			)

	def handle_string(self, parent_names, name):
		self.handle_simple_type_for_decodejson(parent_names, name,
				CppBodyConstant.method_decodejson_array_do_string,
				CppBodyConstant.method_decodejson_object_do_string_template
			)

class CppMethodEncodeHandler(CppMethodBaseHandler):
	def __init__(self, stringtype):
		CppMethodBaseHandler.__init__(self, stringtype)

	def handle_object_start(self, parent_names, name):
		CppMethodBaseHandler.handle_object_start(self, parent_names, name)

		if len(parent_names) > 0:
			if self.is_parent_array(name):
				parent_method_encodejson_array = CppFormat.method_encodejson_array_signature(parent_names, self.stringtype)
				self.methods[parent_method_encodejson_array] += CppBodyConstant.method_encodejson_array_do_object_template.substitute({
					"w": CppFormat.stringtype_w(self.stringtype)
					})
			else:
				parent_method_encodejson_object = CppFormat.method_encodejson_object_signature(parent_names, self.stringtype)
				self.methods[parent_method_encodejson_object] += CppBodyConstant.method_encodejson_object_do_object_template.substitute({
						"jsonname": name,
						"fieldname": CppFormat.fieldname(name),
						"w": CppFormat.stringtype_w(self.stringtype),
						"L": CppFormat.stringtype_L(self.stringtype)
					})

		names = parent_names[:]
		names.append(name)

		method_encodejson_ostream = CppFormat.method_encodejson_ostream_signature(names, self.stringtype)
		self.methods[method_encodejson_ostream] = CppBodyConstant.method_encodejson_ostream_for_object_template.substitute({
				"method_signature": method_encodejson_ostream,
				"w": CppFormat.stringtype_w(self.stringtype)
			})

		method_encodejson_object = CppFormat.method_encodejson_object_signature(names, self.stringtype)
		self.methods[method_encodejson_object] = CppBodyConstant.method_encodejson_object_begin_template.substitute({
				"method_signature": method_encodejson_object
			})

	def handle_object_end(self, parent_names, name):
		names = parent_names[:]
		names.append(name)
		method_encodejson_object = CppFormat.method_encodejson_object_signature(names, self.stringtype)
		self.methods[method_encodejson_object] += CppBodyConstant.method_encodejson_object_end

	def handle_array_start(self, parent_names, name):
		CppMethodBaseHandler.handle_array_start(self, parent_names, name)

		if len(parent_names) > 0:
			if self.is_parent_array(name):
				parent_method_encodejson_array = CppFormat.method_encodejson_array_signature(parent_names, self.stringtype)
				self.methods[parent_method_encodejson_array] += CppBodyConstant.method_encodejson_array_do_array_template.substitute({
					"w": CppFormat.stringtype_w(self.stringtype)
					})
			else:
				parent_method_encodejson_object = CppFormat.method_encodejson_object_signature(parent_names, self.stringtype)
				self.methods[parent_method_encodejson_object] += CppBodyConstant.method_encodejson_object_do_array_template.substitute({
						"jsonname": name,
						"fieldname": CppFormat.fieldname(name),
						"w": CppFormat.stringtype_w(self.stringtype),
						"L": CppFormat.stringtype_L(self.stringtype)
					})

		names = parent_names[:]
		names.append(name)

		method_encodejson_ostream = CppFormat.method_encodejson_ostream_signature(names, self.stringtype)
		self.methods[method_encodejson_ostream] = CppBodyConstant.method_encodejson_ostream_for_array_template.substitute({
				"method_signature": method_encodejson_ostream,
				"w": CppFormat.stringtype_w(self.stringtype)
			})

		method_encodejson_array = CppFormat.method_encodejson_array_signature(names, self.stringtype)
		self.methods[method_encodejson_array] = CppBodyConstant.method_encodejson_array_begin_template.substitute({
				"method_signature": method_encodejson_array
			})

	def handle_array_end(self, parent_names, name):
		names = parent_names[:]
		names.append(name)
		method_encodejson_array = CppFormat.method_encodejson_array_signature(names, self.stringtype)
		self.methods[method_encodejson_array] += CppBodyConstant.method_encodejson_array_end

	def handle_simple_type_for_encodejson(self, parent_names, name):
		if self.is_parent_array(name):
			parent_method_encodejson_array = CppFormat.method_encodejson_array_signature(parent_names, self.stringtype)
			self.methods[parent_method_encodejson_array] += CppBodyConstant.method_encodejson_array_do_simple_type_template.substitute({
				"w": CppFormat.stringtype_w(self.stringtype)
				})
		else:
			parent_method_encodejson_object = CppFormat.method_encodejson_object_signature(parent_names, self.stringtype)
			self.methods[parent_method_encodejson_object] += CppBodyConstant.method_encodejson_object_do_simple_type_template.substitute({
					"jsonname": name,
					"fieldname": CppFormat.fieldname(name),
					"w": CppFormat.stringtype_w(self.stringtype),
					"L": CppFormat.stringtype_L(self.stringtype)
				})

	def handle_boolean(self, parent_names, name):
		self.handle_simple_type_for_encodejson(parent_names, name)

	def handle_float(self, parent_names, name):
		self.handle_simple_type_for_encodejson(parent_names, name)

	def handle_int(self, parent_names, name):
		self.handle_simple_type_for_encodejson(parent_names, name)

	def handle_string(self, parent_names, name):
		self.handle_simple_type_for_encodejson(parent_names, name)

class CppBodyBuilder:
	def __init__(self, namespace, stringtype):
		self.namespace = namespace
		self.stringtype = stringtype
		self.filehandler = CppBodyFileHandler()
		self.methoddecodehandler = CppMethodDecodeHandler(stringtype)
		self.methodencodehandler = CppMethodEncodeHandler(stringtype)

		self.methodhandlers = [self.methoddecodehandler, self.methodencodehandler]
		self.handlers = [self.filehandler]
		self.handlers.extend(self.methodhandlers)

	def content(self):
		method_content = "\n".join([m.content() for m in self.methodhandlers])
		return self.filehandler.file_begin \
			+ CppFormat.namespace_begin(self.namespace) \
			+ method_content \
			+ CppFormat.namespace_end(self.namespace) \
			+ self.filehandler.file_end

	def save_to_dir(self, dirpath):
		f = open(os.path.join(dirpath, self.filehandler.filename), "w")
		f.write(self.content())
		f.close()

class CppTest:
	content_template = string.Template(
"""
/* 
 * The MIT License (MIT)
 * 
 * Copyright (c) 2012 Yuanyang Wu
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
 * OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 * ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 */


#include <iostream>
#include <fstream>
#include "${headerfilename}"

int main(int argc, char ** argv)
{
  std::${w}ifstream is(argv[1]);
  ${namespace}::${classname} val;
  val.DecodeJSON(is);
  val.EncodeJSON(std::${w}cout);
  return 0;
}
"""
	)

	def __init__(self, jsonfile, namespace, stringtype):
		self.filename = "main.cpp"
		self.content = CppTest.content_template.substitute({
				"headerfilename": CppFormat.headerfilename(jsonfile.classname),
				"namespace": namespace,
				"w": CppFormat.stringtype_w(stringtype),
				"classname": CppFormat.classname(jsonfile.classname)
			})

	def savefile(self, filepath):
		f = open(filepath, "w")
		f.write(self.content)
		f.close()

def parse_options():
	import optparse

	usage_msg = """usage: %prog [options] JSONFile"""
	parser = optparse.OptionParser(usage=usage_msg)
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

	options.jsondatafile = reminder[0]

	return options

if __name__ == "__main__":
	options = parse_options()

	j = JSONFile(options.jsondatafile)
	#print("file: " + j.filepath)
	#print("json: " + json.dumps(j.rawjson, indent=2, sort_keys=True))
	#print("class name: " + j.classname)
	#print

	walker = j.jsonwalker
	#walker.json_handlers.append(JSONBaseHandler())
	cppheader = CppHeaderHandler(options.namespace, options.stringtype)
	walker.json_handlers.append(cppheader)

	cppbodybuilder = CppBodyBuilder(options.namespace, options.stringtype)
	walker.json_handlers.extend(cppbodybuilder.handlers)
	#cppbodyfile = CppBodyFileHandler()
	#walker.json_handlers.append(cppbodyfile)
	#cppmethoddecode = CppMethodDecodeHandler()
	#walker.json_handlers.append(cppmethoddecode)
	#cppmethodencode = CppMethodEncodeHandler()
	#walker.json_handlers.append(cppmethodencode)
	walker.walk()

	#print cppheader.filename
	#print cppheader.content()
	cppheader.save_to_dir(options.dstdir)

	#print cppbodybuilder.content()
	cppbodybuilder.save_to_dir(options.dstdir)
	#print cppbodyfile.file_begin + cppbodyfile.file_end
	#print cppmethodprint.content()
	#print cppmethoddecode.content()
	#print cppmethodencode.content()

	if options.gentest:
		cpptest = CppTest(j, options.namespace, options.stringtype)
		cpptest.savefile(os.path.join(options.dstdir, cpptest.filename))
