import headers

import webapp2
import json

from urllib import urlencode
from urlparse import urlparse

from google.appengine.api.urlfetch import fetch

import logging

def ophan_api_key():
	return "6d6abdd9-6860-4261-85dc-496292192a14"

def read_weeks_ophan_data():
	base_url = "http://api.ophan.co.uk/api/mostread"

	params = {
		"api-key" : ophan_api_key,
		"age" : 7 * 24 * 60 * 60
	}

	url = base_url + "?" + urlencode(params)
	
	result = fetch(url, deadline = 9)

	if not result.status_code == 200: return None

	return json.loads(result.content)

def read_content(ophan_data):
	base_url = "http://content.guardianapis.com"

	parsed_url = urlparse(ophan_data["url"])

	logging.info(parsed_url.path)

	url = base_url + parsed_url.path

	result = fetch(url, deadline = 6)

	if not result.status_code == 200: return None

	response = json.loads(result.content)

	content = response.get("response", {}).get("content", {})

	content['views'] = ophan_data['count']
	return content


class ReadOphan(webapp2.RequestHandler):
	def get(self):
		data = {"hello" : "world"}

		headers.json(self.response)

		data['popular_content'] = [read_content(result) for result in read_weeks_ophan_data()]

		self.response.out.write(json.dumps(data))

app = webapp2.WSGIApplication([('/tasks/ophan', ReadOphan)],
                              debug=True)