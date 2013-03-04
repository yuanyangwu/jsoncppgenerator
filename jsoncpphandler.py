#  The MIT License (MIT)
#
#  Copyright (c) 2013 Yuanyang Wu
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

	def handle_object_start(self, parent_names, name, object_type_name = None, base_type_name = None):
		if JSONBaseHandler.print_trace:
			print "--" * len(parent_names) + "handle_object_start " + str(name)

	def handle_object_end(self, parent_names, name, object_type_name = None):
		if JSONBaseHandler.print_trace:
			print "--" * len(parent_names) + "handle_object_end " + str(name)

	def handle_array_start(self, parent_names, name, element_type_name = None):
		if JSONBaseHandler.print_trace:
			print "--" * len(parent_names) + "handle_array_start " + str(name)

	def handle_array_end(self, parent_names, name, element_type_name = None):
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

	def handle_int64(self, parent_names, name):
		if JSONBaseHandler.print_trace:
			print "--" * len(parent_names) + "handle_int64 " + str(name)

	def handle_string(self, parent_names, name):
		if JSONBaseHandler.print_trace:
			print "--" * len(parent_names) + "handle_string " + str(name)

###############################################################################
# Convert JSON to C++
#

class CppFormat:
	def headerfilename(name):
		if name != None and (name.find("::") >= 0):
			# name prefixed with namespace like "detail::IntArray"
			return name.replace("::", "/") + ".h"

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
		if name != None and (name.find("::") >= 0):
			# name prefixed with namespace like "detail::IntArray"
			return name

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
			+ "DecodeJSON(const json_spirit::" + CppFormat.stringtype_w(stringtype) + "Value & val)"

	def method_decodejson_array_signature(names, stringtype):
		return CppFormat.method_decodejson_object_signature(names, stringtype)

	def method_encodejson_ostream_signature(names, stringtype):
		decorator = ""
		if len(names) > 0:
			decorator = CppFormat.class_decorator(names) + "::"
		return "void " + decorator \
			+ "EncodeJSON(std::" + CppFormat.stringtype_w(stringtype) + "ostream & os, bool isPrettyPrint) const"

	def method_encodejson_object_or_array_signature(names, stringtype):
		decorator = ""
		if len(names) > 0:
			decorator = CppFormat.class_decorator(names) + "::"
		return "void " + decorator \
			+ "EncodeJSON(json_spirit::" + CppFormat.stringtype_w(stringtype) + "Value & val) const"

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
	method_encodejson_object_or_array_signature = staticmethod(method_encodejson_object_or_array_signature)

class CppHeaderHandler(JSONBaseHandler):

	file_begin_template = string.Template(
"""
/*
 * The MIT License (MIT)
 *
 * Copyright (c) 2013 Yuanyang Wu
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
${indent}class ${classname} ${inherit_base_class}
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
		self.classname = ""
		self.file_begin = ""
		self.class_decl = ""
		self.file_end = CppHeaderHandler.file_end
		self.dep_types = set()

	def content(self):
		dep_includes = "\n".join(["#include \"" + CppFormat.headerfilename(dep_type) + "\"" \
					for dep_type in sorted(self.dep_types)] ) \
				+ "\n\n"
		return self.file_begin \
			+ dep_includes \
			+ CppFormat.namespace_begin(self.namespace) \
			+ self.class_decl \
			+ CppFormat.namespace_end(self.namespace) \
			+ self.file_end

	def save_to_dir(self, dirpath):
		f = open(os.path.join(dirpath, self.filename), "w")
		f.write(self.content())
		f.close()

	def handle_object_start(self, parent_names, name, object_type_name = None, base_type_name = None):
		gen_class = (object_type_name == None) or ( len(parent_names) == 0 )
		if object_type_name != None:
			self.dep_types.add(object_type_name)

		inherit_base_class = ""
		if base_type_name != None:
			self.dep_types.add(base_type_name)
			inherit_base_class = ": public " + CppFormat.classname(base_type_name)

		classname = CppFormat.classname(name, parent_names)

		if len(parent_names) == 0:
			self.filename = CppFormat.headerfilename(name)
			self.classname = CppFormat.classname(name)
			self.file_begin = CppHeaderHandler.file_begin_template.substitute({
					"classname": classname
				})

		if not gen_class:
			return None

		self.class_decl += CppHeaderHandler.class_begin_template.substitute({
				"indent": CppFormat.indent(len(parent_names)),
				"classname" : classname,
				"inherit_base_class": inherit_base_class,
				"w": CppFormat.stringtype_w(self.stringtype),
				"method_decodejson_signature": CppFormat.method_decodejson_object_signature([], self.stringtype),
				"method_encodejson_signature": CppFormat.method_encodejson_object_or_array_signature([], self.stringtype)
			})

	def handle_object_end(self, parent_names, name, object_type_name = None):
		gen_class = (object_type_name == None) or ( len(parent_names) == 0 )

		if gen_class:
			self.class_decl += CppHeaderHandler.class_end_template.substitute({
					"indent": CppFormat.indent(len(parent_names))
				})

		if len(parent_names) > 0:
			if self.is_parent_array(name):
				if gen_class:
					self.class_decl += CppHeaderHandler.element_type_of_array_template.substitute({
							"indent": CppFormat.indent(len(parent_names)),
							"type": CppFormat.classname(name, parent_names)
						})
			else:
				if object_type_name == None:
					classname = CppFormat.classname(name)
				else:
					classname = CppFormat.classname(object_type_name)

				self.class_decl += CppHeaderHandler.field_of_object_template.substitute({
						"indent": CppFormat.indent(len(parent_names)),
						"type": classname,
						"name": CppFormat.fieldname(name)
					})

	def handle_array_start(self, parent_names, name, element_type_name = None):
		if element_type_name != None:
			self.dep_types.add(element_type_name)

		if len(parent_names) == 0:
			self.filename = CppFormat.headerfilename(name)
			self.classname = CppFormat.classname(name)
			self.file_begin = CppHeaderHandler.file_begin_template.substitute({
					"classname": string.upper(CppFormat.classname(name))
				})

		if len(parent_names) > 0 and element_type_name != None:
			return None

		self.class_decl += CppHeaderHandler.class_begin_template.substitute({
				"indent": CppFormat.indent(len(parent_names)),
				"classname" : CppFormat.classname(name),
				"inherit_base_class": "",
				"w": CppFormat.stringtype_w(self.stringtype),
				"method_decodejson_signature": CppFormat.method_decodejson_array_signature([], self.stringtype),
				"method_encodejson_signature": CppFormat.method_encodejson_object_or_array_signature([], self.stringtype)
			})

	def handle_array_end(self, parent_names, name, element_type_name = None):
		if len(parent_names) == 0 or element_type_name == None:
			if element_type_name != None:
				self.class_decl += CppHeaderHandler.element_type_of_array_template.substitute({
						"indent": CppFormat.indent(len(parent_names) + 1),
						"type": CppFormat.classname(element_type_name)
					})

			self.class_decl += CppHeaderHandler.array_type_of_array_template.substitute({
					"indent": CppFormat.indent(len(parent_names))
				})
			self.class_decl += CppHeaderHandler.class_end_template.substitute({
					"indent": CppFormat.indent(len(parent_names))
				})

		if len(parent_names) > 0:
			if element_type_name == None:
				classname = CppFormat.classname(name, parent_names)
			else:
				classname = CppFormat.classname(element_type_name, parent_names)

			if self.is_parent_array(name):
				self.class_decl += CppHeaderHandler.element_type_of_array_template.substitute({
						"indent": CppFormat.indent(len(parent_names)),
						"type": classname
					})
			else:
				self.class_decl += CppHeaderHandler.field_of_object_template.substitute({
						"indent": CppFormat.indent(len(parent_names)),
						"type": classname,
						"name": CppFormat.fieldname(name)
					})

	def handle_boolean(self, parent_names, name):
		self.handle_simple_type(parent_names, name, "bool")

	def handle_float(self, parent_names, name):
		self.handle_simple_type(parent_names, name, "double")

	def handle_int(self, parent_names, name):
		self.handle_simple_type(parent_names, name, "int")

	def handle_int64(self, parent_names, name):
		self.handle_simple_type(parent_names, name, "boost::int64_t")

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
 * Copyright (c) 2013 Yuanyang Wu
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
  DecodeJSON(value);
}
"""
	)

	method_decodejson_object_begin_template = string.Template(
"""${method_signature}
{
  ${call_base_method}
  const json_spirit::${w}Object & obj(val.get_obj());
  BOOST_FOREACH(const json_spirit::${w}Pair & pair, obj)
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

	method_decodejson_object_do_int64_template = string.Template(
"""    if (pair.name_ == ${L}"${jsonname}")
    {
      ${fieldname} = pair.value_.get_int64();
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
      value.DecodeJSON(pair.value_);
      ${fieldname} = value;
    }
    else
"""
	)

	method_decodejson_object_do_array_template = string.Template(
"""    if (pair.name_ == ${L}"${jsonname}")
    {
      ${classname} value;
      value.DecodeJSON(pair.value_);
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
  DecodeJSON(value);
}
"""
	)

	method_decodejson_array_begin_template = string.Template(
"""${method_signature}
{
  const json_spirit::${w}Array & array(val.get_array());
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

	method_decodejson_array_do_int64 = """      element = value.get_int64();
"""

	method_decodejson_array_do_float = """      element = value.get_real();
"""

	method_decodejson_array_do_string = """      element = value.get_str();
"""

	method_decodejson_array_do_object_or_array_template = string.Template(
"""      ${classname} e;
      e.DecodeJSON(value);
      element = e;
"""
	)

	###############################
	# encodejson
	method_encodejson_ostream_for_object_or_array_template = string.Template(
"""${method_signature}
{
  json_spirit::${w}Value value;
  EncodeJSON(value);
  unsigned int options = json_spirit::remove_trailing_zeros;
  if (isPrettyPrint)
  {
    options = json_spirit::pretty_print|json_spirit::remove_trailing_zeros;
  }
  json_spirit::write(value, os, options);
}
"""
	)

	method_encodejson_object_begin_template = string.Template(
"""${method_signature}
{
  ${call_base_method}
  if (json_spirit::null_type == val.type())
  {
    val = json_spirit::${w}Object();
  }

"""
	)

	method_encodejson_object_end = """
}
"""

	method_encodejson_object_do_simple_type_template = string.Template(
"""  if (${fieldname}) { val.get_obj().push_back(json_spirit::${w}Pair(${L}"${jsonname}", *${fieldname})); }
"""
	)

	method_encodejson_object_do_object_or_array_template = string.Template(
"""  if (${fieldname})
  {
    json_spirit::${w}Value child;
    (*${fieldname}).EncodeJSON(child);
    val.get_obj().push_back(json_spirit::${w}Pair(${L}"${jsonname}", child));
  }
"""
	)

	method_encodejson_array_begin_template = string.Template(
"""${method_signature}
{
  json_spirit::${w}Array array;
  BOOST_FOREACH(const ArrayElementType & value, m_array)
  {
"""
	)

	method_encodejson_array_end = """  }
  val = array;
}
"""

	method_encodejson_array_do_simple_type_template = string.Template(
"""
    if (value) { array.push_back(json_spirit::${w}Value(*value)); }
    else { array.push_back(json_spirit::${w}Value()); }
"""
	)

	method_encodejson_array_do_object_or_array_template = string.Template(
"""    if (value)
    {
      json_spirit::${w}Value child;
      (*value).EncodeJSON(child);
      array.push_back(child);
    }
    else { array.push_back(json_spirit::${w}Value()); }

"""
	)

class CppBodyFileHandler(JSONBaseHandler):
	def __init__(self):
		self.filename = ""
		self.file_begin = ""
		self.file_end = CppBodyConstant.file_end

	def handle_object_start(self, parent_names, name, object_type_name = None, base_type_name = None):
		if len(parent_names) == 0:
			self.filename = CppFormat.bodyfilename(name)
			self.file_begin = CppBodyConstant.file_begin_template.substitute({
					"headerfilename": CppFormat.headerfilename(name)
				})

	def handle_array_start(self, parent_names, name, element_type_name = None):
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

	def handle_object_start(self, parent_names, name, object_type_name = None, base_type_name = None):
		if len(parent_names) == 0:
			self.filename = CppFormat.bodyfilename(name)

	def handle_array_start(self, parent_names, name, element_type_name = None):
		if len(parent_names) == 0:
			self.filename = CppFormat.bodyfilename(name)

class CppMethodDecodeHandler(CppMethodBaseHandler):
	def __init__(self, stringtype):
		CppMethodBaseHandler.__init__(self, stringtype)

	def handle_object_start(self, parent_names, name, object_type_name = None, base_type_name = None):
		CppMethodBaseHandler.handle_object_start(self, parent_names, name, object_type_name)
		gen_class = (object_type_name == None) or ( len(parent_names) == 0 )

		if len(parent_names) > 0:
			if self.is_parent_array(name):
				if object_type_name == None:
					classname = CppFormat.classname(name, parent_names)
				else:
					classname = CppFormat.classname(object_type_name)

				parent_method_decodejson_array = CppFormat.method_decodejson_array_signature(parent_names, self.stringtype)
				self.methods[parent_method_decodejson_array] += CppBodyConstant.method_decodejson_array_do_object_or_array_template.substitute({"classname": classname})
			else:
				if object_type_name == None:
					classname = CppFormat.classname(name)
				else:
					classname = CppFormat.classname(object_type_name)

				parent_method_decodejson_object = CppFormat.method_decodejson_object_signature(parent_names, self.stringtype)
				self.methods[parent_method_decodejson_object] += CppBodyConstant.method_decodejson_object_do_object_template.substitute({
						"jsonname": name,
						"fieldname": CppFormat.fieldname(name),
						"classname": classname,
						"L": CppFormat.stringtype_L(self.stringtype)
					})

		if not gen_class:
			return None

		names = parent_names[:]
		names.append(name)

		method_decodejson_istream = CppFormat.method_decodejson_istream_signature(names, self.stringtype)
		self.methods[method_decodejson_istream] = CppBodyConstant.method_decodejson_istream_for_object_template.substitute({
				"method_signature": method_decodejson_istream,
				"w": CppFormat.stringtype_w(self.stringtype)
			})

		call_base_method = ""
		if base_type_name != None:
			call_base_method = CppFormat.classname(base_type_name) + "::DecodeJSON(val);"

		method_decodejson_object = CppFormat.method_decodejson_object_signature(names, self.stringtype)
		self.methods[method_decodejson_object] = CppBodyConstant.method_decodejson_object_begin_template.substitute({
				"call_base_method": call_base_method,
				"method_signature": method_decodejson_object,
				"w": CppFormat.stringtype_w(self.stringtype)
			})

	def handle_object_end(self, parent_names, name, object_type_name = None):
		gen_class = (object_type_name == None) or ( len(parent_names) == 0 )
		if not gen_class:
			return None

		names = parent_names[:]
		names.append(name)
		method_decodejson_object = CppFormat.method_decodejson_object_signature(names, self.stringtype)
		self.methods[method_decodejson_object] += CppBodyConstant.method_decodejson_object_end

	def handle_array_start(self, parent_names, name, element_type_name = None):
		CppMethodBaseHandler.handle_array_start(self, parent_names, name, element_type_name)

		if len(parent_names) > 0:
			if self.is_parent_array(name):
				if element_type_name == None:
					classname = CppFormat.classname(name, parent_names)
				else:
					classname = CppFormat.classname(element_type_name)

				parent_method_decodejson_array = CppFormat.method_decodejson_array_signature(parent_names, self.stringtype)
				self.methods[parent_method_decodejson_array] += CppBodyConstant.method_decodejson_array_do_object_or_array_template.substitute({"classname": classname})
			else:
				if element_type_name == None:
					classname = CppFormat.classname(name)
				else:
					classname = CppFormat.classname(element_type_name)

				parent_method_decodejson_object = CppFormat.method_decodejson_object_signature(parent_names, self.stringtype)
				self.methods[parent_method_decodejson_object] += CppBodyConstant.method_decodejson_object_do_array_template.substitute({
						"jsonname": name,
						"fieldname": CppFormat.fieldname(name),
						"classname": classname,
						"L": CppFormat.stringtype_L(self.stringtype)
					})

		if len(parent_names) > 0 and element_type_name != None:
			return None

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

	def handle_array_end(self, parent_names, name, element_type_name = None):
		if len(parent_names) > 0 and element_type_name != None:
			return None

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

	def handle_int64(self, parent_names, name):
		self.handle_simple_type_for_decodejson(parent_names, name,
				CppBodyConstant.method_decodejson_array_do_int64,
				CppBodyConstant.method_decodejson_object_do_int64_template
			)

	def handle_string(self, parent_names, name):
		self.handle_simple_type_for_decodejson(parent_names, name,
				CppBodyConstant.method_decodejson_array_do_string,
				CppBodyConstant.method_decodejson_object_do_string_template
			)

class CppMethodEncodeHandler(CppMethodBaseHandler):
	def __init__(self, stringtype):
		CppMethodBaseHandler.__init__(self, stringtype)

	def handle_object_start(self, parent_names, name, object_type_name = None, base_type_name = None):
		CppMethodBaseHandler.handle_object_start(self, parent_names, name, object_type_name)
		gen_class = (object_type_name == None) or ( len(parent_names) == 0 )

		if len(parent_names) > 0:
			if self.is_parent_array(name):
				parent_method_encodejson_array = CppFormat.method_encodejson_object_or_array_signature(parent_names, self.stringtype)
				self.methods[parent_method_encodejson_array] += CppBodyConstant.method_encodejson_array_do_object_or_array_template.substitute({
					"w": CppFormat.stringtype_w(self.stringtype)
					})
			else:
				parent_method_encodejson_object = CppFormat.method_encodejson_object_or_array_signature(parent_names, self.stringtype)
				self.methods[parent_method_encodejson_object] += CppBodyConstant.method_encodejson_object_do_object_or_array_template.substitute({
						"jsonname": name,
						"fieldname": CppFormat.fieldname(name),
						"w": CppFormat.stringtype_w(self.stringtype),
						"L": CppFormat.stringtype_L(self.stringtype)
					})

		if not gen_class:
			return None

		names = parent_names[:]
		names.append(name)

		method_encodejson_ostream = CppFormat.method_encodejson_ostream_signature(names, self.stringtype)
		self.methods[method_encodejson_ostream] = CppBodyConstant.method_encodejson_ostream_for_object_or_array_template.substitute({
				"method_signature": method_encodejson_ostream,
				"w": CppFormat.stringtype_w(self.stringtype)
			})

		call_base_method = ""
		if base_type_name != None:
			call_base_method = CppFormat.classname(base_type_name) + "::EncodeJSON(val);"

		method_encodejson_object = CppFormat.method_encodejson_object_or_array_signature(names, self.stringtype)
		self.methods[method_encodejson_object] = CppBodyConstant.method_encodejson_object_begin_template.substitute({
				"method_signature": method_encodejson_object,
				"w": CppFormat.stringtype_w(self.stringtype),
				"call_base_method": call_base_method
			})

	def handle_object_end(self, parent_names, name, object_type_name = None):
		gen_class = (object_type_name == None) or ( len(parent_names) == 0 )
		if not gen_class:
			return None

		names = parent_names[:]
		names.append(name)
		method_encodejson_object = CppFormat.method_encodejson_object_or_array_signature(names, self.stringtype)
		self.methods[method_encodejson_object] += CppBodyConstant.method_encodejson_object_end

	def handle_array_start(self, parent_names, name, element_type_name = None):
		CppMethodBaseHandler.handle_array_start(self, parent_names, name, element_type_name)

		if len(parent_names) > 0:
			if self.is_parent_array(name):
				parent_method_encodejson_array = CppFormat.method_encodejson_object_or_array_signature(parent_names, self.stringtype)
				self.methods[parent_method_encodejson_array] += CppBodyConstant.method_encodejson_array_do_object_or_array_template.substitute({
					"w": CppFormat.stringtype_w(self.stringtype)
					})
			else:
				parent_method_encodejson_object = CppFormat.method_encodejson_object_or_array_signature(parent_names, self.stringtype)
				self.methods[parent_method_encodejson_object] += CppBodyConstant.method_encodejson_object_do_object_or_array_template.substitute({
						"jsonname": name,
						"fieldname": CppFormat.fieldname(name),
						"w": CppFormat.stringtype_w(self.stringtype),
						"L": CppFormat.stringtype_L(self.stringtype)
					})

		if len(parent_names) > 0 and element_type_name != None:
			return None

		names = parent_names[:]
		names.append(name)

		method_encodejson_ostream = CppFormat.method_encodejson_ostream_signature(names, self.stringtype)
		self.methods[method_encodejson_ostream] = CppBodyConstant.method_encodejson_ostream_for_object_or_array_template.substitute({
				"method_signature": method_encodejson_ostream,
				"w": CppFormat.stringtype_w(self.stringtype)
			})

		method_encodejson_array = CppFormat.method_encodejson_object_or_array_signature(names, self.stringtype)
		self.methods[method_encodejson_array] = CppBodyConstant.method_encodejson_array_begin_template.substitute({
				"method_signature": method_encodejson_array,
				"w": CppFormat.stringtype_w(self.stringtype)
			})

	def handle_array_end(self, parent_names, name, element_type_name = None):
		if len(parent_names) > 0 and element_type_name != None:
			return None

		names = parent_names[:]
		names.append(name)
		method_encodejson_array = CppFormat.method_encodejson_object_or_array_signature(names, self.stringtype)
		self.methods[method_encodejson_array] += CppBodyConstant.method_encodejson_array_end

	def handle_simple_type_for_encodejson(self, parent_names, name):
		if self.is_parent_array(name):
			parent_method_encodejson_array = CppFormat.method_encodejson_object_or_array_signature(parent_names, self.stringtype)
			self.methods[parent_method_encodejson_array] += CppBodyConstant.method_encodejson_array_do_simple_type_template.substitute({
				"w": CppFormat.stringtype_w(self.stringtype)
				})
		else:
			parent_method_encodejson_object = CppFormat.method_encodejson_object_or_array_signature(parent_names, self.stringtype)
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

	def handle_int64(self, parent_names, name):
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
 * Copyright (c) 2013 Yuanyang Wu
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
  val.EncodeJSON(std::${w}cout, true);
  return 0;
}
"""
	)

	def __init__(self, classname, namespace, stringtype):
		self.filename = "main.cpp"
		self.content = CppTest.content_template.substitute({
				"headerfilename": CppFormat.headerfilename(classname),
				"namespace": namespace,
				"w": CppFormat.stringtype_w(stringtype),
				"classname": CppFormat.classname(classname)
			})

	def savefile(self, filepath):
		f = open(filepath, "w")
		f.write(self.content)
		f.close()

