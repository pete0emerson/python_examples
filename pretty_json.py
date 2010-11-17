#!/usr/bin/env python

import simplejson
import sys

stdin = ''.join(sys.stdin.readlines())

try:
	data = simplejson.loads(stdin)
except:
	data = simplejson.loads('{"status":"Error reading JSON from STDIN"}')

print simplejson.dumps(data, indent=4)
