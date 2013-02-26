import headers
import configuration

from models import OphanData

import webapp2
import json

from urllib import urlencode
from urlparse import urlparse

from google.appengine.api.urlfetch import fetch
from google.appengine.api import memcache

import logging

OPHAN_API_KEY = configuration.lookup("OPHAN_API_KEY")

def read_weeks_ophan_data():
	cached_content = memcache.get("ophan_summary")

	if cached_content:
		return json.loads(cached_content)

	base_url = "http://api.ophan.co.uk/api/mostread"

	params = {
		"api-key" : OPHAN_API_KEY,
		"age" : 7 * 24 * 60 * 60,
		"count" : 100,
	}

	url = base_url + "?" + urlencode(params)
	
	result = fetch(url, deadline = 9)

	if not result.status_code == 200: return None

	memcache.add("ophan_summary", result.content)

	return json.loads(result.content)

def read_content(ophan_data):
	base_url = "http://content.guardianapis.com"

	params = {
		"show-fields" : "standfirst,headline,thumbnail",
		"show-tags" : "all",
		"format" : "json",
	}

	parsed_url = urlparse(ophan_data["url"])

	cached_data = memcache.get(parsed_url.path)

	if cached_data:
		return json.loads(cached_data)

	logging.debug(parsed_url.path)

	url = base_url + parsed_url.path + "?" + urlencode(params)

	logging.info(url)

	result = fetch(url, deadline = 6)

	if not result.status_code == 200: return None

	response = json.loads(result.content)

	content = response.get("response", {}).get("content", {})

	memcache.add(parsed_url.path, json.dumps(content), 3 * 60)

	content['views'] = ophan_data['count']
	return content


class ReadOphan(webapp2.RequestHandler):
	def get(self):
		data = {"hello" : "world"}

		headers.json(self.response)

		cached_data = memcache.get("popular_content")

		if not cached_data:

			ophan_data = read_weeks_ophan_data()
			popular_content = [read_content(result) for result in ophan_data]
			popular_content = [item for item in popular_content if item]

			data['popular_content'] = popular_content
			memcache.set("popular_content", json.dumps(popular_content))

		if cached_data:
			data['popular_content'] = json.loads(cached_data)

		self.response.out.write(json.dumps(data))

class RecordOphan(webapp2.RequestHandler):
	def get(self):
		data = {"hello" : "world"}

		headers.json(self.response)

		ophan_data = read_weeks_ophan_data()

		data['ophan_data'] = ophan_data

		for content in ophan_data:
			logging.info(content)
			OphanData(url = content['url'], count = content['count']).put()

		self.response.out.write(json.dumps(data))

app = webapp2.WSGIApplication([('/tasks/ophan', ReadOphan),
	('/tasks/ophan/record', RecordOphan),], debug=True)