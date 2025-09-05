
def neo_tag(tag_name):
	def set_decorator(func):
		func.tag_name = tag_name
		return func
	return set_decorator

def get_functions_from_neo_tag(loc:dict,tag):
	return dict([(name, obj) for name, obj in loc.items() if
		  	     	               hasattr(obj, "tag_name") and getattr(obj, "tag_name") == tag])