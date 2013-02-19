import logging

def type_tags(item):
	return [tag for tag in item.get("tags", []) if "type" == tag.get("type", "")]

def tone_tags(item):
	return [tag for tag in item.get("tags", []) if "tone" == tag.get("type", "")]

def of_type(content_type, item):
	return content_type in map(lambda x: x.get("id", ""), type_tags(item))

def with_tone(tone, item):
	return tone in [tag.get("id", "") for tag in tone_tags(item)]

def video(item) : return of_type("type/video", item)
def article(item) : return of_type("type/article", item)

def news(item) : return with_tone("tone/news", item)
def features(item) : return with_tone("tone/features", item)
def blog(item) : return with_tone("tone/blog", item) and not with_tone("tone/minutebyminute", item)

def live(item) : return with_tone("tone/blog", item) and with_tone("tone/minutebyminute", item)
def review(item) : return with_tone("tone/review", item)

def with_section(section_name, item):
	return section_name == item.get("sectionId", "")


def sport(item) : return with_section("sport", item)