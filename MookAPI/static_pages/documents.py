from MookAPI.core import db
from MookAPI.sync import SyncableDocumentJsonSerializer, SyncableDocument

class StaticPageJsonSerializer(SyncableDocumentJsonSerializer):
    pass

class StaticPage(StaticPageJsonSerializer, SyncableDocument):

    page_id = db.StringField(unique=True, required=True)
    """An unique id used to reference this page"""

    footer_link_text = db.StringField(required=True)
    """The text that appears on the link towards this page"""

    html_content = db.StringField(required=True)
    """An HTML string containing the text of the page."""
