#!/usr/bin/python

import json
import sys
import types

TRACE = True

def is_equal_with_src_none_skipped(src, dst):
	if (src == dst) or (src == None):
		return True

	if type(src) != type(dst):
		if TRACE: print "different type: " + type(src) + " " + type(dst)
		return False

	if type(src) == types.DictType:
		src_keys = src.keys()
		dst_keys = dst.keys()

		src_only_keys = [k for k in src_keys if k not in dst_keys]
		for k in src_only_keys:
			# only skip None item
			if src[k] != None:
				if TRACE: print "non-None src only item: src[" + str(k) + "]=" + str(src[k])
				return False

		dst_only_keys = [k for k in dst_keys if k not in src_keys]
		if len(dst_only_keys) > 0:
			if TRACE: print "non-empty dst only keys: " + str(dst_only_keys)
			return False

		common_keys = [k for k in src_keys if k in dst_keys]
		for k in common_keys:
			if not is_equal_with_src_none_skipped(src[k], dst[k]):
				if TRACE: print "diff value on key=" + str(k) + ", src=" + str(src[k]) + ", dst=" + str(dst[k])
				return False

		return True

	if type(src) == types.ListType:
		if len(src) != len(dst):
			if TRACE: print "diff array len: src=" + str(src) + ", dst=" + str(dst)
			return False

		for i in xrange(0, len(src)):
			if not is_equal_with_src_none_skipped(src[i], dst[i]):
				if TRACE: print "diff value on index=" + str(i) + ", src=" + str(src[i]) + ", dst=" + str(dst[i])
				return False
		return True

	# simple type, src != dst
	return False

if len(sys.argv) != 3:
	print """Usage: diff_json.py SRCFILE DSTFILE"""
	exit(2)

src_dict = json.load(open(sys.argv[1]))
dst_dict = json.load(open(sys.argv[2]))

if is_equal_with_src_none_skipped(src_dict, dst_dict):
	exit(0)
else:
	exit(1)

