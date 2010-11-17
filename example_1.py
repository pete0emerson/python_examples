#!/usr/bin/env python

import ConfigParser
import web
import simplejson
import datetime
import sys
import memcache
import hashlib

config = ConfigParser.ConfigParser()

config.read('example_1.cfg')

# If we don't have certain entries in our config file, print a useful sample config file and then exit
try:
	config.get('DEFAULT', 'mysql_host')
	config.get('DEFAULT', 'mysql_database')
	config.get('DEFAULT', 'mysql_username')
	config.get('DEFAULT', 'mysql_password')
	config.get('DEFAULT', 'memcache_host')
	config.get('DEFAULT', 'memcache_port')
except:
	print """Specify the following in db.cfg (edit to apply to your configuration needs):

[DEFAULT]
mysql_host=127.0.0.1
mysql_database=sample
mysql_username=username
mysql_password=password
memcache_host=127.0.0.1
memcache_port=11211

"""
	sys.exit(1)

# Connect to memcached
mc = memcache.Client([config.get('DEFAULT', 'memcache_host') + ':' + config.get('DEFAULT', 'memcache_port')], debug=1)

# Make sure we can set and get something from memcached; exit if we can't
mc.set("sample1.connection", 1)
value = mc.get("sample1.connection")
if value is None:
	print "Unable to connect to memcache at " + config.get('DEFAULT', 'memcache_host') + ':' + config.get('DEFAULT', 'memcache_port')
	sys.exit(1)

# Clear the only key / value we're using in this example
check = mc.get('sql')
if check:
	mc.delete('sql')

# Test the database connection; exit if we can't connect to it
try:
	db = web.database(dbn='mysql', host=config.get('DEFAULT', 'mysql_host'), user=config.get('DEFAULT', 'mysql_username'), pw=config.get('DEFAULT', 'mysql_password'), db=config.get('DEFAULT', 'mysql_database'))
	test = db.query('show databases')
except:
	print "Unable to connect to database " + config.get('DEFAULT', 'mysql_database') + ' on host ' + config.get('DEFAULT', 'mysql_host') + ' using username ' + config.get('DEFAULT', 'mysql_username')
	sys.exit(1)

# This connects our URLs to our sample1 class
urls = (
  '/(.*)', 'example1'
)

app = web.application(urls, globals())

class example1:
    def GET(self, request):
		# If the favicon or an empty respose is requested, cut the process short
		if request == 'favicon.ico':
			return '{}'
		if request == '':
			return '{ "response" : "failed" }'

		# Parse the GET parameters to create the WHERE clause of the SQL statement
		params = web.input()
		wheres = []
		joiner = 'AND'
		for key in params:
			# If we pass in join=or, then we'll use OR in our WHERE clause instead of AND
			if key == 'join':
				if params[key].upper() == 'OR':
					joiner = 'OR'
			else:
				valuesList = web.websafe(params[key]).split(',')
				wheres.append(key + ' IN ("' + '", "'.join(valuesList) + '")')
		sql = "SELECT * FROM " + request

		if wheres:
			sql = sql + ' WHERE ' + (' ' + joiner + ' ').join(wheres)

		# Create a hash of the query for a memcache lookup
		sqlhash = hashlib.md5(sql).hexdigest()

		# Pull the result from memcache if we can
		result = mc.get(sqlhash)
		if not result:
			try:
			        todos = db.query(sql)
			except:
				return '{ "response" : "failed" }'
			result = {}
			result['response'] = 'okay'
			result['memcache'] = 'miss'
			result['data'] = []
			for record in todos:
				entry = {}
				for col in record:
					# datetime has to be converted to a string, so treat that as a special case
					if isinstance(record[col], datetime.datetime):
						entry[col] = record[col].strftime('%Y-%m-%d %H:%M:%S')
					else:
						entry[col] = record[col]
				result['data'].append(entry)
			# Store the results back in memcache, to expire in 5 seconds
			mc.set(sqlhash, simplejson.dumps(result), 5)
			return simplejson.dumps(result)
		else:
			# Note in the data that we got a memcache hit
			decoded=simplejson.loads(result)
			decoded['memcache'] = sqlhash
			return simplejson.dumps(decoded)

if __name__ == "__main__":
    app.run()
