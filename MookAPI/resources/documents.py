from MookAPI import db
import datetime

from content_documents import *


class Resource(db.Document):
	"""
	Any elementary pedagogical resource.
	Contains the metadata and an embedded ResourceContent document.
	"""
	
	### PROPERTIES - METADATA

	## Title of the resource
	title = db.StringField(required=True)

	## Type of content
	## Allowed values: 
	## - video
	## - rich_text
	content_type = db.StringField(required=True)
	
	## Creator should reference a user
	## Will be implemented later
	# creator = db.ReferenceField('User')

	## Short description of the resource
	description = db.StringField()

	## List of keywords
	keywords = db.ListField(db.StringField())

	## Tags need to belong to a separate collection for indexation
	## Will be implemented later
	# tags = db.ListField(db.ReferenceField('ResourceTag'))

	## Date of creation
	date = db.DateTimeField(default=datetime.datetime.now, required=True)
	
	### PROPERTIES - CONTENT

	## Content of the resource
	content = db.EmbeddedDocumentField(ResourceContent)

	### METHODS

	def __unicode__(self):
		return self.title

	def toJSONObject(self):
		ret = {}
		ret["title"] = self.title.encode('utf_8')
		ret["content_type"] = self.content_type.encode('utf_8')
		ret["description"] = self.description.encode('utf_8')
		ret["date"] = self.date
		if ret["content_type"] == "video":
			resourceContent = ExternalVideoContent(self.content)
		elif ret["content_type"] == "rich_text":
			resourceContent = RichTextContent(self.content)
		ret["content"] = resourceContent.toJSONObject()
		return ret
