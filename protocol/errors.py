# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 nowrap:

ERRORS = {
	0x01: 'Unknown error',
	0x02: 'Server not found',
	0x03: 'Protocol error',
	0x10: 'Authentication error',
	0x11: 'User expired',
	0x12: 'Account disabled',
	0x13: 'Account banned',
}

class ProtocolError(Exception):
	pass
