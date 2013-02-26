from google.appengine.ext import ndb

class Configuration(ndb.Model):
	key = ndb.StringProperty()
	value = ndb.StringProperty()

class OphanData(ndb.Model):
	date = ndb.DateProperty(auto_now_add = True)
	url = ndb.StringProperty(required = True)
	count = ndb.IntegerProperty(required = True)
