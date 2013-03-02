#!/usr/bin/python

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

from jsoncpphandler import JSONBaseHandler, CppHeaderHandler, CppBodyBuilder, CppTest

class JSONDataWalker:
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
		child_name = None
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
		return JSONDataWalker(self.rawjson, self.classname)

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
		cpptest = CppTest(cppheader.classname, options.namespace, options.stringtype)
		cpptest.savefile(os.path.join(options.dstdir, cpptest.filename))

