import data_filters

import webapp2
import jinja2
import os
import json
import logging
from urllib import quote, urlencode
from google.appengine.api import urlfetch
from google.appengine.api import memcache

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

def categorise_content(content):
	if not content: return {}

	return {"videos" : [item for item in content if data_filters.video(item)],
		"news" : [item for item in content if data_filters.news(item)]}

class MainPage(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('index.html')
		
		popular_content = json.loads(memcache.get("popular_content"))

		template_values = {'popular_content' : popular_content}

		template_values.update(categorise_content(popular_content))

		self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage)], debug=True)