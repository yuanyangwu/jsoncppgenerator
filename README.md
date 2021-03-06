# JSON C++ Code Generator
Tool of generating JSON Spirit C++ code from JSON data

## What is it?
We can use the tool to generate C++ codec against a JSON data file.
For the following JSON file "object_simple.json",

	{
	  "stringValue": "str1",
	  "intValue": 1,
	  "realValue": 1.23,
	  "boolValue": false
	}

We can run the command.
	python jsondata2cpp.py object_simple.json

Then it generats following C++ code.

	class ObjectSimple
	{
	public:
	  void DecodeJSON(std::istream & is);
	  void EncodeJSON(std::ostream & os, bool isPrettyPrint = false) const;
	
	  boost::optional<bool> m_boolValue;
	  boost::optional<int> m_intValue;
	  boost::optional<double> m_realValue;
	  boost::optional<std::string> m_stringValue;
	};

## Usage
### jsondata2cpp.py
	Usage: jsondata2cpp.py [options] JSONFile
	
	Options:
	  -h, --help            show this help message and exit
	  --dstdir=DSTDIR       directory to save the generated code files, default is
	                        current directory
	  --namespace=NAMESPACE
	                        C++ namespace seperated with "::", for example,
	                        "com::company". Default is no namespace
	  --stringtype=STRINGTYPE
	                        C++ string type, std::string or std::wstring, default
	                        is std::string
	  --gentest             generate test code "main.cpp", default is false

## Dependencies
* Running the script requires
  * Python v2.6+ (not verified under v3.x)
* Building generated code requires
  * [JSON Spirit C++ Library v4.05](http://www.codeproject.com/Articles/20027/JSON-Spirit-A-C-JSON-Parser-Generator-Implemented)
  * BOOST C++ Library
* Running test requires
  * GNU Make
  * BASH

## Code Status
* [![Build Status](https://travis-ci.org/yuanyangwu/jsoncppgenerator.png)](https://travis-ci.org/yuanyangwu/jsoncppgenerator)

## License
JSON C++ Code Generator and the code generated by it are under [MIT License](http://www.opensource.org/licenses/MIT)

