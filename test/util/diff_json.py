#!/usr/bin/python

import json
import sys

if len(sys.argv) != 3:
	print """Usage: diff_json.py SRCFILE DSTFILE"""
	exit(2)

src_dict = json.load(open(sys.argv[1]))
dst_dict = json.load(open(sys.argv[2]))

if src_dict == dst_dict:
	exit(0)
else:
	exit(1)

