"""Definition of the Proxy File content type
"""
import os
import mimetypes
from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from collective.fsproxy.interfaces import IProxyFile
from collective.fsproxy.config import PROJECTNAME
from collective.fsproxy import fsproxyMessageFactory as _
from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName

ProxyFileSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    atapi.StringField(
        name='fsposition',
        required=1,
#        validators=('isURL',),
        widget=atapi.StringWidget(
            label=_(u"label_file_fs_position", default=u"Filesystem position for file to proxy"),
            description=_(u"help_file_position", default=u"Please enter the filesystem position where the file is."),
            i18n_domain="collective.fsproxy",
        ),
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

ProxyFileSchema['title'].storage = atapi.AnnotationStorage()
ProxyFileSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(ProxyFileSchema, moveDiscussion=False)


class ProxyFile(base.ATCTContent):
    """Description of the Example Type"""
    implements(IProxyFile)

    meta_type = "ProxyFile"
    schema = ProxyFileSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    security = ClassSecurityInfo()

    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    def getObjSize(self):
        return self.file_size()

    def get_data(self):
        field = self.getField('fsposition')
        path = field.get(self)
        tmp = open(path, 'r')
        return tmp.read()

    security.declareProtected(View, 'size')
    def file_size(self):
        """Get size (image_view.pt)
        """
        field = self.getField('fsposition')
        path = field.get(self)
        return os.path.getsize(path)

    def filename(self):
        field = self.getField('fsposition')
        path = field.get(self)
        filename = path.rsplit('/',1)[1]
        return filename

    def mime_type(self):
        failed = 'text/x-unknown-content-type'
        field = self.getField('fsposition')
        path = field.get(self)
        if mimetypes.guess_type(path) == (None,None):
            return failed
        return mimetypes.guess_type(path)[0]

    def getIcon(self, context):
        mtr = getToolByName(self, 'mimetypes_registry')
        res = mtr.lookup(self.mime_type())
        if len(res):
            return res[0].icon_path
        else:
            return "application.png"
    def mimetype_name(self):
        mtr = getToolByName(self, 'mimetypes_registry')
        res = mtr.lookup(self.mime_type())
        if len(res):
            return res[0].name()
        else:
            return "application"

    security.declareProtected(View, 'download')
    def download(self, REQUEST=None, RESPONSE=None):
        """Download the file (use default index_html)
        """
        if REQUEST is None:
            REQUEST = self.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE
        field = self.getField('fsposition')
        path = field.get(self)
        tmp = open(path, 'r')
        RESPONSE.setHeader("Content-type",self.mime_type()) 
        RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.filename())
#        RESPONSE.setHeader('Content-Length', len(str(sdata))) 
        return RESPONSE.write(tmp.read())

    security.declareProtected(View, 'get_content_type')
    def get_content_type(self):
        field = self.getField('fsposition')
        path = field.get(self)
        tmp = open(path, 'r')
        return len(tmp.read())

atapi.registerType(ProxyFile, PROJECTNAME)