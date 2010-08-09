# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 nowrap:
import json

def encrypt(data):
	""" Encrypt the data """
	result = json.dumps(data)
	print("edata: {0}".format(result))
	result_len = int(result.__len__())
	return "%032d%s" % (result_len, result)

def decrypt(data):
	""" Decrypt the data """
	result = json.loads(data)
	print("ddata: {0}".format(result))
	return result
