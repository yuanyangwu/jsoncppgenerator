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
import os

from jsoncpphandler import CppHeaderHandler, CppBodyBuilder

class JSONArrayClassWalker:
	def __init__(self):
		self.json_handlers = []

	def walk(self, arrayclass):
		parent_names = []
		name = arrayclass
		for handler in self.json_handlers:
			handler.handle_array_start(parent_names, name)

		child_parent_names = parent_names[:]
		child_parent_names.append(name)
		# array element has no name
		# use "None" to indicate parent is array
		child_name = None
		for handler in self.json_handlers:
			if arrayclass == "BooleanArray":
				handler.handle_boolean(child_parent_names, child_name)
			elif arrayclass == "DoubleArray":
				handler.handle_float(child_parent_names, child_name)
			elif arrayclass == "IntArray":
				handler.handle_int(child_parent_names, child_name)
			elif arrayclass == "Int64Array":
				handler.handle_int64(child_parent_names, child_name)
			elif arrayclass == "StringArray":
				handler.handle_string(child_parent_names, child_name)
			else:
				assert False, ("Unsupported type: " + arrayclass)

		for handler in self.json_handlers:
			handler.handle_array_end(parent_names, name)

class JSONDetailCppClass:
	def __init__(self):
		self.arrayclasses = ["IntArray", "Int64Array", "BooleanArray", "DoubleArray", "StringArray"]

	def is_detail_class(self, classname):
		ns = "detail::"
		if not classname.startswith(ns):
			return False
		return classname[len(ns):] in self.arrayclasses

	def save_to_dir(self, classname, dirpath, namespace, stringtype):
		assert self.is_detail_class(classname), ("class name \"" + classname + "\" must be among " + ", ".join(self.arrayclasses))

		ns = "detail::"
		classname = classname[len(ns):]

		dirpath = os.path.join(dirpath, "detail")

		if namespace == "":
			namespace = "detail"
		else:
			namespace = namespace + "::" + "detail"

		if not os.path.exists(dirpath):
			os.makedirs(dirpath)

		self.generate_arrayclass(classname, dirpath, namespace, stringtype)

	def generate_arrayclass(self, arrayclass, dirpath, namespace, stringtype):
		walker = JSONArrayClassWalker()

		cppheader = CppHeaderHandler(namespace, stringtype)
		walker.json_handlers.append(cppheader)
		cppbodybuilder = CppBodyBuilder(namespace, stringtype)
		walker.json_handlers.extend(cppbodybuilder.handlers)

		walker.walk(arrayclass)

		cppheader.save_to_dir(dirpath)
		cppbodybuilder.save_to_dir(dirpath)

if __name__ == "__main__":
	detailCpp = JSONDetailCppClass()
	detailCpp.save_to_dir("detail::IntArray", "t", "", "std::string")
