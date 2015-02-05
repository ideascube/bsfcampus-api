from MookAPI import db
import flask

def formatObjectToJSONCompliant(resource, firstPass=False):
	print('formatObjectToJSONCompliant {firstPass}'.format(firstPass=firstPass))
	if hasattr(resource, 'content'):
		print(resource.content)
	if firstPass:
		ret = {"id": str(resource.id)}
	else:
		ret = {}
	for prop in resource:
		print(prop)
		if prop != "id":
			print(type(resource[prop]))
			if isinstance(resource[prop], unicode):
				print(1)
				ret[prop] = resource[prop].encode('utf_8')
			elif resource[prop] == None:
				print(2)
				ret[prop] = None
			elif isinstance(resource[prop], list):
				print(3)
				ret[prop] = resource[prop]
			elif isinstance(resource[prop], db.EmbeddedDocument):
				print(4)
				ret[prop] = formatObjectToJSONCompliant(resource[prop])
			else:
				print(5)
				ret[prop] = resource[prop]
	print(ret)
	return ret