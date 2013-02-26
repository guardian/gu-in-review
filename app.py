import data_filters

import webapp2
import jinja2
import os
import json
import logging
from urllib import quote, urlencode
from google.appengine.api import urlfetch
from google.appengine.api import memcache

from collections import namedtuple

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

ContentSection = namedtuple("ContentSection", ["id", "title", "size", "items"])

def categorise_content(content):
	if not content: return {}

	return {"videos" : [item for item in content if data_filters.video(item)],
		"news" : [item for item in content if data_filters.news(item)],
		"features" : [item for item in content if data_filters.features(item)],
		"blogs" : [item for item in content if data_filters.blog(item)],		
		"liveblogs" : [i for i in content if data_filters.live(i)],
		"reviews" : [i for i in content if data_filters.review(i)],
		"sport" : [i for i in content if data_filters.sport(i)],}

class MainPage(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('index.html')
		template_values = {}
		
		cached_content = memcache.get("popular_content")

		if cached_content:
			popular_content = json.loads(cached_content)
			popular_content = [i for i in popular_content if i]

			template_values['popular_content'] = popular_content

			categorised_content = categorise_content(popular_content)
			template_values.update(categorised_content)

			template_values["content_sections"] = sorted([ContentSection(k, k.title(), len(v), v) for k, v in categorised_content.items()], key = lambda x: x.size, reverse = True)

		self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage)], debug=True)