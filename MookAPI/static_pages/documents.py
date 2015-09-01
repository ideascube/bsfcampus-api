from flask import url_for
from MookAPI.core import db
from MookAPI.sync import SyncableDocumentJsonSerializer, SyncableDocument

class StaticPageJsonSerializer(SyncableDocumentJsonSerializer):
    pass

class StaticPage(StaticPageJsonSerializer, SyncableDocument):

    page_id = db.StringField(unique=True, required=True)
    """An unique id used to reference this page"""

    footer_link_text = db.StringField(required=True)
    """The text that appears on the link towards this page"""

    html_content = db.StringField()
    """An HTML string containing the text of the page."""

    external_link = db.StringField()
    """if the link should redirect to an external page"""

    ### VIRTUAL PROPERTIES

    @property
    def url(self, _external=False):
        return url_for("static_pages.get_static_page", page_id=self.page_id, _external=_external)
