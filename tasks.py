import headers

import webapp2
import json

from urllib import urlencode
from urlparse import urlparse

from google.appengine.api.urlfetch import fetch
from google.appengine.api import memcache

import logging

def ophan_api_key():
	return '1aba9898-5635-43d3-b545-9a01fec1ebf6'

def read_weeks_ophan_data():
	cached_content = memcache.get("ophan_summary")

	if cached_content:
		return json.loads(cached_content)

	base_url = "http://api.ophan.co.uk/api/mostread"

	params = {
		"api-key" : ophan_api_key(),
		"age" : 7 * 24 * 60 * 60,
		"count" : 50,
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

		ophan_data = read_weeks_ophan_data()
		popular_content = [read_content(result) for result in ophan_data]

		data['popular_content'] = popular_content
		memcache.add("popular_content", json.dumps(popular_content))

		self.response.out.write(json.dumps(data))

app = webapp2.WSGIApplication([('/tasks/ophan', ReadOphan)],
                              debug=True)